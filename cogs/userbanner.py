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
USER_EMOJI = "<:user:1447601102362247291>"

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

class Banner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =========================
    # PREFIX ×banner
    # =========================
    @commands.command(name="banner")
    async def banner_prefix(self, ctx, user: discord.User = None):
        user = user or ctx.author
        await self.send_banner(ctx, user)

    # =========================
    # SLASH /banner
    # =========================
    @app_commands.command(
        name="banner",
        description="Show banner of a user"
    )
    async def banner_slash(
        self,
        interaction: discord.Interaction,
        user: discord.User = None
    ):
        user = user or interaction.user
        await self.send_banner(interaction, user)

    # =========================
    # MAIN LOGIC
    # =========================
    async def send_banner(self, source, user: discord.User):
        # Fetch user to access banner
        fetched = await self.bot.fetch_user(user.id)
        requester = source.user if isinstance(source, discord.Interaction) else source.author

        # ❌ No banner
        if not fetched.banner:
            embed = discord.Embed(
                title=f"{ERROR} No Banner Found",
                description=f"{USER_EMOJI} **{user}** does not have a banner.",
                color=discord.Color.red()
            )
            embed.set_footer(text=footer_text(requester), icon_url=requester.display_avatar.url)

            if isinstance(source, discord.Interaction):
                await source.response.send_message(embed=embed, ephemeral=True)
            else:
                await source.send(embed=embed)
            return

        banner_url = fetched.banner.url

        # ✅ Banner embed
        embed = discord.Embed(
            title=f"{SUCCESS} User Banner",
            description=f"{USER_EMOJI} **{user}**",
            color=0x87CEEB
        )
        embed.set_image(url=banner_url)
        embed.set_footer(text=footer_text(requester), icon_url=requester.display_avatar.url)

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
    await bot.add_cog(Banner(bot))