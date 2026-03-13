"""
EvoClaw Trainer
Online LoRA fine-tuning via Tinker cloud.
Supports:
  - GRPO (Reinforcement Learning from conversation rewards)
  - OPD (On-Policy Distillation from high-quality responses)
No GPU required. Runs from your laptop.
"""
import os, time, asyncio, threading
from typing import Optional
from dataclasses import dataclass
from collections import deque

try:
    import tinker
    from tinker import types as tinker_types
    TINKER_AVAILABLE = True
except ImportError:
    TINKER_AVAILABLE = False


@dataclass
class TrainingSample:
    user_msg: str
    assistant_msg: str
    reward: float           # PRM score (0.0–1.0)
    skill_injected: str     # Skills that were injected (context)


class EvoClawTrainer:
    """
    Wraps Tinker API for EvoClaw's online training loop.
    Collects samples from the proxy, trains in background when batch is full.
    """

    def __init__(self, config):
        self.config = config
        self._samples: deque = deque(maxlen=config.batch_size * 4)
        self._step = 0
        self._training_client = None
        self._sampling_client = None
        self._tokenizer = None
        self._lock = threading.Lock()
        self._running = False
        self._train_thread = None

        if not TINKER_AVAILABLE:
            print("⚠️  tinker not installed — training disabled. pip install tinker")
            return

        api_key = os.environ.get("TINKER_API_KEY", "")
        if not api_key:
            print("⚠️  TINKER_API_KEY not set — training disabled.")
            return

        self._init_tinker()

    def _init_tinker(self):
        try:
            print(f"🔧 Connecting to Tinker ({self.config.model_name})...")
            service_client = tinker.ServiceClient()
            self._training_client = service_client.create_lora_training_client(
                base_model=self.config.model_name,
                rank=self.config.lora_rank,
            )
            self._tokenizer = self._training_client.get_tokenizer()
            print(f"✅ Tinker connected. Model: {self.config.model_name}")
        except Exception as e:
            print(f"⚠️  Tinker init error: {e}")
            self._training_client = None

    def add_sample(self, sample: TrainingSample):
        """Add a scored sample to the training buffer."""
        with self._lock:
            self._samples.append(sample)
            count = len(self._samples)

        # Trigger training when buffer is full
        if count >= self.config.batch_size and self._training_client:
            self._trigger_training()

    def _trigger_training(self):
        """Kick off async training in a background thread."""
        if self._running:
            return
        self._running = True
        self._train_thread = threading.Thread(target=self._train_loop, daemon=True)
        self._train_thread.start()

    def _train_loop(self):
        try:
            with self._lock:
                batch = list(self._samples)[-self.config.batch_size:]

            if self.config.loss_fn in ("grpo", "importance_sampling"):
                self._train_grpo(batch)
            else:
                self._train_opd(batch)

            self._step += 1

            # Save weights to Tinker periodically
            if self._step % self.config.tinker_save_every == 0:
                self._save_weights()

        except Exception as e:
            print(f"⚠️  Training loop error: {e}")
        finally:
            self._running = False

    def _train_grpo(self, batch: list[TrainingSample]):
        """
        GRPO: Group Relative Policy Optimization
        Uses PRM scores as reward signal. High-score responses get positive gradient.
        """
        if not self._training_client or not self._tokenizer:
            return

        print(f"🏋️  GRPO training step {self._step + 1} on {len(batch)} samples...")
        tokenizer = self._tokenizer

        datums = []
        for sample in batch:
            # Format as chat: inject skills into system prompt
            system = "You are a helpful AI assistant."
            if sample.skill_injected:
                system += f"\n\n{sample.skill_injected}"

            prompt_text = (
                f"<|im_start|>system\n{system}<|im_end|>\n"
                f"<|im_start|>user\n{sample.user_msg}<|im_end|>\n"
                f"<|im_start|>assistant\n"
            )
            completion_text = f"{sample.assistant_msg}<|im_end|>\n"

            prompt_tokens = tokenizer.encode(prompt_text, add_special_tokens=True)
            completion_tokens = tokenizer.encode(completion_text, add_special_tokens=False)

            # Weight completions by reward (GRPO-style)
            # Positive reward = learn from it. Low reward = suppress it.
            reward_weight = max(0.0, (sample.reward - 0.5) * 2)  # Normalize to [-1, 1] then clip

            tokens = prompt_tokens + completion_tokens
            weights = [0.0] * len(prompt_tokens) + [reward_weight] * len(completion_tokens)

            input_tokens = tokens[:-1]
            target_tokens = tokens[1:]
            weights = weights[1:]

            datum = tinker_types.Datum(
                model_input=tinker_types.ModelInput.from_ints(tokens=input_tokens),
                loss_fn_inputs=dict(
                    weights=weights,
                    target_tokens=target_tokens,
                )
            )
            datums.append(datum)

        try:
            fwd_future = self._training_client.forward_backward(datums, "cross_entropy")
            opt_future = self._training_client.optim_step(
                tinker_types.AdamParams(learning_rate=self.config.learning_rate)
            )
            fwd_result = fwd_future.result()
            opt_future.result()

            import numpy as np
            # Compute mean reward of batch
            mean_reward = sum(s.reward for s in batch) / len(batch)
            print(f"   ✅ Step {self._step+1}: mean_reward={mean_reward:.3f}")

        except Exception as e:
            print(f"⚠️  GRPO training error: {e}")

    def _train_opd(self, batch: list[TrainingSample]):
        """
        OPD: On-Policy Distillation
        Learn directly from high-quality responses (reward >= threshold).
        """
        if not self._training_client or not self._tokenizer:
            return

        # Filter only high-quality samples
        good_samples = [s for s in batch if s.reward >= self.config.prm_threshold]
        if not good_samples:
            print("   ℹ️  No high-quality samples for OPD this step")
            return

        print(f"🏋️  OPD training step {self._step + 1} on {len(good_samples)}/{len(batch)} high-quality samples...")
        tokenizer = self._tokenizer
        datums = []

        for sample in good_samples:
            system = "You are a helpful AI assistant."
            if sample.skill_injected:
                system += f"\n\n{sample.skill_injected}"

            prompt_text = (
                f"<|im_start|>system\n{system}<|im_end|>\n"
                f"<|im_start|>user\n{sample.user_msg}<|im_end|>\n"
                f"<|im_start|>assistant\n"
            )
            completion_text = f"{sample.assistant_msg}<|im_end|>\n"

            prompt_tokens = tokenizer.encode(prompt_text, add_special_tokens=True)
            completion_tokens = tokenizer.encode(completion_text, add_special_tokens=False)

            tokens = prompt_tokens + completion_tokens
            weights = [0] * len(prompt_tokens) + [1] * len(completion_tokens)

            input_tokens = tokens[:-1]
            target_tokens = tokens[1:]
            weights = weights[1:]

            datum = tinker_types.Datum(
                model_input=tinker_types.ModelInput.from_ints(tokens=input_tokens),
                loss_fn_inputs=dict(weights=weights, target_tokens=target_tokens)
            )
            datums.append(datum)

        try:
            fwd_future = self._training_client.forward_backward(datums, "cross_entropy")
            opt_future = self._training_client.optim_step(
                tinker_types.AdamParams(learning_rate=self.config.learning_rate)
            )
            fwd_future.result()
            opt_future.result()
            print(f"   ✅ OPD step {self._step+1} complete")
        except Exception as e:
            print(f"⚠️  OPD training error: {e}")

    def _save_weights(self):
        """Save model weights to Tinker for later download/deployment."""
        if not self._training_client:
            return
        try:
            print(f"💾 Saving weights to Tinker ({self.config.tinker_model_tag}-step{self._step})...")
            self._sampling_client = self._training_client.save_weights_and_get_sampling_client(
                name=f"{self.config.tinker_model_tag}-step{self._step}"
            )
            print(f"   ✅ Weights saved: {self.config.tinker_model_tag}-step{self._step}")
        except Exception as e:
            print(f"⚠️  Weight save error: {e}")

    def get_status(self) -> dict:
        return {
            "step": self._step,
            "buffer_size": len(self._samples),
            "tinker_connected": self._training_client is not None,
            "is_training": self._running,
            "model": self.config.model_name,
        }
