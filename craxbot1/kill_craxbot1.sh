#!/bin/sh

kill $(ps -ef | grep -v grep | grep "craxbot1.py" | awk '{print $2}')
exit 0