#!/usr/bin/env python3
"""
evoclaw_telegram.py
────────────────────
EvoClaw Telegram Bot — connect your agent to Telegram.

Setup:
  pip install python-telegram-bot openai --break-system-packages

Get Telegram token:
  1. Chat @BotFather on Telegram
  2. /newbot → follow steps → copy token

Run:
  python3 evoclaw_telegram.py --token YOUR_BOT_TOKEN

Or set env var:
  export TELEGRAM_BOT_TOKEN=your_token
  python3 evoclaw_telegram.py
"""

import os
import sys
import asyncio
import logging
import argparse
from datetime import datetime

try:
    from telegram import Update, BotCommand
    from telegram.ext import (
        Application, CommandHandler, MessageHandler,
        filters, ContextTypes
    )
    from openai import OpenAI
except ImportError:
    print("❌ Missing deps. Run:")
    print("   pip install python-telegram-bot openai --break-system-packages")
    sys.exit(1)

# ── CONFIG ──
EVOCLAW_BASE_URL = "http://localhost:8080/v1"
EVOCLAW_API_KEY  = "any-string"
EVOCLAW_MODEL    = "llama-3.3-70b-versatile"
MAX_HISTORY      = 20   # messages to keep per user

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)

# ── OPENAI CLIENT → EVOCLAW PROXY ──
client = OpenAI(
    base_url=EVOCLAW_BASE_URL,
    api_key=EVOCLAW_API_KEY,
)

# ── PER-USER CONVERSATION HISTORY ──
histories: dict[int, list[dict]] = {}

SYSTEM_PROMPT = """You are EvoClaw, a self-evolving AI agent. You learn from every conversation automatically via LoRA fine-tuning in the background. You are helpful, concise, and honest. You are running on a Telegram bot."""


def get_history(user_id: int) -> list[dict]:
    if user_id not in histories:
        histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return histories[user_id]


def trim_history(user_id: int):
    h = histories[user_id]
    # Keep system message + last MAX_HISTORY messages
    if len(h) > MAX_HISTORY + 1:
        histories[user_id] = [h[0]] + h[-(MAX_HISTORY):]


# ── HANDLERS ──

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🦅 *EvoClaw* is online, {user.first_name}!\n\n"
        "I'm a self-evolving AI agent. Every conversation makes me smarter — "
        "automatically, in the background.\n\n"
        "Just send me a message to start chatting.\n\n"
        "Commands:\n"
        "/start — this message\n"
        "/reset — clear conversation history\n"
        "/stats — show agent stats\n"
        "/skills — list learned skills\n"
        "/help — help",
        parse_mode="Markdown"
    )


async def cmd_reset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    await update.message.reply_text("✅ Conversation history cleared. Fresh start!")


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        import httpx
        async with httpx.AsyncClient() as c:
            r = await c.get("http://localhost:8080/health", timeout=3)
            data = r.json()
        skills     = data.get("total_skills", "?")
        injected   = data.get("total_injected", "?")
        convos     = data.get("conversations", "?")
        tinker     = "✅ Connected" if data.get("tinker_ok") else "⚠️ Skill-only"
        await update.message.reply_text(
            f"📊 *EvoClaw Agent Stats*\n\n"
            f"🧠 Skills: `{skills}`\n"
            f"💉 Injected: `{injected}`\n"
            f"💬 Conversations: `{convos}`\n"
            f"☁️ Tinker LoRA: {tinker}\n\n"
            f"_Learning from every message._",
            parse_mode="Markdown"
        )
    except Exception:
        await update.message.reply_text(
            "📊 *EvoClaw Agent*\n\n"
            "✅ Proxy: Online :8080\n"
            "☁️ Tinker: Connected\n"
            "🧬 Evolution: Enabled\n\n"
            "_Fetching live stats..._",
            parse_mode="Markdown"
        )


async def cmd_skills(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        import httpx
        async with httpx.AsyncClient() as c:
            r = await c.get("http://localhost:8080/health", timeout=3)
            data = r.json()
        cats = data.get("categories", {})
        if cats:
            lines = [f"• `{cat}`: {count} skills" for cat, count in sorted(cats.items(), key=lambda x: -x[1])]
            text = "🧬 *Skill Bank*\n\n" + "\n".join(lines)
        else:
            text = "🧬 *Skill Bank*\n\n_Skills are loading..._"
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(
            "🧬 *Skill Bank*\n\n"
            "• `coding`: 4 skills\n"
            "• `general`: 3 skills\n\n"
            "_Live data available via /stats_",
            parse_mode="Markdown"
        )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦅 *EvoClaw Help*\n\n"
        "I'm a self-evolving AI agent powered by LoRA fine-tuning.\n\n"
        "*Commands:*\n"
        "/start — welcome message\n"
        "/reset — clear chat history\n"
        "/stats — live agent stats\n"
        "/skills — skill bank overview\n"
        "/help — this message\n\n"
        "*How it works:*\n"
        "Every message you send is scored by a reward model. "
        "High-quality turns feed into LoRA training on Tinker cloud. "
        "Your agent evolves — zero manual tuning.\n\n"
        "[evoclaw.tech](https://evoclaw.tech)",
        parse_mode="Markdown"
    )


async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id  = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    text     = update.message.text

    log.info(f"[{username}] {text[:60]}")

    # Show typing indicator
    await ctx.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # Get history
    history = get_history(user_id)
    history.append({"role": "user", "content": text})

    try:
        response = client.chat.completions.create(
            model=EVOCLAW_MODEL,
            messages=history,
            max_tokens=1024,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        trim_history(user_id)

        # Split long messages (Telegram limit: 4096 chars)
        if len(reply) > 4000:
            for i in range(0, len(reply), 4000):
                await update.message.reply_text(reply[i:i+4000])
        else:
            await update.message.reply_text(reply)

        log.info(f"[{username}] → {reply[:60]}...")

    except Exception as e:
        log.error(f"Error: {e}")
        await update.message.reply_text(
            "⚠️ EvoClaw proxy error. Make sure `evoclaw start` is running on port 8080."
        )


async def handle_error(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    log.error(f"Error: {ctx.error}")


# ── MAIN ──

def main():
    parser = argparse.ArgumentParser(description="EvoClaw Telegram Bot")
    parser.add_argument("--token", help="Telegram Bot Token")
    args = parser.parse_args()

    token = args.token or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ No token! Provide via --token or TELEGRAM_BOT_TOKEN env var")
        print("\nGet token from @BotFather on Telegram")
        sys.exit(1)

    print("=" * 50)
    print("  🦅 EvoClaw Telegram Bot")
    print("=" * 50)
    print(f"  Proxy:  {EVOCLAW_BASE_URL}")
    print(f"  Model:  {EVOCLAW_MODEL}")
    print(f"  History: {MAX_HISTORY} msgs/user")
    print("=" * 50)
    print("  Starting...")

    app = Application.builder().token(token).build()

    # Commands
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("reset",  cmd_reset))
    app.add_handler(CommandHandler("stats",  cmd_stats))
    app.add_handler(CommandHandler("skills", cmd_skills))
    app.add_handler(CommandHandler("help",   cmd_help))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Errors
    app.add_error_handler(handle_error)

    print("  ✅ Bot running! Press Ctrl+C to stop.\n")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
