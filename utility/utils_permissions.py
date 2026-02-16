import discord
from discord.ext import commands

def is_admin(ctx: commands.Context) -> bool:
    return ctx.author.guild_permissions.administrator