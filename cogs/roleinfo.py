# cogs/roleinfo.py
import discord
from discord.ext import commands
from discord import app_commands

# =========================
# EMOJIS
# =========================
ROLE_EMOJI = "<:Role:1445424800242598068>"
PERM_EMOJI = "<:Permission:1446457764917411870>"
SETTINGS   = "<:settings:1445424812020338842>"
POSITION   = "<:Position:1450829603160588319>"

COLOR = 0x87CEEB

def embed(title, desc=None):
    return discord.Embed(title=title, description=desc, color=COLOR)

# =========================
# COG
# =========================
class RoleInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------- PREFIX ----------
    @commands.command(name="roleinfo", aliases=["ri"])
    async def roleinfo_prefix(self, ctx, role: discord.Role = None):
        role = role or ctx.author.top_role
        await ctx.send(embed=self.build_embed(role, ctx.guild, ctx.author))

    # ---------- SLASH ----------
    @app_commands.command(name="roleinfo", description="Show detailed information about a role")
    @app_commands.describe(role="Select the role to get info for")
    async def roleinfo_slash(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(
            embed=self.build_embed(role, interaction.guild, interaction.user)
        )

    # ---------- EMBED BUILDER ----------
    def build_embed(self, role: discord.Role, guild: discord.Guild, requester: discord.User):
        created = f"<t:{int(role.created_at.timestamp())}:F>"
        members = len(role.members)

        perms = [
            perm.replace("_", " ").title()
            for perm, value in role.permissions
            if value
        ]
        perms_text = ", ".join(perms) if perms else "No Permissions"

        e = embed(
            f"{ROLE_EMOJI} Role Information",
            f"Details for **{role.name}**"
        )

        # General Info
        e.add_field(
            name=f"{SETTINGS} General",
            value=(
                f"**Role ID:** `{role.id}`\n"
                f"**Created:** {created}\n"
                f"**Members:** `{members}`"
            ),
            inline=False
        )

        # Role Settings
        e.add_field(
            name=f"{POSITION} Role Settings",
            value=(
                f"**Position:** `{role.position}`\n"
                f"**Color:** `{str(role.color)}`\n"
                f"**Hoisted:** `{role.hoist}`\n"
                f"**Mentionable:** `{role.mentionable}`"
            ),
            inline=False
        )

        # Permissions
        e.add_field(
            name=f"{PERM_EMOJI} Permissions",
            value=perms_text[:1024],
            inline=False
        )

        e.set_footer(text=f"Requested by {requester}", icon_url=requester.display_avatar.url)
        return e

# =========================
# SETUP
# =========================
async def setup(bot):
    await bot.add_cog(RoleInfo(bot))