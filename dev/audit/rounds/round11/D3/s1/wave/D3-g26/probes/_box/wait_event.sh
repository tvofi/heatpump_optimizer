#!/usr/bin/env bash
# exit when a new gate event, inbox command, or driver terminal line appears
P=$HOME/.boxcomms-r11-D3-g26/tree/PROGRESS.log
n0=$(grep -cE "gate done|null gate done|BLOCKED" $P); c0=$(wc -l < $HOME/comms_loop.log); g0=$(grep -cE "GATES-DONE|NULL-MISSING|EXIT" $HOME/gate_wave.log)
until [ $(grep -cE "gate done|null gate done|BLOCKED" $P) -gt $n0 ] || [ $(wc -l < $HOME/comms_loop.log) -gt $c0 ] || [ $(grep -cE "GATES-DONE|NULL-MISSING|EXIT" $HOME/gate_wave.log) -gt $g0 ]; do sleep 30; done
date -u; tail -3 $P; tail -4 $HOME/gate_wave.log; tail -2 $HOME/comms_loop.log
