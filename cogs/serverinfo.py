import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta, timezone

# =========================
# CUSTOM EMOJIS
# =========================
INFO = "<:info:1445424802994192426>"
SERVER = "<:Server:1447531451968127080>"
OWNER = "<:Owner:1447531446486040618>"
CHANNELS = "<:Channels:1447531449191370845>"
BOOST = "<:Boost:1445424796031782923>"
USER = "<:user:1447601102362247291>"
ROLE = "<:Role:1445424800242598068>"
TIME = "<:Time:1446882540832030790>"

# =========================
# Bangladesh timezone UTC+6
# =========================
BD_TZ = timezone(timedelta(hours=6))

def bangladesh_now():
    """Return current datetime in Bangladesh timezone."""
    return datetime.now(BD_TZ)

def smart_footer_time():
    now = bangladesh_now()
    today = now.date()
    yesterday = today - timedelta(days=1)

    if now.date() == today:
        day = "Today"
    elif now.date() == yesterday:
        day = "Yesterday"
    else:
        day = now.strftime("%b %d, %Y")

    return f"{day} at {now.strftime('%H:%M')}"

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =========================
    # PREFIX ×serverinfo | ×si
    # =========================
    @commands.command(name="serverinfo", aliases=["si"])
    async def serverinfo_prefix(self, ctx):
        await self.send_info(ctx.guild, ctx.author, ctx.send)

    # =========================
    # SLASH /serverinfo
    # =========================
    @app_commands.command(name="serverinfo", description="Show information about this server")
    async def serverinfo_slash(self, interaction: discord.Interaction):
        await self.send_info(interaction.guild, interaction.user, interaction.response.send_message)

    # =========================
    # EMBED FUNCTION
    # =========================
    async def send_info(self, guild: discord.Guild, requester, send_func):
        created_ts = int(guild.created_at.timestamp())

        embed = discord.Embed(
            title=f"{INFO} Server Information",
            description=f"**{guild.name}**\n{guild.description or '*No description set.*'}",
            color=0x87CEEB
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        # -------------------------
        # General Info
        # -------------------------
        embed.add_field(
            name=f"{SERVER} General Info",
            value=(
                f"Name: {guild.name}\n"
                f"Server ID: {guild.id}\n"
                f"Owner: {guild.owner.mention if guild.owner else 'Unknown'}\n"
                f"Created: <t:{created_ts}:F>\n"
                f"Age: <t:{created_ts}:R>"
            ),
            inline=False
        )

        # -------------------------
        # Members & Roles
        # -------------------------
        embed.add_field(
            name=f"{USER} Members & Roles",
            value=(
                f"Members: {guild.member_count}\n"
                f"Roles: {len(guild.roles)}\n"
                f"Verification Level: {guild.verification_level.name.title()}"
            ),
            inline=False
        )

        # -------------------------
        # Boost Info
        # -------------------------
        embed.add_field(
            name=f"{BOOST} Boost Status",
            value=(
                f"Boost Level: {guild.premium_tier}\n"
                f"Boosts: {guild.premium_subscription_count}\n"
                f"AFK Timeout: {int(guild.afk_timeout / 60)} minutes"
            ),
            inline=False
        )

        # -------------------------
        # Channels Info
        # -------------------------
        embed.add_field(
            name=f"{CHANNELS} Channels",
            value=(
                f"Text: {len(guild.text_channels)}\n"
                f"Voice: {len(guild.voice_channels)}\n"
                f"Categories: {len(guild.categories)}"
            ),
            inline=False
        )

        # -------------------------
        # Footer
        # -------------------------
        embed.set_footer(
            text=f"Requested by {requester} | {smart_footer_time()}",
            icon_url=requester.display_avatar.url
        )

        await send_func(embed=embed)


async def setup(bot):
    await bot.add_cog(ServerInfo(bot))