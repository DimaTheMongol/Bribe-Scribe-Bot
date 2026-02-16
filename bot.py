# ==============================
# Main Imports
# ==============================

import os
from dotenv import load_dotenv

# ==============================
# Discord Imports
# ============================== 

import discord
from discord.ext import commands

# ==============================
# OpenAi Imports
# ==============================

from openai import OpenAI

# ==============================
# Internal Imports
# ==============================

from economy import init_db
from betting import init_betting_db
from commands.economy_commands import setup_economy_commands
from commands.llm_commands import setup_llm_commands
from commands.betting_commands import setup_betting_commands


# ==============================
# Configuration & Constants
# ==============================

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
client = OpenAI()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==============================
# Discord Bot Setup
# ==============================

@bot.event
async def on_ready():
    print("on_ready fired, initialising DB...")
    init_db()
    init_betting_db()
    print("DB init complete")
    print("Commands loaded:", [c.name for c in bot.commands])
    print(f"Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

# ==============================
# Commands
# ==============================

setup_llm_commands(bot, client)
setup_economy_commands(bot)
setup_betting_commands(bot)

# ==============================
# Finisher
# ==============================

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN missing in .env")
    bot.run(DISCORD_TOKEN)

