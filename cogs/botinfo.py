import discord
import os
import sys
import time
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta, timezone

# =========================
# CUSTOM EMOJIS
# =========================
INFO = "<:info:1445424802994192426>"
STATS = "<:Stats:1447905705720811520>"
CMDS = "<:Commands:1447905708417749022>"
SYSTEM = "<:System:1447905715451723859>"
CODE = "<:Code:1447905718685536256>"
DEV = "<:Dev:1447905711676981248>"
PY = "<:Python:1446882550462025728>"

START_TIME = time.time()

# =========================
# Bangladesh Time UTC+6
# =========================
BD_TZ = timezone(timedelta(hours=6))

def uptime():
    s = int(time.time() - START_TIME)
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{d}d {h}h {m}m {s}s"

def code_stats():
    files = lines = words = 0
    for root, _, file_list in os.walk("."):
        for f in file_list:
            if f.endswith(".py"):
                files += 1
                with open(os.path.join(root, f), errors="ignore") as fp:
                    txt = fp.read()
                    lines += txt.count("\n")
                    words += len(txt.split())
    return files, lines, words

def footer_time():
    """Returns current Bangladesh time in HH:MM format"""
    now = datetime.now(BD_TZ)
    return f"{now.strftime('%H:%M')}"

class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ×botinfo | ×bi
    @commands.command(name="botinfo", aliases=["bi"])
    async def botinfo_prefix(self, ctx):
        await self.send(ctx)

    # /botinfo
    @app_commands.command(name="botinfo", description="Show bot information")
    async def botinfo_slash(self, interaction: discord.Interaction):
        await self.send(interaction)

    async def send(self, source):
        bot = self.bot

        servers = len(bot.guilds)
        users = sum(g.member_count for g in bot.guilds)
        py_files, loc, words = code_stats()

        embed = discord.Embed(
            title=f"{INFO} Bot Information",
            color=0x87CEEB
        )
        embed.set_thumbnail(url=bot.user.display_avatar.url)

        # 📊 Stats
        embed.add_field(
            name=f"{STATS} Statistics",
            value=(
                f"**Servers:** `{servers}`\n"
                f"**Users:** `{users}`\n"
                f"**Latency:** `{round(bot.latency * 1000)}ms`\n"
                f"**Uptime:** `{uptime()}`"
            ),
            inline=False
        )

        # ⚙ Commands
        embed.add_field(
            name=f"{CMDS} Commands",
            value=(
                f"**Prefix Commands:** `{len(bot.commands)}`\n"
                f"**Slash Commands:** `{len(bot.tree.get_commands())}`"
            ),
            inline=False
        )

        # 🖥 System
        embed.add_field(
            name=f"{SYSTEM} System",
            value=(
                f"**Language:** Python\n"
                f"**Library:** discord.py `{discord.__version__}`\n"
                f"**Python:** `{sys.version.split()[0]}`"
            ),
            inline=False
        )

        # 🧠 Code
        embed.add_field(
            name=f"{CODE} Codebase",
            value=(
                f"**Files:** `{py_files}`\n"
                f"**Lines:** `{loc}`\n"
                f"**Words:** `{words}`"
            ),
            inline=False
        )

        # 👑 Developer (BOTTOM)
        embed.add_field(
            name=f"{DEV} Developer",
            value=f"**T4min**\n{PY} Python Developer",
            inline=False
        )

        # ✅ Footer with Discord-accurate Bangladesh time
        embed.set_footer(
            text=f"{bot.user.name} • {footer_time()} ",
            icon_url=bot.user.display_avatar.url
        )

        if isinstance(source, discord.Interaction):
            await source.response.send_message(embed=embed)
        else:
            await source.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BotInfo(bot))