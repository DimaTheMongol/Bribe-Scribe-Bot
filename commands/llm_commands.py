# ==============================
# Discord Imports
# ============================== 

import discord
from discord.ext import commands

# ==============================
# Internal Imports
# ==============================

from llm_service import generate_text_async

# ==============================
# Commands – LLM / Thematic
# ==============================

def setup_llm_commands(bot: commands.Bot, client):
    @bot.command()
    async def rumour(ctx):
        prompt = (
            "Generate ONE Bribe Scribe rumour grounded in LEAGUE DATA. "
            "Pick a random team/coach/player from LEAGUE DATA and centre the rumour on them. "
            "Choose a scandal angle that is NOT the same as your last output (discipline, ref drama, warpstone market, sponsorship, training bust-up, contract dispute, injury gossip). "
            "Include a short 'on-pitch impact' line. "
            "Output format: choose one of the rotation formats described in the system prompt."
        )

        async with ctx.typing():
            text = await generate_text_async(client, prompt)

        await ctx.send(text)

    @bot.command()
    async def odds(ctx, *, matchup: str = ""):
        if matchup:
            prompt = (
                f"Create odds for {matchup} using only teams in LEAGUE DATA. "
                "Output:\n"
                "- MONEYLINE: Team A (x.xx) | Team B (x.xx)\n"
                "- 2 PROPS tied to factions/playstyle (x.xx)\n"
                "- One sentence explaining why the line looks like that (injuries, form, coaching, corruption hint). "
                "Keep it concise."
            )
        else:
            prompt = (
                "Post odds for each fixture in Round 2 Fixtures from LEAGUE DATA. "
                "For each fixture provide:\n"
                "- MONEYLINE in decimal odds\n"
                "- 1 PROP\n"
                "Keep each fixture to two lines max. "
                "Add one brief 'market note' at the end about odds movement or suspicious money."
            )

        async with ctx.typing():
            text = await generate_text_async(client, prompt)

        await ctx.send(text)