#!/bin/bash
set -euo pipefail
API=https://api.github.com; ACCEPT='Accept: application/vnd.github+json'; repo=tvofi/heatpump_optimizer; cid=6371729358
idir="${HPO_IDENTITY_DIR:-$HOME/.zcode}"; appid=$(cat "$idir/identity-approver.appid"); key="$idir/identity-approver.pem"
[[ $appid =~ ^[0-9]+$ ]] && [ -s "$key" ]
umask 077; PRIV=$(mktemp -d); trap 'curl -fsS -X DELETE -H @"$PRIV/token.h" -H "$ACCEPT" "$API/installation/token" >/dev/null 2>&1 || true; rm -rf "$PRIV"' EXIT
b64() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }
now=$(date +%s); h=$(printf '{"alg":"RS256","typ":"JWT"}'|b64); p=$(printf '{"iat":%d,"exp":%d,"iss":"%s"}' $((now-60)) $((now+540)) "$appid"|b64)
s=$(printf '%s.%s' "$h" "$p" | openssl dgst -sha256 -sign "$key" -binary | b64)
printf 'Authorization: Bearer %s.%s.%s\n' "$h" "$p" "$s" > "$PRIV/jwt.h"
inst=$(curl -fsS -H @"$PRIV/jwt.h" -H "$ACCEPT" "$API/repos/$repo/installation" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
curl -fsS -X POST -H @"$PRIV/jwt.h" -H "$ACCEPT" "$API/app/installations/$inst/access_tokens" | python3 -c 'import sys,json;open(sys.argv[1],"w").write("Authorization: Bearer %s\n"%json.load(sys.stdin)["token"])' "$PRIV/token.h"
python3 -c 'import sys,json;json.dump({"body":open(sys.argv[1]).read()},open(sys.argv[2],"w"))' new.md "$PRIV/c.json"
curl -fsS -X PATCH -H @"$PRIV/token.h" -H "$ACCEPT" "$API/repos/$repo/issues/comments/$cid" --data-binary @"$PRIV/c.json" | python3 -c 'import sys,json;d=json.load(sys.stdin);print("PATCHED",d["id"],d["user"]["login"])'
