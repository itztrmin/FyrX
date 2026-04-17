import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

class UserAvatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # PREFIX COMMAND
    @commands.command(name="useravatar")
    async def useravatar_prefix(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        avatar_url = member.display_avatar.url

        embed = discord.Embed(
            title=f"<:info:1445424802994192426> User Avatar - {member}",
            color=0x87CEEB  # Sky blue
        )
        embed.set_image(url=avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        # Button
        view = View()
        button = Button(label="Click Here", url=avatar_url, style=discord.ButtonStyle.link)
        view.add_item(button)

        await ctx.send(embed=embed, view=view)

    # SLASH COMMAND
    @app_commands.command(name="useravatar", description="Shows the avatar of a user")
    async def useravatar_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user

        avatar_url = member.display_avatar.url

        embed = discord.Embed(
            title=f"<:info:1445424802994192426> User Avatar - {member}",
            color=0x87CEEB  # Sky blue
        )
        embed.set_image(url=avatar_url)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        # Button
        view = View()
        button = Button(label="Click Here", url=avatar_url, style=discord.ButtonStyle.link)
        view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(UserAvatar(bot))