#!/bin/bash
# 300 s loop, 90 min. Relays coordinator-fired reviewers when their probe ref appears; checks rows for 2557/2558.
D=/Users/timmalmstrom/hpo-orch/r10s4
R=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt
export PATH="$R/tools/audit/seat/shims:$PATH"
cd "$R" || exit 1
LOG=$D/coord-loop.log
DONE=$D/coord-loop.done
touch "$DONE"
END=$(( $(date +%s) + 5400 ))
# pr nonce head
TARGETS="2559 d63af2393eeaa21f6c75c7b3e356a3b6 39f465739706edd44c7446a7cdebc0e0c5b30091
2531 a7f748b64d36d03677e8c6487ff5cf32 708927198d91ca8cfbc79d1843cf401904782d6d
2560 fa6eb2e975611e9aca353f4d9f00ea4d 085a4cafa84022120460fd23701a21883321536f
2548 2246ae046f7e4d4683a374de41c516aa f2f204fc3ed608a69b56ee9ebc0c2eee23e74dc1
2529 5a067b503faa6da9926b251336626c65 044edcc2b32ef6fb9172b79bfc169c7beeb0dc38
2563 4781a1280f18f8b3240d780b7dc421bf 829ea7c7238d62293a58bb9d9625e844ac7fd09d
2567 68a19d6bd6420145d20641357a1b572a 93015ecada7190edc054e49a47538704b14e1f34
2559 a8bfe1057ec1aa34a14f6aae1d415383 5756617f185bbed71852ed1273c19b1e45787c9d
2527 3417d19a57ee47d2124a34be56bab9b1 d809c1f30f02b417dfd2d29ac5a98b6dd2803a55
2560 6abf0de1f258dffa046f06ddd148adc0 2108fcb09ef16a53119dedb8b731bd89f0fea0ad
2559 a3eee38c3144cc46f38b3f801f78f093 2e77ed3e6aa2f03565bd02274ac847227bc619b5
2521 7b4fa5ee6cfb88d3dab2c78e78093b49 a85e97a7325fc48767ba5abb1ec4c6fb92506939
2524 1253d5aed794d2d9b104a3b1dd1921e3 c071fa5f37abdac0da2284547b9282549eb4d607
2528 6f43192ea7aa130e69cbd1ebe0306a7b b18052f664039d36da73ef745a2a8423f82d2c46
2567 add37b67f64bb470070faa4b0f8e06af f16956542b2c4470de5a3e12fc843f97cef1840e
2571 4754a76a2b269a20cfbe6c86d9b4e3a8 90788b1e5ea8ce015e7ae6c432d308d7a5aab476
2570 30159a7900c7363a6498f101d0bf8479 4a97526f61d754a4e833882d1fe2f8344ccae973
2559 8ddeb923d0afccbb941906ea350d89f1 802b38503eb5de20e87c278ba7923508a50c0f1f
2569 277db9ac1c42a10b967e4edadf5a17d4 5ffbaaaeb827f184ed44abd9ead267ee8e626b08
2569 060a085f4ed98e9def007eee9b4aa4d7 8c008227a25192fc542bca64abbd4098a2862d1a
2549 347dd5f47f9a56ca94bb88316fc66043 61fd4f27cbd3e3e3eb092044b6e55fa24028683f
2572 cecf419ef61f5daf10cddb3679e265ca 441d19932f40475ddc0420f3b67ba8d90202eb2c
2575 393597344df1a6c95b4c1280a13dcad9 ea5f660303823ce04ed55af4022b4f7064ee403e
2578 d495ed9002400d88ebb148c78bead593 3f22a805c7ca335f15a6b218d6aa15a7cec8bb20
2529 6a90cc3dbdedf45b14fd822bc8d7958d 8f026328dd45d8113e05c51c64038fa47a3a4b67
2580 d81197b47dc8c4f3a8b76b9d08ceb8b3 a8a2778e155e0f13527ec2864f856d8ddd942e31
2580 6ed39626378f4923fe2e58ee0552fedb a54aed8b9e756aaa47ea18e9a13bf33a06878a0b
2576 4e030b94445cb86f87f436bd597d7054 fe1365f0f992b1d53d79c8e0a1d94804a74f53d8
2547 c2c5075c4ebcb40ffb1e164a8ee4f777 90bab078d19dd6aebba140fa360576b7780a560a
2576 4942e7460eab68db29c0ef60597171a3 1ebbae78756a3802009081f1fd5a1df4918e7ee5
2567 cdda16118cf7b9ea9ddfcd538c68d6d3 4ef1a8270f3bd30bc6c313c950f6f44713a1442d
2576 71d2e101ef8e59ecfb4f697cd84adb00 df70cb6bca69c7b1717abcc317233ff1bc994df3
2567 7d363d3179d4917c247b34f2a4fb0303 54bf182104e450c0ac2e6eb007da59b9315e0565
2528 b5c87533bd83cca7b8de279dd5a2019d 5332c59f9b5e883d1b1638a6f310fbc7237bdaa9
2578 a40c3488651515a962e45d98fbdbf21c 50c4a681d0e3bee30e415a1ecc663ff5eab158f8
2563 4004edbfe5086f63375b4065c95e4a1d 9851d39de867653f4fdc4412c3a1eea8dcb5f7b3
2571 aa42fa3468a15c64be454da5c30aa04d cb48de247b39b47ffe9e010689f8ff4f971b7e32"
ROWS="2557 fix/r10-rca-orch-continuity 01d7ac8c75533bf9e4eff9cbc73d5205a65d6f1f
2558 fix/r10-plan-artifact 43b1307e5db4f6959e2705fff38afea38a137f75"
# pr nonce8 head: the full nonce is needed by cloud_relay; the 8-char ref name is matched
while [ ! -f "$D/coord-loop.stop" ]; do
  now=$(date -u +%H:%M:%SZ)
  refs=$(git ls-remote origin 'refs/heads/probe/rev-*' 2>/dev/null)
  echo "$TARGETS" | while read pr nonce head; do
    [ -z "$pr" ] && continue
    grep -q "^$pr $head" "$D/coord-loop.done" 2>/dev/null && continue
    if echo "$refs" | grep -q "probe/rev-$pr-${nonce:0:8}\$"; then
      out=$(bash tools/audit/seat/cloud_relay.sh --confirm "$pr" "$nonce" "$head" 2>&1); rc=$?
      echo "$now relay $pr nonce=$nonce head=${head:0:8} rc=$rc: $(echo "$out" | grep -E 'POSTED|OWED|refus|REFUS|cloud_relay' | tail -2 | tr '\n' ' ')" >> "$LOG"
      if [ $rc -eq 0 ]; then
        first=$(gh pr view "$pr" --repo tvofi/heatpump_optimizer --json comments --jq '[.comments[] | select(.body|startswith("Fix review:"))] | last | .body' 2>/dev/null | head -1)
        echo "$now verdict $pr: $first" >> "$LOG"
        echo "$pr $head" >> "$DONE"
      else
        echo "$now REFUSED $pr head=${head:0:8}: report to main, not retried" >> "$LOG"
        echo "$pr $head" >> "$DONE"
      fi
    fi
  done
  echo "$ROWS" | while read pr br head; do
    [ -z "$pr" ] && continue
    grep -q "^row-$pr" "$DONE" 2>/dev/null && continue
    cur=$(git ls-remote origin "refs/heads/$br" 2>/dev/null | cut -f1)
    git fetch -q origin "$br" 2>/dev/null
    if git cat-file -e "$cur:dev/programme/delivery/$pr.md" 2>/dev/null; then
      echo "$now ROW-LANDED $pr at ${cur:0:8}" >> "$LOG"; echo "row-$pr" >> "$DONE"
    fi
  done
  hb=$(git ls-remote origin refs/heads/handoff-body/r10-row-only-update 2>/dev/null | cut -f1)
  if [ -n "$hb" ] && ! echo "$hb" | grep -q '^b2f83c79'; then
    grep -q "^handoff-moved $hb" "$DONE" 2>/dev/null || { echo "$now HANDOFF-MOVED handoff-body/r10-row-only-update from b2f83c79 to ${hb:0:8}" >> "$LOG"; echo "handoff-moved $hb" >> "$DONE"; }
  fi
  nf=$(git ls-remote origin refs/heads/handoff-body/r10-night-folds 2>/dev/null | cut -f1)
  if [ -n "$nf" ] && ! echo "$nf" | grep -q '^070c5cb4'; then
    grep -q "^handoff-moved $nf" "$DONE" 2>/dev/null || { echo "$now HANDOFF-MOVED handoff-body/r10-night-folds from 070c5cb4 to ${nf:0:8}" >> "$LOG"; echo "handoff-moved $nf" >> "$DONE"; }
  fi
  ph=$(git ls-remote origin refs/heads/fix/r10-row-only-update 2>/dev/null | cut -f1)
  if [ -n "$ph" ] && ! echo "$ph" | grep -q '^f1695654'; then
    grep -q "^pr-head-moved $ph" "$DONE" 2>/dev/null || { echo "$now HEAD-MOVED fix/r10-row-only-update (PR 2567) from f1695654 to ${ph:0:8}" >> "$LOG"; echo "pr-head-moved $ph" >> "$DONE"; }
  fi
  echo "$now tick" >> "$LOG"
  sleep 300
done
echo "$(date -u +%H:%M:%SZ) END 90 min" >> "$LOG"
