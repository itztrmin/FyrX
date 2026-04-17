import discord
from discord.ext import commands
import time

SERVER = "<:Server:1447531451968127080>"
ERROR = "<:Error:1445424808476016651>"
HEART = "<a:Heart:1447609087922540565>"

class MentionResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}  # {guild_id: [timestamps]}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Respond only if message starts with mention
        if not message.content.startswith(f"<@{self.bot.user.id}>") and \
           not message.content.startswith(f"<@!{self.bot.user.id}>"):
            return

        guild_id = message.guild.id

        # Anti-spam
        now = time.time()
        if guild_id not in self.cooldowns:
            self.cooldowns[guild_id] = []

        self.cooldowns[guild_id].append(now)
        self.cooldowns[guild_id] = [t for t in self.cooldowns[guild_id] if now - t <= 10]

        if len(self.cooldowns[guild_id]) >= 3:
            embed = discord.Embed(
                description=f"{ERROR} **Relax... I'm Alive!**",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Requested by {message.author} • FyrX™", icon_url=self.bot.user.display_avatar.url)
            return await message.reply(embed=embed)

        # Main embed
        prefix = "×"
        embed = discord.Embed(
            description=(
                f"{SERVER} **{message.guild.name}**\n"
                f"Hey {message.author.mention}\n\n"
                f"**Prefix for this server:** `{prefix}`\n"
                f"**Server ID:** `{message.guild.id}`\n\n"
                f"Type `×help` for more information."
            ),
            color=discord.Color.dark_gray()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Requested by {message.author} • FyrX™", icon_url=self.bot.user.display_avatar.url)

        # Buttons below embed
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Invite",
            url="https://discord.com/oauth2/authorize?client_id=1272871619731390505&permissions=8&scope=bot+applications.commands",
            style=discord.ButtonStyle.link
        ))
        view.add_item(discord.ui.Button(
            label="Web",
            url="https://your-link-here.com",
            style=discord.ButtonStyle.link
        ))
        view.add_item(discord.ui.Button(
            label="Vote",
            url="https://your-link-here.com",
            style=discord.ButtonStyle.link
        ))

        await message.reply(embed=embed, view=view)

        # Process other commands
        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(MentionResponder(bot))