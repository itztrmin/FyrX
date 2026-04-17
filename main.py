import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# --------------------------
# LOAD ENV VARIABLES
# --------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "×"
OWNER_ID = 1287359604736659489  # Your Discord ID

if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found in .env file!")

# --------------------------
# INTENTS
# --------------------------
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

# --------------------------
# PREFIX FUNCTION
# --------------------------
def get_prefix(bot, message):
    if message.author.id == OWNER_ID:
        # Always check PREFIX first, then no-prefix
        return [PREFIX, ""]
    return [PREFIX]

# --------------------------
# BOT CLASS
# --------------------------
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )

    async def setup_hook(self):
        # Load all cogs
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"✅ Loaded cog: {filename}")
                except Exception as e:
                    print(f"❌ Failed to load cog {filename}: {e}")
        # Sync slash commands globally
        await self.tree.sync()
        print("🌐 Slash commands synced.")

# --------------------------
# BOT INSTANCE
# --------------------------
bot = Bot()

# --------------------------
# ON READY EVENT
# --------------------------
@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Streaming(
            name="Prefix × | /help",
            url="https://twitch.tv/discord"
        )
    )
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Owner no-prefix ENABLED. Others require × prefix.")
    print("Bot is fully operational!")

# --------------------------
# RUN BOT
# --------------------------
bot.run(TOKEN)