import discord
from discord.ext import commands
from discord import app_commands
import json, os, time, re

# =========================
# EMOJIS
# =========================
AFK_EMOJI = "<:Afk:1447775032729403483>"
SUCCESS   = "<:Successful:1445424805762302016>"
ERROR     = "<:Error:1445424808476016651>"
MENTION   = "<:Mention:1449672888025088070>"
DISTURB   = "<:Disturb:1449672885508636682>"

AFK_FILE = "data/afk.json"

# =========================
# HELPERS
# =========================
def sky_blue_embed(title=None, description=None):
    return discord.Embed(title=title, description=description, color=0x87CEEB)

def ensure_file():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(AFK_FILE):
        with open(AFK_FILE, "w") as f:
            json.dump({}, f)

def load_afk():
    ensure_file()
    try:
        with open(AFK_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_afk(data):
    ensure_file()
    with open(AFK_FILE, "w") as f:
        json.dump(data, f, indent=4)

def contains_link(text: str):
    if not text:
        return False
    return bool(re.search(r"(https?://|www\.|\.(com|net|org|gg|io|xyz))", text.lower()))

def duration(sec):
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    if h:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"

# =========================
# VIEWS
# =========================
class AfkScopeView(discord.ui.View):
    def __init__(self, user, reason, msg, callback):
        super().__init__(timeout=60)
        self.user = user
        self.reason = reason
        self.msg = msg
        self.callback = callback

    async def interaction_check(self, i):
        return i.user.id == self.user.id

    @discord.ui.button(label="Guild", style=discord.ButtonStyle.blurple)
    async def guild(self, i, _):
        await i.response.defer()
        await self.callback(i, "guild", self.reason, self.msg)

    @discord.ui.button(label="Global", style=discord.ButtonStyle.green)
    async def global_(self, i, _):
        await i.response.defer()
        await self.callback(i, "global", self.reason, self.msg)

class AfkDMView(discord.ui.View):
    def __init__(self, user, scope, reason, msg, callback):
        super().__init__(timeout=60)
        self.user = user
        self.scope = scope
        self.reason = reason
        self.msg = msg
        self.callback = callback

    async def interaction_check(self, i):
        return i.user.id == self.user.id

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, i, _):
        await i.response.defer()
        await self.callback(i, self.scope, self.reason, True, self.msg)

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, i, _):
        await i.response.defer()
        await self.callback(i, self.scope, self.reason, False, self.msg)

# =========================
# COG
# =========================
class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk = load_afk()

    def reload(self):
        self.afk = load_afk()

    # ---------- CHECK ----------
    def is_already_afk(self, user_id, guild_id, scope):
        entry = self.afk.get(user_id)
        if not entry:
            return False

        if entry["scope"] == "global":
            return True

        if scope == "guild" and entry["guild_id"] == str(guild_id):
            return True

        return False

    # ---------- PREFIX ----------
    @commands.command(name="afk")
    async def afk_prefix(self, ctx, *, reason=None):
        reason = reason or "I'm AFK:) "
        self.reload()

        if contains_link(reason):
            return await ctx.send(embed=sky_blue_embed(
                f"{ERROR} Invalid Reason",
                "Links are not allowed in AFK reasons."
            ))

        embed = sky_blue_embed(
            f"{AFK_EMOJI} AFK Setup",
            "How do you want to set your AFK?\n\n**Guild** or **Global**"
        )

        msg = await ctx.send(embed=embed)
        await msg.edit(view=AfkScopeView(ctx.author, reason, msg, self.ask_dm))

    # ---------- SLASH ----------
    @app_commands.command(name="afk", description="Set yourself as AFK")
    async def afk_slash(self, interaction: discord.Interaction, reason: str = None):
        reason = reason or "I'm AFK:) "
        self.reload()

        if contains_link(reason):
            return await interaction.response.send_message(
                embed=sky_blue_embed(f"{ERROR} Invalid Reason", "Links are not allowed."),
                ephemeral=True
            )

        embed = sky_blue_embed(
            f"{AFK_EMOJI} AFK Setup",
            "How do you want to set your AFK?\n\n**Guild** or **Global**"
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)
        msg = await interaction.original_response()
        await msg.edit(view=AfkScopeView(interaction.user, reason, msg, self.ask_dm))

    # ---------- STEP 2 ----------
    async def ask_dm(self, interaction, scope, reason, msg):
        uid = str(interaction.user.id)

        if self.is_already_afk(uid, interaction.guild.id, scope):
            return await msg.edit(
                embed=sky_blue_embed(
                    f"{ERROR} Already AFK",
                    "You are already AFK with this scope."
                ),
                view=None
            )

        embed = sky_blue_embed(
            "Mention Alerts",
            "Should I DM you when someone mentions you while AFK?"
        )

        await msg.edit(
            embed=embed,
            view=AfkDMView(interaction.user, scope, reason, msg, self.enable_afk)
        )

    # ---------- FINAL ----------
    async def enable_afk(self, interaction, scope, reason, dm, msg):
        uid = str(interaction.user.id)

        self.afk[uid] = {
            "reason": reason,
            "since": int(time.time()),
            "mentions": 0,
            "dm": dm,
            "scope": scope,
            "guild_id": str(interaction.guild.id) if scope == "guild" else None
        }

        save_afk(self.afk)
        self.reload()

        embed = sky_blue_embed(
            f"{AFK_EMOJI} **AFK Enabled**",
            f"**{interaction.user.display_name}** is now AFK.\n\n"
            f"**Reason:** {reason}\n"
            f"**Scope:** {scope.title()}"
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await msg.edit(embed=embed, view=None)

    # ---------- LISTENER ----------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        self.reload()
        uid = str(message.author.id)

        # REMOVE AFK
        if uid in self.afk:
            entry = self.afk[uid]
            if entry["scope"] == "global" or entry["guild_id"] == str(message.guild.id):
                removed = self.afk.pop(uid)
                save_afk(self.afk)

                await message.channel.send(embed=sky_blue_embed(
                    f"{SUCCESS} Welcome Back!",
                    f"AFK Duration: {duration(int(time.time() - removed['since']))}\n"
                    f"Mentions: {removed['mentions']}"
                ))

        # MENTION CHECK
        for member in message.mentions:
            entry = self.afk.get(str(member.id))
            if not entry:
                continue
            if entry["scope"] == "guild" and entry["guild_id"] != str(message.guild.id):
                continue

            entry["mentions"] += 1
            save_afk(self.afk)

            await message.reply(
                embed=sky_blue_embed(
                    f"{DISTURB} User is AFK",
                    f"**{member.display_name}** is AFK\nReason: {entry['reason']}"
                ),
                mention_author=False
            )

async def setup(bot):
    await bot.add_cog(AFK(bot))