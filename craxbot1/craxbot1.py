import discord
import pathlib
import random
import datetime
import json
import os
import subprocess
import calendar
import sys
import asyncio
from discord.ext import tasks

# install and/or import requests
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'requests'])
finally:
    import requests


########### START FUNCTIONS ###############

class Set_Return():
    def __init__(self, status_code = 0, result = None, reason = None):
        self.status_code = status_code
        self.result      = result
        self.reason      = reason

    def __str__(self):
        return "{\"status_code\":\"" + str(self.status_code) + "\", \"result\":\"" + str(self.result) + "\", \"reason\":\"" + str(self.reason) + "\"}"

def Check_Directory(_Path):
    if not os.path.exists(_Path):
        print('\tNot found: ' + _Path)
        try:
            os.makedirs(_Path)
        except BaseException as e:
            print('\t\tError creating folder: ' + _Path)
            return False
        except Exception as e:
            print('\t\tError creating folder: ' + _Path)
            return False
        print('\t\tFolder created.')
    else:
        print('\tFound: ' + _Path)
    return True
    
def Import_Json(file: pathlib.Path):
    result = None
    status_codes = {
        FileNotFoundError: 999,
        PermissionError: 999,
        ValueError: 999,
        IOError: 999
    }
    status_messages = {
        FileNotFoundError: 'Error opening file. File not found: ',
        PermissionError: 'You do not have permission to open the file! ',
        ValueError: 'Invalid data format!',
        IOError: 'An error occurred while writing to the file!'
    }

    if os.path.exists(file):
        try:
            with open(file, "r", encoding = "utf-8-sig") as sfile:
                result = json.load(sfile)
            print("\tLoaded successfully: " + str(file))
            return Set_Return(0,result,'ok')
        except tuple(status_codes.keys()) as e:
            error_code = status_codes[type(e)]
            error_message = status_messages[type(e)] + str(file)
            print(f"\t{error_message} - {e}")
            return Set_Return(error_code, None, error_message)

def Export_Dict(_Dict,_File):
    _result = None

    try:
        with open(_File, "w") as file_:
            json.dump(_Dict, file_)
        _result = Set_Return(0,'ok')
    except Exception as e:
        _result = Set_Return(999,"Error",'Error updating file: ' + str(_File) +  "\nError Message: " + str(e))
    except FileNotFoundError as e:
        _result = Set_Return(999,"Error",'Error updating file. File not found: ' + str(_File))
    except PermissionError as e:
        _result = Set_Return(999,"Error",'You do not have permission to open the file! ' + str(_File))
    except ValueError as e:
        _result = Set_Return(999,"Error",'Invalid data format!' + str(_File))
    except IOError as e:
        _result = Set_Return(999,"Error",'An error occurred while writing to the file!' + str(_File))
    finally:
        file_.close()
    print('\tSuccessfully export a dict to file: ' + str(_File))
    return _result
    
def Get_FileContentToList(_File):
    _result = []
    
    if os.path.exists(_File):
        try:
            with open(_File, 'r') as file:
                _result = [line.strip() for line in file]
            _result = Set_Return(0,_result,'ok')
        except FileNotFoundError as e:
            _result = Set_Return(999,"Error",'Error opening file. File not found: ' + str(_File))
            print(_result.reason)
        except PermissionError as e:
            _result = Set_Return(999,"Error",'You do not have permission to open the file! ' + str(_File))
            print(_result.reason)
        except ValueError as e:
            _result = Set_Return(999,"Error",'Invalid data format!' + str(_File))
            print(_result.reason)
        except IOError as e:
            _result = Set_Return(999,"Error",'An error occurred while writing to the file!' + str(_File))
            print(_result.reason)
    return _result

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

def WriteTo_File(_File,_Value):
    _result = None
    mode_ = "w"
    MangaTitle_ = _Value
    if os.path.exists(_File):
        mode_ = "a"
        MangaTitle_ = "\n" + str(_Value)
    try:
        with open(_File, mode_) as file_:
            file_.write(MangaTitle_)
        _result = Set_Return(0,"ok")
    except Exception as e:
        _result = Set_Return(999,"Error",'[' + str(_Value) + ']' + 'Error updating file: ' + str(_File) +  "\nError Message: " + str(e))
        print(_result.reason)
    except FileNotFoundError as e:
        _result = Set_Return(999,"Error",'[' + str(_Value) + ']' + 'Error updating file. File not found: ' + str(_File))
        print(_result.reason)
    except PermissionError as e:
        _result = Set_Return(999,"Error",'[' + str(_Value) + ']' + 'You do not have permission to open the file! ' + str(_File))
        print(_result.reason)
    except ValueError as e:
        _result = Set_Return(999,"Error",'[' + str(_Value) + ']' + 'Invalid data format!' + str(_File))
        print(_result.reason)
    except IOError as e:
        _result = Set_Return(999,"Error",'[' + str(_Value) + ']' + 'An error occurred while writing to the file!' + str(_File))
        print(_result.reason)
    finally:
        file_.close()
    print('\tSuccessfully wrote to file: ' + str(_File) + "\n\t\tValue: " + str(_Value))
    return _result

def Send_Get(_baseURL,_endpoint,_headers):
    _URI = str(_baseURL) + str(_endpoint)

    try:
        _response = _session.get(url = _URI, headers = _headers)
    except requests.exceptions.HTTPError as e:
        _response = Set_Return(999,"Error","[HTTPError] API failed. URI = " + str(_URI) + ". Reason: " + e.args[0])
        print(_response.reason)
    except requests.exceptions.ReadTimeout as e:
        _response = Set_Return(999,"Error","[Timed Out] API failed. URI = " + str(_URI) + "")
        print(_response.reason)
    except requests.exceptions.MissingSchema as e:
        _response = Set_Return(999,"Error","[MissingSchema] API failed. URI = " + str(_URI) + "")
        print(_response.reason)
    except requests.exceptions.ConnectionError as e:
        _response = Set_Return(999,"Error","[ConnectionError] API failed. URI = " + str(_URI))
        print(_response.reason)
    except requests.exceptions.RequestException as e:
        _response = Set_Return(999,"Error","[RequestException] API failed. URI = " + str(_URI) + "")
        print(_response.reason)
    return _response

def Get_Manga(_CachedFile,_WriteToFile = False):
    Limit_ = 24
    SelectedManga_ = None

    while SelectedManga_ == None:
        # Get mangas
        Result_ = Get_MangaList(Limit_)

        # import cached manga titles
        CachedTitles_ = Get_FileContentToList(_CachedFile)

        if (CachedTitles_.status_code == 0):
            CachedTitles_ = CachedTitles_.result

        if (Result_.status_code == 200):
            Result_ = Result_.json()
            SelectedManga_ = Select_Manga(Result_['data'],CachedTitles_)

            if (SelectedManga_ != None):
                if (_WriteToFile):
                    WriteTo_File(_CachedFile,SelectedManga_['Title'])
                return SelectedManga_
        else:
            print()
            print("Status Code: " + str(Result_.status_code))
            print("Message: " + str(Result_.reason))
            return None
        # increase number of manga to query; reset variable
        Limit_ = Limit_ + 8
        SelectedManga_ = None
    
def Get_MangaList(_Limit):
    _baseURL= "https://api.mangadex.org"
    _endpoint = "/manga?limit=" + str(_Limit) + "&order%5BfollowedCount%5D=desc"
    _result = Send_Get(_baseURL,_endpoint,None)
    return _result

def Get_MangaRating(_MangaID):
    _baseURL= "https://api.mangadex.org"
    _endpoint = "/statistics/manga/" + str(_MangaID)
    _result = Send_Get(_baseURL,_endpoint,None)
    return _result

def Get_MangaArtFilename(_CoverArtID):
    _baseURL= "https://api.mangadex.org"
    _endpoint = "/cover/" + str(_CoverArtID) + "?includes%5B%5D=manga"
    _result = Send_Get(_baseURL,_endpoint,None)
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

def Get_Movie(_CachedFile,_Token,_WriteToFile = False):
    _baseURL= "https://imdb236.p.rapidapi.com/imdb"
    _endpoint = "/most-popular-movies"  # Most Popular movie
    # _endpoint = "//imdb/top250-movies"  # Top 250 movies
    _headers = {
        'x-rapidapi-key': _Token,
        'x-rapidapi-host': "imdb236.p.rapidapi.com"
    }
    SelectedMovie_ = None

    _result = Send_Get(_baseURL,_endpoint,_headers)

    if _result.status_code == 200:
        _result = _result.json()
        movie_count_ = len(_result)
        CachedTitles_ = Get_FileContentToList(_CachedFile)

        if (CachedTitles_.status_code == 0):
            CachedTitles_ = CachedTitles_.result

        num_ = 0 # number of attempts; if this exceeds 50, force break
        limit_ = 50
        while True:
            rand_ = random.randrange(movie_count_ - 1)
            if _result[rand_]['primaryTitle'] not in CachedTitles_:
            # if _result[rand_]['primaryTitle'] == 'The Odyssey':
                SelectedMovie_ = _result[rand_]
                break

            # break loop if num is greater than limit_
            if num_ > limit_:
                return None
            num_ = num_ + 1
    else:
        print(_result.reason)
        return None
    
    # convert genre from array to string
    SelectedMovie_['genres'] = ','.join(map(str,SelectedMovie_['genres']))
    
    if (_WriteToFile):
        WriteTo_File(_CachedFile,SelectedMovie_['primaryTitle'])
    return SelectedMovie_

def Create_MangaEmbed(_objJSON):
    print()
    print('Title:   ' + _objJSON['Title'])
    print('Link:    ' + _objJSON['Link'])
    print('Cover:   ' + _objJSON['Image'])
    print('Rating:  ' + _objJSON['Rating'] + " | " + str(type(_objJSON['Rating'])))
    print('Follows: ' + _objJSON['Follows'] + " | " + str(type(_objJSON['Follows'])))
    print()

    embed = discord.Embed(title = "**" + str(_objJSON['Title']) + "**", url = str(_objJSON['Link']), description = str(_objJSON['Description']), color = discord.Color.blue())
    embed.set_author(name="MangaDex", url="https://mangadex.org/")

    if (_objJSON['Image']) != None:
        embed.set_image(url = str(_objJSON['Image']))

    if (_objJSON['Rating']) == None:
        embed.add_field(name = " ", value = " ⭐ **Avg. Rating:** " + "* N/A *")
    else:
        embed.add_field(name = " ", value = " ⭐ **Avg. Rating:** " + "*{:,}*".format(float(_objJSON['Rating'])))

    if (_objJSON['Follows']) == None:
        embed.add_field(name = " ", value = " 🔖 **Bookmarks:** " + "* N/A *")
    else:
        embed.add_field(name = " ", value = " 🔖 **Bookmarks:** " + "*{:,}*".format(int(_objJSON['Follows'])))
    return embed

def Create_MovieEmbed(_objJSON):
    print()
    print('Title:          ' + str(_objJSON['primaryTitle']))
    print('Link:           ' + str(_objJSON['url']))
    print('Release Date:   ' + str(_objJSON['releaseDate']))
    print('Cover:          ' + str(_objJSON['primaryImage']))
    print('Genre:          ' + str(_objJSON['genres']))
    print('Rating:         ' + str(_objJSON['averageRating']) + " | " + str(type(_objJSON['averageRating'])))
    print('Total Runtime:  ' + str(_objJSON['runtimeMinutes'] )+ " | " + str(type(_objJSON['runtimeMinutes'])))
    print()

    embed = discord.Embed(title = "**" + str(_objJSON['primaryTitle']) + "**", url = str(_objJSON['url']), description = str(_objJSON['description']), color = discord.Color.teal())
    embed.set_author(name="IMDB", url="https://www.imdb.com/")

    if (_objJSON['primaryImage'] != None):
        embed.set_image(url = str(_objJSON['primaryImage']))

    if (_objJSON['averageRating'] == None):
        embed.add_field(name = " ", value = " 👍 **Avg. Rating:** " + "* N/A *")
    else:
        embed.add_field(name = " ", value = " 👍 **Avg. Rating:** " + "*{:,}*".format(float(_objJSON['averageRating'])))

    if (_objJSON['runtimeMinutes'] == None):
        embed.add_field(name = " ", value = " 🎬 **Total Runtime:** " + "* N/A *")
    else:
        embed.add_field(name = " ", value = " 🎬 **Total Runtime:** " + "*{:,}*".format(int(_objJSON['runtimeMinutes'])) + " minutes")

    embed.add_field(name=u"\u200b", value=u"\u200b")

    if (_objJSON['releaseDate'] == None):
        embed.add_field(name = " ", value = " ⌛ **Release Date:** " + "* N/A *")
    else:
        embed.add_field(name = " ", value = " ⌛ **Release Date:** " + str(_objJSON['releaseDate']))

    if (_objJSON['genres'] == None):
        embed.add_field(name = " ", value = " 🎭 **Genres:** " + "* N/A *")
    else:
        embed.add_field(name = " ", value = " 🎭 **Genres:** " + str(_objJSON['genres']))
    return embed

def Get_Screenshot(_Path,_Count):
    DirFiles_       = []
    SelectedFiles_  = []
    FileName_       = None

    # get all filenames inside folder _Path
    for x in os.listdir(_Path):
        if x.lower().endswith(('jpeg','jpg','png','bmp','webm')):   # only allow specific file types
            DirFiles_.append(x)
    DirFilesLength_ = len(DirFiles_)

    if DirFilesLength_ > 0 and DirFilesLength_ > _Count:
        LoopCount_ = 1              # tracks to current number of loops
        LoopLimit_ = _Count + 20    # limits the loop to total count plus 20 loops, so it does not get stuck in a loop
        while len(SelectedFiles_) < _Count:
            try:
                FileName_ = random.choice(DirFiles_)  # get random file from DirFiles_ list
                if FileName_ not in SelectedFiles_:
                    SelectedFiles_.append(FileName_)
            except Exception as e:
                print('Encountered an error: ' + e)
            except BaseException as e:
                print('Encountered an error: ' + e)
            
            if LoopCount_ == LoopLimit_:    # check if looplimit has been reacher. Break look if it reached limit
                print('Loop limit reached: ' + str(LoopLimit_))
                return None
            LoopCount_ = LoopCount_ + 1     # increment the loop count by 1
            FileName_ = None                # clear variable for next loop
    elif DirFilesLength_ == 0:              # if folder does not have files, return None
        return None
    else:
        SelectedFiles_ = DirFiles_          # just get all files inside directory  
    return SelectedFiles_

def Load_CraxData(_FilePath,_Report = False):
    # set variables
    CraxData_           = None
    thanksgiving        = None
    mothersday          = None
    fathersday          = None

    # import holidays from a file
    CraxData_ = Import_Json(_FilePath)

    if (CraxData_.status_code == 0):
        CraxData_ = CraxData_.result
        # output tokens
        print()
        print('\tIMDB Token: ' + str(CraxData_['imdbToken']))
        print('\tBot Token:  ' + str(CraxData_['Token']))
        print('\tOwner ID:   ' + str(CraxData_['Owner']['ID']))

        # formulate holidays
        thanksgiving    = find_nth_weekday(datetime.datetime.now().year, 11, 3, 4) # November, thursday, 4th week
        mothersday      = find_nth_weekday(datetime.datetime.now().year, 5, 6, 2) # 2nd sunday of may
        fathersday      = find_nth_weekday(datetime.datetime.now().year, 6, 6, 3) # 3rd sunday of june

        print()
        # update days on holidays var
        CraxData_['thanksgiving']['Day'] = thanksgiving['Day']
        CraxData_['mothersday']['Day']   = mothersday['Day']
        CraxData_['fathersday']['Day']   = fathersday['Day']
        print('\tUpdated the days of thanks giving, mothers day, and fathers day holidays.')

        # generate random times for screenshots to be posted
        if (CraxData_['Screenshots']['RandomHours']):
            CraxData_['Screenshots']['Hours'][str(datetime.datetime.today().weekday())] = random.sample(range(1,24),CraxData_['Screenshots']['NumberOfHours'])
            print('\t\tRandom hours?    ' + str(CraxData_['Screenshots']['RandomHours']))
            print('\t\tNumber of Hours: ' + str(CraxData_['Screenshots']['NumberOfHours']))
    else:
        return Set_Return(999,'Error',CraxData_.reason)
    return Set_Return(0,CraxData_,'ok')

def Add_StringFiller(_String,_MaxLength):
    Outstring_  = None
    StringLen_  = len(_String)

    if StringLen_ < _MaxLength:
        Outstring_ = _String + (' ' * (_MaxLength - StringLen_))
    return Outstring_

def Create_HolidayReport(_Data):
    Date_       = None
    Year_       = datetime.datetime.now().year
    PostMsg_    = None

    for key in _Data:
        if 'Holiday' in _Data[key]:
            try:
                Date_               = datetime.date(Year_, _Data[key]['Month'], _Data[key]['Day'])

                # create post strings
                if (PostMsg_ != None):
                    PostMsg_ = PostMsg_ + '\n' + Add_StringFiller(Date_.strftime("%B %d, %Y"),20) + ' | ' + _Data[key]['Holiday']
                else:
                    PostMsg_ = Add_StringFiller(Date_.strftime("%B %d, %Y"),20) + ' | ' + _Data[key]['Holiday']
            except Exception as e:
                print(f'\tError creating embed: {e}')
            except BaseException as e:
                print(f'\tError creating embed: {e}')
    return PostMsg_

def restart_bot(): 
  os.execv(sys.executable, ['python'] + sys.argv)

############ END OF FUNCTIONS ###############

# files and folders full path
CurrentDir          = pathlib.Path(__file__).parent.absolute()      # path to discord bot script
TempPath            = os.path.join(CurrentDir,"Temp")               # path to Temp folder
ScreenshotsPath     = os.path.join(CurrentDir,"Screenshots")        # path to Screenshots folder
SArchivedPath       = os.path.join(ScreenshotsPath,"Archived")      # path to Screenshots folder
CachedMangaFile     = os.path.join(TempPath,".mangaList")           # file
CachedMovieFile     = os.path.join(TempPath,".movieList")           # file
CraxDataFile        = os.path.join(TempPath,"craxbot_data.json")    # file
CraxDataFileMod     = os.path.join(TempPath,"craxbot_dataNEW.json") # file

# OnCrax Channel IDs
chan_announ             = 1040696808797650974   #announcements channel
chan_gen                = 845072862397333506    #general in text channel
chan_tests              = 1356541658753269951   #tests in text channel
chan_craxstats          = 1138670086861897738   #crax_stats channel
chan_craxevents         = 1140037396151418951   #crax_events channel
chan_craxservers        = 1124176437344211115   #crax_servers channel
chan_craxmanga          = 1040813089735577652   #crax_animemangarecommendation channel
chan_craxmovie          = 1349947144249020417   # movie-recommendations
chan_clipshighlights    = 845072862397333507    # clips-and-highligths

# check if all directories exists; create if not
print()
print('Checking all folders: ' + str(datetime.datetime.now()))
Check_Directory(TempPath)
Check_Directory(ScreenshotsPath)
Check_Directory(SArchivedPath)

# bot = discord.Bot(intents=discord.Intents.all())
bot = discord.Bot(intents=discord.Intents.all())

# start a requests session
_session = requests.Session()

# load crax data file and update holidays dates
print()
print('Loading Crax data file:')
CraxData = Load_CraxData(CraxDataFile)

if (CraxData.status_code == 0):
    CraxData = CraxData.result

    # Update craxdata
    # Export_Dict(CraxData,CraxDataFileMod)

    print()
    HolidayReport  = None
    HolidayReport  = Create_HolidayReport(CraxData)

    print()
    print('\t========================    Thanksgiving      ========================')
    print(f'\tHoliday: '  + str(CraxData['thanksgiving']['Holiday']))
    print(f'\tHour: '     + str(CraxData['thanksgiving']['Hour']))
    print(f'\tDay: '      + str(CraxData['thanksgiving']['Day']))
    print(f'\tMonth: '    + str(CraxData['thanksgiving']['Month']))
    # print(f'Image: '    + str(holidays['thanksgiving']['Image']))
    # print(f'Msg: \n'    + str(holidays['thanksgiving']['Message']))
    print('\t========================    Mothers Day       ========================')
    print(f'\tHoliday: '  + str(CraxData['mothersday']['Holiday']))
    print(f'\tHour: '     + str(CraxData['mothersday']['Hour']))
    print(f'\tDay: '      + str(CraxData['mothersday']['Day']))
    print(f'\tMonth: '    + str(CraxData['mothersday']['Month']))
    print('\t========================     Fathers Day      ========================')
    print(f'\tHoliday: '  + str(CraxData['fathersday']['Holiday']))
    print(f'\tHour: '     + str(CraxData['fathersday']['Hour']))
    print(f'\tDay: '      + str(CraxData['fathersday']['Day']))
    print(f'\tMonth: '    + str(CraxData['fathersday']['Month']))
    print('\t======================== Screenshots Schedule ========================')
    print('\tDays - Hours are in 24h format')
    print('\t\t[0] Mondays  : ' + ', '.join(map(str,CraxData['Screenshots']['Hours']['0'])))
    print('\t\t[1] Tuesday  : ' + ', '.join(map(str,CraxData['Screenshots']['Hours']['1'])))
    print('\t\t[2] Wednesday: ' + ', '.join(map(str,CraxData['Screenshots']['Hours']['2'])))
    print('\t\t[3] Thursday : ' + ', '.join(map(str,CraxData['Screenshots']['Hours']['3'])))
    print('\t\t[4] Friday   : ' + ', '.join(map(str,CraxData['Screenshots']['Hours']['4'])))
    print('\t\t[5] Saturday : ' + ', '.join(map(str,CraxData['Screenshots']['Hours']['5'])))
    print('\t\t[6] Sunday   : ' + ', '.join(map(str,CraxData['Screenshots']['Hours']['6'])))
    
    print()
    print('\t\tCurrent day      : ' + str(datetime.datetime.today().weekday()) + ' | Data type: ' + str(type(datetime.datetime.today().weekday())))
    print('\t\tScheduled Hours  : ' + ', '.join(map(str,CraxData['Screenshots']['Hours'][str(datetime.datetime.today().weekday())])) + ' | Element Data type:' + str(type(CraxData['Screenshots']['Hours'][str(datetime.datetime.today().weekday())][0])))
    print('\t\tScheduled Mins   : ' + ', '.join(map(str,CraxData['Screenshots']['Minutes'])) + ' | Element Data type:' + str(type(CraxData['Screenshots']['Minutes'][0])))
    print('\t======================================================================')
else:
    print('\tError: ' + CraxData.reason)
    asyncio.sleep(30)
    sys.exit(500)


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
    # print(f'Current CurrentDir: {CurrentDir}')
    # crax_stats = bot.get_channel(chan_craxstats)
    # await crax_stats.purge(limit=100)
    # Delete Saved message ID file; for craxStats Channel
    # oldStats_path = f"{CurrentDir}\\temps\\.oldstats"
    # print(oldStats_path)
    # os.remove(oldStats_path)

@bot.slash_command(name='restartbot')
async def restart(ctx):
    print()
    print(f'```{ctx.author} [{ctx.author.id}] requested to restart the bot at {datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")}```')

    try:
        owner = await bot.fetch_user(CraxData['Owner']['ID'])
        embed = discord.Embed(title = "**CraxBot0t Restart Request**", description = "", color = discord.Color.red())
        embed.add_field(name = "**Requester**", value = str(ctx.author), inline = False)
        embed.add_field(name = "**Server Name**", value = "OnCrax", inline = False)
        embed.add_field(name = "**Channel Name**", value = str(ctx.channel), inline = False)
        embed.add_field(name = "**Timestamp** ", value = datetime.datetime.now().strftime("%B %d, %Y %I:%M %p"), inline = False)
    except BaseException as e:
        print(e)
    except Exception as e:
        print(e)
        
    await owner.send(embed=embed)
    
    if ctx.author.id == CraxData['Owner']['ID']: # owener's discord id
        await ctx.respond("```Restarting bot...```")
        restart_bot()
    else:
        await ctx.respond(f'```Unauthorized access attempt by user {ctx.author}. This has been logged.```')

@bot.slash_command(name='crax', description="Just for testing slash command.", guild_ids=[845072861915512897])
async def crax(ctx):
    print(f'\n{ctx.author} checked if bot is online at {datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")}.')
    await ctx.respond(f'I am alive, {ctx.author.mention}')

@bot.slash_command(name='changebotgame', description="Changes what game Craxbot is playing.", guild_ids=[845072861915512897])
async def botgame(ctx, game: str):
    # game = random.choice(bot_games)
    await bot.change_presence(activity=discord.Game(name=game))
    await ctx.respond(f'```Bot game changed to {game}.```')

@bot.slash_command(name='reloaddata', description="Force reload crax data such as holiday dates.")
async def botgame(ctx):
    print()
    print("============== Reload Crax Data ==============")
    print('Timestamp: ' + str(datetime.datetime.now()))
    message_channel = bot.get_channel(chan_tests)
    CraxDataTemp = None
    CraxDataTemp = Load_CraxData(CraxDataFile)
    if CraxDataTemp.status_code == 0:
        CraxData = CraxDataTemp.result
        Export_Dict(CraxData,CraxDataFile)
        print('\tSuccessfully reloaded crax data: ' + CraxDataFile)
        await message_channel.send('```Reloaded crax data```')
        await ctx.respond('```Reloaded crax data```', delete_after=0)
    else:
        await message_channel.send('```Failed to reload crax data.```')
        await ctx.respond('```Failed to reload crax data.```', delete_after=0)
    print("\n============ END Reload Crax Data ============")
    
@bot.slash_command(name='servers', description="Will attempt to get a list of servers owned by Crax.")
async def embed(ctx):
    print()
    print("============== servers ==============")
    print('Timestamp: ' + str(datetime.datetime.now()))
    channeltosend = bot.get_channel(ctx.channel.id)
    print('Target Channel: ' + str(channeltosend))

    # re-import holidays from a file
    # CraxData = Import_Json(CraxDataFile)

    try:
        CraxData['Servers']
        if CraxData['Servers']['noServers']:
            await ctx.respond("```There are no servers being hosted by Crax at this moment. Please check again later.```")
        else:
            embedList = []
            # embed = discord.Embed(title = "**List of Servers**", description = "Here are the list of servers managed by Crax.", color = discord.Color.green())
            for game in CraxData['Servers']:
                if (type(CraxData['Servers'][game]) == dict):
                    for server in CraxData['Servers'][game]:
                        if (type(CraxData['Servers'][game][server]) == dict):
                            embed = discord.Embed(title = "", description = "", color = discord.Color.green())
                            embed.add_field(name = "**Game:** " + str(CraxData['Servers'][game][server]['game']), value = "", inline = False)
                            embed.add_field(name = "**Server Name:** " + str(CraxData['Servers'][game][server]['servername']), value = "", inline = False)
                            embed.add_field(name = "**IP & Port:** " + str(CraxData['Servers'][game][server]['ip']) + ":" + str(CraxData['Servers'][game][server]['port']), value = "", inline = False)
                            if (CraxData['Servers'][game][server]['password'] != ''):
                                embed.add_field(name = "**Password:** " + str(CraxData['Servers'][game][server]['password']), value = "", inline = False)
                            if (CraxData['Servers'][game][server]['note'] != ''):
                                embed.add_field(name = "**Notes:** ", value = str(CraxData['Servers'][game][server]['note']), inline = False)
                            embedList.append(embed)
            print('EmbedList: ' + str(embedList))
            await ctx.respond("Crax servers found.", delete_after=0)
            await channeltosend.send(embeds=embedList)
        print("============ END servers ============")
    except Exception as e:
        await ctx.respond("```Something went wrong. Please contact your discord admin.```")
        print('\tError: ' + str(e))
        print("========================== END servers ==========================")

@bot.slash_command(name='adminmanga', description="Force post new recommended manga in a channel.")
async def embed(ctx):
    print()
    print("============================ adminmanga ============================")
    # message_channel = bot.get_channel(chan_craxmanga)
    message_channel = bot.get_channel(chan_tests)
    cManga = Get_Manga(CachedMangaFile)

    if cManga != None:
        embed_ = None
        embed_ = Create_MangaEmbed(cManga)
        print("Posted new manga recommendation: " + str(cManga['Title']))
        try:
            await ctx.respond("Successfully added a manga recommendation to " + str(message_channel) + " channel.", delete_after=0)
            await message_channel.send(embed=embed_)
        except Exception as e:
            print('Error: ' + str(e))
    else:
        await ctx.respond("```Error retrieving a manga title.```")
    print('========================== END adminmanga ==========================')

@bot.slash_command(name='adminmovie', description="Force post new recommended movie in a channel.")
async def embed(ctx):
    print()
    print("============================ adminmovie ============================")
    message_channel = bot.get_channel(chan_tests)
    cMovie = None
    cMovie = Get_Movie(CachedMovieFile,CraxData['imdbToken'])

    if cMovie != None:
        embed_ = None
        embed_ = Create_MovieEmbed(cMovie)
        print("Posted new movie recommendation: " + str(cMovie['primaryTitle']))
        try:
            await ctx.respond("Successfully added a movie recommendation to " + str(message_channel) + " channel.", delete_after=0)
            await message_channel.send(embed=embed_)
        except Exception as e:
            print('Error: ' + str(e))
    else:
        print('Get_Movie function returned None.')
        await ctx.respond("```Error retrieving a movie title.```")
    print('========================== END adminmovie ==========================')

@bot.slash_command(name='screenshot', description="Find a screenshot to share from server folder.")
async def embed(ctx):
    print()
    print("============================ screenshot ============================")
    print('Caller         : ' + str(ctx.author))
    message_channel = bot.get_channel(chan_tests)
    Screenshots = []
    Screenshots = Get_Screenshot(ScreenshotsPath,1)

    if Screenshots != None:
        for x in Screenshots:
            File                = None
            FilePath            = None
            FilePath            = os.path.join(ScreenshotsPath,x)
            File                = discord.File(FilePath, filename=x)
            # AttachmentString    = "attachment://" + str(x)
            # embed               = discord.Embed(title = " ", description = " ", color = discord.Color.green())
            # embed.set_image(url = AttachmentString)

            # try:
            #     await message_channel.send(file=File, embed=embed)
            #     await ctx.respond("Successfully posted an image in " + str(message_channel) + " channel.", delete_after=0)
            # except Exception as e:
            #     print('Error: ' + str(e))
            try:
                await ctx.respond("Successfully posted an image in " + str(message_channel) + " channel.", delete_after=0)
                await message_channel.send(file=File)
                print('Posted image: ' + str(x))

                # move local file to another folder
                # os.rename(FilePath, os.path.join(SArchivedPath,x))
            except Exception as e:
                print('Error: ' + str(e))
    
            print('Selected Images: ' + ', '.join(Screenshots))
    else:
        await ctx.respond("```No screenshots available to share. Try again later.```")
        print('No images found at ' + ScreenshotsPath)
    print('========================== END screenshot ==========================')

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

    # testing getting meesages on channel
    if (message.channel.id == chan_tests and message.content == 'l'):
        crax_chan   = bot.get_channel(chan_tests)
        crax_movie  = bot.get_channel(chan_craxmovie)
        # messages = [message async for message in discord.ext.interaction.guild.get_channel(0).history(limit=12)]
        messages = await crax_movie.history(limit=1).flatten()
        print(messages[0])
        print(messages[0].content)
        print(messages[0].author)
        print(messages[0].created_at)

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



# Days: (CurrentDay.weekday())
# Monday    = 0
# Tuesday   = 1
# Wednesday = 2
# Thursday  = 3
# Friday    = 4
# Saturday  = 5
# Dunday    = 6
# Hours is on 24

@tasks.loop(minutes=1)
async def called_every_min():
    # updates the time and date; must stay here every loop to get updated time and date
    CurrentTime    = datetime.datetime.now()
    CurrentDay     = datetime.datetime.today()

    # if ((CurrentTime.day % 7) == 0 and CurrentTime.hour == 4 and CurrentTime.minute == 0): # attempt to clear channels; CurrentTime.hour to 4 since servers are set to restart at 5
    #     crax_serv = bot.get_channel(chan_craxservers)
    #     crax_evnt = bot.get_channel(chan_craxevents)
    #     await crax_serv.purge(limit=500)
    #     await crax_evnt.purge(limit=500)

    if CurrentDay.weekday() == 5 and CurrentTime.hour == 8 and CurrentTime.minute == 0: # Post Hot manga; CurrentDay().weekday() = 0 is monday, sunday is 6.
        print()
        print('It is Saturday! ' + str(CurrentTime))
        message_channel = bot.get_channel(chan_craxmanga)
        cManga = Get_Manga(CachedMangaFile,True)

        if cManga != None:
            embed_ = None
            embed_ = Create_MangaEmbed(cManga)
            print("Posted new manga recommendation: " + str(cManga['Title']))
        await message_channel.send(embed=embed_)

    if CurrentDay.weekday() == 5 and CurrentTime.hour == 7 and CurrentTime.minute == 59: # Post trending movie; CurrentDay().weekday() = 0 is monday, sunday is 6.
        print()
        print('Movie night! ' + str(CurrentTime))
        message_channel = bot.get_channel(chan_craxmovie)
        cMovie = None
        cMovie = Get_Movie(CachedMovieFile,CraxData['imdbToken'],True)

        if cMovie != None:
            embed_ = None
            embed_ = Create_MovieEmbed(cMovie)
            print("Posted new movie recommendation: " + str(cMovie['primaryTitle']))
        await message_channel.send(embed=embed_)
    
    # print()
    # print(f'Curent Hour: {CurrentTime.hour} | Type: {type(CurrentTime.hour)}')
    # print('Screenshot Hours: ' + ', '.join(map(str,CraxData['Screenshots']['Hours'][str(CurrentDay.weekday())])))
    if CurrentTime.hour in (CraxData['Screenshots']['Hours'][str(CurrentDay.weekday())]) and CurrentTime.minute in (CraxData['Screenshots']['Minutes']):         # post random screenshot
        print()
        print('Time for sreenshots! ' + str(CurrentTime))
        message_channel = bot.get_channel(chan_clipshighlights)
        Screenshots = []
        Screenshots = Get_Screenshot(ScreenshotsPath,1)

        if Screenshots != None:
            for x in Screenshots:
                File                = None
                FilePath            = None
                FilePath            = os.path.join(ScreenshotsPath,x)
                File                = discord.File(FilePath, filename=x)
                try:
                    await message_channel.send(file=File)
                    print('Posted image: ' + str(x))

                    # move local file to another folder
                    os.rename(FilePath, os.path.join(SArchivedPath,x))
                except Exception as e:
                    print('Error: ' + str(e))
        
                print('Selected Images: ' + ', '.join(Screenshots))
        else:
            print('No images found at ' + ScreenshotsPath)

    # Holiday greetings
    if CurrentTime.day == CraxData['thanksgiving']['Day'] and CurrentTime.month == CraxData['thanksgiving']['Month'] and CurrentTime.hour == CraxData['thanksgiving']['Hour'] and CurrentTime.minute == 0: #ThanksGiving
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url=CraxData['thanksgiving']['Image'])
        await message_channel.send(CraxData['thanksgiving']['Message'], embed=embed)

    if CurrentTime.day == CraxData['christmas']['Day'] and CurrentTime.month == CraxData['christmas']['Month'] and CurrentTime.hour == CraxData['christmas']['Hour'] and CurrentTime.minute == 0: #Christmas
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url=CraxData['christmas']['Image'])
        await message_channel.send(CraxData['christmas']['Message'], embed=embed)

    if CurrentTime.day == CraxData['newyear']['Day'] and CurrentTime.month == CraxData['newyear']['Month'] and CurrentTime.hour == CraxData['newyear']['Hour'] and CurrentTime.minute == 0: #NewYear
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url=CraxData['newyear']['Image'])
        await message_channel.send(CraxData['newyear']['Message'], embed=embed)

    if CurrentTime.day == CraxData['mothersday']['Day'] and CurrentTime.month == CraxData['mothersday']['Month'] and CurrentTime.hour == CraxData['mothersday']['Hour'] and CurrentTime.minute == 0: #MothersDay
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url=CraxData['mothersday']['Image'])
        await message_channel.send(CraxData['mothersday']['Message'], embed=embed)

    if CurrentTime.day == CraxData['fathersday']['Day'] and CurrentTime.month == CraxData['fathersday']['Month'] and CurrentTime.hour == CraxData['fathersday']['Hour'] and CurrentTime.minute == 0: #FathersDay
        message_channel = bot.get_channel(chan_announ)
        embed = discord.Embed(title='', description='')
        embed.set_image(url=CraxData['fathersday']['Image'])
        await message_channel.send(CraxData['fathersday']['Message'], embed=embed)

    if CraxData['test']['Enable'] and CurrentTime.day == CraxData['test']['Day'] and CurrentTime.month == CraxData['test']['Month'] and CurrentTime.hour == CraxData['test']['Hour'] and CurrentTime.minute == 0: # Test
        message_channel = bot.get_channel(chan_tests)
        embed = discord.Embed(title='', description='')
        embed.set_image(url=CraxData['test']['Image'])
        await message_channel.send(CraxData['test']['Message'], embed=embed)

print()
@called_every_min.before_loop
async def before():
    await bot.wait_until_ready()

    # send embedded holiday dates to discord
    if (HolidayReport != None):
        print(f'Found holiday report.')
        try:
            channel = bot.get_channel(chan_tests)
            await channel.send(f'```{HolidayReport}```')
            channel     = None
        except Exception as e:
            print('Error sending embedded holiday dates: ', str(e))
        except BaseException as e:
            print('Error sending embedded holiday dates: ', str(e))

    print()
    print("Scheduled Tasks started!")

called_every_min.start()
#end

bot.run(CraxData['Token'])