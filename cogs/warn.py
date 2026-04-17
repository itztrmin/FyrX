import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import json
import os
import math

# CONFIG
WARN_ICON    = "<:Warn:1453410451286266100>" 
LIST_ICON    = "📜"
ERROR_ICON   = "<:Error:1445424808476016651>"
SUCCESS_ICON = "<:Successful:1445424805762302016>"
LINE         = "<:Line:1451857219690823691>"
COLOR        = 0x87CEEB 
DATA_FILE    = "warns.json"

def format_time(dt_obj=None):
    now = datetime.utcnow() + timedelta(hours=6)
    target = dt_obj if dt_obj else now
    date_str = target.strftime("%d/%m/%Y")
    today_str = now.strftime("%d/%m/%Y")
    yesterday_str = (now - timedelta(days=1)).strftime("%d/%m/%Y")
    time_part = target.strftime("%H:%M")
    if date_str == today_str: return f"Today at {time_part}"
    elif date_str == yesterday_str: return f"Yesterday at {time_part}"
    else: return f"{date_str} at {time_part}"

class WarnPaginator(discord.ui.View):
    def __init__(self, data, author, guild_name):
        super().__init__(timeout=60)
        self.data, self.author, self.guild_name = data, author, guild_name
        self.current_page = 0
        self.items_per_page = 5
        self.total_pages = math.ceil(len(data) / self.items_per_page)

    async def get_page_embed(self):
        start = self.current_page * self.items_per_page
        page_data = self.data[start:start + self.items_per_page]
        embed = discord.Embed(title=f"{LIST_ICON} Server Warnings: {self.guild_name}", color=COLOR)
        description = ""
        for index, w in enumerate(page_data, start=start + 1):
            description += f"**{index}.** {LINE} <@{w['user_id']}>\n   └─ **Reason:** {w['reason']}\n   └─ **Mod:** <@{w['mod_id']}> • **Date:** {w['time']}\n\n"
        embed.description = description or "No warnings found."
        embed.set_footer(text=f"Requested by {self.author.name} | {format_time()}", icon_url=self.author.display_avatar.url)
        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=await self.get_page_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id: return
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=await self.get_page_embed(), view=self)

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f: json.dump({}, f)

    def get_data(self):
        try:
            with open(DATA_FILE, "r") as f:
                content = json.load(f)
                return content if isinstance(content, dict) else {}
        except: return {}

    def save_data(self, data):
        with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)

    async def send_error(self, ctx_or_int, title, message):
        author = ctx_or_int.user if isinstance(ctx_or_int, discord.Interaction) else ctx_or_int.author
        embed = discord.Embed(title=f"{ERROR_ICON} {title}", description=message, color=COLOR)
        embed.set_footer(text=f"Requested by {author.name} | {format_time()}", icon_url=author.display_avatar.url)
        if isinstance(ctx_or_int, discord.Interaction):
            await (ctx_or_int.followup.send if ctx_or_int.response.is_done() else ctx_or_int.response.send_message)(embed=embed, ephemeral=True)
        else: await ctx_or_int.send(embed=embed)

    async def process_warn(self, ctx_or_int, member, reason):
        author = ctx_or_int.user if isinstance(ctx_or_int, discord.Interaction) else ctx_or_int.author
        if member.id == author.id: return "You cannot warn yourself."
        if member.bot: return "Bots cannot be warned."
        if member.top_role >= author.top_role and author.id != ctx_or_int.guild.owner_id:
            return "Role Hierarchy: Target has equal/higher role."
        time_now = format_time()
        try:
            dm = discord.Embed(title=f"{WARN_ICON} You have been warned", description=f"Server: **{ctx_or_int.guild.name}**", color=discord.Color.red())
            dm.add_field(name="Reason", value=reason)
            dm.set_footer(text=time_now)
            await member.send(embed=dm)
        except: pass 
        data = self.get_data()
        gid, mid = str(ctx_or_int.guild.id), str(member.id)
        if gid not in data: data[gid] = {}
        if mid not in data[gid]: data[gid][mid] = []
        data[gid][mid].append({"mod_id": author.id, "reason": reason, "time": time_now})
        self.save_data(data)
        return None

    # ---------- WARN COMMANDS ----------

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(member="Member to warn", reason="Reason is required")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        await interaction.response.defer()
        err = await self.process_warn(interaction, member, reason)
        if err: return await self.send_error(interaction, "Action Failed", err)
        embed = discord.Embed(description=f"{SUCCESS_ICON} **{member.mention} has been warned**\n{LINE} **Reason:** {reason}", color=COLOR)
        embed.set_footer(text=f"Requested by {interaction.user.name} | {format_time()}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @commands.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn_prefix(self, ctx, member: discord.Member, *, reason: str):
        err = await self.process_warn(ctx, member, reason)
        if err: return await self.send_error(ctx, "Action Failed", err)
        embed = discord.Embed(description=f"{SUCCESS_ICON} **{member.mention} has been warned**\n{LINE} **Reason:** {reason}", color=COLOR)
        embed.set_footer(text=f"Requested by {ctx.author.name} | {format_time()}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    # ---------- WARNLIST COMMANDS ----------

    @app_commands.command(name="warnlist", description="View server warnings")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnlist_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.execute_warnlist(interaction)

    @commands.command(name="warnlist")
    @commands.has_permissions(moderate_members=True)
    async def warnlist_prefix(self, ctx):
        await self.execute_warnlist(ctx)

    async def execute_warnlist(self, ctx_or_int):
        data = self.get_data()
        guild = ctx_or_int.guild
        author = ctx_or_int.user if isinstance(ctx_or_int, discord.Interaction) else ctx_or_int.author
        
        gid = str(guild.id)
        guild_data = data.get(gid, {})
        all_warns = []
        
        for uid, warns in guild_data.items():
            for w in warns:
                w['user_id'] = uid
                all_warns.append(w)
        
        if not all_warns: 
            return await self.send_error(ctx_or_int, "Empty", "No warnings found in this server.")
        
        all_warns.reverse() # Show newest first
        view = WarnPaginator(all_warns, author, guild.name)
        
        if isinstance(ctx_or_int, discord.Interaction):
            await ctx_or_int.followup.send(embed=await view.get_page_embed(), view=view)
        else:
            await ctx_or_int.send(embed=await view.get_page_embed(), view=view)

async def setup(bot):
    await bot.add_cog(Warn(bot))
