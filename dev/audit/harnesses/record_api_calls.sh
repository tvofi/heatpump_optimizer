#!/bin/bash
# record_api_calls.sh [SINCE] -- the REST calls Governance's `record` job makes
# on one push to main, counted offline (dev/audit/rca/install-ratelimit.md).
#
#     bash dev/audit/harnesses/record_api_calls.sh            # window = last v* tag
#     bash dev/audit/harnesses/record_api_calls.sh v7.0.1     # a wider window
#
# Runs the three policy_lint.mjs modes the job runs (--record, --stats,
# --sunset) over SINCE..origin/main with a stub `curl` first on PATH that logs
# each URL and answers a well-formed empty 200, so no request leaves the host
# and no token is spent. Prints one line per mode and the total. The stub
# answers `/commits/<sha>/pulls` with [], so the merges are recovered from their
# "Merge pull request #N" subjects (the GAP line) -- the same PR set the API
# arm resolves on this repository, so the per-PR reads count the same.
# The count is the job's real call count while the job reads through `ghGet`;
# a fix that shares one window walk across the modes moves the total, a null
# control (an empty window, SINCE=origin/main) reads 0.
set -euo pipefail
ROOT=$(git rev-parse --show-toplevel)
SINCE=${1:-$(git -C "$ROOT" describe --tags --abbrev=0 --match 'v*' origin/main)}
WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
mkdir "$WORK/bin"
cat > "$WORK/bin/curl" <<'EOF'
#!/bin/bash
cat >/dev/null
url="${@: -1}"; echo "$url" >> "$CURL_LOG"
case "$url" in
  */pulls/[0-9]*/reviews*|*/issues/*/comments*|*/commits/*/pulls) printf '[]\n200' ;;
  */pulls/[0-9]*) printf '{"body":"","title":"x","user":{"login":"a"}}\n200' ;;
  *) printf '{}\n200' ;;
esac
EOF
chmod +x "$WORK/bin/curl"
total=0
for mode in record stats sunset; do
  : > "$WORK/$mode.log"
  (cd "$ROOT" && CURL_LOG="$WORK/$mode.log" PATH="$WORK/bin:$PATH" GITHUB_TOKEN=stub \
    node tools/policy/policy_lint.mjs "--$mode" --since "$SINCE" > "$WORK/$mode.out" 2>&1) || true
  n=$(wc -l < "$WORK/$mode.log" | tr -d ' ')
  if grep -q 'curl failed' "$WORK/$mode.out"; then echo "record_api_calls: --$mode aborted under the stub; its count is partial" >&2; exit 1; fi
  echo "--$mode $n call(s) over $SINCE..origin/main"
  total=$((total + n))
done
echo "TOTAL $total call(s) per push to main, before policy-docs, env-matrix and the other jobs"
