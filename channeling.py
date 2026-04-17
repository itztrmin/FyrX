# cogs/info.py
import discord
from discord.ext import commands
from discord import app_commands

# -------------------------
# EMOJIS
# -------------------------
CHANNEL_EMOJI = "<:Server:1447531451968127080>"
SETTINGS_EMOJI = "<:settings:1445424812020338842>"
POSITION_EMOJI = "<:Position:1450829603160588319>"
USER_EMOJI = "<:user:1447601102362247291>"
ENABLED = "<:Successful:1445424805762302016>"
DISABLED = "<:Error:1445424808476016651>"

# -------------------------
# HELPERS
# -------------------------
def sky_blue_embed(title=None, description=None):
    return discord.Embed(title=title, description=description, color=0x87CEEB)

# -------------------------
# COG
# -------------------------
class ChannelInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------- PREFIX --------
    @commands.command(name="channelinfo", aliases=["ci"])
    async def channelinfo_prefix(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await self.send_channel_embed(ctx, channel)

    # -------- SLASH --------
    @app_commands.command(name="channelinfo", description="Get detailed info about a channel")
    async def channelinfo_slash(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        channel = channel or interaction.channel
        await self.send_channel_embed(interaction, channel)

    # -------- HELPER FUNCTION --------
    async def send_channel_embed(self, ctx_or_interaction, channel: discord.TextChannel):
        embed = sky_blue_embed(
            title=f"{CHANNEL_EMOJI} Channel Information",
            description=f"Details of **{channel.name}**"
        )

        embed.add_field(name=f"{SETTINGS_EMOJI} Channel ID", value=f"`{channel.id}`", inline=True)
        embed.add_field(name=f"{POSITION_EMOJI} Position", value=f"`{channel.position}`", inline=True)
        embed.add_field(name=f"{USER_EMOJI} Category", value=f"{channel.category.name if channel.category else 'None'}", inline=True)
        embed.add_field(name=f"NSFW", value=ENABLED if channel.is_nsfw() else DISABLED, inline=True)
        embed.add_field(name=f"Slowmode", value=f"{channel.slowmode_delay}s", inline=True)
        embed.add_field(name=f"Topic", value=channel.topic or "None", inline=False)
        embed.set_footer(text=f"Requested by {ctx_or_interaction.user}", icon_url=ctx_or_interaction.user.display_avatar.url)

        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(embed=embed)
        else:
            await ctx_or_interaction.response.send_message(embed=embed)

# -------------------------
# SETUP
# -------------------------
async def setup(bot):
    await bot.add_cog(ChannelInfo(bot))