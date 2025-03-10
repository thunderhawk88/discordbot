import discord,pathlib,random,datetime,json,os,subprocess
from discord.ext import commands, tasks

path_ = pathlib.Path(__file__).parent.absolute() # path to discord bot script
temppath = os.path.join(path_,"temps")
serverList = os.path.join(temppath, "servers.json")
getMangaScript = os.path.join(path_,"Get-Manga.ps1")
mangaRecommended = os.path.join(temppath,"manga.json")
mangaRecommended2 = os.path.join(temppath,"manga2.json")

#OnCrax Channel IDs
chan_announ = 1040696808797650974 #announcements channel
chan_gen = 845072862397333506 #general in text channel
chan_tests = 1041382186793848922 #tests in text channel
chan_craxstats = 1138670086861897738 #crax_stats channel
chan_craxevents = 1140037396151418951 #crax_events channel
chan_craxservers = 1124176437344211115 #crax_servers channel
chan_craxmanga = 1040813089735577652 #crax_animemangarecommendation channel
#end channels

def getServers():
    _craxservers = None

    if os.path.isfile(serverList):
        try:
            with open(serverList, "r") as sfile:
                _craxservers = json.load(sfile)
            print("Loaded successfully: " + str(serverList))
        except:
            _craxservers = None
            print("Error loading server json file.")

        if (_craxservers != None):
            return _craxservers
        else:
            return None
    else:
        return 404
    
def getManga():
    _manga = None
    _p = subprocess.Popen(["powershell.exe", "-File", getMangaScript])
    _p.communicate()

    try:
        with open(mangaRecommended, "r", encoding = "utf-8-sig") as sfile:
            _manga = json.load(sfile)
        print("Loaded successfully: " + str(mangaRecommended))
    except:
        _manga != None
        print("Error loading manga json file.")

    if (_manga != None):
        return _manga
    else:
        return None
    
def getManga2():
    _manga = None

    try:
        with open(mangaRecommended2, "r", encoding = "utf-8-sig") as sfile:
            _manga = json.load(sfile)
        print("Loaded successfully: " + str(mangaRecommended2))
    except Exception as e:
        _manga = None
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)

    if (_manga != None):
        _rand = random.randint(1, len(_manga))
        return _manga[str(_rand)]
    else:
        return None

# delete oldStats.txt
# os.remove(f'{path_}/oldstats.txt')

# bot = discord.Bot(intents=discord.Intents.all())
bot = discord.Bot(intents=discord.Intents.all())

bot_games = ['Palworld','Starfield','Apex Legends','Grounded','Valheim','DCS World','Plate Up','Terraria','Phasmophobia','Green Hell','Dead by Daylight','Icarus','Sons of the Forest','Outlast Trials','Diablo 4','Remnant II','Jagged Alliance 3']
@bot.event
async def on_ready():
    # Setting `Playing ` status
    await bot.change_presence(activity=discord.Game(name=random.choice(bot_games)))
    # # Setting `Streaming ` status
    # await bot.change_presence(activity=discord.Streaming(name="My Stream", url=my_twitch_url))
    # # Setting `Listening ` status
    # await bot.change_presence(activity=discord. Activity(type=discord.ActivityType.listening, name='Mariah Carey - All I Want For Christmas Is You'))
    # # Setting `Watching ` status
    # await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="a movie"))
    # Clear CraxStats Channel
    # print(f'Current path_: {path_}')
    # crax_stats = bot.get_channel(chan_craxstats)
    # await crax_stats.purge(limit=100)
    # Delete Saved message ID file; for craxStats Channel
    # oldStats_path = f"{path_}\\temps\\.oldstats"
    # print(oldStats_path)
    # os.remove(oldStats_path)

@bot.slash_command(name='crax', description="Just for testing slash command.", guild_ids=[845072861915512897])
async def crax(ctx):
	await ctx.respond('I am alive!')

@bot.slash_command(name='changebotgame', description="Changes what game Craxbot is playing.", guild_ids=[845072861915512897])
async def botgame(ctx, game: str):
    # game = random.choice(bot_games)
    await bot.change_presence(activity=discord.Game(name=game))
    await ctx.respond(f'Bot game changed to {game}.')

@bot.slash_command(name='servers', description="Will attempt to get a list of servers owned by Crax.")
async def embed(ctx):
    channeltosend = bot.get_channel(ctx.channel.id)
    cservers = getServers()
    if cservers != None and cservers != 404:
        embedList = []
        # embed = discord.Embed(title = "**List of Servers**", description = "Here are the list of servers managed by Crax.", color = discord.Color.green())
        for game in cservers:
            for server in cservers[game]:
                if (type(cservers[game][server]) == dict):
                    embed = discord.Embed(title = "", description = "", color = discord.Color.green())
                    embed.add_field(name = "**Game:** " + str(cservers[game][server]['game']), value = "", inline = False)
                    embed.add_field(name = "**Server Name:** " + str(cservers[game][server]['servername']), value = "", inline = False)
                    embed.add_field(name = "**IP & Port:** " + str(cservers[game][server]['ip']) + ":" + str(cservers[game][server]['port']), value = "", inline = False)
                    if (cservers[game][server]['password'] != ''):
                        embed.add_field(name = "**Password:** " + str(cservers[game][server]['password']), value = "", inline = False)
                    if (cservers[game][server]['note'] != ''):
                        embed.add_field(name = "**Notes:** ", value = str(cservers[game][server]['note']), inline = False)
                    embedList.append(embed)
        print(embedList)
        # await ctx.respond(embed=embedList)
        await channeltosend.send(embeds=embedList)
        await ctx.respond("Crax servers")
        embedList = []
    elif cservers == 404:
        await ctx.respond("Server file not found.")
    else:
        await ctx.respond("Error!")

@bot.slash_command(name='manga', description="Retrieve one 'HOT' manga at Mangakakalot.")
async def embed(ctx):
    cManga = getManga2()
    if cManga != None:
        embed = discord.Embed(title = "**" + str(cManga['Title']) + "**", url = str(cManga['Link']), description = str(cManga['Description']), color = discord.Color.blue())
        embed.set_image(url = str(cManga['Image']))
        embed.add_field(name = " ", value = " 👁️ **Reads:** " + "*{:,}*".format(cManga['Reads']), inline = False)
        print('Picked manga: ' + str(cManga['Title']))
        await ctx.respond(embed=embed)
    else:
        await ctx.respond("Error retrieving a manga title.")

@bot.slash_command(name='adminmanga', description="Force post new recommended manga in a channel.")
async def embed(ctx):
    print("adminmanga has been called.")
    # message_channel = bot.get_channel(chan_craxmanga)
    message_channel = bot.get_channel(chan_tests)
    cManga = getManga()
    if cManga != None:
        embed = discord.Embed(title = "**" + str(cManga['Title']) + "**", url = str(cManga['Link']), description = str(cManga['Description']), color = discord.Color.blue())
        embed.set_image(url = str(cManga['Image']))
        embed.set_author(name="MangaDex", url="https://mangadex.org/")
        embed.add_field(name = " ", value = " ⭐ **Avg. Rating:** " + "*{:,}*".format(cManga['Rating']))
        embed.add_field(name = " ", value = " 🔖 **Bookmarks:** " + "*{:,}*".format(cManga['Follows']))
        # embed.set_footer(text="This is made possible by mangadex.org",icon_url="https://styles.redditmedia.com/t5_fljgj/styles/communityIcon_dodprbccfsy71.png")
        print("Posted new manga recommendation: " + str(cManga['Title']))
        await message_channel.send(embed=embed)
        await ctx.respond("Successfully added a manga recommendation to " + str(message_channel) + " channel.")
    else:
        await ctx.respond("Error retrieving a manga title.")

### BEGIN ACTIONS

@bot.user_command(guild_ids=[845072861915512897])
async def punch(ctx, user):
    await ctx.send(f'{ctx.author.mention} punched :right_facing_fist::skin-tone-1: {user.mention}!' )

@bot.user_command(guild_ids=[845072861915512897])
async def poke(ctx, user):
    await ctx.send(f'{ctx.author.mention} poked :point_right::skin-tone-1: {user.mention}!')

@bot.user_command(guild_ids=[845072861915512897])
async def pat(ctx, user):
    await ctx.send(f'{ctx.author.mention} patted :palm_down_hand::skin-tone-1: {user.mention} head!')

### END ACTIONS

### BEGIN REACTIONS
reacts_ = ['good morning','nice','noice','anya','happy thanks giving','happy thanks giving!','crax_test']
anya_url = ['https://media0.giphy.com/media/FWAcpJsFT9mvrv0e7a/giphy.gif?cid=ecf05e47sakbuikp7qgb0g5y9gexu5wckjpntefroo4pj9c7&rid=giphy.gif&ct=g',
            'https://media0.giphy.com/media/zZC2AqB84z7zFnlkbF/giphy.gif?cid=ecf05e47sakbuikp7qgb0g5y9gexu5wckjpntefroo4pj9c7&rid=giphy.gif&ct=g',
            'https://media1.giphy.com/media/7m2HklUvR2oFkeeiDg/giphy.gif?cid=ecf05e47sakbuikp7qgb0g5y9gexu5wckjpntefroo4pj9c7&rid=giphy.gif&ct=g',
            'https://media0.giphy.com/media/q1R1ZiUskINVOn6bz3/giphy.gif?cid=ecf05e470q7hxze8kykosvpw48tob02ytl6z3ybqfjsd6qsw&rid=giphy.gif&ct=g',
            'https://media4.giphy.com/media/37Md3lHS7s6k2tHIp7/giphy.gif?cid=ecf05e470q7hxze8kykosvpw48tob02ytl6z3ybqfjsd6qsw&rid=giphy.gif&ct=g',
            'https://media1.giphy.com/media/tpYaafBDNVKn1soXNI/giphy.gif?cid=ecf05e470q7hxze8kykosvpw48tob02ytl6z3ybqfjsd6qsw&rid=giphy.gif&ct=g',
            'https://media3.giphy.com/media/9k9OEZ3aRHPlR8YAei/giphy.gif?cid=ecf05e470q7hxze8kykosvpw48tob02ytl6z3ybqfjsd6qsw&rid=giphy.gif&ct=g',
            'https://media2.giphy.com/media/Zh0De6qyNjDdmxy8Za/giphy.gif?cid=ecf05e470q7hxze8kykosvpw48tob02ytl6z3ybqfjsd6qsw&rid=giphy.gif&ct=g',
            'https://media1.giphy.com/media/LxPhEh5yYHkviFtLUy/giphy.gif?cid=ecf05e470q7hxze8kykosvpw48tob02ytl6z3ybqfjsd6qsw&rid=giphy.gif&ct=g',
            'https://media1.giphy.com/media/edGzBC6GDOhutW32ps/giphy.gif?cid=ecf05e470q7hxze8kykosvpw48tob02ytl6z3ybqfjsd6qsw&rid=giphy.gif&ct=g',
            'https://media3.giphy.com/media/DNe4LKL6iwZ2goCSx6/giphy.gif?cid=ecf05e470q7hxze8kykosvpw48tob02ytl6z3ybqfjsd6qsw&rid=giphy.gif&ct=g',
            'https://media1.giphy.com/media/wcFkRXdMmDrRi1Vo08/giphy.gif?cid=ecf05e470q7hxze8kykosvpw48tob02ytl6z3ybqfjsd6qsw&rid=giphy.gif&ct=g',
            'https://media1.giphy.com/media/NRO0LLcPb4jKcU375F/giphy.gif?cid=ecf05e470q7hxze8kykosvpw48tob02ytl6z3ybqfjsd6qsw&rid=giphy.gif&ct=g',
            'https://media2.giphy.com/media/TBdMZk2TOONwu0g9YS/giphy.gif?cid=ecf05e470q7hxze8kykosvpw48tob02ytl6z3ybqfjsd6qsw&rid=giphy.gif&ct=g']
htg_url =  ['https://media4.giphy.com/media/iq6sLARdMgGgDJ1ZYa/giphy.gif?cid=ecf05e47x329gkdslk1obw3db37ektlgxus3ay1h0yxd7euh&rid=giphy.gif&ct=g',
            'https://media2.giphy.com/media/W0VvyXqyGjlWJFZqLG/giphy.gif?cid=ecf05e47x329gkdslk1obw3db37ektlgxus3ay1h0yxd7euh&rid=giphy.gif&ct=g',
            'https://media1.giphy.com/media/YRoJR1ycDEkZd5VErv/giphy.gif?cid=ecf05e47x329gkdslk1obw3db37ektlgxus3ay1h0yxd7euh&rid=giphy.gif&ct=g']

# oldStats = ''
@bot.event
async def on_message(message, guild_ids=[845072861915512897]):  
    if (message.channel.id == chan_craxstats and message.content == 'clearstats'):
        crax_chan = bot.get_channel(chan_craxstats)
        _thisMessage = await crax_chan.fetch_message(message.id)
        # print(f'[DEBUG] Message ID: {_thisMessage}\n')
        await _thisMessage.delete()
        await crax_chan.purge(limit=500)

    if (message.channel.id == chan_craxevents and message.content == 'clearchannel'):
        crax_chan = bot.get_channel(chan_craxevents)
        await crax_chan.purge(limit=500)

    if (message.channel.id == chan_craxservers and message.content == 'clearchannel'):
        crax_chan = bot.get_channel(chan_craxservers)
        await crax_chan.purge(limit=500)

    if message.author.bot: 
        return
    else:
        for word in reacts_:
            # if word.casefold() in message.content.casefold():
            if message.content.casefold() == word.casefold():
                channeltosend = bot.get_channel(message.channel.id)
                embed = discord.Embed(title='', description='')
                color = 0x9b59b6
                if word.casefold() == reacts_[1] or word.casefold() == reacts_[2]: #noice react
                    #embed.add_field(name="**Add something**", value="Or delete this.", inline=False) 
                    embed.set_image(url='https://media0.giphy.com/media/yJFeycRK2DB4c/giphy.gif?cid=ecf05e47tgg97mt1gz6laeirur2kk5z8qb3pcd7urcgbnq1r&rid=giphy.gif&ct=g')
                    #embed.set_footer(text="add if u want something on the botton")
                    await message.delete()
                    await channeltosend.send(f'From {message.author.mention}\n', embed=embed)
                    break
                elif word.casefold() == reacts_[3]: #anya react
                    #embed.add_field(name="**Add something**", value="Or delete this.", inline=False) 
                    embed.set_image(url=random.choice(anya_url))
                    #embed.set_footer(text="add if u want something on the botton")
                    await message.delete()
                    await channeltosend.send(f'From {message.author.mention}\n', embed=embed)
                    break
### END REACTIONS

#Holiday greetings
@tasks.loop(hours=1)
async def called_every_hour():
    current_time = datetime.datetime.now()
    current_day = datetime.datetime.today()
    if ((current_time.day % 7) == 0 and current_time.hour == 4): # attemp to clear channels; current_time.hour to 4 since servers are set to restart at 5
        crax_serv = bot.get_channel(chan_craxservers)
        crax_evnt = bot.get_channel(chan_craxevents)
        await crax_serv.purge(limit=500)
        await crax_evnt.purge(limit=500)
    elif current_day.weekday() == 5 and current_time.hour == 8: # Post Hot manga; current_day().weekday() = 0 is monday, sunday is 6.
        print("It is Saturday!")
        message_channel = bot.get_channel(chan_craxmanga)
        cManga = getManga()
        if cManga != None:
            embed = discord.Embed(title = "**" + str(cManga['Title']) + "**", url = str(cManga['Link']), description = str(cManga['Description']), color = discord.Color.blue())
            embed.set_image(url = str(cManga['Image']))
            # embed.add_field(name = " ", value = " 👁️ **Reads:** " + "*{:,}*".format(cManga['Reads']), inline = False)
            embed.add_field(name = " ", value = " ⭐ **Avg. Rating:** " + "*{:,}*".format(cManga['Rating']), inline = False)
            embed.set_footer(text="This is made possible by mangadex.org",icon_url="https://styles.redditmedia.com/t5_fljgj/styles/communityIcon_dodprbccfsy71.png")
            print("Posted new manga recommendation: " + str(cManga['Title']))
        await message_channel.send(embed=embed)
    elif current_time.day == 27 and current_time.month == 11 and current_time.hour == 6: #ThanksGiving
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url='https://res.cloudinary.com/display97/image/upload/q_auto,fl_lossy,f_auto/v1362515922/-158162.jpg')
        await message_channel.send(f'@everyone\n\nWishing you a Thanksgiving full of **love** and **happiness**.\n\nI hope all the good things happen in your life.\n\n...', embed=embed)
    elif current_time.day == 25 and current_time.month == 12 and current_time.hour == 00: #Christmas
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url='https://media3.giphy.com/media/ABPYR9xUWHPsBH9A6y/giphy.gif?cid=ecf05e47ro4htl9036r9qvz775nwnmf1x8bqkqaj2c6i2rp5&ep=v1_gifs_search&rid=giphy.gif&ct=g')
        await message_channel.send(f'@everyone\n\nDear Santa,\n\nThis year please give me a big fat bank account and a slim body.\nYou mixed those two up last year.\n\n...', embed=embed)
    elif current_time.day == 1 and current_time.month == 1 and current_time.hour == 00: #NewYear
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url='https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnZpNTUzcDFlNGw0cmM0cTFlOWdiZTVlMzVmc25qNzdhNmhjY3NpdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/MnIcBxlyyZ9BeCmTnD/giphy.gif')
        await message_channel.send(f'@everyone\n\nMay all your troubles last as long\nas your New Year\'s resolutions.\n\n...', embed=embed)
    elif current_time.day == 11 and current_time.month == 5 and current_time.hour == 00: #MothersDay
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url='https://media.giphy.com/media/l0Iy6CDDwhhx8ogGQ/giphy.gif')
        await message_channel.send(f'@everyone\n\nHappy Mothers Day!\n\n...', embed=embed)
    elif current_time.day == 15 and current_time.month == 6 and current_time.hour == 00: #FathersDay
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOGRmMjIzMzNjNmRkMjNmMTBiZjY1ZTBiMWVlMmFhZmMzNjAzNzAyOSZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/fSkOEaXP639Xr5mI8E/giphy.gif')
        await message_channel.send(f'@everyone\n\nHappy Fathers Day!\n\n...', embed=embed)

@called_every_hour.before_loop
async def before():
    await bot.wait_until_ready()
    # print("Finished waiting")

called_every_hour.start()
#end

bot.run('TOKEN')