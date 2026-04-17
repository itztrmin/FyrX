import discord

def sky_blue_embed(title=None, description=None):
    """Return a simple sky blue embed."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=0x87CEEB  # Sky blue color
    )
    return embed