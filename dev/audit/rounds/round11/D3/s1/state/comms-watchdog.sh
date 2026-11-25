#!/usr/bin/env bash
# Box D3-u1a watchdog: box_comms.sh can exit mid-push (a transient git/network error under set -e)
# leaving $ST/lock behind, after which every heartbeat/checkpoint fails "lock stuck" and the loop dies.
# Every 60 s: clear a lock older than 300 s when no box_comms.sh process is alive; restart the loop if dead.
L=$HOME/.boxcomms-r11-D3-u1a/lock
while :; do
  alive=$(ps -eo args | grep -c '^bash /root/box_comms.sh')
  if [ -d "$L" ] && [ $(( $(date +%s) - $(stat -c %Y "$L") )) -gt 300 ] && [ "$alive" -eq 0 ]; then rmdir "$L" && echo "$(date -u +%FT%TZ) cleared stale lock"; fi
  if ! ps -eo args | grep -q '^bash /root/box_comms.sh loop'; then
    ( . $HOME/.boxcomms.env; setsid nohup bash $HOME/box_comms.sh loop 600 >> $HOME/boxloop.log 2>&1 < /dev/null & ); echo "$(date -u +%FT%TZ) restarted loop"
  fi
  sleep 60
done
