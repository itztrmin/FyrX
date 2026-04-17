# cogs/channelinfo.py
import discord
from discord.ext import commands
from discord import app_commands

# =========================
# EMOJIS
# =========================
CHANNEL_EMOJI   = "<:Server:1447531451968127080>"
SETTINGS_EMOJI  = "<:settings:1445424812020338842>"
POSITION_EMOJI  = "<:Position:1450829603160588319>"
USER_EMOJI      = "<:user:1447601102362247291>"
ENABLED         = "<:Successful:1445424805762302016>"
DISABLED        = "<:Error:1445424808476016651>"
SLOWMODE_EMOJI  = "<:Slowmode:1450836785872764989>"
TOPIC_EMOJI     = "<:Topic:1450836783347798147>"
CREATED_EMOJI   = "<:Accountcrated:1446457776988622868>"

# =========================
# HELPERS
# =========================
def sky_blue_embed(title=None, description=None):
    return discord.Embed(title=title, description=description, color=0x87CEEB)

# =========================
# COG
# =========================
class ChannelInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------- PREFIX --------
    @commands.command(name="channelinfo", aliases=["ci"])
    async def channelinfo_prefix(self, ctx, channel: discord.TextChannel = None):
        # If no channel provided, use current
        channel = channel or ctx.channel
        await self.send_channel_embed(ctx, channel)

    # -------- SLASH --------
    @app_commands.command(name="channelinfo", description="Get detailed info about a channel")
    @app_commands.describe(channel="Select the channel to get info for")
    async def channelinfo_slash(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self.send_channel_embed(interaction, channel)

    # -------- EMBED FUNCTION --------
    async def send_channel_embed(self, ctx_or_interaction, channel: discord.TextChannel):
        embed = sky_blue_embed(
            title=f"{CHANNEL_EMOJI} Channel Information",
            description=f"Details of **#{channel.name}**"
        )

        embed.add_field(name=f"{SETTINGS_EMOJI} Channel ID", value=f"`{channel.id}`", inline=True)
        embed.add_field(name=f"{POSITION_EMOJI} Position", value=f"`{channel.position}`", inline=True)
        embed.add_field(name=f"{USER_EMOJI} Category", value=f"{channel.category.name if channel.category else 'None'}", inline=True)
        embed.add_field(name="NSFW", value=ENABLED if channel.is_nsfw() else DISABLED, inline=True)
        embed.add_field(name=f"{SLOWMODE_EMOJI} Slowmode", value=f"`{channel.slowmode_delay}s`", inline=True)
        embed.add_field(name=f"{TOPIC_EMOJI} Topic", value=f"{channel.topic or 'None'}", inline=False)
        embed.add_field(name=f"{CREATED_EMOJI} Created At", value=f"`{channel.created_at.strftime('%Y-%m-%d %H:%M:%S')}`", inline=False)

        embed.set_footer(text=f"Requested by {ctx_or_interaction.author if isinstance(ctx_or_interaction, commands.Context) else ctx_or_interaction.user}", 
                         icon_url=(ctx_or_interaction.author.display_avatar.url if isinstance(ctx_or_interaction, commands.Context) else ctx_or_interaction.user.display_avatar.url))

        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(embed=embed)
        else:
            await ctx_or_interaction.response.send_message(embed=embed)

# =========================
# SETUP
# =========================
async def setup(bot):
    await bot.add_cog(ChannelInfo(bot))