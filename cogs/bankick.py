import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

# ==========================
# EMOJIS & CONFIG
# ==========================
BAN_EMOJI   = "<:Ban:1451836885952364555>"
KICK_EMOJI  = "<:Kick:1451836883469598761>"
SUCCESS     = "<:Successful:1445424805762302016>"
ERROR       = "<:Error:1445424808476016651>"
LINE        = "<:Line:1451857219690823691>"
COLOR       = 0x87CEEB 

def format_time():
    """Formats time to Today, Yesterday, or Date in 24h format (UTC+6)"""
    now = datetime.utcnow() + timedelta(hours=6)
    date_str, today_str = now.strftime("%d/%m/%Y"), now.strftime("%d/%m/%Y")
    yesterday_str = (now - timedelta(days=1)).strftime("%d/%m/%Y")
    time_part = now.strftime("%H:%M")
    
    if date_str == today_str: return f"Today at {time_part}"
    elif date_str == yesterday_str: return f"Yesterday at {time_part}"
    return f"{date_str} at {time_part}"

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_error(self, ctx_or_int, title, message):
        """Unified error sender for both Prefix and Slash commands"""
        author = ctx_or_int.user if isinstance(ctx_or_int, discord.Interaction) else ctx_or_int.author
        embed = discord.Embed(title=f"{ERROR} {title}", description=message, color=COLOR)
        embed.set_footer(text=f"Requested by {author.name} | {format_time()}", icon_url=author.display_avatar.url)
        
        if isinstance(ctx_or_int, discord.Interaction):
            if ctx_or_int.response.is_done(): await ctx_or_int.followup.send(embed=embed, ephemeral=True)
            else: await ctx_or_int.response.send_message(embed=embed, ephemeral=True)
        else:
            await ctx_or_int.send(embed=embed)

    # ---------- ERROR HANDLERS ----------
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not ctx.command or ctx.command.cog is not self: return

        if isinstance(error, (commands.BadArgument, commands.MemberNotFound, commands.UserNotFound)):
            await self.send_error(ctx, "Invalid User", f"I couldn't find that user. Please mention them or use their ID.\n\n{LINE} **Example:** `{ctx.prefix}{ctx.command} @User reason`")
        elif isinstance(error, commands.MissingRequiredArgument):
            await self.send_error(ctx, "Missing Argument", f"Required argument missing.\n\n{LINE} **Usage:** `{ctx.prefix}{ctx.command} @user [reason]`")
        elif isinstance(error, (commands.MissingPermissions, commands.NotOwner)):
            await self.send_error(ctx, "Permission Denied", "You don't have the necessary permissions.")
        elif isinstance(error, commands.BotMissingPermissions):
            await self.send_error(ctx, "Bot Error", f"I am missing: `{', '.join(error.missing_permissions)}`")
        elif isinstance(error, commands.CommandOnCooldown):
            await self.send_error(ctx, "Slow Down", f"Cooldown active. Try again in `{error.retry_after:.1f}s`.")
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if isinstance(original, discord.Forbidden):
                await self.send_error(ctx, "Forbidden", "I can't do that. My role might be too low.")
            elif isinstance(original, discord.HTTPException) and original.code == 50035:
                await self.send_error(ctx, "Input Error", "The reason is too long (Max 512 chars).")
            else:
                await self.send_error(ctx, "Action Failed", f"Something went wrong: `{str(original)}`")

    # ---------- BAN, KICK, & UNBAN ----------

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_prefix(self, ctx, member: discord.User, *, reason: str = "No reason provided"):
        await self.handle_action(ctx, ctx.guild.get_member(member.id) or member, reason, "ban")

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_prefix(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        await self.handle_action(ctx, member, reason, "kick")

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_prefix(self, ctx, user_id: str, *, reason: str = "No reason provided"):
        await self.handle_unban_logic(ctx, user_id, reason)

    # ---------- SLASH COMMANDS ----------

    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_slash(self, it: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await it.response.defer(); await self.handle_action(it, member, reason, "ban")

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick_slash(self, it: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await it.response.defer(); await self.handle_action(it, member, reason, "kick")

    @app_commands.command(name="unban", description="Unban a user by ID")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban_slash(self, it: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        await it.response.defer(); await self.handle_unban_logic(it, user_id, reason)

    # ---------- CORE LOGIC ----------

    async def handle_unban_logic(self, ctx_or_it, user_id, reason):
        try:
            uid = int(user_id.strip("<@!>"))
            user = await self.bot.fetch_user(uid)
            await ctx_or_it.guild.unban(user, reason=reason)
            
            author = ctx_or_it.user if isinstance(ctx_or_it, discord.Interaction) else ctx_or_it.author
            embed = discord.Embed(title=f"{SUCCESS} User Unbanned", color=COLOR)
            embed.description = f"**{user.name}** has been unbanned.\n{LINE} **Reason:** {reason}"
            embed.set_footer(text=f"By {author.name} | {format_time()}", icon_url=author.display_avatar.url)
            
            if isinstance(ctx_or_it, discord.Interaction): await ctx_or_it.followup.send(embed=embed)
            else: await ctx_or_it.send(embed=embed)
        except (ValueError, discord.NotFound):
            await self.send_error(ctx_or_it, "Search Failed", "Invalid ID or user not found/banned.")
        except Exception as e:
            await self.send_error(ctx_or_it, "Error", str(e))

    async def handle_action(self, ctx_or_it, member, reason: str, action: str):
        author = ctx_or_it.user if isinstance(ctx_or_it, discord.Interaction) else ctx_or_it.author
        guild, t = ctx_or_it.guild, format_time()

        # Hierarchy & Logic Checks
        if member.id == author.id: return await self.send_error(ctx_or_it, "Error", f"You can't {action} yourself.")
        if isinstance(member, discord.Member):
            if member.id == guild.owner_id: return await self.send_error(ctx_or_it, "Error", "Can't touch the owner.")
            if member.top_role >= author.top_role and author.id != guild.owner_id:
                return await self.send_error(ctx_or_it, "Hierarchy Error", "Your role is too low.")
            if member.top_role >= guild.me.top_role:
                return await self.send_error(ctx_or_it, "Hierarchy Error", "My role is below theirs.")

        emoji = BAN_EMOJI if action == "ban" else KICK_EMOJI
        
        # DM Attempt
        try:
            dm = discord.Embed(title=f"{emoji} {action.capitalize()}ed", color=COLOR)
            dm.description = f"**Server:** {guild.name}\n**Reason:** {reason}\n**Time:** {t}"
            await member.send(embed=dm)
        except: pass

        # Execution
        try:
            if action == "ban": await guild.ban(member, reason=reason)
            else: await member.kick(reason=reason)

            res = discord.Embed(title=f"{emoji} Member {action.capitalize()}ed", color=COLOR)
            res.description = f"{SUCCESS} **{member}** was processed successfully."
            res.add_field(name="Details", value=f"{LINE} **Reason:** {reason}\n{LINE} **Time:** {t}")
            res.set_footer(text=f"Mod: {author.name}", icon_url=author.display_avatar.url)

            if isinstance(ctx_or_it, discord.Interaction): await ctx_or_it.followup.send(embed=res)
            else: await ctx_or_it.send(embed=res)
        except Exception as e:
            await self.send_error(ctx_or_it, "Critical Error", str(e))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
