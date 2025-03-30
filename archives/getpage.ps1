[CmdletBinding()]
param(
    [Parameter(Mandatory=$false,Position=0,HelpMessage="Normal: Logs any errors during runtime. Otherwuse, None")]
    [ValidateSet('None', 'Normal')]
	[string]$LogLevel = 'Normal',
    [Parameter(Mandatory=$false,Position=1,HelpMessage="Text file listing Manga titles")]
    [string]$CacheSource = '.\temps\.mangaList',
    [Parameter(Mandatory=$false,Position=2,HelpMessage="Debug mode")]
    [Switch]$DebugMode
)

Function LogEntry {
    Param(
        [ValidateSet('Information', 'Error', 'Debug')]
        $Category = 'Information',
        $Message
    )

    If ($LogLevel -eq 'None') {
        Return
    }

    $private:myLogEntry = [PSCustomObject]@{
        DateTime = (Get-Date).ToString()
        Category = $Category
        Message  = $Message
    }

    Write-Host $Message -ForegroundColor Cyan
    Export-Csv -Path $LogFile -InputObject $myLogEntry -NoTypeInformation -Append
}

Function Get-RawHTML {
    param(
        [Parameter(Mandatory=$true,Position=0,HelpMessage="Website URL")]
        [string]$URL
    )

    $private:HTMLPage = $null

    try {
        $HTMLPage = Invoke-WebRequest -URI $url -ErrorAction Stop
        return $HTMLPage
    } catch {
        LogEntry -Message "Unabled to send web request to `"$URL`": $($Error[0])" -Category 'Error'
        return $false
    }
}

Function Get-ItemDetails {
    param(
        [Parameter(Mandatory=$true,Position=0,HelpMessage="Array of objects containing the mangas,")]
        $Source
    )

    $private:Mangas = @()
    $private:Temp = $null

    # Patterns
    [string]$private:ImagePattern = '(?<= src=").+?(?=" width)'                          # get all strings between " src="" and "">"
    [string]$private:LinkPattern1  = '(?<=<H3><A title=").+?(?=">)'                      # get all strings between "<H3><A title="" and "" rel="
    [string]$private:LinkPattern2  = '(?<=<A class=read-more href=").+?(?=">)'                   # get all strings between "<H3><A title=" and "" rel="
    [string]$private:LinkCleanUp  = '(.*).+?(?=http)'                                    # remove any strings before "http"
    # [string]$private:ReadsPattern = '(?<=<SPAN class=aye_icon>).+?(?=</SPAN> </DIV>)'

    foreach ($item in $Source) {
        $Mangas += [PSCustomObject]@{
            Title = ($item.innerText -split '\n')[1].Trim()
            Description = ($item.innerText -split '\n')[7].Trim() -Replace " More.","..."
            Image = ([regex]::Matches($item.innerHTML,$ImagePattern)).Value
            # Reads = [int]([regex]::Matches($item.innerHTML,$ReadsPattern)).Value
            Reads = [int]($item.innerText -split '\n')[3].Trim()
            Link  = $(
                        $Temp = ([regex]::Matches($item.innerHTML,$LinkPattern1)).Value
                        if (-not($Temp)) {$Temp = ([regex]::Matches($item.innerHTML,$LinkPattern2)).Value}
                        $Temp -Replace $LinkCleanUp
                    )
        }
        Write-Host $(([regex]::Matches($item.innerHTML,$LinkPattern1)).Value) -ForegroundColor Cyan
    }
    return $Mangas
}

# Directories
[string]$CurrentPath = $(Get-Location | ForEach {$_.Path})
[string]$LogPath = Join-Path $CurrentPath "Logs"
[string]$TempPath = Join-Path $CurrentPath "temps"
[string]$LogFile = Join-Path $LogPath "Get-ItemDetails.log"
[string]$MangaRecommended = Join-Path $tempPath "manga.json"
[string]$MangaListFile = Join-Path $tempPath ".mangaList"

$ErrorActionPreference = 'Stop'
$CacheItems = $(if (Test-Path -Path $CacheSource) {Get-Content -Path $CacheSource} else {@()})
$HTMLPage = $null
$ElementDIV = $null
$MangaItems = $null
[int]$MaxTitleinPage = 24
[int]$TargetPage = 1

# get the website page based on cacheditems
$TargetPage = [math]::Floor($CacheItems.Count / $MaxTitleinPage) + 1

# Website url
# $URL = "https://mangakakalot.com/manga_list?type=topview&category=all&state=all&page=$TargetPage" # old website

if ($TargetPage -EQ 1) {
    $URL = "https://www.mangakakalot.gg/manga-list/hot-manga"
} else {
    $URL = "https://www.mangakakalot.gg/manga-list/hot-manga?page=$TargetPage"
}

if ($DebugMode) {Write-Host "Target Page: $URL" -ForegroundColor Cyan}

# Do webrequest to get raw html
$HTMLPage = Get-RawHTML -URL $URL

# check if webrequest was successfull. Exit otherwise
if (-not($HTMLPage)) {
    if ($DebugMode) {Write-Host "Error: $($LastError)" -ForegroundColor Red}
    exit 503
}

$ElementDIV = $HTMLPage.AllElements | Where-Object {$_.tagName -EQ 'div'}
$MangaItems = $ElementDIV | Where-Object {$_.class -EQ "list-truyen-item-wrap"}

if ($DebugMode) {
    Write-Host
    Write-Host "Number of Items: $($MangaItems.Count)" -ForegroundColor Cyan
    Write-Host "Target Page: $TargetPage" -ForegroundColor Cyan
}

$Mangas = Get-ItemDetails -Source $MangaItems

# Select a manga
foreach ($Manga in $Mangas) {
    if ($DebugMode) {
        Write-Host
        Write-Host "Manga Title : $($Manga.Title)" -ForegroundColor Yellow
        Write-Host "Description : $($Manga.Description)" -ForegroundColor Cyan
        Write-Host "Manga Image : $($Manga.Image)" -ForegroundColor Cyan
        Write-Host "Manga Link  : $($Manga.Link)" -ForegroundColor Cyan
        Write-Host "Manga Reads : $($Manga.Reads)" -ForegroundColor Cyan
    }

    if ($Manga.Title -NOTIN $CacheItems) {
        $Manga | ConvertTo-Json | Out-File -Encoding utf8 -FilePath $MangaRecommended   # export a json of selected manga. Other program then can use the json.
        $Manga.title | Out-File -FilePath $MangaListFile -Encoding utf8 -Append         # Add manga title to a text file to keep track of already selected mangas
        if ($DebugMode) {
            Write-Host
            Write-Host "RECOMMENDED MANGA: $($Manga.Title)" -ForegroundColor Green
        }
        break
    }
}

exit 0