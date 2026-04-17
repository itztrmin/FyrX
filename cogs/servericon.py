import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

class ServerAvatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # PREFIX COMMAND
    @commands.command(name="serveravatar")
    async def serveravatar_prefix(self, ctx):
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used in a server!")
            return

        avatar_url = guild.icon.url if guild.icon else None
        if not avatar_url:
            await ctx.send("This server has no avatar!")
            return

        embed = discord.Embed(
            title=f"<:info:1445424802994192426> Server Avatar - {guild.name}",
            color=0x87CEEB  # Sky Blue
        )
        embed.set_image(url=avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        # Button
        view = View()
        button = Button(label="Click Here", url=avatar_url, style=discord.ButtonStyle.link)
        view.add_item(button)

        await ctx.send(embed=embed, view=view)

    # SLASH COMMAND
    @app_commands.command(name="serveravatar", description="Shows the server's avatar")
    async def serveravatar_slash(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command can only be used in a server!", ephemeral=True)
            return

        avatar_url = guild.icon.url if guild.icon else None
        if not avatar_url:
            await interaction.response.send_message("This server has no avatar!", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"<:info:1445424802994192426> Server Avatar - {guild.name}",
            color=0x87CEEB  # Sky Blue
        )
        embed.set_image(url=avatar_url)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        # Button
        view = View()
        button = Button(label="Click Here", url=avatar_url, style=discord.ButtonStyle.link)
        view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ServerAvatar(bot))