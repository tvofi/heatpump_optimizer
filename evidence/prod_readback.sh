RB_TRIES=${APP_PUSH_READBACK_TRIES:-6}
RB_SLEEP=${APP_PUSH_READBACK_SLEEP:-2}

# One read of the pull request. On stdout, one verdict token:
#   ok            open, head == $2, body identical to $3 modulo one newline
#   stale <sha>   open, but the live head is <sha>, not $2 (the index is behind)
#   body          open at $2, but the body is not byte-identical
#   bad <why>     the API answered a shape this read does not vouch for
#   error <why>   the read could not be performed at all
read_once() { # url head body -> verdict token
  local url=$1 head=$2 body=$3 out
  out=$(curl -fsS -H @"$PRIV/token.h" -H "$ACCEPT" "$url" 2>/dev/null) \
    || { printf 'error curl-exit-%s' "$?"; return 0; }
  printf '%s' "$out" | python3 -c '
import sys, json
head, f = sys.argv[1], sys.argv[2]
try:
    d = json.loads(sys.stdin.read())
except ValueError:
    print("bad unparseable response"); sys.exit(0)
state = d.get("state"); live = (d.get("head") or {}).get("sha") or ""
if state != "open":
    print("bad state=%s" % state); sys.exit(0)
if live != head:
    print("stale %s" % live); sys.exit(0)
want = open(f).read(); got = d.get("body") or ""
# equal, or differing by EXACTLY ONE trailing newline on either side -- the
# measured shape (GitHub appends one; measured 2026-09-18); the both-sides-
# strip form would refuse the measured shape (live == want + "\n") because
# stripping want too hides the difference it exists to allow.
def eq1(a, b):
    return a == b or (a.endswith("\n") and a[:-1] == b) or (b.endswith("\n") and b[:-1] == a)
print("ok" if eq1(got, want) else "body")' "$head" "$body"
}

# The bounded read-back. Returns 0 when the push is confirmed visible; refuses
# (dies) otherwise, naming which of the two failure states it found. The loop
# breaks on the first `ok`, so a push already visible costs one read and no
# sleep. `stale` is the racing case and keeps polling; a `body` mismatch at the
# right sha is settled, not a race, so it refuses at once as before.
confirm_readback() { # url num head body
  local url=$1 num=$2 head=$3 body=$4 attempt=1 v notvisible=0 detail=""
  while :; do
    v=$(read_once "$url" "$head" "$body")
    case "$v" in
      ok) return 0 ;;
      body) die "pull request #$num's body is not byte-identical to $body modulo one trailing newline" ;;
      stale\ *) notvisible=1; detail="the live head is still ${v#stale }" ;;
      error\ *) detail="the read could not be performed (${v#error })" ;;
      bad\ *) detail="the read answered ${v#bad }" ;;
      *) detail="the read answered <<$v>>" ;;
    esac
    [ "$attempt" -lt "$RB_TRIES" ] || break
    printf 'app_push: read-back %s/%s: %s; sleeping %ss\n' "$attempt" "$RB_TRIES" "$detail" "$RB_SLEEP"
    sleep "$RB_SLEEP"
    attempt=$((attempt + 1))
  done
  if [ "$notvisible" = 1 ]; then
    die "pushed $head but the pull request did not read back at it: pushed and not visible within the budget ($RB_TRIES attempts over ~$((RB_TRIES * RB_SLEEP))s; $detail) -- a race GitHub had not indexed, not a refused push; re-read #$num by hand"
  fi
  die "the pull request did not read back at $head and the read was refused ($detail) -- re-read #$num by hand before touching anything"
}

