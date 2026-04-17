import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone

# Bangladesh / Asia/Dhaka = UTC+6
BDT_OFFSET = 6

def footer_time_text(user):
    """Return footer text with Bangladesh time."""
    now_utc = datetime.utcnow()
    now_local = now_utc + timedelta(hours=BDT_OFFSET)

    today = now_local.date()
    yesterday = today - timedelta(days=1)

    if now_local.date() == today:
        day_text = "Today"
    elif now_local.date() == yesterday:
        day_text = "Yesterday"
    else:
        day_text = now_local.strftime("%b %d, %Y")

    time_text = now_local.strftime("%H:%M")
    return f"Requested by {user} | {day_text} at {time_text}"

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------------
    # PREFIX COMMAND ×say
    # -------------------------
    @commands.command(name="say")
    async def say_prefix(self, ctx, *, message: str):
        embed = discord.Embed(
            description=message,
            color=0x87CEEB
        )
        embed.set_footer(
            text=footer_time_text(ctx.author),
            icon_url=ctx.author.display_avatar.url
        )

        # Delete the user's invoking message
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        await ctx.send(embed=embed)

    # -------------------------
    # SLASH COMMAND /say
    # -------------------------
    @discord.app_commands.command(
        name="say",
        description="Bot repeats your message"
    )
    async def say_slash(self, interaction: discord.Interaction, message: str):
        embed = discord.Embed(
            description=message,
            color=0x87CEEB
        )
        embed.set_footer(
            text=footer_time_text(interaction.user),
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Say(bot))