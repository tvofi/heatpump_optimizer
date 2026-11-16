# BLOCKED: r11-pre-relay-rebuild part 1 is already on main

Question: part 1 of R11-PRE-RELAY-REBUILD (carries 0-4) merged as PR #3648 at 315dda8f629fdb0da523ce4866f4a50f68fac80e, an ancestor of this dispatch's base 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c; this dispatch (465223a768, re-rendered as e75d1ec829) still says "Part 1 of 3: build carries 0-4". Should this seat be re-dispatched as part 2 (carries 5-12), or is the part counter on the roster to be advanced first?

Evidence, each a command at origin/main 367c3b9cac:
- `git merge-base --is-ancestor 981cad4189 origin/main` succeeds: the last handoff/r11-pre-relay-rebuild head is on main.
- `git log --first-parent origin/main | grep relay-rebuild` returns 315dda8f62 "Merge pull request #3648 from tvofi/fix/r11-pre-relay-rebuild".
- Carry 0: `git grep -n handoff-skipped origin/main -- tools/audit/seat/cloud_relay.sh` (level_set handoff-skipped; self-test rows "never skipped in silence (#3358)").
- Carry 1: tools/audit/seat/tick_loop.sh `mut:branchrestart` (checkout -q -B on a clean branch-backed checkout) and the "-> OWED relay-skipped ... (stale <k> consecutive passes)" board line with its one-pass null control.
- Carry 2: tick_loop.sh `relay_gap_sleep` with HPO_TICK_RELAY_GAP and its in-flight null-control row.
- Carry 3: cloud_relay.sh self-test rows "the dispatch's verdict refused by the relay releases HELD-REVIEW" and "disposed releases HELD-REVIEW too".
- Carry 4: cloud_relay.sh `owed_red_text` (`mut:owedred`) with its null control "a PREDICTOR refusal naming no owed red adds no text".

No code built and no code ref pushed: rebuilding merged carries would duplicate main.
