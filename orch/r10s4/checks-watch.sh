#!/bin/bash
# Every 300 s, per PR: read head (gh pr view), then check-runs (gh api) at that head.
# CHECKS-GREEN when no check is pending and no non-nightly-status check failed. CHECKS-RED on a non-nightly failure.
# HEAD-MOVED when a watched PR's head leaves its baseline. Writes to coord-loop.log.
D=/Users/timmalmstrom/hpo-orch/r10s4
R=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt
LOG=$D/coord-loop.log
DONE=$D/checks-watch.done
touch "$DONE"
cd "$R" || exit 1
# pr baseline-head-for-move (empty = no move watch) ; checks run for every pr listed
WATCH="2569 5ffbaaaeb827f184ed44abd9ead267ee8e626b08
2570 4a97526f61d754a4e833882d1fe2f8344ccae973
2549 61fd4f27cbd3e3e3eb092044b6e55fa24028683f
2559 802b38503eb5de20e87c278ba7923508a50c0f1f
2572 441d19932f40475ddc0420f3b67ba8d90202eb2c
2567 54bf182104e450c0ac2e6eb007da59b9315e0565
2563 baa01ed856c09c1a9ac2222ee2177d783b0d7317
2575 ea5f660303823ce04ed55af4022b4f7064ee403e
2577 6684dee65832c7b8e822f8ee0b33fd3f627b54ed
2528 5332c59f9b5e883d1b1638a6f310fbc7237bdaa9
2578 3f22a805c7ca335f15a6b218d6aa15a7cec8bb20
2579 468781122d076f5396f4a27c171b78f64f1c5537
2580 a54aed8b9e756aaa47ea18e9a13bf33a06878a0b
2529 8f026328dd45d8113e05c51c64038fa47a3a4b67"
while [ ! -f "$D/coord-loop.stop" ]; do
  echo "$WATCH" | while read pr base; do
    [ -z "$pr" ] && continue
    h=$(gh pr view $pr --repo tvofi/heatpump_optimizer --json headRefOid --jq .headRefOid 2>/dev/null)
    [ -z "$h" ] && continue
    now=$(date -u +%H:%M:%SZ)
    if [ "$h" != "$base" ]; then
      grep -q "^moved $pr $h" "$DONE" || { echo "$now HEAD-MOVED $pr from ${base:0:8} to ${h:0:8}" >> "$LOG"; echo "moved $pr $h" >> "$DONE"; }
    fi
    st=$(gh api "repos/tvofi/heatpump_optimizer/commits/$h/check-runs?per_page=100" --jq '[.check_runs[]] | group_by(.name) | map(max_by(.started_at)) | .[] | [.name,.status,(.conclusion // "null")] | @tsv' 2>/dev/null)
    pending=$(echo "$st" | awk -F'\t' -v skipq="$pr" '$1!="" && $2!="completed" && $1!="wave-script"' | wc -l | tr -d ' ')
    red=$(echo "$st" | awk -F'\t' '$1!="nightly-status" && $1!="" && $3!="success" && $3!="skipped" && $3!="neutral" && $3!="null"' | head -3 | tr '\n' ' ')
    if [ "$pending" = "0" ] && [ -z "$red" ]; then
      grep -q "^green $pr $h" "$DONE" || { echo "$now CHECKS-GREEN $pr $h (required checks but nightly-status concluded green)" >> "$LOG"; echo "green $pr $h" >> "$DONE"; }
    elif [ -n "$red" ]; then
      grep -q "^red $pr $h" "$DONE" || { echo "$now CHECKS-RED $pr $h: $red" >> "$LOG"; echo "red $pr $h" >> "$DONE"; }
    fi
  done
  sleep 300
done
