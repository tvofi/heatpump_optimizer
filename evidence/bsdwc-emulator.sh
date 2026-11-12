#!/bin/sh
# emulates BSD/macOS wc: pads the count to width 8 (bind-mounted over /usr/bin/wc in a private mount namespace)
/tmp/rev.JENf/wc.real "$@" | awk '{ $1 = sprintf("%8s", $1); print }'
