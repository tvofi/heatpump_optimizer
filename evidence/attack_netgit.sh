#!/bin/sh
echo "NETGIT $*" >> /tmp/evil/netlog
/usr/bin/git ls-remote https://127.0.0.1:9/hb.git >/dev/null 2>&1 && echo reached >> /tmp/evil/netlog || echo "attempted-remote rc=$?" >> /tmp/evil/netlog
exec /usr/bin/git "$@"
