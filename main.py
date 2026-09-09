# -*- coding: utf-8 -*-
"""
Bot base. Lee el token desde la variable de entorno DISCORD_TOKEN
(en Railway la configuras en Settings -> Variables).
"""

import os
import asyncio
import discord
from discord.ext import commands

TOKEN = os.environ.get("DISCORD_TOKEN")
PREFIX = "!"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"Conectado como {bot.user} (id: {bot.user.id})")


async def main():
    async with bot:
        await bot.load_extension("cogs.server_setup")
        await bot.start(TOKEN)


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError(
            "Falta la variable de entorno DISCORD_TOKEN. "
            "Configúrala en Railway (Settings -> Variables)."
        )
    asyncio.run(main())
      
