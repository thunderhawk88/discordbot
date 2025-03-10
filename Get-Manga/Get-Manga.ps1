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
        [Parameter(Mandatory=$false,Position=0)]
        [ValidateSet('Information', 'Error', 'Debug')]
        $Category = 'Information',
        [Parameter(Mandatory=$false,Position=1)]
        [bool]$PrintIt = $false,
        [Parameter(Mandatory=$false,Position=2)]
        $Message
    )

    If ($LogLevel -eq 'None') {Return}

    $private:myLogEntry = [PSCustomObject]@{
        DateTime = (Get-Date).ToString()
        Category = $Category
        Message  = $Message
    }

    if ($PrintIt) {Write-Host $Message -ForegroundColor Cyan}
    Export-Csv -Path $LogFile -InputObject $myLogEntry -NoTypeInformation -Append
}

Function Check-Directory {
    Param (
        [Parameter(Mandatory=$true,Position=0)]
        [string]$path,
        [Parameter(Mandatory=$false,Position=1)]
        [int]$daysOld,
        [Parameter(Mandatory=$false,Position=2)]
        [int]$SizeLimit = 10 #MegaBites
    )

    function Purge-Em {
        Param (
            [Parameter(Mandatory=$true,Position=0)]
            [string]$path,
            [Parameter(Mandatory=$false,Position=1)]
            [int]$daysOld = 62,
            [Parameter(Mandatory=$false,Position=2)]
            [int]$SizeLimit = 10 #MegaBites
        )

        Get-ChildItem -Path $path -Recurse -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$daysOld) -OR $_.Length -gt "$($SizeLimit)MB"} | Remove-Item -Force
    }

    $ErrorActionPreference = 'Stop'

    if (-not(Test-Path -Path $path)) {
        try {
            mkdir $path | Out-Null
            return @{Status = $true; Message = "$path directory has been successfully created."}
        } catch {
            return @{Status = $false; Message = $_.Exception.Message}
        }
    } else {
        if ($daysOld) {
            Purge-Em -Path $path -daysOld $daysOld -SizeLimit $SizeLimit
            return @{Status = $false; Message = "$path already exists. Removed $daysOld days old, and over $SizeLimit MB size files."}
        } else {
            return @{Status = $false; Message = "$path already exists."}
        }
    }
}

Function SendGet{
    param (
        [Parameter(Mandatory=$true,Position=0)]
        [string]$Endpoint
    )

    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $ErrorActionPreference = 'Stop'
    $BaseURL = "https://api.mangadex.org"
    $URL = $BaseURL + $Endpoint
    $Result = $null

    try {
        $Result = Invoke-RestMethod -URI $URL
    } catch {
        $Result = @{result = "Error";Message = $_.Exception.Message}
    }

    return $Result
}

Function Get-MangaTags {
    param (
        [Parameter(Mandatory=$false,Position=0)]
        [bool]$DebugMode = $false
    )

    LogEntry -Category Debug -Message "Get Manga Tag List" -PrintIt $DebugMode

    $Endpoint = '/manga/tag'

    $ErrorActionPreference = 'Stop'
    $Result = $null
    $Result = SendGet -Endpoint $Endpoint

    LogEntry -Category Debug -Message "Manga Tag API Result - Status: $($Result.result) | Message: $(
        if ($Result.result -NE 'Error') {
            "Total manga tags found is $($Result.total)"
        } else {
            ($Result.Message) # exception message from function SendGet
        }
    )" -PrintIt $DebugMode

    LogEntry -Category Debug -Message "End Get Manga Tag List`n" -PrintIt $DebugMode

    return $Result
}

Function Get-Manga {
    param (
        [Parameter(Mandatory=$false,Position=0)]
        [int]$Limit = 24,
        [Parameter(Mandatory=$false,Position=1)]
        [bool]$DebugMode = $false
    )

    LogEntry -Category Debug -Message "Get Mangas" -PrintIt $DebugMode

    $Endpoint = "/manga?limit=$Limit&order%5BfollowedCount%5D=desc"

    $ErrorActionPreference = 'Stop'
    $Result = $null
    $Result = SendGet -Endpoint $Endpoint

    LogEntry -Category Debug -Message "Manga API Result - Status: $($Result.result) | Message: $(
        if ($Result.result -NE 'Error') {
            "Success!"
        } else {
            ($Result.Message) # exception message from function SendGet
        }
    )" -PrintIt $DebugMode

    LogEntry -Category Debug -Message "End Get Mangas`n" -PrintIt $DebugMode

    return $Result
}

Function Get-MangaRating {
    param (
        [Parameter(Mandatory=$true,Position=0)]
        [string]$MangaID,
        [Parameter(Mandatory=$false,Position=1)]
        [bool]$DebugMode = $false
    )

    LogEntry -Category Debug -Message "Get Manga Rating" -PrintIt $DebugMode

    $Endpoint = "/statistics/manga/$($MangaID)"

    $ErrorActionPreference = 'Stop'
    $Result = $null
    $Result = SendGet -Endpoint $Endpoint

    LogEntry -Category Debug -Message "Manga API Result - Status: $($Result.result) | Message: $(
        if ($Result.result -NE 'Error') {
            "Success!"
        } else {
            ($Result.Message) # exception message from function SendGet
        }
    )" -PrintIt $DebugMode

    LogEntry -Category Debug -Message "Get Manga Rating`n" -PrintIt $DebugMode

    return $Result
}

Function Get-MangaArtFilename {
    param (
        [Parameter(Mandatory=$true,Position=0)]
        [string]$CoverArtID,
        [Parameter(Mandatory=$false,Position=1)]
        [bool]$DebugMode = $false
    )

    LogEntry -Category Debug -Message "Get Manga Art Filename" -PrintIt $DebugMode

    $Endpoint = "/cover/$($CoverArtID)?includes%5B%5D=manga"

    $ErrorActionPreference = 'Stop'
    $Result = $null
    $Result = SendGet -Endpoint $Endpoint

    LogEntry -Category Debug -Message "Manga API Result - Status: $($Result.result) | Message: $(
        if ($Result.result -NE 'Error') {
            "Success!"
        } else {
            ($Result.Message) # exception message from function SendGet
        }
    )" -PrintIt $DebugMode

    LogEntry -Category Debug -Message "Get Manga Art Filename`n" -PrintIt $DebugMode

    return $Result
}

Function Select-Manga {
    param (
        [Parameter(Mandatory=$true,Position=0)]
        [PSCustomObject]$MangaList,
        [Parameter(Mandatory=$false,Position=1)]
        [array]$CachedTitles,
        [Parameter(Mandatory=$false,Position=2)]
        [bool]$DebugMode = $false
    )
    $ErrorActionPreference = 'Stop'
    $MangaURL = "https://mangadex.org/title/"

    # Attributes to gather
        # Title = $null
        # ID = $null
        # Description = $null
        # Image = $null
        # Link = $null
        # Rating = $null
        # Follows = $null
    
    foreach ($manga in $MangaList) {
        # clear variables
        $Rating             = $null
        $CoverArtID         = $null
        $CoverArtFilename_  = $null
        $CoverArtFilename   = $null
        $ImageLink          = $null

        # check if the mangta title has already been recommended before
        $Title = $(if ($manga.attributes.title.en) {$manga.attributes.title.en} else {$manga.attributes.title.psobject.Properties | Where-Object {$_.TypeNameOfValue -EQ 'System.String'} | Select -ExpandProperty Value})
        
        if ($Title -notin $CachedTitles) {
            # get ratings
            $Rating = Get-MangaRating -MangaID $manga.id -DebugMode $DebugMode

            # get cover art id
            $CoverArtID = $manga.relationships | Where-Object {$_.type -EQ 'cover_art'} | Select-Object -ExpandProperty id

            # get cover art filename
            $CoverArtFilename_ = Get-MangaArtFilename -CoverArtID $CoverArtID -DebugMode $DebugMode

            # generate cover art link
            if ($CoverArtFilename_.result -EQ 'ok') {
                $CoverArtFilename = $CoverArtFilename_.data.attributes.filename
                $ImageLink = "https://uploads.mangadex.org/covers/$($manga.id)/$($CoverArtFilename)"
            } else {
                $ImageLink = "ERROR"
            }

            return [PSCustomObject]@{
                Title       = $Title
                ID          = $manga.id
                Description = $manga.attributes.description.en -replace "\u003e","" -replace "\u003c",""
                Image       = $ImageLink
                Link        = $MangaURL + $manga.id
                Rating      = $(if ($Rating.result -EQ 'ok') {[double]$Rating.statistics."$($manga.id)".rating.average}) # average rating
                Follows     = $(if ($Rating.result -EQ 'ok') {[int]$Rating.statistics."$($manga.id)".follows})
            }
        }
    }

    return $false
}

####################################

# API doc
# https://api.mangadex.org/docs/swagger.html#

# Directories
[string]$CurrentPath = $(Get-Location | ForEach {$_.Path})
[string]$LogPath = Join-Path $CurrentPath "Logs"
[string]$TempPath = Join-Path $CurrentPath "temps"
[string]$LogFile = Join-Path $LogPath "Get-Manga.log"
[string]$MangaRecommended = Join-Path $tempPath "manga.json"
[string]$MangaListFile = Join-Path $tempPath ".mangaList"
$SelectedManga = $null

# create folders if missing. Delete files over 62 days old, and over 10MB size
$dirCheckLog = Check-Directory $LogPath 62 -SizeLimit 10
$dirCheckTemp = Check-Directory $TempPath 62 -SizeLimit 10

LogEntry -Category Debug -Message "Start Directory Checks" -PrintIt $DebugMode
LogEntry -Category Debug -Message "Log dir - Status: $($dirCheckLog.Status) | Message: $($dirCheckLog.Message)" -PrintIt $DebugMode
LogEntry -Category Debug -Message "Temp dir - Status: $($dirCheckTemp.Status) | Message: $($dirCheckTemp.Message)" -PrintIt $DebugMode
LogEntry -Category Debug -Message "End Directory Checks`n" -PrintIt $DebugMode

# $Result = Get-MangaTags -DebugMode $DebugMode
# Clear-Variable Result

$Limit = 24

While(-not $SelectedManga) {
    $Result = Get-Manga -Limit $Limit -DebugMode $DebugMode

    # import list of already used Mnaga titles
    if (Test-Path -Path $MangaListFile) {
        $CachedTitles = $(if (Test-Path -Path $CacheSource) {Get-Content -Path $CacheSource} else {@()})
    }

    # Select unused manga title, then get manga attributes
    $SelectedManga = Select-Manga -MangaList $Result.data -CachedTitles $CachedTitles -DebugMode $DebugMode

    if ($SelectedManga) {
        # generate a json for recommended manga's attributes
        $SelectedManga | ConvertTo-Json -Depth 4 | Out-file -Encoding utf8 -FilePath $MangaRecommended

        # add the recommended manga's title to the used/cached manga titles
        $SelectedManga.Title | Out-File -FilePath $MangaListFile -Encoding utf8 -Append

        # display selected manga title
        Write-Host
        LogEntry -Category Debug -Message "Recommended manga title: $($SelectedManga.Title)" -PrintIt $DebugMode
    }

    $Limit = $Limit + 8
}

Exit 0