Fix review: merge 43221bf168c3dc657a5dbe5baa33652fec6b35a8
bus-nonce: 51c9da83ff518feb7cbc2babb0696ed5

Round 2 — the re-cut of review round 1's single blocking class (B1). Measured at head `43221bf168c3dc657a5dbe5baa33652fec6b35a8`, re-read live immediately before publishing: still the head, `mergeStateStatus: BLOCKED` only by `REVIEW_REQUIRED`; `git merge-tree --write-tree origin/main <head>` exit 0 with no `MERGE-CLAIM:` marker (the branch touches neither claim file) (`evidence/merge-tree.txt`). My detached worktrees: `wt-head` at the head, `wt-before` at the reviewed head `88b452c6a`, `wt-base` at the merge base `a0e7664ea`, `wt-mut` for the mutants. Three-dot diff from `a0e7664ea` is exactly two files, +151/-1: `tools/audit/seat/roster_sync.py` and `dev/programme/delivery/2889.md`. The one-commit delta `88b452c6a..43221bf16` is `roster_sync.py` only, `130+/36-` (`evidence/diff.txt`).
Carry: dismissed: the verdict's own scope statement, no downstream work

## The re-cut, measured end to end

**B1 is repaired, and the fix is test-pinned.** The finder's harness for B1 (the predecessor review's `~/hpo-seats/r10s6/review-2889/ev/driver.py`, out of tree) run verbatim at `88b452c6a` prints `e_two_rows_one_held: appends=[]` with two refusals, `e_finding_two_lost: True`, and `f_null_control_both_append: True` (`evidence/finder-harness-verbatim.txt`). `carried_from` no longer exists at the head, so the same construction is run there by my adapted copy (`evidence/driver.py`; adapted only in the unit-level predicate calls, the end-to-end `roster`/`BODY`/`plan` construction byte-identical and disclosed as adapted): two appends, `refusals=[]`, `e_finding_two_lost: False`, `e_both_distinct_findings_survive: True`, null control still `True` (`evidence/before.txt`, `evidence/after.txt`). Reintroducing the PR-number key reddens 8 self-test checks including both `(B1)` arms, the prose arms and the `#1525` null control (mutant D); deleting the whole call+refusal block reddens 4, the ruling arm 3, the text arm 2 — the body's `4/3/2` reproduced; restore is byte-identical (`sha256 46725beb…`, blob `b9f0e765…`) (`evidence/mutation.txt`).
Carry: dismissed: re-derived at both ends with the null control

**The predicate's edges, each driven.** `#1525` does not suppress `#15` (`e_1525_is_not_15`, `c_other_pr_named_appends`); a second, genuinely different finding from one PR appends (`b_ii_same_pr_distinct_finding_survives`); one finding in different words appends (disclosed, and live on #2625 — N6); shared boilerplate alone does not collapse (`edge_boilerplate_only_appends`); a held carry's unparseable ruling key still matches a row spelling the same key, and with no held match the row appends and the triage gate refuses it (`unresolvable_*` arms) — the residual livelock shape, disclosed. The two channels that can collapse distinct findings are a shared ruling key (N4) and `MARKUP` deleting `_`/`*` (N3).
Carry: R10-ORCH-ROSTER-SCHEMA

**The recorded livelock, live.** `#2625`'s body against the live r10 roster: before, both rows refused by `carried_from(..., 2625)` on a carry that merely names `#2625`; after, item `46c8c550` (the P3 row) `REFUSED` by the `triage P3 (s4)` ruling, item `309b9984` appended, and `triage_refusal` over the appended row returns `None` (`evidence/live2625.txt`).
Carry: dismissed: re-derived on the live body

**Refusal placement, print and non-abort.** The refusal is appended in `carry_plan` (`tools/audit/seat/roster_sync.py:482`) before `apply_plan` (`:570`) and before the write path's `triage_refusal` (`tools/audit/seat/roster_edit.py:643`); it prints `roster_sync: REFUSED Carry:` at `roster_sync.py:588`; it never raises, and the self-test's `apply rc 0` / `apply pushes once` (`:982-983`) pin the non-abort — mutant A reddens them by letting the duplicate reach the gate (`evidence/refusal.txt`, `evidence/mutation.txt`). No row is dropped silently: each refusal is printed with its destination and source PR.
Carry: dismissed: source-read plus the self-test's apply arm

**P ids are unique within each round, re-derived from the tree.** `## P<n>:` headings: s4 4/4, s5 37/37, s6 169/169, zero duplicates at this head (`evidence/pid_unique.txt`). What happens if it stops being true is N5.
Carry: dismissed: re-derived from the tree

**The rest of the claimed figures.** self-test 68→74 (`evidence/selftest.txt`); `MODE: SCOPED -- 1 script(s) run, 32 scoped out`; `STRUCTURE RATCHET PASSED`; `layout self-test: ok`; `ALL 117 closure shrink pins PASSED`; `claims hygiene: a0e7664ea648 ok`; 692 carries / 88 parseable-ruling / 396 naming a PR; exactly 1 destination holds two differently-worded carries sharing a ruling; `CARRY-AUDIT #2889: 2 routed, 0 unrouted` (`evidence/live.txt`, `evidence/carry-audit.txt`). `tests/entities.py` was **not** re-run — it queued on the shared `gate_lock` behind another seat and I released it rather than contend; `ALL 2467 ENTITY CHECKS PASSED` is therefore not verified by me.
Carry: dismissed: cheap figures re-derived; entities is CI's heavy run

## Non-blocking, each measured (no live defect remains)

**N1 — the ruling-key grammar population is narrower than the body says.** `tools/audit/seat/roster_sync.py:390-392`. Of 692 live carries, 88 cite a ruling `rulings()` parses (85 resolvable-only, 3 prose-only) and 2 more cite one it does not: `R10-FLY-ORPHANS-REWRITTEN` `"Fold (s4 triage P1): …"` (round before the id) and `R10-ARCH-DOCS` `"triage P5 ACCEPT"` (no round token) (`evidence/grammar.txt`). Both destinations are `not-started` with no PR, so no transition re-derives them today; a future PR whose row says `triage P1 (s4)` would miss the held carry and, if proposal-sourced, the triage gate would abort the pass. Smallest change: accept the round on either side of the id (or infer it when exactly one round carries that pid) and add a self-test arm using the `(s4 triage P1)` phrasing.
Carry: R10-ORCH-ROSTER-SCHEMA

**N2 — the normalised-text arm cannot see the `Carry:` marker difference.** `tools/audit/seat/roster_sync.py:480` passes the derived row including its trailing `Carry: <GROUP>` to `finding_words` (`:399`). The appended live row ends `… Carry: R10-FLOW-JIDOKA` (`evidence/live2625.txt`), while 646 of 692 live carries do not end with their own marker (46 do); over the roster the text arm collapses 0 held pairs and the ruling arm is the effective mechanism (`evidence/live_pairs.txt`). Smallest change: strip `\s*carry:\s*\S+\s*$` from both sides before comparison, so a re-landed bullet and a markup drift both match.
Carry: R10-ORCH-ROSTER-SCHEMA

**N3 — `MARKUP` deletes `_` and `*`, so distinct texts can normalise equal.** `tools/audit/seat/roster_sync.py:393`. With the trailing marker equal on both sides, `already_carried` matches `"budget 2*3 per pass."` to `"budget 23 per pass."`, `set_state` to `setstate`, and `**Ship it**` to `Ship it` (`evidence/collision.txt`). No live pair collides (`evidence/live_pairs.txt`: 0 text-arm pairs); it needs identical surrounding text and marker. Smallest change: delete only backticks and emphasis pairs (or `_`/`*` only at token edges), so an identifier's `_` and a multiplication `*` survive.
Carry: R10-ORCH-ROSTER-SCHEMA

**N4 — "a triage item is one finding" is false in general.** `tools/audit/seat/roster_sync.py:404-407` states the premise; `dev/programme/triage/s6-batch25.md#P125` is one item carrying two distinct findings ("Arm 1 … -> R10-FLY-OPENPR-ATOMIC", "Arm 2 … -> R10-FLOW-DESIGN-STAGES"), both citing `s6-batch25.md#P125`. The two arms sit in different destinations, so no intra-destination collapse occurs; the only same-destination same-ruling pair on the live roster is the P189 amendment, which is one item (`evidence/live.txt`, `evidence/live_pairs.txt`). The `Q` arm adds a second id namespace (Q ids are proposal ids — the roster's "design-seat items: T2, F5, Q2, Q3, Q7") whose uniqueness is unverified. Smallest change: require the ruling and the normalised text before suppressing, or record the premise as a precondition with the N5 guard.
Carry: R10-ORCH-ROSTER-SCHEMA

**N5 — the "P ids unique within a round" precondition has no guard.** `tools/audit/seat/roster_sync.py:407` asserts it in a docstring; nothing tests it. It holds today (`evidence/pid_unique.txt`). If a later batch re-uses a pid, two distinct triage items share `(round, P<n>)`, `rulings()` becomes ambiguous, and a destination holding a carry citing one refuses a derived finding citing the other: the finding is dropped, printed as `REFUSED Carry:`, and neither the self-test nor a runtime check notices. Smallest change: a self-test arm that counts `^## P<n>:` per round under `dev/programme/triage/` and fails on a duplicate — cheap, no new file.
Carry: R10-ORCH-ROSTER-SCHEMA

**N6 — the disclosed reworded-duplicate append is the live #2625 outcome.** `tools/audit/seat/roster_sync.py:421`. After the fix, item `309b9984` appends and re-words held carry index 7 of `R10-FLOW-JIDOKA` (the same `figure_lint.mjs --pr-body` finding), so that destination records it twice (`evidence/live2625.txt`). The body discloses the direction ("Appending is the safe direction") but does not name that its own live instance produces a duplicate; the append is inert here because the row is not proposal-sourced and `triage_refusal` returns `None`. No code change required; the body could name the row.
Carry: R10-ORCH-ROSTER-SCHEMA

## Checked and held

`VERSION`, `RELEASE_NOTES.md`, the manifest and both claim files are untouched; the three-dot diff is two files (`evidence/diff.txt`). Live check-runs at the head: 43 read, 0 failure, 8 `in_progress` at read; the body's `## Red checks: none` holds, so no root-cause trigger (`evidence/checks.txt`). `dev/programme/delivery/2889.md` is the correct open-row shape. The fix sits in the module owning the concept (`roster_sync.py`) and replaces the predecessor's predicate rather than adding a parallel one; no budget, golden or score moves.
Carry: dismissed: accepted measurement

## Could not establish

- `tests/entities.py` (`ALL 2467 ENTITY CHECKS PASSED`) was not re-run: it queued on the shared `gate_lock` behind another seat and I released it. CI's heavy runs were not re-run (contract step 11). Carry: dismissed: CI's heavy run
- Eight check-runs were `in_progress` at read; a later red is its own root-cause trigger and this verdict does not answer it. Carry: dismissed: a later red is its own trigger

Evidence: `~/hpo-seats/r10s6/review-2889b/ev/` — `head.txt`, `diff.txt`, `selftest.txt`, `before.txt`, `after.txt`, `finder-harness-verbatim.txt`, `mutation.txt`, `collision.txt`, `live.txt`, `live_pairs.txt`, `grammar.txt`, `pid_unique.txt`, `live2625.txt`, `refusal.txt`, `carry-audit.txt`, `checks.txt`, `merge-tree.txt`, and the drivers `driver.py`, `mutator.py`, `mutator_d.py`, `collide.py`, `live_stats.py`, `live_pairs.py`, `grammar_scan.py`, `pid_unique.py`, `live_probe.py`.
