#!/bin/sh
# emulates BSD/macOS wc: pads the count to width 8
/tmp/tmp.cWuuj98Lfu/wc.real "$@" | awk '{ $1 = sprintf("%8s", $1); print }'
