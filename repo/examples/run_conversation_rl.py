"""
EvoClaw — Conversation RL Example
Equivalent to MetaClaw's run_conversation_rl.py

Starts the proxy, then runs a loop that:
1. Generates a response to a task
2. PRM scores it
3. Evolves skills from failures
4. Trains with Tinker LoRA (GRPO)

Usage:
  python examples/run_conversation_rl.py
  python examples/run_conversation_rl.py --mode opd
  python examples/run_conversation_rl.py --no-train  # skill injection only
"""
import asyncio, argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from openai import OpenAI

from evoclaw import EvoClawConfig, EvoClawProxy, SkillBank, PRMScorer, SkillEvolver, EvoClawTrainer, TrainingSample

# Sample tasks (like MetaClaw's task JSONL)
SAMPLE_TASKS = [
    "Explain how gas fees work in Ethereum and how to minimize them.",
    "Write a Python function to fetch token prices from a DeFi protocol.",
    "What are the risks of providing liquidity in a Uniswap v3 pool?",
    "How do I verify a smart contract is safe before interacting with it?",
    "Explain impermanent loss with a numerical example.",
    "Write async Python to monitor a wallet address for incoming transactions.",
    "What is the difference between a CEX and DEX? When would you use each?",
    "Explain the GRPO training algorithm in simple terms.",
]


async def run(config: EvoClawConfig, mode: str = "grpo"):
    config.loss_fn = mode
    
    bank = SkillBank(config)
    scorer = PRMScorer(config)
    evolver = SkillEvolver(config) if config.enable_skill_evolution else None
    trainer = EvoClawTrainer(config) if config.enable_tinker_training else None

    # Point OpenAI client at EvoClaw proxy
    # (Proxy handles injection; here we go direct to Groq for demo)
    client = OpenAI(
        base_url=config.target_api_url,
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    print(f"🦎 EvoClaw Conversation RL — mode={mode}")
    print(f"   Model: {config.target_model}")
    print(f"   Tasks: {len(SAMPLE_TASKS)}")
    print(f"   Tinker: {'enabled' if trainer and trainer.get_status()['tinker_connected'] else 'disabled'}")
    print()

    for step, task in enumerate(SAMPLE_TASKS * 3):  # 3 passes
        # Inject skills
        injection = bank.format_for_injection(task)
        system_msg = "You are a helpful AI assistant."
        if injection:
            system_msg += f"\n\n{injection}"

        # Generate
        try:
            response = client.chat.completions.create(
                model=config.target_model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": task},
                ],
                max_tokens=500,
            )
            assistant_msg = response.choices[0].message.content
        except Exception as e:
            print(f"❌ Generation error: {e}")
            continue

        # Score
        result = await scorer.score_async(task, assistant_msg)
        
        status = "✅" if result.score >= config.prm_threshold else ("⚠️ " if result.score >= config.evolution_threshold else "❌")
        print(f"Step {step+1:3d} | {status} {result.score:.2f} | [{result.skill_category}] {task[:50]}...")

        # Learn skill
        if result.skill_extracted:
            added = bank.add_skill(result.skill_extracted, result.skill_category, result.score)
            if added:
                print(f"          🧠 Skill learned: {result.skill_extracted[:60]}...")

        # Evolve on failure
        if result.is_failure and evolver:
            evolved = await evolver.evolve_async(
                task, assistant_msg, result.score, result.reasoning,
                bank.get_top_skills()
            )
            if evolved:
                bank.add_skill(evolved.text, evolved.category, 0.7, source="evolved")
                print(f"          🧬 Skill evolved: {evolved.text[:60]}...")

        # Train
        if trainer:
            trainer.add_sample(TrainingSample(
                user_msg=task,
                assistant_msg=assistant_msg,
                reward=result.score,
                skill_injected=injection,
            ))

        await asyncio.sleep(0.5)  # Rate limit

    # Final stats
    stats = bank.stats()
    print(f"""
╔════════════════════════════════════╗
║  🦎 EvoClaw Training Complete      ║
║  Total skills: {stats['total_skills']:<20} ║
║  Categories:   {str(stats['categories'])[:20]:<20} ║
╚════════════════════════════════════╝
""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["grpo", "opd"], default="grpo")
    parser.add_argument("--model", default=None)
    parser.add_argument("--no-train", action="store_true")
    args = parser.parse_args()

    # Load env
    env_path = os.path.expanduser("~/.evoclaw/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    if k not in os.environ:
                        os.environ[k] = v

    config = EvoClawConfig.load()
    if args.model:
        config.target_model = args.model
    if args.no_train:
        config.enable_tinker_training = False

    asyncio.run(run(config, args.mode))
