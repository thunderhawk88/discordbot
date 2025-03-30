# This scripts scans a manga website then pick a manga in descending order.
# So if the manga website is ranking hottest manga, this script will start with #1 down.
# The outputs are json file and a text file.
# JSON file contains one manga title with all details such as description, # of reads, and the mange poster/image.
# text file is named ".mangalist". It lists all the manga title that has been selected in the past. This way the script wont recommend the same manga everytime. Unless the ranking changed.
param(
    [switch]$DebugMode
)

Function get-str {
    param(
        $String,
        $Pattern
    )

    $private:result = @()
	$result = $String | Select-String -Pattern $Pattern
    $result.Matches[0].Value
}
Function getpage {
    param(
        $Page = 1
    )

    [string]$private:htmlFile = Join-Path $tempPath "scraped_html.html"
    
    [string]$private:URL = "https://mangakakalot.com/manga_list?type=topview&category=all&state=all&page=$Page"
    [string]$privatE:initConditionLine = "<a href=`"https://mangakakalot.com/manga_list?type=Topview&category=all&state=all&page=1`">Hot manga</a>"
    [string]$privatE:line = '<a rel="nofollow" href='
    [string]$privatE:lineExclude = 'class="list'
    [string]$private:titlePattern = '(?<=title\=").+?(?=">)'
    [string]$private:linkPattern = '(?<=href=").+?(?=" title)'
    [string]$private:descLine = 'title>More.</a>'
    [string]$private:asciiPattern = '(?<=&).+?(?=;)'
    [string]$private:linePattern = '(?<=<a).+?(?=</a>)'
    [string]$private:imgLine = '<img src="'
    [string]$private:imgPattern = '(?<=<img src=").+?(?=" onerror)'
    [string]$private:readsLine = '<span class="aye_icon">'
    [string]$private:readsPattern = '(?<=class="aye_icon">).+?(?=</span>)'

    $private:getPage = $null
    [int32]$private:getPageCode = $null
    [string]$private:getTitle = $null
    [string]$private:getDesc = $null
    [string]$private:getReads = $null
    [string]$private:getLink = $null
    [string]$private:getImg = $null
    [bool]$private:initCondition = $false
    [bool]$private:foundIt = $false
    [bool]$breakLoop = $false
    [bool]$mangaListCheck = $false

    $private:returnthis = [PSCustomObject]@{
        title = $null;
        desc = $null;
        reads = $null;
        link = $null;
        image = $null;
    }
    $private:Ptags = [PSCustomObject]@{
        Content = $null
        Start = 0
        End = 0
    }

    if (-not (Test-Path -Path $tempPath)) {mkdir $tempPath}

    try {
        $getPage = Invoke-WebRequest -URI $url -ErrorAction Stop
    } catch {}
	
	$getPageCode = [int]$getPage.StatusCode
	
    if ($getPageCode -eq 200) {
        $lineNum = 0
        # Write to file
        $getPage.RawContent | Out-File -Encoding 'utf8' $htmlFile
        Get-Content $htmlFile |
        ForEach-Object {
            $lineNum++
            if ($_ -like "$imgLine*") {
                $getImg = get-str $_ $imgPattern
            }

            # check for tag <p> for description
            if (-not($breakLoop)) {
                if ($DebugMode) {Write-Host "`nLine $lineNum"}
                if ((($PTags.Start -EQ 0) -AND ($PTags.End -EQ 0)) -OR (($PTags.Start -EQ 1) -AND ($PTags.End -EQ 0))) {
                    $PTags.Start = $PTags.Start + ([regex]::Matches($_, "<p>")).Count
                    $PTags.End = $PTags.End + ([regex]::Matches($_, "</p>")).Count
                    if ($DebugMode) {Write-Host "`tPtags: $($PTags.Start) | $($PTags.End)" -ForegroundColor Green}
                } elseif ($PTags.Start -GE $PTags.End) {
                    $PTags.Start = 0
                    $PTags.End = 0
                }
                # record all string if Ptag.Start is 1
                if ($PTags.Start -EQ 1) {
                    $PTags.Content = $Ptags.Content + ($_ -replace "<p>","" -replace "'","") + " "
                } else {
                    $PTags.Content = $null
                }
                
                if ($DebugMode) {Write-Host "`tPtags: $($PTags.Start) | $($PTags.End)`n`tPContent: $($PTags.Content)"}
            }

            if (($_ -like "$line*") -AND (-not $foundIt) -AND ($initCondition) -AND (-not $breakLoop)) {
                $getLink = get-str $_ $linkPattern
                $getTitle = get-str $_ $titlePattern
                if (-not ($getTitle -match $lineExclude)) {
                    if ($mangaListCached) {$mangaListCheck = $mangaListCached.Contains($getTitle)}
                    if (-not ($mangaListCheck)) {
                        $foundIt = $true
                        # Write-Host "Title: $_"
                        $returnthis.title = $getTitle
                        $returnthis.link = $getLink
                        $returnthis.image = $getImg
                    }
                }
            } elseif (($foundIt) -AND ($_ -like "$readsline*") -AND (-not $breakLoop)) {
                $getReads = $(get-str $_ $readsPattern)
                $returnthis.reads = [int32]$getReads
            } elseif (($foundIt) -AND ($_ -match $descLine) -AND (-not $breakLoop)) {

                $getDesc = $PTags.Content
                $getDesc = $getDesc.Substring(0,$getDesc.IndexOf('<'))
                if  ($DebugMode) {Write-Host "`n1. Desc: $getDesc" -ForegroundColor Magenta}
                
                # $getDesc = $_ -Replace "($asciiPattern)" , ''
                if  ($DebugMode) {Write-Host "`n2. Desc: $getDesc" -ForegroundColor Magenta}
                
                $getDesc = $getDesc -Replace "&rsquo;","'" -Replace "&#39;","'" -Replace "&rdquo;",""
                if  ($DebugMode) {Write-Host "`n3. Desc: $getDesc" -ForegroundColor Magenta}
                
                $getDesc = $getDesc -Replace "(($linePattern))" , ''
                if  ($DebugMode) {Write-Host "`n4. Desc: $getDesc" -ForegroundColor Magenta}
                
                $getDesc = $getDesc.Replace("<a</a>",'')
                if  ($DebugMode) {Write-Host "`n5. Desc: $getDesc" -ForegroundColor Magenta}

                $getDesc = $getDesc.trim() + "..."
                $returnthis.desc = $getDesc
                $breakLoop = $true
                # reset ptags since a description has been found
                $PTags.Start = 0
                $PTags.End = 0
            }

            if (($_ -EQ $initConditionLine) -AND (-not $initCondition)) {
                $initCondition = $true
            }
        }
        # Remove-Item $htmlFile -Force
        if ($returnthis.title -AND $returnthis.link -AND $returnthis.image) {
            if ($DebugMode) {
                Write-Host
                Write-Host "Manga Details before function return:"
                Write-Host "Manga Title: $($returnthis.title)" -ForegroundColor Yellow
                Write-Host "Description: $($returnthis.desc)" -ForegroundColor Yellow
                Write-Host "Manga Image: $($returnthis.image)" -ForegroundColor Yellow
                Write-Host "Manga Link: $($returnthis.link)" -ForegroundColor Yellow
            }
            return $returnthis
        } else {
            return $false
        }
    } else {
        return $false
    }
}

[string]$GLOBAL:current_dir = $(Get-Location | ForEach {$_.Path})
[string]$GLOBAL:tempPath = Join-Path $current_dir "temps"
[string]$GLOBAL:mangaListFile = Join-Path $tempPath ".mangaList"
[string]$GLOBAL:mangaRecommended = Join-Path $tempPath "manga.json"

$Global:mangaListCached = @()
[int]$MaxTitleinPage = 24
[int]$TargetPage = 1

if ($DebugMode) {
    Write-Host
    Write-Host "Current Dir:                      : $current_dir"
    Write-Host "Temp Dir:                         : $tempPath"
    Write-Host "Manga Title list file:            : $mangaListFile"
    Write-Host "Manga JSON file                   : $mangaRecommended"
    Write-Host "Max number of Titles in Manga site: $MaxTitleinPage"
    Write-Host "Initial Target Page               : $TargetPage"
}

if (Test-Path -Path $mangaListFile) {
    $mangaListCached = Get-Content $mangaListFile
    $TargetPage = [math]::Floor($mangaListCached.Count / $MaxTitleinPage) + 1
    # if ($TargetPage -LT 1) {$TargetPage = 1}

    if ($DebugMode) {
        Write-Host
        Write-Host "Cached Manga Count: $($mangaListCached.Count)" -ForegroundColor Cyan
        Write-Host "Target Page       : $TargetPage" -ForegroundColor Cyan
    }

    $result = getpage -Page $TargetPage
} else {
    if ($DebugMode) {
        Write-Host
        Write-Host "No cached mangas found." -ForegroundColor Cyan
    }
    $result = getpage
}

if ($result) {
    if ($DebugMode) {
        Write-Host
        Write-Host "Manga Title: $($result.title)" -ForegroundColor Cyan
        Write-Host "Description: $($result.desc)" -ForegroundColor Cyan
        Write-Host "Manga Image: $($result.image)" -ForegroundColor Cyan
        Write-Host "Manga Link: $($result.link)" -ForegroundColor Cyan
    }

    $result | ConvertTo-Json | Out-File -Encoding utf8 -FilePath $mangaRecommended
    $result.title | Out-File -FilePath $mangaListFile -Encoding utf8 -Append
}