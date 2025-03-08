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
        [int]$daysOld
    )

    function Purge-Em {
        Param (
            [Parameter(Mandatory=$true,Position=0)]
            [string]$path,
            [Parameter(Mandatory=$false,Position=0)]
            [int]$daysOld = 62
        )

        Get-ChildItem -Path $path -Recurse -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$daysOld) } | Remove-Item -Force
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
            Purge-Em -Path $path -daysOld $daysOld
            return @{Status = $false; Message = "$path already exists. Removed $daysOld days old files."}
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

    $ErrorActionPreference = 'Stop'
    $BaseURL = "https://api.mangadex.org"
    $URL = $BaseURL + $Endpoint
    $Result = $null

    try {
        $Result = Invoke-RestMethod -URI $URL -UseBasicParsing
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
            "Total manga tags found are $(($Result.data | Measure-Object).Count)"
        } else {
            ($Result.Message)
        }
    )" -PrintIt $DebugMode

    LogEntry -Category Debug -Message "End Get Manga Tag List`n" -PrintIt $DebugMode

    return $Result
}

Function Get-Manga {
    param (
        [Parameter(Mandatory=$false,Position=0)]
        [bool]$DebugMode = $false
    )

    LogEntry -Category Debug -Message "Get Mangas" -PrintIt $DebugMode

    $Endpoint = '/manga'

    $ErrorActionPreference = 'Stop'
    $Result = $null
    $Result = SendGet -Endpoint $Endpoint

    LogEntry -Category Debug -Message "Manga API Result - Status: $($Result.result) | Message: $(
        if ($Result.result -NE 'Error') {
            "Total manga tags found are $(($Result.data | Measure-Object).Count)"
        } else {
            ($Result.Message)
        }
    )" -PrintIt $DebugMode

    LogEntry -Category Debug -Message "End Get Mangas`n" -PrintIt $DebugMode

    return $Result
}

####################################

# Directories
[string]$CurrentPath = $(Get-Location | ForEach {$_.Path})
[string]$LogPath = Join-Path $CurrentPath "Logs"
[string]$TempPath = Join-Path $CurrentPath "temps"
[string]$LogFile = Join-Path $LogPath "Get-Manga.log"
[string]$MangaRecommended = Join-Path $tempPath "manga.json"
[string]$MangaListFile = Join-Path $tempPath ".mangaList"

$dirCheckLog = Check-Directory $LogPath 62
$dirCheckTemp = Check-Directory $TempPath 62

LogEntry -Category Debug -Message "Start Directory Checks" -PrintIt $DebugMode
LogEntry -Category Debug -Message "Log dir - Status: $($dirCheckLog.Status) | Message: $($dirCheckLog.Message)" -PrintIt $DebugMode
LogEntry -Category Debug -Message "Temp dir - Status: $($dirCheckTemp.Status) | Message: $($dirCheckTemp.Message)" -PrintIt $DebugMode
LogEntry -Category Debug -Message "End Directory Checks`n" -PrintIt $DebugMode

$Result = Get-MangaTags -DebugMode $DebugMode
Clear-Variable Result

$Result = 

Exit 0