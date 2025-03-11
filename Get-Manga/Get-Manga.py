import discord,pathlib,random,datetime,json,os,subprocess,calendar,requests,csv,sys
from discord.ext import commands, tasks

def SendGet(_endpoint):
    _BaseURL= "https://api.mangadex.org"
    _URI = str(_BaseURL) + str(_endpoint)

    try:
        _response = _session.get(url = _URI)
    except Exception as e:
        print("[" + str(_response.status_code) + "] API failed. URI = " + str(_URI) + "")
    
    return _response

def Get_Manga(_Limit):
    _endpoint = "/manga?limit=" + str(_Limit) + "&order%5BfollowedCount%5D=desc"

    try:
        _result = SendGet(_endpoint)
    except Exception as e:
        print('Error retrieving mangas: ')

    return _result

def Get_MangaRating(_MangaID):
    _endpoint = "/statistics/manga/" + str(_MangaID)

    try:
        _result = SendGet(_endpoint)
    except Exception as e:
        print('Error retrieving manga rating: ' + str(e))

    return _result

def Get_MangaArtFilename(_CoverArtID):
    _endpoint = "/cover/" + str(_CoverArtID) + "?includes%5B%5D=manga"

    try:
        _result = SendGet(_endpoint)
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
                ImageLink_ = "https://uploads.mangadex.org/covers/" + str(MangaID_) + "/$(" + str(CoverArtFilename_['data']['attributes']['fileName'])
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



##########################

_session = requests.Session()

path_ = pathlib.Path(__file__).parent.absolute() # path to discord bot script
temppath = os.path.join(path_,"temps")
mangaRecommended = os.path.join(temppath,"manga.json")
CachedFile = os.path.join(temppath,".mangaList")

# Get mangas
Result = Get_Manga(24)
# print(Result.content)

# import cached manga titles
CachedTitles = []
if os.path.exists(CachedFile):
        with open(CachedFile, 'r') as file:
            CachedTitles_ = [line.strip() for line in file]


if (Result.status_code == 200):
    Result = Result.json()
    SelectedManga = Select_Manga(Result['data'],CachedTitles)

    print()
    print('SELECTED MANGA')
    print('Title:       ' + SelectedManga['Title'])
    print('Image:       ' + SelectedManga['Image'])
    print('Link:        ' + SelectedManga['Link'])
    print('Rating:      ' + SelectedManga['Rating'])
    print('Follows:     ' + SelectedManga['Follows'])
    print('Description: \n' + SelectedManga['Description'])

    # write to file
    mode = "w"
    MangaTitle = SelectedManga['Title']
    if CachedTitles:
        mode = "a"
        MangaTitle = "\n" + str(SelectedManga['Title'])
    try:
        with open(CachedFile, mode) as file:
            file.write(MangaTitle)

        with open(mangaRecommended, 'w', encoding='utf-8') as file:
            json.dump(SelectedManga, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print('Error updating manga titles: ' + str(e))
else:
    print()
    print("Status Code: " + str(Result.status_code))
    print("Message: " + str(Result.reason))

print()