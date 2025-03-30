param(
    [int]$page = 4,
    [switch]$DebugMode
)

Function get-str {
    param(
        $String,
        $Pattern
    )

    $private:result = @()

    if ($DebugMode) {
        Write-Host "`nString: $String"
        Write-Host "`tPattern: $Pattern"
    }

	try {
        $ErrorActionPreference = 'Stop'
        $result = $String | Select-String -Pattern $Pattern -ErrorAction Stop
        $result.Matches[0].Value
    } catch {
        $result = $false
    }
}

Function getpage {
    [string]$private:htmlFile = Join-Path $tempPath "scraped_html.html"
    
    [string]$private:URL = 'https://mangakakalot.com/manga_list?type=topview&category=all&state=all&page=1'
    [string]$privatE:initConditionLine = '<a href="https://mangakakalot.com/manga_list?type=Topview&category=all&state=all&page=1">Hot manga</a>'
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
    [bool]$mangaListCheck = $false
    [string]$private:URL = ""

    $private:returnthis = [PSCustomObject]@{
        title = $null;
        desc = $null;
        reads = $null;
        link = $null;
        image = $null;
    }

    if (-not (Test-Path -Path $tempPath)) {mkdir $tempPath}

    $private:mangas = [PSCustomObject]@{}
    [int]$count = 1
    for ($i = 1; $i -le $page; $i++) {
        $URL = "https://mangakakalot.com/manga_list?type=topview&category=all&state=all&page=$i"
        try {
            $getPage = Invoke-WebRequest -URI $url -ErrorAction Stop
        } catch {}
    
	    $getPageCode = [int]$getPage.StatusCode
    
        if ($getPageCode -eq 200) {
            # Write to file
            $getPage.RawContent | Out-File -Encoding 'utf8' $htmlFile
            Get-Content $htmlFile |
            ForEach-Object {
                # Write-host "Init? $initCondition"
                if ($_ -like "$imgLine*") {
                    $getImg = get-str $_ $imgPattern
                }
                if (($_ -like "$line*") -AND (-not $foundIt) -AND ($initCondition)) {
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
                } elseif (($foundIt) -AND ($_ -like "$readsline*")) {
                    $getReads = $(get-str $_ $readsPattern)
                    $returnthis.reads = [int32]$getReads.Replace(',','')

                } elseif (($foundIt) -AND ($_ -match $descLine)) {
                    # Write-Host "Desc: $_"
                    $getDesc = $_ -Replace "($asciiPattern)" , ''
                    $getDesc = $getDesc.Replace("&;",'')
                    $getDesc = $getDesc -Replace "(($linePattern))" , ''
                    $getDesc = $getDesc.Replace("<a</a>",'')
                    $getDesc = "$getDesc..."
                    $returnthis.desc = $getDesc

                    $mangas | Add-Member -Name $count -MemberType NoteProperty -Value $returnthis
                    $count++
                    $foundIt = $false

                    $returnthis = [PSCustomObject]@{
                        title = $null;
                        desc = $null;
                        reads = $null;
                        link = $null;
                        image = $null;
                    }
                }

                if (($_ -EQ $initConditionLine) -AND (-not $initCondition)) {
                    $initCondition = $true
                }
            }
            Remove-Item $htmlFile -Force
        }
        Start-Sleep 2
    }
    # $mangas | ConvertTo-Json | Set-Content $mangaRecommended -Encoding UTF8
    return $mangas
}

[string]$GLOBAL:current_dir = $(Get-Location | ForEach {$_.Path})
[string]$GLOBAL:tempPath = Join-Path $current_dir "temps"
# [string]$GLOBAL:mangaListFile = Join-Path $tempPath ".mangaList"
[string]$GLOBAL:mangaRecommended = Join-Path $tempPath "manga2.json"

# $Global:mangaListCached = @()

# if (Test-Path -Path $mangaListFile) {
#     $mangaListCached = Get-Content $mangaListFile
#     if ($mangaListCached.Count -EQ 24) {
#         Remove-Item $mangaListFile -Force
#     }
# }

$result = getpage

if ($result) {
    # Write-Host "`nManga Title: $($result.title)"
    # Write-Host "`nDescription: $($result.desc)"
    # Write-Host "`nManga Image: $($result.image)"
    # Write-Host "Manga Link: $($result.link)`n"

    # $mangas | ConvertTo-Json | Set-Content $mangaRecommended -Encoding UTF8
    # $result.title | Out-File -FilePath $mangaListFile -Encoding utf8 -Append
}