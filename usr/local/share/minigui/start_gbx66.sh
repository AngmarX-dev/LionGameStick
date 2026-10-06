#!/bin/sh -x	
killall -9 game_nosdcard &
sleep 0.2
sync &
echo 3 > /proc/sys/vm/drop_caches
export MG_CFG_PATH=/usr/local/share/minigui/hdmicfg
/usr/bin/game &
