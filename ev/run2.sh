#!/bin/bash
exec 9>>"$1"
python3 -I -c 'import fcntl, sys; exec("try: fcntl.flock(9, fcntl.LOCK_EX | fcntl.LOCK_NB)\nexcept BlockingIOError: sys.exit(75)")' || exit $?
cd "$2"; git -c gc.auto=100 -c gc.autoDetach=true gc --auto 2>&1
echo "run exits"
