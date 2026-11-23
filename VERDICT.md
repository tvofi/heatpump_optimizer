Fix review: merge 5e9f76ec51340eb43ce7f448c9dd9b0878cdfeb9

bus-nonce: af67eb39e493baf7a2680450b52aa2b4
pending-ci: gate

## Scope

This is round 1 and a full review: the packet has no `--reviewed-head`. The diff is two record files, `dev/audit/rca/R11-RCA-MUTATION-VACUOUS.md` (269 lines) and `dev/programme/delivery/3876.md` (1 line). It writes no production, test, workflow or instrument line. Under fix-review.md C5 a record can only take `Note:` lines. Nothing here touches `custom_components/`. The reviewer's local copy of the role contract is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Findings

- Note: figure: section 7 says "4 of 15 are on `tools/`" and lists the sister mutant #6 as its own population. Section 2's table puts #10 to #14 on `tools/`, which is 5, and #6 is already one of the 9 `custom_components/` blocks. The line sums to 15 only because it counts #6 twice and undercounts tools by one. No decision in section 4 or 5 reads this line: the rule C reach counts #10 separately, and "population T, 4 of 15" there means #11 to #14. Carry: dismissed: record-only count slip, no downstream consumer
- Note: figure-unverified: section 4 says "119 reverts before the docstring filter (`null_controls.sh`, v1)" and "after the filter they drew 0, 4, 13 and 0 on the four 72 h merges". The only null-control output in the prototype's `ev/` is `null_controls_7d_v2.txt`. Its C-fire column also adds up to 119 over 23 PRs, and it contains none of the 72 h merges. So the before/after split, and which output is v1, cannot be re-derived from the evidence the record cites. Only the 5.2-per-PR mean (119/23) re-derives. The LINE_REVERT cost estimate uses 5.2, so the verdict is unaffected. Carry: #3314
- Note: harness out-of-tree: the enumerator (`enumerate_blocks.sh`), the probe (`vacuous_probe.py`) and every `ev/` file cited by the record exist only under the orchestrator state directory (`r11/proto/mutation-vacuous/`). They land only if P-R11-MUTATION-VACUOUS survives round-end triage (fix-review.md step 9, fixer.md 18). The reviewer re-ran them there. This is disclosed as the RCA seat's instrument, not a finder's. Carry: #3314
- Note: instrument defect for the prototype when it lands: `enumerate_blocks.sh` filters probe refs with a lexical `[[ "$t" < "$SINCE" ]]` and sorts with a lexical `sort`, over `%cI` stamps that mix `Z` and `+01:00`. A `+01:00` stamp up to one hour before `SINCE` passes the filter. Here the effect is nil: after UTC normalisation, 0 rows fall before v10.0.0 and 0 rows fall within 2 h of the 72 h edge (`ev/rederive.txt`). The tracked build should normalise to UTC (`%ct` or `git log --date=iso-strict-local` with TZ=UTC). Carry: #3314
- Note: body: the PR body's `## Figures` says "none", but its summary quotes figures (311, 88, 30, 15 of 26, 72 s, 201 min, 14 min, 300 min, 23 of 23). writing-for-agents.md puts the literal of a figure from an out-of-tree corpus in `## Figures`, with its enumerator. `figure_lint` reads 0 figures at the head, so none was checked by the instrument. All were checked by hand below. Carry: dismissed: paperwork, every figure re-derived by hand in this verdict

## Evidence

- RESULT re-derivation of sections 1 and 4 from `ev/enum_since_v10.txt`, with timestamps normalised to UTC (`ev/rederive.txt`):
  - since v10.0.0: 311 verdicts, 88 blocks, 30 `mutation-vacuous`, next class `class-open` 18, over 7.72 days, which is 3.88 a day
  - 72 h window: 95 verdicts, 26 blocks, 15 `mutation-vacuous` on 11 PRs, 58%
  - round trip: n=25, median 272 min, min 57, max 4189
  - All match the record. The 15 window rows are the 15 (PR, head) pairs of section 2's table.
- RESULT release cycle: tags v10.0.0 (2026-11-15T05:22:47Z) to v10.1.2 (2026-11-21T20:36:38Z) span 6 cycles (10.0.1, 10.0.2, 10.0.3, 10.1.0, 10.1.1, 10.1.2) in 6.64 days, a mean of 26.6 h. Derived from these:
  - 3.88/day x 26.6 h = 4.3 blocks per cycle
  - A+B benefit: 2/72 h is 0.74 per cycle; x 272 = 201 min, x 111 = 82 min
  - LINE_REVERT benefit: 3/72 h is 1.11 per cycle; x 272 = 301 min (record: 300), x 111 = 123 min (record: 122)
  - standing cost: 311/7.72 = 40.3 heads a day, 45 per cycle, x 1.6 s = 72 s
  - driver time: 7.4 x 5.2 x 11 s = 423 s, about 7 min
  - All match the record within rounding.
- RESULT rule reach: `ev/reach_out.txt` shows exactly the record's reach column:
  - #3873:4126 DRAWN and #3847 prelude.py:470 DRAWN
  - #3838 6311 and 11334 HAND-OWED
  - #3835:1121 DRAWN at both heads
  - everything else not-reached
- RESULT the detector demonstrated (defect-root-cause.md), re-run by the reviewer from the prototype directory with the live PR bodies fetched read-only (`ev/probe_reruns.txt`):
  - `--self-test`: SELF-TEST PASSED
  - #3866 at 19eafc0f, rules AB: `FAIL -- 7 changed production file(s); rule A 2, B 1`, rc 1. Both A lines and the B line name `pump_arbiter.py:936` in `_boost_ceiling_c`.
  - after `ev/fix-3866.diff` was applied to a worktree at 19eafc0f, `--head WORKTREE`: `PASS -- rule A 0, B 0, C 0`, rc 0
  - #3873 at 73797a57, rule C: `FAIL -- rule C 6`, and it includes `coordinator.py:4126` (base text `return CoordinatorDiagnostics.of(self)`, the reviewer's M8)
- RESULT reviewer's own perturbation of the input: the #3866 body with only its two "deleted from `_boost_ceiling_c`" sentences removed gives `PASS -- rule A 0, B 0`. Rule A moves under its own perturbation, so it is not void. B also goes to 0, because its "body records an equivalent/surviving mutant in `f`" condition is met by the same sentence ("was an equivalent mutant"). This matches the docstring's rule B.
- RESULT null control: `ev/null_controls_7d_v2.txt` holds 23 PRs, all `AB: PASS`, and each line prints a non-zero changed-file count. This matches section 6.2.
- RESULT repeat guard: `ev/repeat_demo.txt` prints ANSWERABLE on #3834 r1->r2, r2->r3 and #3866. This is the failure the record states in section 6.3. A fourth line (#3835) is the sister, not a repeat, and the record does not count it.
- RESULT `ev/mutrun-936.txt`: `SURVIVED NULL`, `SURVIVED pump_arbiter.py:936:GUARD_OFF`, real 21.66 s, as quoted.
- RESULT the proposal is filed: `P-R11-MUTATION-VACUOUS` is at `r11/R11-PROPOSALS.md:108` in the orchestrator state directory, for round-end triage. Issue #3314 is OPEN ("recurring friction: mutation-vacuous").
- RESULT step 1 (mutation): n/a. The diff writes no production line. The `tests / mutation` lane draws no mutant (`changed_lines`).
- RESULT steps 4, 5: no claim file, golden, `VERSION`, manifest, `RELEASE_NOTES.md` or `*_budgets.json` is touched.
- RESULT step 7: the PR body's `## Head` names `5e9f76ec51340eb43ce7f448c9dd9b0878cdfeb9`, the head reviewed. The authored head is fb178c8e. 5d2ba7e1 is the orchestrator's automatic main merge.
- RESULT step 13: `git merge-tree --write-tree origin/main 5e9f76ec` gives tree 1ed6315d9c, rc 0. It merges cleanly.
- RESULT step 14: the diff moves no instrument number.
- Not re-derived:
  - The CI state at #3866 f36611dd (`mutation-autofix` `skip-measure-failed`, `MUTATION TABLE INCONCLUSIVE`) was read from the record, not from the run log.
  - So were the "4/13" and "5/14 (24 h)" readings in section 1, and the 1.6 s timing.
- CI: `merge_train.py classify 5e9f76ec51340eb43ce7f448c9dd9b0878cdfeb9 --pr 3876` polled about every 60 s from 2026-11-23T00:00Z to 00:33Z and printed `WAIT 5e9f76ec51340eb43ce7f448c9dd9b0878cdfeb9 pending: gate red: none` (rc 3) on every run. The review is otherwise complete, so it is returned `pending-ci: gate`. owed-reds is the set `merge_train.py owed-reds` prints. No red stood at the head when last read, so no `## Red checks` answer is owed. The packet's `introduced-red: unreadable` refusal came from `governance / instrument-self-tests` still queued at render. classify decides.
