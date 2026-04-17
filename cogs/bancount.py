import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

# ==========================
# CONFIG & EMOJIS
# ==========================
BAN_EMOJI   = "<:Ban:1451836885952364555>"
ERROR       = "<:Error:1445424808476016651>"
LINE        = "<:Line:1451857219690823691>"
COLOR       = 0x87CEEB 

def format_time():
    """Formats time to Today, Yesterday, or Date in 24h format (UTC+6)"""
    # Offset for Bangladesh (UTC+6)
    now = datetime.utcnow() + timedelta(hours=6)
    
    date_str = now.strftime("%d/%m/%Y")
    today_str = now.strftime("%d/%m/%Y")
    yesterday_str = (now - timedelta(days=1)).strftime("%d/%m/%Y")
    
    time_part = now.strftime("%H:%M")
    
    if date_str == today_str:
        return f"Today at {time_part}"
    elif date_str == yesterday_str:
        return f"Yesterday at {time_part}"
    else:
        return f"{date_str} at {time_part}"

class BanCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================
    # ERROR HANDLER UTILITY
    # ==========================
    async def send_error(self, ctx_or_int, title, message):
        author = ctx_or_int.user if isinstance(ctx_or_int, discord.Interaction) else ctx_or_int.author
        embed = discord.Embed(title=f"{ERROR} {title}", description=message, color=COLOR)
        embed.set_footer(text=f"Requested by {author.name} | {format_time()}", icon_url=author.display_avatar.url)
        
        if isinstance(ctx_or_int, discord.Interaction):
            if ctx_or_int.response.is_done(): await ctx_or_int.followup.send(embed=embed, ephemeral=True)
            else: await ctx_or_int.response.send_message(embed=embed, ephemeral=True)
        else: await ctx_or_int.send(embed=embed)

    # ==========================
    # COMMANDS
    # ==========================
    @app_commands.command(name="bancount", description="Professional overview of server ban statistics")
    @app_commands.checks.has_permissions(ban_members=True)
    async def bancount_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.execute_count(interaction)

    @commands.command(name="bancount")
    @commands.has_permissions(ban_members=True)
    async def bancount_prefix(self, ctx):
        await self.execute_count(ctx)

    async def execute_count(self, ctx_or_int):
        guild = ctx_or_int.guild
        author = ctx_or_int.user if isinstance(ctx_or_int, discord.Interaction) else ctx_or_int.author
        
        if not guild.me.guild_permissions.ban_members:
            return await self.send_error(ctx_or_int, "Permission Error", "I lack the `Ban Members` permission.")

        try:
            ban_list = [entry async for entry in guild.bans(limit=None)]
            ban_count = len(ban_list)
            member_count = guild.member_count or 1
            ban_ratio = (ban_count / member_count) * 100

            embed = discord.Embed(title=f"{BAN_EMOJI} Server Audit: Ban Registry", color=COLOR)
            if guild.icon: embed.set_thumbnail(url=guild.icon.url)

            embed.add_field(
                name="<:Position:1450829603160588319> Statistics",
                value=(
                    f"{LINE} **Total Banned:** `{ban_count:,}`\n"
                    f"{LINE} **Server Members:** `{member_count:,}`\n"
                    f"{LINE} **Ban Percentage:** `{ban_ratio:.2f}%`"
                ),
                inline=False
            )

            if ban_count > 0:
                last_user = ban_list[0].user
                embed.add_field(name="Latest Ban", value=f"{LINE} {last_user.name} (`{last_user.id}`)", inline=False)

            # UPDATED FOOTER
            embed.set_footer(
                text=f"Requested by {author.name} | {format_time()}",
                icon_url=author.display_avatar.url
            )

            if isinstance(ctx_or_int, discord.Interaction):
                await ctx_or_int.followup.send(embed=embed)
            else:
                await ctx_or_int.send(embed=embed)

        except Exception as e:
            await self.send_error(ctx_or_int, "Registry Error", str(e))

    # ==========================
    # ERROR HANDLERS
    # ==========================
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not ctx.command or not ctx.command.cog or not isinstance(ctx.command.cog, BanCount): return
        if isinstance(error, commands.MissingPermissions):
            await self.send_error(ctx, "Access Denied", "You need `Ban Members` permission.")
        elif isinstance(error, commands.CommandOnCooldown):
            await self.send_error(ctx, "Cooldown", f"Try again in {error.retry_after:.1f}s.")

    async def cog_app_command_error(self, interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await self.send_error(interaction, "Access Denied", "You need `Ban Members` permission.")
        else:
            await self.send_error(interaction, "Error", str(error))

async def setup(bot):
    await bot.add_cog(BanCount(bot))
