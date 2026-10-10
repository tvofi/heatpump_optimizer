#!/bin/bash
# OWN HARNESS (reviewer-built, disclosed as mine). Drives the PRODUCTION
# confirm_readback extracted verbatim from the head's tools/pr/app_push.sh
# (prod_readback.sh, sha256 2507fa6f...) against a fake `curl` I wrote, with a
# temp state dir I own. No network, no key, no push.
set -u
SCR=/Users/timmalmstrom/hpo-seats/r9rev-2117
ARM=$1            # ok | race | stale | error | bad | closed
TRIES=${2:-6}
SLEEP=${3:-2}
W=$(mktemp -d "$SCR/arm-XXXXXX")
mkdir -p "$W/bin" "$W/priv"
PRIV="$W/priv"; : > "$PRIV/token.h"
printf 'body-live\n' > "$W/body.md"

# --- fake curl: emits VALID JSON via python3 ---------------------------------
cat > "$W/bin/curl" <<'STUB'
#!/bin/bash
n=$(cat "$ARM_DIR/get-n" 2>/dev/null || echo 0); n=$((n + 1)); printf '%s' "$n" > "$ARM_DIR/get-n"
case "$ARM_MODE" in
  error) exit 22 ;;
esac
ARM_N=$n python3 - "$ARM_MODE" "$ARM_HEAD" "$ARM_OLD" "$ARM_RACE_N" <<'PY'
import json, os, sys
mode, head, old, race_n = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
n = int(os.environ["ARM_N"])
if mode == "ok":
    d = {"number": 7, "state": "open", "head": {"sha": head}, "body": "body-live\n"}
elif mode == "race":
    sha = old if n <= race_n else head
    body = "old body\n" if n <= race_n else "body-live\n"
    d = {"number": 7, "state": "open", "head": {"sha": sha}, "body": body}
elif mode == "stale":
    d = {"number": 7, "state": "open", "head": {"sha": old}, "body": "body-live\n"}
elif mode == "bad":
    d = {"number": 7, "state": "open", "head": {"sha": head}, "body": "edited by someone else\n"}
elif mode == "closed":
    d = {"number": 7, "state": "closed", "head": {"sha": head}, "body": "body-live\n"}
else:
    d = {}
sys.stdout.write(json.dumps(d))
PY
STUB
chmod +x "$W/bin/curl"
export ARM_DIR="$W" ARM_MODE="$ARM"
export ARM_HEAD=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
export ARM_OLD=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
export ARM_RACE_N=1
export PATH="$W/bin:$PATH"

API=https://api.github.com
ACCEPT='Accept: application/vnd.github+json'
die() { printf 'app_push: REFUSE: %s\n' "$*" >&2; exit 1; }
export APP_PUSH_READBACK_TRIES=$TRIES APP_PUSH_READBACK_SLEEP=$SLEEP
source "$SCR/prod_readback.sh"

T0=$(python3 -c 'import time;print(time.time())')
( confirm_readback "$API/repos/o/r/pulls/7" 7 "$ARM_HEAD" "$W/body.md" ) > "$W/out" 2> "$W/err"
rc=$?
T1=$(python3 -c 'import time;print(time.time())')
echo "ARM=$ARM TRIES=$TRIES SLEEP=$SLEEP rc=$rc reads=$(cat "$W/get-n" 2>/dev/null || echo 0) settles=$(grep -c '^app_push: read-back ' "$W/out") elapsed=$(python3 -c "print(round($T1-$T0,1))")"
sed 's/^/  out| /' "$W/out"
sed 's/^/  err| /' "$W/err"
rm -rf "$W"
