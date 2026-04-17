# cogs/uptime.py
import discord
from discord.ext import commands
from discord import app_commands
import time

# =========================
# EMOJI
# =========================
UPTIME_EMOJI = "<:Uptime:1451216710030983290>"

# =========================
# HELPERS
# =========================
def format_duration(seconds: int):
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, sec = divmod(rem, 60)
    return f"{days}d {hours}h {minutes}m {sec}s"

# =========================
# COG
# =========================
class Uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    async def build_embed(self, user):
        uptime_text = format_duration(int(time.time() - self.start_time))
        embed = discord.Embed(
            title=f"{UPTIME_EMOJI} **Uptime**",
            description=f"Here's how long I've been running smoothly!\n**{uptime_text}**",
            color=0x1ABC9C
        )
        embed.set_footer(text=f"Requested by {user} • FyrX™", icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        return embed

    # ---------- PREFIX ----------
    @commands.command(name="uptime", aliases=["up"])
    async def uptime_prefix(self, ctx):
        embed = await self.build_embed(ctx.author)
        await ctx.send(embed=embed)

    # ---------- SLASH ----------
    @app_commands.command(name="uptime", description="Shows how long the bot has been online")
    async def uptime_slash(self, interaction: discord.Interaction):
        embed = await self.build_embed(interaction.user)
        await interaction.response.send_message(embed=embed)

# =========================
# SETUP
# =========================
async def setup(bot):
    await bot.add_cog(Uptime(bot))