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
#
# The modes run with the flags the job passes: `--window-cache` is given to a
# mode here only when governance.yml's `record` job gives it to that mode, so a
# cache the job stopped passing reads back as the per-mode cost. It REFUSES
# (rc 1) rather than print a count that measured nothing: a mode that printed a
# failure marker (the enumeration skip, the stats fetch guard, the sunset
# `no friction data`, a dead curl) is partial, and a zero on a window holding
# first-parent commits means the window was never walked (no github remote).
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
COMMITS=$(git -C "$ROOT" rev-list --first-parent --count "$SINCE..origin/main")
# The record job's text, continuation lines joined, so one line per invocation.
JOB=$(awk '/^  record:/{on=1;next} on&&/^  [a-z][a-z-]*:/{exit} on' "$ROOT/.github/workflows/governance.yml" | sed -e ':a' -e '/\\$/N; s/\\\n//; ta')
total=0
for mode in record stats sunset; do
  : > "$WORK/$mode.log"
  cache=()
  # Every invocation of the mode (the job keeps a `.claude/workflows` arm beside
  # the live one) must carry the flag before the harness passes it.
  calls=$(grep -oE -- "--$mode[[:space:]]+--since [^;|]*" <<<"$JOB" || true)
  if [ -n "$calls" ] && ! grep -v -q -- '--window-cache' <<<"$calls"; then cache=(--window-cache "$WORK/window.json"); fi
  (cd "$ROOT" && CURL_LOG="$WORK/$mode.log" PATH="$WORK/bin:$PATH" GITHUB_TOKEN=stub \
    node tools/policy/policy_lint.mjs "--$mode" --since "$SINCE" "${cache[@]}" > "$WORK/$mode.out" 2>&1) || true
  n=$(wc -l < "$WORK/$mode.log" | tr -d ' ')
  if grep -qE 'curl failed|merge-enumeration|could not fetch pull-request|no friction data' "$WORK/$mode.out"; then
    echo "record_api_calls: --$mode printed a failure marker under the stub; its count is partial:" >&2
    grep -E 'curl failed|merge-enumeration|could not fetch pull-request|no friction data' "$WORK/$mode.out" | head -3 >&2
    exit 1
  fi
  echo "--$mode $n call(s) over $SINCE..origin/main${cache[*]:+ (--window-cache, as the job passes it)}"
  total=$((total + n))
  if [ "$mode" = record ] && [ "$n" -eq 0 ] && [ "$COMMITS" -gt 0 ]; then
    echo "record_api_calls: --record read 0 over $COMMITS first-parent commit(s); the window was not walked" >&2
    exit 1
  fi
done
echo "TOTAL $total call(s) per push to main, before policy-docs, env-matrix and the other jobs"
