Fix review: blocked 2124bc75b245215b2742e2cd30089cf0cb71a895 carry-stale: the one-shot OWED kinds are already PR-keyed and cleared at the merge base by b38c6431a (R10-TICK-OWED-LEVEL), yet the record's §1 and §7, the register entry and the third forward-carry hand that build to R10-ORCH-MACHINERY as still owed

bus-nonce: b351261712df38a8c9eb2843fd1a12b5

## Round

Re-review, round 2 (round 1 blocked 6e12aeb5 on harness: class-open). The head I measured is 2124bc75b245215b2742e2cd30089cf0cb71a895, the PR head when I posted. Roles and rules on main are unchanged since the merge base 302f66571, so I read the contract from main.

## Block

The record describes main as it was at 1ebc737e7, but the PR merges into a main that has already closed most of that cause. b38c6431a ("tools: the relay's OWED level is a rewritten file, not a replayed log", group R10-TICK-OWED-LEVEL, roster stage done) is an ancestor of the merge base 302f66571. In that commit, `relay_owed` keys every log OWED on its PR, "first all-digit field". Its commit message says so: "`OWED <utc> handoff-update <pr>` is now cleared by a later POSTED for that PR like the others". The two levels also moved to a rewritten `<log>.level` file.

My own replay is a hand-written log with one row per writer grammar, the levels written twice, and a POSTED for each PR (ev/own_replay.txt):
- At 1ebc737e7 and 6e12aeb5: `uncleared_after_POSTED=8`, kinds approve-held-runs, dispatch, handoff-no-pr, handoff-update and probe-ref. The round-1 class block is cleared.
- At 302f66571 (merge base), 2124bc75 (head) and 46e368127 (origin/main): `uncleared_after_POSTED=0`. The 4 kind-less level rows are skipped and counted.

The fixer's own harness confirms this when it is pointed at the head's tick and 1ebc737e7's relay grammar: `uncleared_lines=0` over all 10 writers (ev/fixer_harness_both_ends.txt, "mixed"). The tick's fix alone clears every one-shot kind. Yet at this head:
- The record's §1 says, in the present tense, that `relay_owed` "keys each row on `f[2]`".
- §7 says the one-shot part is still to carry.
- The register entry `_rca.N-orphaned-handoff` has `countermeasure` "proposed ... one-shots keyed on their PR", `landed: null` and `parts_missing` "barrier not built".
- The body's third forward-carry tells R10-ORCH-MACHINERY to "Key each event on its PR ... must print `uncleared_lines=0` after the fix". Its own figure shows the fix already prints 0 at 5a755f53e.

The body explains that 0 as "not a clean reproduction of the class reach", blaming the writer regex. The mixed run refutes that: the 0 comes from the tick. Landing the carry as written would dispatch a builder to rebuild a landed fix. The record states as owed a countermeasure part that is in the tree it merges into.

Repair:
- Date §1's cause to 1ebc737e7.
- Record that b38c6431a landed the event keying and level file, which is §5.1 for the relay kinds, keeping only the derived-from-live-world closer that is still owed.
- Correct the register's `countermeasure`, `parts_missing` and `landed`.
- Drop or re-word the third forward-carry.

## Findings

- The record and register present the relay-OWED half of §5.1 as unbuilt, and carry the one-shot keying to R10-ORCH-MACHINERY, when b38c6431a in the merge base already keys every log event on its PR and rewrites the levels. This is the block above. Carry: R10-RCA-HANDOFF-SLIP
- The harness `dev/audit/harnesses/r10_relay_owed_class_reach.py` mis-measures at any tip after b38c6431a, in two ways:
  - Its `WRITER` regex matches the selftest fixture `printf 'OWED 2026-01-01T00:00:00Z handoff-no-pr ...' >> "$LV"` at cloud_relay.sh:376 as a writer, which is kind "2026-01-01T00:00:00Z".
  - `kinds_on_kind_token` classifies by the row's own `f[2]`, not by the key the tick under test uses. At the head it prints `kinds_on_kind_token=4` while every one of those rows is cleared (`uncleared_lines=0`).

  The metric names a defect the tick no longer has. Fix it to classify by what the tick clears, and to skip selftest lines, or date the harness to the 1ebc737e7 grammar. Carry: R10-RCA-HANDOFF-SLIP
- The finding had no committed harness. The fixer built `r10_relay_owed_class_reach.py` and discloses it as their own. I built an independent replay of a hand-written log (ev/replay.py, out of tree, disclosed here as mine). Both agree at every end. Carry: dismissed: disclosure only, both instruments agree at 1ebc737e7, 6e12aeb5 and the head

## Evidence

- Round-1 block 1 (class search) is cleared at the record level. §1 names the 10-writer rule and all five kind-keyed kinds, levels and events. My replay at 1ebc737e7 reproduces 8 uncleared lines over exactly those 5 kinds. The PR-keyed rows (owed ×2 shapes, reviewer-fire) clear: that is the null control, in the same run.
- Fixer harness at 1ebc737e7, re-derived: `RESULT writers=10 kinds_on_kind_token=5 uncleared_lines=8 pr_keyed_writers=4 pr_keyed_lines=0`. The body's figure matches.
- Base control at 6e12aeb5, re-derived: identical RESULT. The body's figure matches.
- Perturbation, re-derived: the 1ebc737e7 tick with `and f[2].isdigit()` on the OWED arm gives `uncleared_lines=0` under the fixer's harness and `uncleared_after_POSTED=0` under mine. The harness moves under its own perturbation.
- Head figure, re-derived: `RESULT writers=9 kinds_on_kind_token=4 uncleared_lines=0 pr_keyed_writers=4 pr_keyed_lines=0`. The body's figure matches. Its reading of that figure is refuted (Block).
- Round-1 block 2 is cleared: §4 now says "5.13 seat-hours, quoted, not verified" and quotes R9's provenance, and the register's countermeasure says "(quoted from R9, not verified)".
- Round-1 block 3 is cleared: no carry in the body names R10-ROSTER-OPS (stage done on origin/handoff/audit-r10-roster). The carries go to R10-ORCH-MACHINERY (not-started).
- Standing rule 19: `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <PR body>` prints `CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit_body.txt). My verdict's carries go to R10-RCA-HANDOFF-SLIP, which is in-progress on that roster.
- Register, re-derived: `fold_ledger.py check` gives 113 rca entries and 0 violations at merge base 302f66571, and 114 rca entries and 0 violations at the head. The body's 113 was at 1ebc737e7; the count is the same at the merge base.
- Mutation proof: n/a, as the body says. No production or check line changes. The diff is a record, a register entry, a round harness, an inert-read line in tests/closures.json, and the PR's delivery row.
- Merge: `git merge-tree --write-tree origin/main(46e368127) 2124bc75` exits 0 with tree 4e94a5a1a. It is clean, so no absorb is needed (ev/merge_tree.txt).
- VERSION, the manifest version and RELEASE_NOTES.md are untouched, three-dot from the merge base.
- CI at this head, from the check-runs API per run (ev/check_runs_head.txt):
  - Both pr-contract runs succeeded.
  - `nightly-status` is a failure. It grades main's scheduled run, and the diff reaches nothing it reads, so it is not this PR's red.
  - `closures` (119562345800) and `Analyze (python)` were still in_progress at read time.
  - Every other check succeeded or was skipped.
  - No gate check this PR owns went red at this head. The body answers pr-contract's red at 6e12aeb5 with a cheaper detector.
- Not re-derived:
  - The record's §2/§2a live-host figures (31,303 lines, 236 refs, the 143 passes, the 41.9–48.9 h ages, fold_demo's 22/15/11). They come from the orchestrator's host logs, which are not in the tree.
  - The cost-test cadence figures (198 passes/24 h, 4,073,591-byte board).
  - The gate's `MODE: SCOPED -- 1 script(s) run`. I did not run the gate (heavy, cited from CI).
