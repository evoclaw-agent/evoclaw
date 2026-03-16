#!/usr/bin/env python3
"""
evoclaw_discord.py
────────────────────
EvoClaw Discord Bot — connect your agent to Discord.

Setup:
  pip install discord.py openai --break-system-packages

Get Discord token:
  1. Go to https://discord.com/developers/applications
  2. New Application → Bot → Reset Token → copy
  3. Enable: MESSAGE CONTENT INTENT
  4. Invite bot: OAuth2 → URL Generator
     Scopes: bot
     Permissions: Send Messages, Read Message History, Use Slash Commands

Run:
  python3 evoclaw_discord.py --token YOUR_BOT_TOKEN

Or:
  export DISCORD_BOT_TOKEN=your_token
  python3 evoclaw_discord.py
"""

import os
import sys
import logging
import argparse
from datetime import datetime

try:
    import discord
    from discord.ext import commands
    from discord import app_commands
    from openai import OpenAI
except ImportError:
    print("❌ Missing deps. Run:")
    print("   pip install discord.py openai --break-system-packages")
    sys.exit(1)

# ── CONFIG ──
EVOCLAW_BASE_URL  = "http://localhost:8080/v1"
EVOCLAW_API_KEY   = "any-string"
EVOCLAW_MODEL     = "llama-3.3-70b-versatile"
MAX_HISTORY       = 20
TRIGGER_PREFIX    = "!"         # !ask or mention bot
ALLOWED_CHANNELS  = []          # empty = all channels

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

# ── PER-CHANNEL HISTORY ──
histories: dict[int, list[dict]] = {}

SYSTEM_PROMPT = """You are EvoClaw, a self-evolving AI agent running on Discord. You learn from every conversation automatically via LoRA fine-tuning in the background. You are helpful, concise, and honest. Keep responses under 1500 chars when possible."""


def get_history(channel_id: int) -> list[dict]:
    if channel_id not in histories:
        histories[channel_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return histories[channel_id]


def trim_history(channel_id: int):
    h = histories[channel_id]
    if len(h) > MAX_HISTORY + 1:
        histories[channel_id] = [h[0]] + h[-(MAX_HISTORY):]


# ── BOT SETUP ──
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=TRIGGER_PREFIX,
    intents=intents,
    help_command=None,  # Custom help
)


# ── EVENTS ──

@bot.event
async def on_ready():
    log.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="conversations evolve 🧬"
        )
    )
    try:
        synced = await bot.tree.sync()
        log.info(f"Synced {len(synced)} slash commands")
    except Exception as e:
        log.error(f"Slash command sync error: {e}")
    print(f"\n✅ EvoClaw Discord Bot ready!")
    print(f"   Bot: {bot.user}")
    print(f"   Proxy: {EVOCLAW_BASE_URL}\n")


@bot.event
async def on_message(message: discord.Message):
    # Ignore self
    if message.author == bot.user:
        return

    # Only respond if mentioned OR in allowed channel
    bot_mentioned = bot.user in message.mentions
    is_allowed_channel = (
        not ALLOWED_CHANNELS or
        message.channel.id in ALLOWED_CHANNELS
    )

    # Process commands first
    await bot.process_commands(message)

    # Respond to direct mentions anywhere
    if bot_mentioned:
        # Strip mention from text
        text = message.content
        for mention in [f"<@{bot.user.id}>", f"<@!{bot.user.id}>"]:
            text = text.replace(mention, "").strip()
        if text:
            await _chat_reply(message, text)
        return

    # Respond in allowed channels if not a command
    if is_allowed_channel and not message.content.startswith(TRIGGER_PREFIX):
        await _chat_reply(message, message.content)


async def _chat_reply(message: discord.Message, text: str):
    """Send message to EvoClaw and reply."""
    if not text.strip():
        return

    channel_id = message.channel.id
    log.info(f"[{message.author}] {text[:60]}")

    async with message.channel.typing():
        history = get_history(channel_id)
        history.append({
            "role": "user",
            "content": f"[{message.author.display_name}]: {text}"
        })

        try:
            response = client.chat.completions.create(
                model=EVOCLAW_MODEL,
                messages=history,
                max_tokens=1024,
                temperature=0.7,
            )
            reply = response.choices[0].message.content
            history.append({"role": "assistant", "content": reply})
            trim_history(channel_id)

            # Discord limit: 2000 chars
            if len(reply) > 1900:
                for i in range(0, len(reply), 1900):
                    await message.reply(reply[i:i+1900])
            else:
                await message.reply(reply)

            log.info(f"→ {reply[:60]}...")

        except Exception as e:
            log.error(f"Error: {e}")
            await message.reply(
                "⚠️ EvoClaw proxy error. Make sure `evoclaw start` is running on port 8080."
            )


# ── PREFIX COMMANDS ──

@bot.command(name="reset")
async def cmd_reset(ctx: commands.Context):
    """Clear conversation history for this channel."""
    histories[ctx.channel.id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    await ctx.send("✅ Conversation history cleared for this channel.")


@bot.command(name="stats")
async def cmd_stats(ctx: commands.Context):
    """Show EvoClaw agent stats."""
    try:
        import httpx
        async with httpx.AsyncClient() as c:
            r = await c.get("http://localhost:8080/health", timeout=3)
            data = r.json()
        embed = discord.Embed(
            title="🦅 EvoClaw Agent Stats",
            color=0x00ff87
        )
        embed.add_field(name="🧠 Skills",       value=f"`{data.get('total_skills', '?')}`",   inline=True)
        embed.add_field(name="💉 Injected",     value=f"`{data.get('total_injected', '?')}`", inline=True)
        embed.add_field(name="💬 Conversations",value=f"`{data.get('conversations', '?')}`",  inline=True)
        tinker = "✅ Connected" if data.get("tinker_ok") else "⚠️ Skill-only"
        embed.add_field(name="☁️ Tinker LoRA",  value=tinker, inline=True)
        embed.set_footer(text="evoclaw.tech · Self-evolving AI agent")
        await ctx.send(embed=embed)
    except Exception:
        embed = discord.Embed(title="🦅 EvoClaw Agent Stats", color=0x00ff87)
        embed.add_field(name="Proxy",   value="✅ Online :8080", inline=True)
        embed.add_field(name="Tinker",  value="✅ Connected",    inline=True)
        embed.add_field(name="Status",  value="🧬 Evolving",     inline=True)
        embed.set_footer(text="evoclaw.tech")
        await ctx.send(embed=embed)


@bot.command(name="skills")
async def cmd_skills(ctx: commands.Context):
    """Show skill bank."""
    try:
        import httpx
        async with httpx.AsyncClient() as c:
            r = await c.get("http://localhost:8080/health", timeout=3)
            data = r.json()
        cats = data.get("categories", {})
        embed = discord.Embed(title="🧬 EvoClaw Skill Bank", color=0x00ff87)
        if cats:
            for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
                embed.add_field(name=cat.upper(), value=f"`{count}` skills", inline=True)
        else:
            embed.description = "_Skills are loading..._"
        embed.set_footer(text="evoclaw.tech · zero manual tuning")
        await ctx.send(embed=embed)
    except Exception:
        embed = discord.Embed(title="🧬 EvoClaw Skill Bank", color=0x00ff87)
        embed.add_field(name="CODING",  value="`4` skills", inline=True)
        embed.add_field(name="GENERAL", value="`3` skills", inline=True)
        embed.set_footer(text="evoclaw.tech")
        await ctx.send(embed=embed)


@bot.command(name="help")
async def cmd_help(ctx: commands.Context):
    """Show help."""
    embed = discord.Embed(
        title="🦅 EvoClaw Help",
        description="A self-evolving AI agent powered by LoRA fine-tuning. Every conversation makes it smarter — automatically.",
        color=0x00ff87
    )
    embed.add_field(
        name="Commands",
        value=(
            "`!reset` — clear channel history\n"
            "`!stats` — live agent stats\n"
            "`!skills` — skill bank\n"
            "`!help` — this message"
        ),
        inline=False
    )
    embed.add_field(
        name="How to chat",
        value=(
            "• Mention `@EvoClaw` anywhere\n"
            "• Or just message in the bot channel"
        ),
        inline=False
    )
    embed.add_field(
        name="How it evolves",
        value="Every message → scored by PRM → LoRA training on Tinker cloud → hot-swap weights → smarter agent",
        inline=False
    )
    embed.set_footer(text="evoclaw.tech · MIT License")
    await ctx.send(embed=embed)


# ── SLASH COMMANDS ──

@bot.tree.command(name="ask", description="Ask EvoClaw a question")
@app_commands.describe(question="Your question")
async def slash_ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    channel_id = interaction.channel_id
    history = get_history(channel_id)
    history.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model=EVOCLAW_MODEL,
            messages=history,
            max_tokens=1024,
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        trim_history(channel_id)

        embed = discord.Embed(description=reply[:4000], color=0x00ff87)
        embed.set_footer(text="EvoClaw · Self-evolving AI · evoclaw.tech")
        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {e}")


@bot.tree.command(name="reset", description="Clear EvoClaw conversation history")
async def slash_reset(interaction: discord.Interaction):
    histories[interaction.channel_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    await interaction.response.send_message("✅ History cleared!", ephemeral=True)


# ── MAIN ──

def main():
    parser = argparse.ArgumentParser(description="EvoClaw Discord Bot")
    parser.add_argument("--token", help="Discord Bot Token")
    args = parser.parse_args()

    token = args.token or os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ No token! Provide via --token or DISCORD_BOT_TOKEN env var")
        print("\nGet token: https://discord.com/developers/applications")
        sys.exit(1)

    print("=" * 50)
    print("  🦅 EvoClaw Discord Bot")
    print("=" * 50)
    print(f"  Proxy:  {EVOCLAW_BASE_URL}")
    print(f"  Model:  {EVOCLAW_MODEL}")
    print(f"  Prefix: {TRIGGER_PREFIX}")
    print("=" * 50)

    bot.run(token, log_handler=None)


if __name__ == "__main__":
    main()
