#!/bin/sh

# run "chmod +x run_craxbot1.sh" to make this bash script executable

if pgrep -f "craxbot1.py" > /dev/null ; then
        exit 1
else
        #mailing program
        python3 /home/truenas_admin/discordbot/craxbot1.py
        exit 0
fi
