import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta, timezone

# =========================
# EMOJIS
# =========================
INFO = "<:info:1445424802994192426>"
SUCCESS = "<:Successful:1445424805762302016>"
ERROR = "<:Error:1445424808476016651>"

# =========================
# Bangladesh Time UTC+6
# =========================
BD_TZ = timezone(timedelta(hours=6))

def bangladesh_now():
    """Return current datetime in Bangladesh timezone."""
    return datetime.now(BD_TZ)

def footer_text(user: discord.User):
    now = bangladesh_now()
    today = now.date()
    yesterday = today - timedelta(days=1)

    if now.date() == today:
        day = "Today"
    elif now.date() == yesterday:
        day = "Yesterday"
    else:
        day = now.strftime("%b %d, %Y")

    return f"Requested by {user} | {day} at {now.strftime('%H:%M')}"

class ServerBanner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =========================
    # PREFIX ×serverbanner
    # =========================
    @commands.command(name="serverbanner")
    async def serverbanner_prefix(self, ctx):
        await self.send_server_banner(ctx)

    # =========================
    # SLASH /serverbanner
    # =========================
    @app_commands.command(
        name="serverbanner",
        description="Show the server banner"
    )
    async def serverbanner_slash(self, interaction: discord.Interaction):
        await self.send_server_banner(interaction)

    # =========================
    # MAIN LOGIC
    # =========================
    async def send_server_banner(self, source):
        guild = source.guild
        requester = source.user if isinstance(source, discord.Interaction) else source.author

        if not guild or not guild.banner:
            embed = discord.Embed(
                title=f"{ERROR} No Server Banner",
                description="This server does not have a banner.",
                color=discord.Color.red()
            )
            embed.set_footer(
                text=footer_text(requester),
                icon_url=requester.display_avatar.url
            )

            if isinstance(source, discord.Interaction):
                await source.response.send_message(embed=embed, ephemeral=True)
            else:
                await source.send(embed=embed)
            return

        banner_url = guild.banner.url

        embed = discord.Embed(
            title=f"{SUCCESS} Server Banner",
            description=f"**{guild.name}**",
            color=0x87CEEB
        )
        embed.set_image(url=banner_url)
        embed.set_footer(
            text=footer_text(requester),
            icon_url=requester.display_avatar.url
        )

        # ✅ Button to open banner
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Click Here",
                url=banner_url,
                style=discord.ButtonStyle.link
            )
        )

        if isinstance(source, discord.Interaction):
            await source.response.send_message(embed=embed, view=view)
        else:
            await source.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ServerBanner(bot))