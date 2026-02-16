# ==============================
# Discord Imports
# ============================== 

import discord
from discord.ext import commands

# ==============================
# Internal Imports
# ==============================

from betting import parse_fixture_lines, create_fixtures_for_round, list_fixtures
from utility.utils_permissions import is_admin

# Update this to whatever you want as the canonical season label
SEASON_NAME = "Sugarbowl Season IV"

def setup_betting_commands(bot: commands.Bot):

    @bot.command()
    async def openround(ctx, round_number: int, *, fixtures_text: str = ""):
        """
        Usage:
          !openround 3 Shiny Klawz vs The Ball Boys
          !openround 3 <paste multiple lines>
        """
        if not is_admin(ctx):
            await ctx.send("Only the Commissioner can open a round.")
            return

        if not fixtures_text.strip():
            await ctx.send(
                "Paste fixtures after the round number, one per line.\n"
                "Example:\n"
                "`!openround 3 Shiny Klawz vs The Ball Boys`\n"
                "Or paste multiple lines:\n"
                "```\nTeam A vs Team B\nTeam C vs Team D\n```"
            )
            return

        try:
            fixtures = parse_fixture_lines(fixtures_text)
            count = create_fixtures_for_round(SEASON_NAME, round_number, fixtures)
        except ValueError as e:
            await ctx.send(str(e))
            return

        lines = [f"Round {round_number} is open. {count} fixtures logged:"]
        rows = list_fixtures(SEASON_NAME, round_number)
        for r in rows:
            lines.append(f'{r["fixture_id"]}) {r["home_team"]} vs {r["away_team"]} (scheduled)')

        await ctx.send("\n".join(lines))

    @bot.command()
    async def fixtures(ctx, round_number: int = 0):
        """
        Usage:
          !fixtures       (lists all fixtures for the season)
          !fixtures 3     (lists round 3 fixtures)
        """
        rnd = None if round_number == 0 else round_number
        rows = list_fixtures(SEASON_NAME, rnd)
        if not rows:
            await ctx.send("No fixtures found yet.")
            return

        lines = ["Fixtures:"]
        for r in rows:
            score = ""
            if r["home_score"] is not None and r["away_score"] is not None:
                score = f' [{r["home_score"]}-{r["away_score"]}]'
            lines.append(f'R{r["round"]} | {r["fixture_id"]}) {r["home_team"]} vs {r["away_team"]}{score} ({r["status"]})')

        await ctx.send("\n".join(lines))