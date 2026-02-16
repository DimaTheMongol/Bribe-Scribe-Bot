# ==============================
# Discord Imports
# ============================== 

import discord
from discord.ext import commands

# ==============================
# Internal Imports
# ==============================

from economy import get_balance, get_recent_transactions, claim_daily, transfer, top_balances, grant, DAILY_AMOUNT, set_balance
from warpstone import ws
from utils_permissions import is_admin

# ==============================
# Commands – Economy
# ==============================

def setup_economy_commands(bot: commands.Bot):
    
    @bot.command()
    async def bank(ctx):
        bal = get_balance(ctx.author.id)
        await ctx.send(f"{ctx.author.display_name} has {ws(bal)}")

    @bot.command()
    async def statement(ctx, n: int = 5):
        rows = get_recent_transactions(ctx.author.id, limit=max(1, min(n, 10)))

        if not rows:
            await ctx.send("No transactions yet.")
            return

        lines = [f"Recent Warp Stone transactions for {ctx.author.display_name}:"]
        for r in rows:
            lines.append(f'{r["tx_id"]}: {r["amount"]:+d} ({r["reason"]})')

        await ctx.send("\n".join(lines))

    @bot.command()
    async def daily(ctx):
        ok, msg, new_balance, remaining = claim_daily(ctx.author.id)

        if ok:
            await ctx.send(
                f"{msg} Your sponsors have wired +{ws(DAILY_AMOUNT)}"
                f"You now have a total balance of {ws(new_balance)}"
            )
        else:
            # remaining is in seconds
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            await ctx.send(f"{msg} Next payout in {hours}h {minutes}m.")

    @bot.command()
    async def pay(ctx, member: discord.Member, amount: int):
        # Basic guardrails
        if member.bot:
            await ctx.send("Bots do not accept Warp Stones.")
            return

        if member.id == ctx.author.id:
            await ctx.send("Paying yourself is not money laundering, it is just confusing.")
            return

        ok, msg = transfer(ctx.author.id, member.id, amount)

        if ok:
            await ctx.send(
                f"{ctx.author.display_name} paid {member.display_name} {ws(amount)}"
            )
        else:
            await ctx.send(msg)

    @bot.command()
    async def leaderboard(ctx):
        rows = top_balances(limit=5)
        if not rows:
            await ctx.send("The bookies have no accounts on record yet.")
            return

        lines = ["Top bookie credit lines (Warp Stones):"]
        for i, r in enumerate(rows, start=1):
            user_id = int(r["user_id"])

            member = ctx.guild.get_member(user_id)
            if member is None:
                try:
                    member = await ctx.guild.fetch_member(user_id)
                except Exception:
                    member = None

            name = member.display_name if member else f"User {user_id}"
            balance = int(r["balance"])
            lines.append(f"{i}) {name}: {ws(balance)}")

        await ctx.send("\n".join(lines))

    @bot.command()
    async def grantwarp(ctx, member: discord.Member, amount: int):
        if not is_admin(ctx):
            await ctx.send("Nice try. Only the Commissioner and accredited bookies can issue new Warp Stones.")
            return
        if member.bot:
            await ctx.send("Bots do not accept Warp Stones.")
            return

        ok, msg, new_bal = grant(member.id, amount, reason=f"admin_grant_by:{ctx.author.id}")
        if ok:
            await ctx.send(f"Ledger updated. {member.display_name} now has {ws(new_bal)} ")
        else:
            await ctx.send(msg)

    @bot.command()
    async def setwarp(ctx, member: discord.Member, new_balance: int):
        if not is_admin(ctx):
            await ctx.send("Only the Commissioner can rewrite the ledger.")
            return
        if member.bot:
            await ctx.send("Bots do not accept Warp Stones.")
            return

        ok, msg, final_bal, delta = set_balance(member.id, new_balance, reason=f"admin_set_by:{ctx.author.id}")
        if ok:
            sign = "+" if delta >= 0 else ""
            await ctx.send(f"Ledger rewritten. {member.display_name}'s balance was set to {ws(final_bal)} ({sign}{delta}).")
        else:
            await ctx.send(msg)
