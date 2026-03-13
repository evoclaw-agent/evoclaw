"""
EvoClaw CLI
evoclaw init     → setup API keys
evoclaw start    → start proxy on localhost:8080
evoclaw status   → show skill bank + trainer status
evoclaw skills   → list all learned skills
evoclaw clear    → reset skill bank
evoclaw train    → run training loop directly (no proxy)
"""
import os, sys, json, argparse

def cmd_init():
    print("🦎 EvoClaw Setup\n")
    
    # Groq
    groq_key = input("Groq API key (from console.groq.com): ").strip()
    if groq_key:
        _write_env("GROQ_API_KEY", groq_key)
        print("✅ GROQ_API_KEY saved")

    # Tinker
    tinker_key = input("Tinker API key (from thinkingmachines.ai): ").strip()
    if tinker_key:
        _write_env("TINKER_API_KEY", tinker_key)
        print("✅ TINKER_API_KEY saved")

    # Optional Redis
    redis = input("Upstash Redis URL (optional, press Enter to skip): ").strip()
    if redis:
        redis_token = input("Upstash Redis Token: ").strip()
        _write_env("REDIS_URL", redis)
        _write_env("REDIS_TOKEN", redis_token)
        print("✅ Redis configured")

    # Model
    print("\nModel options (Tinker):")
    print("  1. Qwen/Qwen3-4B  (fast, free tier)")
    print("  2. meta-llama/Llama-3.1-8B  (balanced)")
    print("  3. moonshotai/Kimi-K2.5  (best, same as MetaClaw)")
    choice = input("Choose [1-3, default=1]: ").strip() or "1"
    models = {
        "1": "Qwen/Qwen3-4B",
        "2": "meta-llama/Llama-3.1-8B",
        "3": "moonshotai/Kimi-K2.5",
    }
    model = models.get(choice, "Qwen/Qwen3-4B")
    
    # Save config
    from .config import EvoClawConfig
    config = EvoClawConfig(
        model_name=model,
        redis_url=redis or None,
        redis_token=redis_token if redis else None,
    )
    config.save()
    
    print(f"""
✅ EvoClaw configured!
   Model: {model}
   
Next step:
  evoclaw start
""")


def cmd_start(args):
    # Load env from .evoclaw/.env
    _load_env()
    
    from .config import EvoClawConfig
    from .proxy import EvoClawProxy
    
    config = EvoClawConfig.load()
    if hasattr(args, 'port') and args.port:
        config.proxy_port = args.port
    if hasattr(args, 'model') and args.model:
        config.target_model = args.model
    if hasattr(args, 'no_train') and args.no_train:
        config.enable_tinker_training = False

    proxy = EvoClawProxy(config)
    proxy.run()


def cmd_status():
    _load_env()
    from .config import EvoClawConfig
    from .skills import SkillBank
    
    config = EvoClawConfig.load()
    bank = SkillBank(config)
    stats = bank.stats()
    
    print(f"""
🦎 EvoClaw Status
─────────────────
Model:           {config.model_name}
Proxy port:      {config.proxy_port}
Target API:      {config.target_api_url}

Skills:          {stats['total_skills']} total
Injected:        {stats['total_injected']} times
Categories:      {json.dumps(stats['categories'], indent=14)}

Tinker training: {'enabled' if config.enable_tinker_training else 'disabled'}
Skill evolution: {'enabled' if config.enable_skill_evolution else 'disabled'}
PRM scoring:     {'enabled' if config.use_prm else 'disabled'}
""")


def cmd_skills(args):
    _load_env()
    from .config import EvoClawConfig
    from .skills import SkillBank
    
    config = EvoClawConfig.load()
    bank = SkillBank(config)
    
    category_filter = getattr(args, 'category', None)
    
    skills = bank._data["skills"]
    if category_filter:
        skills = [s for s in skills if s["category"] == category_filter]
    
    print(f"\n🦎 EvoClaw Skills ({len(skills)} total)\n")
    for i, s in enumerate(skills, 1):
        source_tag = f"[{s.get('source', 'default')}]"
        print(f"  {i:3}. [{s['category']}] {source_tag}")
        print(f"       {s['text'][:100]}")
        print()


def cmd_clear():
    _load_env()
    confirm = input("⚠️  This will delete all learned skills. Type 'yes' to confirm: ")
    if confirm.strip().lower() != "yes":
        print("Cancelled.")
        return
    
    from .config import EvoClawConfig
    config = EvoClawConfig.load()
    path = config.skills_path
    if os.path.exists(path):
        os.remove(path)
    print("✅ Skill bank cleared. Defaults will reload on next start.")


def cmd_train(args):
    """Run training loop directly from a JSONL conversation file."""
    _load_env()
    from .config import EvoClawConfig
    from .skills import SkillBank
    from .scorer import PRMScorer
    from .evolver import SkillEvolver
    from .trainer import EvoClawTrainer, TrainingSample
    
    config = EvoClawConfig.load()
    bank = SkillBank(config)
    scorer = PRMScorer(config)
    trainer = EvoClawTrainer(config)

    file = getattr(args, 'file', None)
    if not file or not os.path.exists(file):
        print(f"❌ File not found: {file}")
        print("Usage: evoclaw train --file conversations.jsonl")
        print("Format: {\"user\": \"...\", \"assistant\": \"...\"}")
        return

    with open(file) as f:
        lines = [json.loads(l) for l in f if l.strip()]
    
    print(f"🏋️  Training on {len(lines)} conversations...")
    for i, line in enumerate(lines, 1):
        user = line.get("user", "")
        assistant = line.get("assistant", "")
        if not user or not assistant:
            continue
        
        result = scorer.score(user, assistant)
        print(f"  {i}/{len(lines)} score={result.score:.2f} [{result.skill_category}]")
        
        if result.skill_extracted:
            added = bank.add_skill(result.skill_extracted, result.skill_category, result.score)
            if added:
                print(f"    🧠 Skill learned!")
        
        if trainer:
            trainer.add_sample(TrainingSample(
                user_msg=user,
                assistant_msg=assistant,
                reward=result.score,
                skill_injected=bank.format_for_injection(user),
            ))

    print(f"\n✅ Training complete. Skills: {bank.stats()['total_skills']}")


def _write_env(key: str, value: str):
    env_path = os.path.expanduser("~/.evoclaw/.env")
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    lines = []
    if os.path.exists(env_path):
        with open(env_path) as f:
            lines = [l for l in f.readlines() if not l.startswith(f"{key}=")]
    lines.append(f"{key}={value}\n")
    with open(env_path, "w") as f:
        f.writelines(lines)


def _load_env():
    env_path = os.path.expanduser("~/.evoclaw/.env")
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                if k not in os.environ:
                    os.environ[k] = v


def main():
    parser = argparse.ArgumentParser(
        prog="evoclaw",
        description="🦎 EvoClaw — Self-evolving AI agents via LoRA"
    )
    sub = parser.add_subparsers(dest="command")

    # init
    sub.add_parser("init", help="Setup API keys and config")

    # start
    p_start = sub.add_parser("start", help="Start the proxy server")
    p_start.add_argument("--port", type=int, help="Proxy port (default: 8080)")
    p_start.add_argument("--model", type=str, help="Override target model")
    p_start.add_argument("--no-train", action="store_true", help="Disable Tinker training")

    # status
    sub.add_parser("status", help="Show current status")

    # skills
    p_skills = sub.add_parser("skills", help="List learned skills")
    p_skills.add_argument("--category", type=str, help="Filter by category")

    # clear
    sub.add_parser("clear", help="Reset skill bank")

    # train
    p_train = sub.add_parser("train", help="Train from JSONL file")
    p_train.add_argument("--file", type=str, required=True, help="Path to JSONL file")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init()
    elif args.command == "start":
        cmd_start(args)
    elif args.command == "status":
        cmd_status()
    elif args.command == "skills":
        cmd_skills(args)
    elif args.command == "clear":
        cmd_clear()
    elif args.command == "train":
        cmd_train(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
