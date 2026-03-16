#!/usr/bin/env python3
"""
setup_bots.py
─────────────
Setup & launcher for EvoClaw Telegram + Discord bots.
Jalankan dari: ~/evoclaw/repo/
"""

import os, sys, subprocess

print("""
╔══════════════════════════════════════════╗
║   🦅 EvoClaw Bot Setup                  ║
╚══════════════════════════════════════════╝
""")

# ── Install deps ──
print("📦 Installing dependencies...")
subprocess.run([
    sys.executable, "-m", "pip", "install",
    "python-telegram-bot", "discord.py", "openai", "httpx",
    "--break-system-packages", "-q"
], check=True)
print("✅ Dependencies installed\n")

# ── Get tokens ──
print("═" * 44)
print("  TELEGRAM SETUP")
print("═" * 44)
print("1. Open Telegram → search @BotFather")
print("2. Send: /newbot")
print("3. Follow steps, copy the token\n")
tg_token = input("Paste Telegram Bot Token (or Enter to skip): ").strip()

print()
print("═" * 44)
print("  DISCORD SETUP")
print("═" * 44)
print("1. Go to: https://discord.com/developers/applications")
print("2. New Application → Bot → Reset Token → copy")
print("3. Enable: MESSAGE CONTENT INTENT (under Bot settings)")
print("4. Invite URL: OAuth2 → bot → Send Messages + Read Messages\n")
dc_token = input("Paste Discord Bot Token (or Enter to skip): ").strip()

# ── Save to .env ──
env_lines = []
if tg_token:
    env_lines.append(f"TELEGRAM_BOT_TOKEN={tg_token}")
if dc_token:
    env_lines.append(f"DISCORD_BOT_TOKEN={dc_token}")

if env_lines:
    with open(".env_bots", "w") as f:
        f.write("\n".join(env_lines) + "\n")
    print("\n✅ Tokens saved to .env_bots")

# ── Create screen launchers ──
if tg_token:
    with open("start_telegram.sh", "w") as f:
        f.write(f"""#!/bin/bash
export TELEGRAM_BOT_TOKEN="{tg_token}"
echo "🦅 Starting EvoClaw Telegram Bot..."
python3 evoclaw_telegram.py
""")
    os.chmod("start_telegram.sh", 0o755)
    print("✅ start_telegram.sh created")

if dc_token:
    with open("start_discord.sh", "w") as f:
        f.write(f"""#!/bin/bash
export DISCORD_BOT_TOKEN="{dc_token}"
echo "🦅 Starting EvoClaw Discord Bot..."
python3 evoclaw_discord.py
""")
    os.chmod("start_discord.sh", 0o755)
    print("✅ start_discord.sh created")

# ── Instructions ──
print("""
╔══════════════════════════════════════════╗
║   ✅ Setup complete!                     ║
╚══════════════════════════════════════════╝

Run bots in background (screen):
""")

if tg_token:
    print("  # Telegram:")
    print("  screen -S evoclaw-telegram")
    print("  bash start_telegram.sh")
    print("  Ctrl+A then D (detach)\n")

if dc_token:
    print("  # Discord:")
    print("  screen -S evoclaw-discord")
    print("  bash start_discord.sh")
    print("  Ctrl+A then D (detach)\n")

print("  # Check all running screens:")
print("  screen -ls\n")

if not tg_token and not dc_token:
    print("  ⚠️ No tokens entered. Run again when ready.\n")
    print("  Or run manually:")
    print("  python3 evoclaw_telegram.py --token YOUR_TOKEN")
    print("  python3 evoclaw_discord.py --token YOUR_TOKEN")
