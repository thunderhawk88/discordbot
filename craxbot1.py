import discord,pathlib,random,datetime,json,os,subprocess,calendar,requests,csv,time
from discord.ext import commands, tasks

path_ = pathlib.Path(__file__).parent.absolute() # path to discord bot script
temppath = os.path.join(path_,"temps")
serverList = os.path.join(temppath, "servers.json")
getMangaScript = os.path.join(path_,"Get-Manga.ps1")
mangaRecommended = os.path.join(temppath,"manga.json")
CachedMangaFile = os.path.join(temppath,".mangaList")
CachedMovieFile = os.path.join(temppath,".movieList")
CraxDataFile = os.path.join(temppath,"craxbot_data.json")

#OnCrax Channel IDs
chan_announ = 1040696808797650974 #announcements channel
chan_gen = 845072862397333506 #general in text channel
chan_tests = 1041382186793848922 #tests in text channel
chan_craxstats = 1138670086861897738 #crax_stats channel
chan_craxevents = 1140037396151418951 #crax_events channel
chan_craxservers = 1124176437344211115 #crax_servers channel
chan_craxmanga = 1040813089735577652 #crax_animemangarecommendation channel
chan_craxmovie = 1349947144249020417 # movie-recommendations
#end channels

def getServers():
    _craxservers = None

    if os.path.isfile(serverList):
        try:
            with open(serverList, "r") as sfile:
                _craxservers = json.load(sfile)
            print("Loaded successfully: " + str(serverList))
        except Exception as e:
            _craxservers = None
            print("Error loading server json file.")
            print(e)

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
    except Exception as e:
        _manga != None
        print("Error loading manga json file.")
        print(e)

    if (_manga != None):
        return _manga
    else:
        return None
    
def getMangaV2(_CachedFile,_mangaRecommended):
    Limit_ = 24
    SelectedManga_ = None

    while SelectedManga_ == None:
        # Get mangas
        Result_ = Get_Manga(Limit_)
        # print(Result.content)

        # import cached manga titles
        CachedTitles_ = []
        if os.path.exists(_CachedFile):
            with open(_CachedFile, 'r') as file:
                CachedTitles_ = [line.strip() for line in file]
        
        # for _title in CachedTitles_:
        #     print('[' + _title + ']')

        if (Result_.status_code == 200):
            Result_ = Result_.json()
            SelectedManga_ = Select_Manga(Result_['data'],CachedTitles_)

            if (SelectedManga_ != None):
                # print()
                # print('SELECTED MANGA')
                # print('Title:       ' + SelectedManga_['Title'])
                # print('Image:       ' + SelectedManga_['Image'])
                # print('Link:        ' + SelectedManga_['Link'])
                # print('Rating:      ' + SelectedManga_['Rating'])
                # print('Follows:     ' + SelectedManga_['Follows'])
                # print('Description: \n' + SelectedManga_['Description'])

                # write to file
                mode = "w"
                MangaTitle_ = SelectedManga_['Title']
                if CachedTitles_:
                    mode = "a"
                    MangaTitle_ = "\n" + str(SelectedManga_['Title'])
                try:
                    with open(_CachedFile, mode) as file:
                        file.write(MangaTitle_)

                    # with open(_mangaRecommended, 'w', encoding='utf-8') as file:
                    #     json.dump(SelectedManga_, file, ensure_ascii=False, indent=4)
                except Exception as e:
                    print('Error updating manga titles: ' + str(e))

                return SelectedManga_
        else:
            print()
            print("Status Code: " + str(Result_.status_code))
            print("Message: " + str(Result_.reason))
            return None
        Limit_ = Limit_ + 8
        SelectedManga_ = None
    
def getCraxData(_CraxDataFile):
    _data = None

    try:
        with open(_CraxDataFile, "r", encoding = "utf-8-sig") as sfile:
            _data = json.load(sfile)
        print("Loaded successfully: " + str(_CraxDataFile))
    except Exception as e:
        _data != None
        print("Error loading manga json file.")
        print(e)

    if (_data != None):
        return _data
    else:
        return None

def find_nth_weekday(year, month, weekday, nth):
    """Find the nth occurrence of a specific weekday within a given month."""
    month_calendar = calendar.monthcalendar(year, month)
    weekday_count = 0
    for week in month_calendar:
        if week[weekday] != 0: # weekday indexing starts from 0 (Monday)
            weekday_count += 1
            if weekday_count == nth:
                return {"Year": year, "Month": month, "Day": week[weekday]}
    return None

def make_json(csvFilePath,_key):
    data = {}
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            key = rows[_key]
            data[key] = rows
    return data

def SendGet(_baseURL,_endpoint,_headers):
    _URI = str(_baseURL) + str(_endpoint)

    try:
        _response = _session.get(url = _URI, headers = _headers)
    except Exception as e:
        print("[" + str(_response.status_code) + "] API failed. URI = " + str(_URI) + "")
    
    return _response

def Get_Movie(_CachedFile,_Token):
    _baseURL= "https://imdb236.p.rapidapi.com/imdb"
    _endpoint = "/most-popular-movies"
    _headers = {
        'x-rapidapi-key': _Token,
        'x-rapidapi-host': "imdb236.p.rapidapi.com"
    }
    SelectedMovie_ = None

    try:
        _result = SendGet(_baseURL,_endpoint,_headers)
    except Exception as e:
        print('Error retrieving mangas: ')

    if _result.status_code == 200:
        _result = _result.json()
        movie_count_ = len(_result)
        CachedTitles_ = []

        if os.path.exists(_CachedFile):
            with open(_CachedFile, 'r') as file:
                CachedTitles_ = [line.strip() for line in file]

        while SelectedMovie_ == None:
            rand_ = random.randrange(movie_count_ - 1)
            if _result[rand_]['primaryTitle'] not in CachedTitles_:
                SelectedMovie_ = _result[rand_]
                break
    else:
        print('Error Movie API')
        return None
    
    # convert genre from array to string
    SelectedMovie_['genres'] = ','.join(map(str,SelectedMovie_['genres']))
    
    # write to file
    mode = "w"
    MovieTitle_ = SelectedMovie_['primaryTitle'] 
    if CachedTitles_:
        mode = "a"
        MovieTitle_ = "\n" + str(SelectedMovie_['primaryTitle'])

    try:
        with open(_CachedFile, mode) as file:
            file.write(MovieTitle_)
    except Exception as e:
        print('Error updating movie titles: ' + str(e))

    return SelectedMovie_

def Get_Manga(_Limit):
    _baseURL= "https://api.mangadex.org"
    _endpoint = "/manga?limit=" + str(_Limit) + "&order%5BfollowedCount%5D=desc"

    try:
        _result = SendGet(_baseURL,_endpoint,None)
    except Exception as e:
        print('Error retrieving mangas: ')

    return _result

def Get_MangaRating(_MangaID):
    _baseURL= "https://api.mangadex.org"
    _endpoint = "/statistics/manga/" + str(_MangaID)

    try:
        _result = SendGet(_baseURL,_endpoint,None)
    except Exception as e:
        print('Error retrieving manga rating: ' + str(e))

    return _result

def Get_MangaArtFilename(_CoverArtID):
    _baseURL= "https://api.mangadex.org"
    _endpoint = "/cover/" + str(_CoverArtID) + "?includes%5B%5D=manga"

    try:
        _result = SendGet(_baseURL,_endpoint,None)
    except Exception as e:
        print('Error retrieving cover filename: ' + str(e))

    return _result

def Select_Manga(_MangaList,_CachedTitles):
    MangaURL_ = "https://mangadex.org/title/"

    for manga in _MangaList:
        # clear variables
        Rating_ = None
        CoverArtID_ = None
        CoverArtFilename_ = None
        ImageLink_ = None
        MangaID_ = None
        Follows_ = None
        Title = None

        # check if the mangta title has already been recommended before
        if 'en' in manga['attributes']['title']:
            Title = manga['attributes']['title']['en']
        else:
            for key in manga['attributes']['title']: 
                Title = manga['attributes']['title'][key]
                break

        if Title not in _CachedTitles:
            MangaID_ = manga['id']

            # get ratings
            Rating_ = Get_MangaRating(MangaID_)
            if (Rating_.status_code == 200):
                Rating_ = Rating_.json()
                Follows_ = Rating_['statistics'][MangaID_]['follows']
                Rating_ = Rating_['statistics'][MangaID_]['rating']['average']

            # get cover art id
            # loop thru the array to find an element with type=cover_art; return the id
            CoverArtID_ = [cdict for cdict in manga['relationships'] if cdict["type"] == 'cover_art'][0]['id']

            # get cover art filename
            CoverArtFilename_ = Get_MangaArtFilename(CoverArtID_)

            # generate cover art link
            if (CoverArtFilename_.status_code == 200):
                CoverArtFilename_ = CoverArtFilename_ .json()
                ImageLink_ = "https://uploads.mangadex.org/covers/" + str(MangaID_) + "/" + str(CoverArtFilename_['data']['attributes']['fileName'])
            else:
                ImageLink_ = "ERROR"

            return json.loads(json.dumps({
                "Title": Title,
                "ID": str(MangaID_),
                "Description": str(manga['attributes']['description']['en'].replace("\u003e","").replace("\u003c","")),
                "Image": str(ImageLink_),
                "Link": str(MangaURL_) + str(MangaID_),
                "Rating": str(Rating_), # average rating
                "Follows": str(Follows_)
            }))
    return None


############ END OF FUNCTIONS ###############

# bot = discord.Bot(intents=discord.Intents.all())
bot = discord.Bot(intents=discord.Intents.all())

# start a requests session
_session = requests.Session()

# load json file with Holiday details
try:
    # import holidays from a file
    CraxData = getCraxData(CraxDataFile)

    # formulate holidays
    thanksgiving = find_nth_weekday(datetime.datetime.now().year, 11, 3, 4) # November, thursday, 4th week
    mothersday = find_nth_weekday(datetime.datetime.now().year, 5, 6, 2) # 2nd sunday of may
    fathersday = find_nth_weekday(datetime.datetime.now().year, 6, 6, 3) # 3rd sunday of june

    # update days on holidays var
    CraxData['thanksgiving']['Day'] = thanksgiving['Day']
    CraxData['mothersday']['Day'] = mothersday['Day']
    CraxData['fathersday']['Day'] = fathersday['Day']
    print('\nUpdated the days of thanks giving, mothers day, and fathers day holidays.')
    print('\nIMDB Token: ' + str(CraxData['imdbToken']))
    print('Bot Token:  ' + str(CraxData['Token']))
except Exception as e:
    print(e)

if (CraxData['test']['Enable'] == 'True'):
    print()
    print(f'Holiday: '  + str(CraxData['thanksgiving']['Holiday']))
    print(f'Hour: '     + str(CraxData['thanksgiving']['Hour']))
    print(f'Day: '      + str(CraxData['thanksgiving']['Day']))
    print(f'Month: '    + str(CraxData['thanksgiving']['Month']))
    # print(f'Image: '    + str(holidays['thanksgiving']['Image']))
    # print(f'Msg: \n'    + str(holidays['thanksgiving']['Message']))
    print('===========================================')
    print(f'Holiday: '  + str(CraxData['mothersday']['Holiday']))
    print(f'Hour: '     + str(CraxData['mothersday']['Hour']))
    print(f'Day: '      + str(CraxData['mothersday']['Day']))
    print(f'Month: '    + str(CraxData['mothersday']['Month']))
    print('===========================================')
    print(f'Holiday: '  + str(CraxData['fathersday']['Holiday']))
    print(f'Hour: '     + str(CraxData['fathersday']['Hour']))
    print(f'Day: '      + str(CraxData['fathersday']['Day']))
    print(f'Month: '    + str(CraxData['fathersday']['Month']))
    print('===========================================')

bot_games = ['Apex Legends','Terraria','Kingdom Come Deliverance 2','Monster Hunter Wild','Lost Ark','Civilization 7','Helldivers 2','NBA 2K25']
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
    print("\nChecking if bot is online.")
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

# @bot.slash_command(name='manga', description="Retrieve one 'HOT' manga at Mangakakalot.")
# async def embed(ctx):
#     cManga = getManga2()
#     if cManga != None:
#         embed = discord.Embed(title = "**" + str(cManga['Title']) + "**", url = str(cManga['Link']), description = str(cManga['Description']), color = discord.Color.blue())
#         embed.set_image(url = str(cManga['Image']))
#         embed.add_field(name = " ", value = " 👁️ **Reads:** " + "*{:,}*".format(cManga['Reads']), inline = False)
#         print('Picked manga: ' + str(cManga['Title']))
#         await ctx.respond(embed=embed)
#     else:
#         await ctx.respond("Error retrieving a manga title.")

@bot.slash_command(name='adminmanga', description="Force post new recommended manga in a channel.")
async def embed(ctx):
    print("\nadminmanga has been called.")
    # message_channel = bot.get_channel(chan_craxmanga)
    message_channel = bot.get_channel(chan_tests)
    cManga = getMangaV2(CachedMangaFile,mangaRecommended)

    if cManga != None:
        print()
        print('Title:   ' + cManga['Title'])
        print('Link:    ' + cManga['Link'])
        print('Cover:   ' + cManga['Image'])
        print('Rating:  ' + cManga['Rating'] + " | " + str(type(cManga['Rating'])))
        print('Follows: ' + cManga['Follows'] + " | " + str(type(cManga['Follows'])))
        print()

        embed = discord.Embed(title = "**" + str(cManga['Title']) + "**", url = str(cManga['Link']), description = str(cManga['Description']), color = discord.Color.blue())
        embed.set_image(url = str(cManga['Image']))
        embed.set_author(name="MangaDex", url="https://mangadex.org/")
        embed.add_field(name = " ", value = " ⭐ **Avg. Rating:** " + "*{:,}*".format(float(cManga['Rating'])))
        embed.add_field(name = " ", value = " 🔖 **Bookmarks:** " + "*{:,}*".format(int(cManga['Follows'])))
        # embed.set_footer(text="This is made possible by mangadex.org",icon_url="https://styles.redditmedia.com/t5_fljgj/styles/communityIcon_dodprbccfsy71.png")
        print("Posted new manga recommendation: " + str(cManga['Title']))
        await message_channel.send(embed=embed)
        await ctx.respond("Successfully added a manga recommendation to " + str(message_channel) + " channel.")
    else:
        await ctx.respond("Error retrieving a manga title.")

@bot.slash_command(name='adminmovie', description="Force post new recommended movie in a channel.")
async def embed(ctx):
    print("\nadminmovie has been called.")
    message_channel = bot.get_channel(chan_tests)
    cMovie = None
    cMovie = Get_Movie(CachedMovieFile,CraxData['imdbToken'])

    if cMovie != None:
        print()
        print('Title:          ' + str(cMovie['primaryTitle']))
        print('Link:           ' + str(cMovie['url']))
        print('Release Date:   ' + str(cMovie['releaseDate']))
        print('Cover:          ' + str(cMovie['primaryImage']))
        print('Genre:          ' + str(cMovie['genres']))
        print('Rating:         ' + str(cMovie['averageRating']) + " | " + str(type(cMovie['averageRating'])))
        print('Total Runtime:  ' + str(cMovie['runtimeMinutes'] )+ " | " + str(type(cMovie['runtimeMinutes'])))
        print()

        embed = discord.Embed(title = "**" + str(cMovie['primaryTitle']) + "**", url = str(cMovie['url']), description = str(cMovie['description']), color = discord.Color.teal())
        embed.set_image(url = str(cMovie['primaryImage']))
        embed.set_author(name="IMDB", url="https://www.imdb.com/")
        if (cMovie['averageRating'] == None):
            embed.add_field(name = " ", value = " 👍 **Avg. Rating:** " + "* N/A *")
        else:
            embed.add_field(name = " ", value = " 👍 **Avg. Rating:** " + "*{:,}*".format(float(cMovie['averageRating'])))
        embed.add_field(name = " ", value = " 🎬 **Total Runtime:** " + "*{:,}*".format(int(cMovie['runtimeMinutes'])) + " minutes")
        embed.add_field(name=u"\u200b", value=u"\u200b")
        embed.add_field(name = " ", value = " ⌛ **Release Date:** " + str(cMovie['releaseDate']))
        embed.add_field(name = " ", value = " 🎭 **Genres:** " + str(cMovie['genres']))
        # embed.set_footer(text="This is made possible by mangadex.org",icon_url="https://styles.redditmedia.com/t5_fljgj/styles/communityIcon_dodprbccfsy71.png")
        print("Posted new movie recommendation: " + str(cMovie['primaryTitle']))
        await message_channel.send(embed=embed)
        await ctx.respond("Successfully added a movie recommendation to " + str(message_channel) + " channel.")
    else:
        await ctx.respond("Error retrieving a movie title.")
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
@tasks.loop(minutes=1)
async def called_every_hour():
    current_time = datetime.datetime.now()
    current_day = datetime.datetime.today()
    if ((current_time.day % 7) == 0 and current_time.hour == 4 and current_time.minute == 0): # attemp to clear channels; current_time.hour to 4 since servers are set to restart at 5
        crax_serv = bot.get_channel(chan_craxservers)
        crax_evnt = bot.get_channel(chan_craxevents)
        await crax_serv.purge(limit=500)
        await crax_evnt.purge(limit=500)
    elif current_day.weekday() == 5 and current_time.hour == 8 and current_time.minute == 0: # Post Hot manga; current_day().weekday() = 0 is monday, sunday is 6.
        print("\nIt is Saturday!")
        message_channel = bot.get_channel(chan_craxmanga)
        cManga = getMangaV2(CachedMangaFile,mangaRecommended)

        if cManga != None:
            print()
            print('Title:   ' + cManga['Title'])
            print('Link:    ' + cManga['Link'])
            print('Cover:   ' + cManga['Image'])
            print('Rating:  ' + cManga['Rating'] + " | " + str(type(cManga['Rating'])))
            print('Follows: ' + cManga['Follows'] + " | " + str(type(cManga['Follows'])))
            print()

            embed = discord.Embed(title = "**" + str(cManga['Title']) + "**", url = str(cManga['Link']), description = str(cManga['Description']), color = discord.Color.blue())
            embed.set_image(url = str(cManga['Image']))
            # embed.add_field(name = " ", value = " 👁️ **Reads:** " + "*{:,}*".format(cManga['Reads']), inline = False)
            embed.add_field(name = " ", value = " ⭐ **Avg. Rating:** " + "*{:,}*".format(cManga['Rating']), inline = False)
            embed.set_footer(text="This is made possible by mangadex.org",icon_url="https://styles.redditmedia.com/t5_fljgj/styles/communityIcon_dodprbccfsy71.png")
            print("Posted new manga recommendation: " + str(cManga['Title']))
        await message_channel.send(embed=embed)
    elif current_day.weekday() == 4 and current_time.hour == 19 and current_time.minute == 8: # Post trnding movie; current_day().weekday() = 0 is monday, sunday is 6.
        print("\nMovie night!")
        message_channel = bot.get_channel(chan_craxmovie)
        cMovie = None
        cMovie = Get_Movie(CachedMovieFile,CraxData['imdbToken'])

        if cMovie != None:
            print()
            print('Title:          ' + str(cMovie['primaryTitle']))
            print('Link:           ' + str(cMovie['url']))
            print('Release Date:   ' + str(cMovie['releaseDate']))
            print('Cover:          ' + str(cMovie['primaryImage']))
            print('Genre:          ' + str(cMovie['genres']))
            print('Rating:         ' + str(cMovie['averageRating']) + " | " + str(type(cMovie['averageRating'])))
            print('Total Runtime:  ' + str(cMovie['runtimeMinutes'] )+ " | " + str(type(cMovie['runtimeMinutes'])))
            print()

            embed = discord.Embed(title = "**" + str(cMovie['primaryTitle']) + "**", url = str(cMovie['url']), description = str(cMovie['description']), color = discord.Color.teal())
            embed.set_image(url = str(cMovie['primaryImage']))
            embed.set_author(name="IMDB", url="https://www.imdb.com/")
            if (cMovie['averageRating'] == None):
                embed.add_field(name = " ", value = " 👍 **Avg. Rating:** " + "* N/A *")
            else:
                embed.add_field(name = " ", value = " 👍 **Avg. Rating:** " + "*{:,}*".format(float(cMovie['averageRating'])))
            embed.add_field(name = " ", value = " 🎬 **Total Runtime:** " + "*{:,}*".format(int(cMovie['runtimeMinutes'])) + " minutes")
            embed.add_field(name=u"\u200b", value=u"\u200b")
            embed.add_field(name = " ", value = " ⌛ **Release Date:** " + str(cMovie['releaseDate']))
            embed.add_field(name = " ", value = " 🎭 **Genres:** " + str(cMovie['genres']))
            print("Posted new movie recommendation: " + str(cMovie['primaryTitle']))
        await message_channel.send(embed=embed)
    elif current_time.day == CraxData['thanksgiving']['Day'] and current_time.month == CraxData['thanksgiving']['Month'] and current_time.hour == CraxData['thanksgiving']['Hour'] and current_time.minute == 0: #ThanksGiving
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url=CraxData['thanksgiving']['Image'])
        await message_channel.send(CraxData['thanksgiving']['Message'], embed=embed)
    elif current_time.day == CraxData['christmas']['Day'] and current_time.month == CraxData['christmas']['Month'] and current_time.hour == CraxData['christmas']['Hour'] and current_time.minute == 0: #Christmas
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url=CraxData['christmas']['Image'])
        await message_channel.send(CraxData['christmas']['Message'], embed=embed)
    elif current_time.day == CraxData['newyear']['Day'] and current_time.month == CraxData['newyear']['Month'] and current_time.hour == CraxData['newyear']['Hour'] and current_time.minute == 0: #NewYear
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url=CraxData['newyear']['Image'])
        await message_channel.send(CraxData['newyear']['Message'], embed=embed)
    elif current_time.day == CraxData['mothersday']['Day'] and current_time.month == CraxData['mothersday']['Month'] and current_time.hour == CraxData['mothersday']['Hour'] and current_time.minute == 0: #MothersDay
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url=CraxData['mothersday']['Image'])
        await message_channel.send(CraxData['mothersday']['Message'], embed=embed)
    elif current_time.day == CraxData['fathersday']['Day'] and current_time.month == CraxData['fathersday']['Month'] and current_time.hour == CraxData['fathersday']['Hour'] and current_time.minute == 0: #FathersDay
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url=CraxData['fathersday']['Image'])
        await message_channel.send(CraxData['fathersday']['Message'], embed=embed)
    elif current_time.hour == CraxData['test']['Hour'] and current_time.minute == 0 and CraxData['test']['Enable'] == 'True': #FathersDay
        message_channel = bot.get_channel(chan_tests)
        embed = discord.Embed(title='', description='')
        embed.set_image(url=CraxData['fathersday']['Image'])
        await message_channel.send(CraxData['fathersday']['Message'], embed=embed)

@called_every_hour.before_loop
async def before():
    await bot.wait_until_ready()
    # print("Finished waiting")

called_every_hour.start()
#end

bot.run(CraxData['Token'])