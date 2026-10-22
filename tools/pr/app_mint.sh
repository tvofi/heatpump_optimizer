# app_mint.sh -- the `hpo-author` App's token mint, sourced by the scripts that
# write to GitHub as that App: app_push.sh (push, open, re-body) and
# tools/audit/seat/body_patch.sh (re-body alone). One mint, so a change to how a
# token is signed, held or revoked is made once. SOURCED, never run: no shebang,
# no `set`, no exit of its own. The sourcing script defines `die` (a function
# that exits) and `ACCEPT` and `API` before it calls anything here.
#
#   mint_identity            reads $HPO_IDENTITY_DIR/hpo-author.{appid.txt,pem}
#                            (default directory ~/.zcode); sets MINT_APPID and
#                            MINT_KEY. Fails closed, before any call, when the id
#                            file is not digits only or the key is missing.
#   mint_token <owner/repo>  makes the mode-700 private directory PRIV, writes the
#                            JWT and the installation token as mode-600 curl
#                            header files there (jwt.h, token.h), and installs the
#                            EXIT trap `mint_cleanup`. Never on a command line.
#   mint_cleanup             revokes the installation token and removes PRIV.
#
# The secrets rules are app_push.sh's header: the JWT and token live only in
# header files inside PRIV, and the trap revokes the token on every path.

mint_cleanup() {
  if [ -s "${PRIV:-}/token.h" ]; then
    curl -fsS -X DELETE -H @"$PRIV/token.h" -H "$ACCEPT" "$API/installation/token" >/dev/null 2>&1 \
      || printf '%s: warning: revoking the installation token failed; it expires within the hour\n' "${MINT_NAME:-app_mint}" >&2
  fi
  [ -z "${PRIV:-}" ] || rm -rf "$PRIV"
}

mint_identity() {
  local idir="${HPO_IDENTITY_DIR:-$HOME/.zcode}"
  local appid_f="$idir/hpo-author.appid.txt"
  MINT_KEY="$idir/hpo-author.pem"
  [ -s "$appid_f" ] || die "App id file missing or empty: $appid_f (fail closed)"
  [ -s "$MINT_KEY" ] || die "App private key missing or empty: $MINT_KEY (fail closed)"
  MINT_APPID=$(cat "$appid_f")
  [[ $MINT_APPID =~ ^[0-9]+$ ]] || die "App id file must hold digits only: $appid_f (fail closed)"
}

mint_token() { # owner/repo -> PRIV with jwt.h and token.h
  local repo=$1 now h p s inst
  umask 077
  PRIV=$(mktemp -d "${TMPDIR:-/tmp}/${MINT_NAME:-app_mint}.XXXXXX") || die "could not create a private directory"
  trap mint_cleanup EXIT
  trap 'exit 130' INT TERM HUP
  # SIGKILL is the one signal no trap catches: a kill -9 mid-push can leave the token file in $PRIV, and the backstop is the one already documented -- the token expires within the hour.
  chmod 700 "$PRIV"
  b64() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }
  now=$(date +%s)
  h=$(printf '{"alg":"RS256","typ":"JWT"}' | b64)
  p=$(printf '{"iat":%d,"exp":%d,"iss":"%s"}' $((now - 60)) $((now + 540)) "$MINT_APPID" | b64)
  s=$(printf '%s.%s' "$h" "$p" | openssl dgst -sha256 -sign "$MINT_KEY" -binary | b64) && [ -n "$s" ] \
    || die "signing the App JWT with $MINT_KEY failed"
  printf 'Authorization: Bearer %s.%s.%s\n' "$h" "$p" "$s" > "$PRIV/jwt.h"
  inst=$(curl -fsS -H @"$PRIV/jwt.h" -H "$ACCEPT" "$API/repos/$repo/installation" \
    | python3 -c 'import sys,json; print(int(json.load(sys.stdin)["id"]))') \
    || die "the App has no installation on $repo, or its JWT was refused"
  curl -fsS -X POST -H @"$PRIV/jwt.h" -H "$ACCEPT" "$API/app/installations/$inst/access_tokens" \
    | python3 -c 'import sys,json
t = json.load(sys.stdin)["token"]
open(sys.argv[1], "w").write("Authorization: Bearer %s\n" % t)' "$PRIV/token.h" && [ -s "$PRIV/token.h" ] \
    || die "minting the installation token failed"
  chmod 600 "$PRIV/token.h" "$PRIV/jwt.h"
}
