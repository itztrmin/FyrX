import discord
from discord.ext import commands
from discord import app_commands
import re

# ==========================
# EMOJIS & CONFIG
# ==========================
UNBAN_EMOJI = "<:Permission:1446457764917411870>"
ERROR       = "<:Error:1445424808476016651>"
LINE        = "<:Line:1451857219690823691>"
COLOR       = 0x87CEEB

# ==========================
# FEATURE 3: THE MODAL
# ==========================
class UnbanReasonModal(discord.ui.Modal, title="Provide Unban Reason"):
    reason_input = discord.ui.TextInput(
        label="Reason",
        placeholder="Why is this user being unbanned?",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )

    def __init__(self, cog, user_id, is_slash):
        super().__init__()
        self.cog = cog
        self.user_id = user_id
        self.is_slash = is_slash

    async def on_submit(self, interaction: discord.Interaction):
        # Once the modal is submitted, call the unban handler
        await interaction.response.defer(ephemeral=True)
        await self.cog.handle_unban(interaction, str(self.user_id), self.reason_input.value, is_slash=True)

# ==========================
# THE COG
# ==========================
class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # FEATURE 1: AUTOCOMPLETE LOGIC
    async def unban_autocomplete(self, interaction: discord.Interaction, current: str):
        bans = [entry async for entry in interaction.guild.bans(limit=25)]
        return [
            app_commands.Choice(name=f"{entry.user.name} ({entry.user.id})", value=str(entry.user.id))
            for entry in bans if current.lower() in entry.user.name.lower() or current in str(entry.user.id)
        ]

    @app_commands.command(name="unban", description="Unban a user with autocomplete and reason prompt")
    @app_commands.describe(user="Select a user or enter an ID", reason="Optional reason (if empty, a popup will appear)")
    @app_commands.autocomplete(user=unban_autocomplete)
    async def unban_slash(self, interaction: discord.Interaction, user: str, reason: str = None):
        if not interaction.user.guild_permissions.ban_members:
            return await interaction.response.send_message("Missing Permissions.", ephemeral=True)

        # If no reason is provided, show the Modal popup
        if not reason:
            return await interaction.response.send_modal(UnbanReasonModal(self, user, True))

        await interaction.response.defer(ephemeral=True)
        await self.handle_unban(interaction, user, reason, is_slash=True)

    # ==========================================================
    # CORE HANDLER (Used by both Modal and Command)
    # ==========================================================
    async def handle_unban(self, ctx_or_int, user_input: str, reason: str, is_slash: bool):
        guild = ctx_or_int.guild
        author = ctx_or_int.user if is_slash else ctx_or_int.author
        
        # Extract ID
        match = re.search(r"\d{17,20}", user_input)
        if not match:
            return await self.send_error(ctx_or_int, "Invalid User ID format.", is_slash)
        
        user_id = int(match.group())
        
        try:
            # Check if user is actually banned
            ban_entry = await guild.fetch_ban(discord.Object(id=user_id))
            banned_user = ban_entry.user
            
            await guild.unban(banned_user, reason=reason)
            
            # Success Embed
            embed = discord.Embed(
                title=f"{UNBAN_EMOJI} User Unbanned",
                description=f"{LINE} **User:** {banned_user} (`{user_id}`)\n{LINE} **By:** {author.mention}\n{LINE} **Reason:** {reason}",
                color=COLOR
            )
            
            if is_slash:
                await ctx_or_int.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx_or_int.send(embed=embed)

        except discord.NotFound:
            await self.send_error(ctx_or_int, "User is not banned.", is_slash)
        except discord.Forbidden:
            await self.send_error(ctx_or_int, "I lack permissions to unban.", is_slash)

    async def send_error(self, ctx_or_int, message, is_slash):
        embed = discord.Embed(title=f"{ERROR} Error", description=message, color=0xFF0000)
        if is_slash:
            if ctx_or_int.response.is_done():
                await ctx_or_int.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx_or_int.response.send_message(embed=embed, ephemeral=True)
        else:
            await ctx_or_int.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Unban(bot))
