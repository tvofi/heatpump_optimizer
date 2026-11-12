#!/bin/sh
echo "EVILGIT $*" >> /tmp/evil/log
exec /usr/bin/git "$@"
