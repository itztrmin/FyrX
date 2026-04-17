import discord
from discord.ext import commands
from discord import app_commands

# =========================
# EMOJIS (clean & minimal)
# =========================
BOOST_EMOJI  = "<:Boost:1445424796031782923>"
SERVER_EMOJI = "<:Server:1447531451968127080>"
USER_EMOJI   = "<:user:1447601102362247291>"
BOT_EMOJI    = "<:Bot:1450440681762984037>"
# =========================
# EMBED HELPER
# =========================
def blue_embed(title: str, description: str):
    return discord.Embed(
        title=title,
        description=description,
        color=0x87CEEB
    )

# =========================
# COG
# =========================
class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------------
    # BOOST COUNT (PREFIX)
    # -------------------------
    @commands.command(name="boostcount", aliases=["bc"])
    async def boostcount_prefix(self, ctx: commands.Context):
        guild = ctx.guild

        boosts = guild.premium_subscription_count or 0
        level = guild.premium_tier

        embed = blue_embed(
            f"{BOOST_EMOJI} Server Boost Statistics",
            f"**Server:** {guild.name}\n"
            f"**Boosts:** `{boosts}`\n"
            f"**Boost Level:** `Level {level}`"
        )

        await ctx.send(embed=embed)

    # -------------------------
    # BOOST COUNT (SLASH)
    # -------------------------
    @app_commands.command(name="boostcount", description="Show server boost count and level")
    async def boostcount_slash(self, interaction: discord.Interaction):
        guild = interaction.guild

        boosts = guild.premium_subscription_count or 0
        level = guild.premium_tier

        embed = blue_embed(
            f"{BOOST_EMOJI} Server Boost Statistics",
            f"**Server:** {guild.name}\n"
            f"**Boosts:** `{boosts}`\n"
            f"**Boost Level:** `Level {level}`"
        )

        await interaction.response.send_message(embed=embed)

    # -------------------------
    # MEMBER COUNT (PREFIX)
    # -------------------------
    @commands.command(name="membercount", aliases=["mc"])
    async def membercount_prefix(self, ctx: commands.Context):
        guild = ctx.guild

        total = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = total - humans

        embed = blue_embed(
            f"{SERVER_EMOJI} Server Member Statistics",
            f"**Server:** {guild.name}\n"
            f"**Total Members:** `{total}`\n"
            f"{USER_EMOJI} **Humans:** `{humans}`\n"
            f"{BOT_EMOJI} **Bots:** `{bots}`"
        )

        await ctx.send(embed=embed)

    # -------------------------
    # MEMBER COUNT (SLASH)
    # -------------------------
    @app_commands.command(name="membercount", description="Show server member statistics")
    async def membercount_slash(self, interaction: discord.Interaction):
        guild = interaction.guild

        total = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = total - humans

        embed = blue_embed(
            f"{SERVER_EMOJI} Server Member Statistics",
            f"**Server:** {guild.name}\n"
            f"**Total Members:** `{total}`\n"
            f"{USER_EMOJI} **Humans:** `{humans}`\n"
            f"{BOT_EMOJI} **Bots:** `{bots}`"
        )

        await interaction.response.send_message(embed=embed)

# =========================
# SETUP
# =========================
async def setup(bot):
    await bot.add_cog(ServerStats(bot))