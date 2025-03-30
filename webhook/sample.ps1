param([bool]$mode)

if ($mode) {
    $message = '"```{0} New update for DCS has been detected. Restarting the server.```"' -f (get-date -f "yyyy/MM/dd hh:mm:ss tt")
} else {
    $message = '":loudspeaker: [Restarted]```This is a test for discord webhook.```"'
}
$webHook = "https://discord.com/api/webhooks/1124176562913288296/3wAl90F7kww0XfRLGFsBBS7xT6scU4bmL4RiEpRdb4TPvBKGTx0WL_ySe1OeshoTd1uc"
$discordWH = "C:\Users\defco\Documents\Discord_Bots\webhook\DiscordSendWebhook.exe"
Start-Process -FilePath $discordWH -ArgumentList "-m $message","-n `"CraxTest`"","-w $webHook","-a http://craxgaming.com/craxico.png"