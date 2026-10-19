#!/bin/sh
# run the 7a block and the R10 block in the tree at $1
cd "$1" && python3 tools/audit/seat/features_block.py "# -- live power clamp, 7a" "# --- #1956 the card recommends" 2>&1 | tail -40
