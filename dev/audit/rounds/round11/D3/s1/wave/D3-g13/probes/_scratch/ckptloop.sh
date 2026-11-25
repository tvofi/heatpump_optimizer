#!/bin/bash
# owner ruling (inbox NOTE 1): checkpoint at least every 10 minutes while work may be uncheckpointed
. $HOME/.boxcomms.env
while true; do sleep 600; out=$(bash $HOME/gate_wave.sh ckpt 2>&1); [ -n "$out" ] && bash $HOME/box_comms.sh heartbeat "ckpt: $out" >/dev/null 2>&1; done
