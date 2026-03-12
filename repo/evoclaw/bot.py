"""
evoclaw/bot.py
──────────────
Discord & Telegram Bot Integration for EvoClaw.

Deploy your self-evolving agent to Discord or Telegram with a single command.
Every message from your community becomes training data — the agent evolves
automatically from real conversations.

Usage (Discord):
    python -m evoclaw.bot discord --token YOUR_DISCORD_TOKEN --channel-id 123456

Usage (Telegram):
    python -m evoclaw.bot telegram --token YOUR_TELEGRAM_TOKEN

Or from Python:
    from evoclaw.bot import EvoBotDiscord, EvoBotTelegram

    # Discord
    bot = EvoBotDiscord(
        discord_token="...",
        evoclaw_url="http://localhost:8000",  # Your OpenClaw proxy
        channel_ids=[123456789],              # Channels to listen to
    )
    bot.run()

    # Telegram
    bot = EvoBotTelegram(
        telegram_token="...",
        evoclaw_url="http://localhost:8000",
    )
    bot.run()

Requirements:
    pip install discord.py python-telegram-bot httpx
"""

import asyncio
import json
import os
import httpx
from typing import Optional, List


# ══════════════════════════════════════════════════════════════════════════════
# Shared: call EvoClaw OpenClaw proxy
# ══════════════════════════════════════════════════════════════════════════════

async def call_evoclaw(
    message: str,
    user_id: str,
    evoclaw_url: str = "http://localhost:8000",
    model: str = "moonshotai/Kimi-2.5",
    system_prompt: str = "You are a helpful AI assistant powered by EvoClaw — a self-evolving agent framework.",
) -> str:
    """
    Send a message to the EvoClaw proxy and get a response.
    The proxy automatically handles PRM scoring, skill injection, and Tinker training.
    """
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        "max_tokens": 1024,
        "user": user_id,  # Used for per-user conversation tracking
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{evoclaw_url}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


# ══════════════════════════════════════════════════════════════════════════════
# Discord Bot
# ══════════════════════════════════════════════════════════════════════════════

class EvoBotDiscord:
    """
    Discord bot that connects to your EvoClaw self-evolving agent.

    Args:
        discord_token:  Your Discord bot token (from discord.com/developers)
        evoclaw_url:    URL of your running EvoClaw/OpenClaw proxy
        channel_ids:    List of channel IDs to listen to (empty = all channels)
        model:          Base model name
        prefix:         Command prefix (default: "!")
        system_prompt:  Custom system prompt for the agent
    """

    def __init__(
        self,
        discord_token: Optional[str] = None,
        evoclaw_url: str = "http://localhost:8000",
        channel_ids: Optional[List[int]] = None,
        model: str = "moonshotai/Kimi-2.5",
        prefix: str = "!",
        system_prompt: str = "You are a helpful AI assistant powered by EvoClaw.",
    ):
        try:
            import discord
        except ImportError:
            raise ImportError("Install discord.py: pip install discord.py")

        self.token = discord_token or os.environ.get("DISCORD_TOKEN", "")
        self.evoclaw_url = evoclaw_url
        self.channel_ids = set(channel_ids or [])
        self.model = model
        self.prefix = prefix
        self.system_prompt = system_prompt

        if not self.token:
            raise ValueError("Discord token required. Pass discord_token= or set DISCORD_TOKEN env var.")

        # Setup Discord client
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        self._register_events()

    def _register_events(self):
        import discord

        @self.client.event
        async def on_ready():
            print(f"🦎 EvoClaw Discord Bot ready — logged in as {self.client.user}")
            print(f"   Proxy: {self.evoclaw_url}")
            print(f"   Channels: {'all' if not self.channel_ids else self.channel_ids}")

        @self.client.event
        async def on_message(message):
            # Ignore bot's own messages
            if message.author == self.client.user:
                return

            # Filter channels if specified
            if self.channel_ids and message.channel.id not in self.channel_ids:
                return

            # Only respond to mentions or messages starting with prefix
            bot_mentioned = self.client.user in message.mentions
            has_prefix = message.content.startswith(self.prefix + "ask")

            if not (bot_mentioned or has_prefix):
                return

            # Clean the message
            content = message.content
            if bot_mentioned:
                content = content.replace(f"<@{self.client.user.id}>", "").strip()
            elif has_prefix:
                content = content[len(self.prefix + "ask"):].strip()

            if not content:
                await message.channel.send("Hey! Ask me anything. 🦎")
                return

            # Show typing indicator while processing
            async with message.channel.typing():
                try:
                    response = await call_evoclaw(
                        message=content,
                        user_id=str(message.author.id),
                        evoclaw_url=self.evoclaw_url,
                        model=self.model,
                        system_prompt=self.system_prompt,
                    )
                    # Discord has 2000 char limit — split if needed
                    if len(response) > 1900:
                        chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                        for chunk in chunks:
                            await message.channel.send(chunk)
                    else:
                        await message.channel.send(response)
                except Exception as e:
                    await message.channel.send(f"⚠️ Agent error: {e}")

    def run(self):
        """Start the Discord bot."""
        print("🦎 Starting EvoClaw Discord Bot...")
        self.client.run(self.token)


# ══════════════════════════════════════════════════════════════════════════════
# Telegram Bot
# ══════════════════════════════════════════════════════════════════════════════

class EvoBotTelegram:
    """
    Telegram bot that connects to your EvoClaw self-evolving agent.

    Args:
        telegram_token: Your Telegram bot token (from @BotFather)
        evoclaw_url:    URL of your running EvoClaw/OpenClaw proxy
        model:          Base model name
        system_prompt:  Custom system prompt for the agent
        allowed_chats:  List of chat IDs to respond to (empty = all chats)
    """

    def __init__(
        self,
        telegram_token: Optional[str] = None,
        evoclaw_url: str = "http://localhost:8000",
        model: str = "moonshotai/Kimi-2.5",
        system_prompt: str = "You are a helpful AI assistant powered by EvoClaw.",
        allowed_chats: Optional[List[int]] = None,
    ):
        try:
            from telegram.ext import ApplicationBuilder
        except ImportError:
            raise ImportError("Install python-telegram-bot: pip install python-telegram-bot")

        self.token = telegram_token or os.environ.get("TELEGRAM_TOKEN", "")
        self.evoclaw_url = evoclaw_url
        self.model = model
        self.system_prompt = system_prompt
        self.allowed_chats = set(allowed_chats or [])

        if not self.token:
            raise ValueError("Telegram token required. Pass telegram_token= or set TELEGRAM_TOKEN env var.")

    def run(self):
        """Start the Telegram bot."""
        from telegram import Update
        from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

        async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
            chat_id = update.effective_chat.id

            # Filter chats if specified
            if self.allowed_chats and chat_id not in self.allowed_chats:
                return

            user_id = str(update.effective_user.id)
            text = update.message.text or ""

            if not text:
                return

            # Show typing indicator
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")

            try:
                response = await call_evoclaw(
                    message=text,
                    user_id=user_id,
                    evoclaw_url=self.evoclaw_url,
                    model=self.model,
                    system_prompt=self.system_prompt,
                )
                # Telegram has 4096 char limit
                if len(response) > 4000:
                    chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
                    for chunk in chunks:
                        await update.message.reply_text(chunk)
                else:
                    await update.message.reply_text(response)
            except Exception as e:
                await update.message.reply_text(f"⚠️ Agent error: {e}")

        app = ApplicationBuilder().token(self.token).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print(f"🦎 EvoClaw Telegram Bot started!")
        print(f"   Proxy: {self.evoclaw_url}")
        app.run_polling()


# ══════════════════════════════════════════════════════════════════════════════
# CLI Entry Point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EvoClaw Bot — Deploy your agent to Discord or Telegram")
    subparsers = parser.add_subparsers(dest="platform", required=True)

    # Discord subcommand
    dc = subparsers.add_parser("discord", help="Run Discord bot")
    dc.add_argument("--token", default=os.environ.get("DISCORD_TOKEN"), help="Discord bot token")
    dc.add_argument("--channel-id", type=int, nargs="*", default=[], help="Channel IDs to listen to")
    dc.add_argument("--proxy", default="http://localhost:8000", help="EvoClaw proxy URL")
    dc.add_argument("--model", default="moonshotai/Kimi-2.5", help="Base model")
    dc.add_argument("--system-prompt", default="You are a helpful AI assistant powered by EvoClaw.", help="System prompt")

    # Telegram subcommand
    tg = subparsers.add_parser("telegram", help="Run Telegram bot")
    tg.add_argument("--token", default=os.environ.get("TELEGRAM_TOKEN"), help="Telegram bot token")
    tg.add_argument("--proxy", default="http://localhost:8000", help="EvoClaw proxy URL")
    tg.add_argument("--model", default="moonshotai/Kimi-2.5", help="Base model")
    tg.add_argument("--system-prompt", default="You are a helpful AI assistant powered by EvoClaw.", help="System prompt")
    tg.add_argument("--allowed-chat", type=int, nargs="*", default=[], help="Allowed chat IDs")

    args = parser.parse_args()

    if args.platform == "discord":
        bot = EvoBotDiscord(
            discord_token=args.token,
            evoclaw_url=args.proxy,
            channel_ids=args.channel_id,
            model=args.model,
            system_prompt=args.system_prompt,
        )
        bot.run()

    elif args.platform == "telegram":
        bot = EvoBotTelegram(
            telegram_token=args.token,
            evoclaw_url=args.proxy,
            model=args.model,
            system_prompt=args.system_prompt,
            allowed_chats=args.allowed_chat,
        )
        bot.run()
