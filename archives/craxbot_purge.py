import discord
from discord.ext import commands, tasks
from pathlib import Path
import pathlib
import random
import datetime
import time
path_ = pathlib.Path(__file__).parent.absolute()

#OnCrax Channel IDs
chan_announ = 1040696808797650974 #announcements channel
chan_gen = 845072862397333506 #general in text channel
chan_tests = 1041382186793848922 #tests in text channel
chan_craxstats = 1138670086861897738 #crax_stats channel
#end channels

# bot = discord.Bot(intents=discord.Intents.all())
bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_message(message):
    purgeChannel = bot.get_channel(chan_craxstats)
    await purgeChannel.purge(limit=1,oldest_first=1)

bot.run('MTA0MTM2Nzg0NDQ0NjgxNDI0MA.GTc3_Z.aND0qSWCafrn0tS-tfT2exRq6RklcQtI9YcqNs')