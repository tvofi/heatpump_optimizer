#!/bin/bash
echo $$ >> "$REAP_DIR/pids"
bash -c 'sleep 30; :' & echo $! >> "$REAP_DIR/pids"
bash -c 'sleep 30 & echo $! >> "$0"; wait' "$REAP_DIR/pids" & echo $! >> "$REAP_DIR/pids"
wait; echo PUSHED
