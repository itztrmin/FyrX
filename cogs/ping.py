import discord
from discord.ext import commands
from datetime import datetime, timedelta

# Bangladesh / Asia/Dhaka = UTC+6
BDT_OFFSET = 6

# -------------------------
# Footer helper
# -------------------------
def footer_time_text(user_display):
    """Return footer text with local Bangladesh time and Today/Yesterday logic."""
    now_utc = datetime.utcnow()
    now_local = now_utc + timedelta(hours=BDT_OFFSET)

    today = now_local.date()
    yesterday = today - timedelta(days=1)

    if now_local.date() == today:
        day_text = "Today"
    elif now_local.date() == yesterday:
        day_text = "Yesterday"
    else:
        day_text = now_local.strftime("%Y-%m-%d")

    time_text = now_local.strftime("%H:%M")
    return f"Requested by {user_display} | {day_text} at {time_text}"

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------------
    # PREFIX COMMAND: ×ping
    # -------------------------
    @commands.command(name="ping")
    async def ping_prefix(self, ctx):
        embed = discord.Embed(
            title="<a:Heart:1447609087922540565> Ping & Pong!",
            description=f"Bot Latency: {round(self.bot.latency * 1000)}ms",
            color=0x87CEEB  # Sky blue
        )

        # Thumbnail: bot avatar
        if getattr(self.bot.user, "display_avatar", None):
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        # Footer with Bangladesh time
        embed.set_footer(
            text=footer_time_text(ctx.author),
            icon_url=ctx.author.display_avatar.url
        )

        # ❌ Do NOT delete the invoking message
        await ctx.send(embed=embed)

    # -------------------------
    # SLASH COMMAND: /ping
    # -------------------------
    @discord.app_commands.command(name="ping", description="Check bot latency")
    async def ping_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="<a:Heart:1447609087922540565> Ping & Pong!",
            description=f"Bot Latency: {round(self.bot.latency * 1000)}ms",
            color=0x87CEEB
        )

        # Thumbnail: bot avatar
        if getattr(self.bot.user, "display_avatar", None):
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        # Footer with Bangladesh time
        embed.set_footer(
            text=footer_time_text(interaction.user),
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))