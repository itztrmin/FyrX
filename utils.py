# utils.py
import discord
from datetime import datetime

def sky_blue_embed(title=None, description=None, user=None):
    embed = discord.Embed(
        title=title,
        description=description,
        color=0x87CEEB
    )

    if user:
        time_str = datetime.utcnow().strftime("%d %b %Y %H:%M UTC")
        embed.set_footer(text=f"Request By {user} | {time_str}")

    return embed