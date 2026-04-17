import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import pytz  # Make sure pytz is installed

# =========================
# EMOJIS
# =========================
CREATED = "<:Accountcrated:1446457776988622868>"
TIME = "<:Time:1446882540832030790>"
AGE = "<:Accountage:1446882544082489344>"

# =========================
# TIMEZONE
# =========================
BD_TZ = pytz.timezone("Asia/Dhaka")

# =========================
# HELPERS
# =========================
def calculate_account_age(created_at: datetime):
    now = datetime.now(BD_TZ)
    created_at = created_at.astimezone(BD_TZ)
    delta = now - created_at

    years = delta.days // 365
    months = (delta.days % 365) // 30
    days = (delta.days % 365) % 30
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    return years, months, days, hours, minutes

def format_age(y, m, d, h, mi):
    return f"{y} Years {m} Months {d} Days {h} Hours {mi} Minutes"

def footer_text(user: discord.User):
    now = datetime.now(BD_TZ)
    today = now.date()
    yesterday = today - timedelta(days=1)

    if now.date() == today:
        day = "Today"
    elif now.date() == yesterday:
        day = "Yesterday"
    else:
        day = now.strftime("%b %d, %Y")

    return f"Requested by {user} | {day} at {now.strftime('%H:%M')}"

# =========================
# COG
# =========================
class AccountAge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------------
    # PREFIX COMMANDS
    # ×accage / ×accountage
    # -------------------------
    @commands.command(name="accage", aliases=["accountage"])
    async def accage_prefix(self, ctx, user: discord.User = None):
        user = user or ctx.author
        y, m, d, h, mi = calculate_account_age(user.created_at)

        embed = discord.Embed(
            title=f"{AGE} Account Age",
            color=0x87CEEB
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name=f"{CREATED} Account Created", value=f"<t:{int(user.created_at.timestamp())}:F>", inline=False)
        embed.add_field(name=f"{TIME} Total Age", value=format_age(y, m, d, h, mi), inline=False)
        embed.set_footer(text=footer_text(ctx.author), icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # -------------------------
    # SLASH COMMAND
    # /accountage
    # -------------------------
    @app_commands.command(name="accountage", description="Show account age of a user")
    async def accountage_slash(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        y, m, d, h, mi = calculate_account_age(user.created_at)

        embed = discord.Embed(
            title=f"{AGE} Account Age",
            color=0x87CEEB
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name=f"{CREATED} Account Created", value=f"<t:{int(user.created_at.timestamp())}:F>", inline=False)
        embed.add_field(name=f"{TIME} Total Age", value=format_age(y, m, d, h, mi), inline=False)
        embed.set_footer(text=footer_text(interaction.user), icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AccountAge(bot))