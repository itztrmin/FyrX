import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import format_dt
from datetime import datetime, timedelta, timezone

# =========================
# EMOJIS
# =========================
INFO = "<:info:1445424802994192426>"
USER = "<:user:1447601102362247291>"
JOINED = "<:Joined:1446457774354464940>"
CREATED = "<:Accountcrated:1446457776988622868>"
ROLE = "<:Role:1445424800242598068>"
PERM = "<:Permission:1446457764917411870>"
BOOST = "<:Boost:1445424796031782923>"

# =========================
# Bangladesh time UTC+6
# =========================
BD_TZ = timezone(timedelta(hours=6))

def bangladesh_now():
    """Return current datetime in Bangladesh timezone."""
    return datetime.now(BD_TZ)

def smart_footer_time():
    now = bangladesh_now()
    today = now.date()
    yesterday = today - timedelta(days=1)

    msg_date = now.date()

    if msg_date == today:
        day = "Today"
    elif msg_date == yesterday:
        day = "Yesterday"
    else:
        day = now.strftime("%b %d, %Y")

    return f"{day} at {now.strftime('%H:%M')}"

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =========================
    # PREFIX ×userinfo | ×ui
    # =========================
    @commands.command(name="userinfo", aliases=["ui"])
    async def userinfo_prefix(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        await self.send_userinfo(ctx, member)

    # =========================
    # SLASH /userinfo
    # =========================
    @app_commands.command(name="userinfo", description="Get information about a user")
    async def userinfo_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await self.send_userinfo(interaction, member)

    # =========================
    # MAIN EMBED FUNCTION
    # =========================
    async def send_userinfo(self, source, member: discord.Member):
        created = format_dt(member.created_at, style="F")
        joined = format_dt(member.joined_at, style="F") if member.joined_at else "Unknown"

        # Roles
        roles = [r.mention for r in member.roles if r.name != "@everyone"]
        roles_display = ", ".join(roles) if roles else "None"

        # Permissions
        perms_display = "Administrator" if member.guild_permissions.administrator else "None"

        # Boost
        boost_display = (
            format_dt(member.premium_since, "F")
            if member.premium_since else "0"
        )

        embed = discord.Embed(
            title=f"{INFO} User Info",
            description=f"**{member}**",
            color=0x87CEEB
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name=f"{USER} Username", value=str(member), inline=True)
        embed.add_field(name=f"{JOINED} Joined Server", value=joined, inline=True)
        embed.add_field(name=f"{CREATED} Account Created", value=created, inline=True)
        embed.add_field(name=f"{ROLE} Roles", value=roles_display, inline=False)
        embed.add_field(name=f"{PERM} Permissions", value=perms_display, inline=False)
        embed.add_field(name=f"{BOOST} Boost", value=boost_display, inline=False)

        # Footer with Bangladesh time
        requester = source.user if isinstance(source, discord.Interaction) else source.author
        embed.set_footer(
            text=f"Requested by {requester} | {smart_footer_time()}",
            icon_url=requester.display_avatar.url
        )

        # Send embed
        if isinstance(source, discord.Interaction):
            await source.response.send_message(embed=embed)
        else:
            await source.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))