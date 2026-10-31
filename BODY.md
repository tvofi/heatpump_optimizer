R10-996-RUNNER-CLAIMS, second PR (the first, #2843, landed the shape-claim grammar): carries 1 (P196/V116) and 2 (P209/V129). The `claimnotes` driver in `tests/env_drift.py` refused every merge where both sides changed the bare claim list. It now merges that list three-way per scenario (`merge_claim_decision`). A scenario one side changed takes that side's lines. One neither side changed keeps its lines. One a side deleted while the other left it alone stays deleted. It refuses, naming the scenarios, when both sides changed one scenario's lines, or changed claims under different `claims-for:` stamps. `merge_claim_defect` checks the result against that decision, not against one side's list. It also checks each scenario's lines are one side's own.

**Policy, under mandate 6329234399.** `dev/governance/rules/claim-files.md` changes "refuses ... when both sides rewrote the bare claim list" to "refuses ... when both sides rewrote the same scenario's claims, or changed claims under different `claims-for:` stamps". It also adds that a deleted scenario and a deleted `may-drift` line stay deleted. This changes what a seat resolving a claim-file conflict must do, so it is policy and needs the owner's approving review before merge. The generated `.claude/rules/claim-files.md` and `.cursor/rules/claim-files.mdc` copies come from `node tools/policy/rules_sync.mjs` (`--check` ok).

**One rule beyond the carry's text, and why.** On the brief's seven recorded refusals, the per-scenario rule alone resolved 2 of the 5 disjoint ones (census below). The other three (#2745 twice, e438816e3) were refused by `merge_claim_defect`'s may-drift check: a may-drift line was lost. In each, one side had deleted a `may-drift` line, the R8-P3 suspension that claims the fixture for the release. Main left the line alone, so the three-way comment merge kept the deletion, and the two-way survival check refused it. The check is now three-way for may-drift lines too. A line one side deleted and the other left alone stays deleted, and any other may-drift line either side carries must survive. That deletion only narrows what the gate exempts (fail-closed direction). Alternatives that lost: (a) keep the two-way check, which resolves 2 of 5 and misses the carry's own count; (b) reinstate the suspended line, which re-exempts a fixture the branch deliberately claimed.

**Carries 1 and 2 disagree on one case, resolved by carry 1.** Carry 2 (P209) says "the deletion shape keeps refusing" because "a union would reinstate a claim a side deleted". Carry 1 (P196) rules that a scenario one side deleted and the other left alone stays deleted. Under a three-way merge nothing is reinstated, so P209's stated reason does not hold for that case, and its pinned control is kept as the refusing shape only where a deletion meets a rewrite. Both carries' disjoint-addition control passes: base empty, ours `everything_on`, theirs `valve_storage_small_tank`. `_CM_UNION_IS_SILENT` still pins why a two-way union stays forbidden.

**Carry 3 (P214, the bot's refusal message) is not in this PR.** Its own text says an `edit-brief` taking `tools/pr/merge_main_bot.py` into this group's `files` lands first, and "no fix touches the bot before it lands". At the base, the group's `files` are `tests/env_drift.py` and `tests/golden/claimed_drift.txt` only. `merge_claim_refusal` now names each refused scenario with both sides' reasons, so the bot only has to relay that text once the edit-brief lands.

Both claim files are byte-identical to the merge base.

## Approval

Pending. This diff changes `dev/governance/rules/claim-files.md` and its generated copies, which is policy. It is drafted under mandate 6329234399, as carries 1 and 2 direct. The owner has not approved it, and it merges only on `tvofi`'s approving review at its head (`main-protect-checks`' code-owner rule). The policy change is one rule: the driver refuses "where both sides rewrote one scenario's claims or stamped differing `claims-for:`", where it refused when "both sides rewrote the bare claim list". A side's deletion of a claim or a `may-drift` line now wins over the other side's silence.

## Head

`dee012f97c99523a14ad2fb2b9ef7d67089e5fea`, measured against merge base `a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0` (= origin/main at 2026-10-31T18:41:55Z). The branch was cut from `7539d1675` and merged `origin/main` three times, the last bringing in #3016 (the wood-fuel change, which also touches `tests/entities.py`, `tests/closures.json` and `tests/golden/claimed_drift.txt`). None conflicted; `tests/closures.json` went through the ledger merge driver. Every figure below, the scoped gate included, was re-taken at `dee012f97c99523a14ad2fb2b9ef7d67089e5fea`.

## Mutation proof

One mutant per rule, each a one-line edit to `tests/env_drift.py`, run through the merge-driver section of `tests/entities.py` (scratch runner, which execs that section with the module's own prelude):

- M1, one side changed -> that side's lines (`elif main == was:` takes `their_blocks`): 6 checks red, among them `claims both sides added on different scenarios are both kept`, `a claim list only one side touched is carried, not refused`, `git resolves claims both sides added on different scenarios`.
- M2, both sides changed one scenario -> refuse (refusal replaced by taking ours): `a scenario both sides rewrote is refused, not unioned`, `a claim one side deleted and the other rewrote is refused`, `and it leaves a conflict for a scenario both sides rewrote`.
- M3, deletion stays deleted (`our_blocks.get(name) or their_blocks.get(name)`): `a claim one side deleted and the other left alone stays deleted`.
- M4, claims-for mismatch -> refuse (stamp test disabled): `claims both sides changed under different claims-for stamps are refused`.
- M5, may-drift three-way (back to the two-way survival test): `a may-drift line one side suspended stays suspended through the merge`.
- M6, provenance (the "neither side's own" return deleted): `the merge verification catches a lost stamp, a lost may-drift line, a smuggled claim and surviving markers`.

Failing first: the new `tests/entities.py` section against the base `tests/env_drift.py` fails `claims both sides added on different scenarios are both kept` (`merged=None`), then stops on `AttributeError: module 'env_drift' has no attribute 'merge_claim_decision'`.

## Null control

At the base driver the census harness reports `refused` on all seven recorded merges, including the five with zero scenario overlap. At the head, the two overlapping shapes still refuse: #2834's five `coord_*` scenarios, and 5bf232eac's overlap of 42. Cases where only one side changed resolve as before: `a claim list only one side touched is carried, not refused` and `merging a file with itself returns it byte-identical` both pass unchanged. A `claims-for:` mismatch refuses (M4's control).

## Figures

- `python3 dev/audit/harnesses/claim_merge_census.py a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0` (the base driver): `RESULT resolved=0`, `RESULT refused=7`. The cases come from P196's list in `dev/programme/triage/s6-batch34.md`. The per-row counts (scenarios each side changed against the merge base; overlap = scenarios both changed to different lines) equal P196's for all seven: #2841 5/1/0, #2745 41/1/0 and 41/5/0, #2834 5/5/5, 3a07c2eaa 3/1/0, e438816e3 4/41/0, 5bf232eac 45/50/42.
- `python3 dev/audit/harnesses/claim_merge_census.py` (the head driver): `RESULT resolved=5`, `RESULT refused=2` (#2834, 5bf232eac), `RESULT hand_same=1`, `RESULT hand_differs=1`. `hand=` compares the driver's claim map with what main's hand-resolved merge committed. 3a07c2eaa matches. e438816e3 differs on four scenarios (`config_flow`, `valve_storage_flat_prices`, `valve_storage_low_target`, `valve_storage_small_tank`). Those four were lines its first parent carried from main, and the hand resolution dropped them ("main's four inherited claim lines are dropped", its commit message). The driver keeps them as that side's lines. At a PR's three-dot they equal the fork point's and are inert (`excusing_claims`, R9-F10.8), so the gate judges the two results the same. 5bf232eac refuses, so it has no comparison.
- Mutants: six, each killed (`## Mutation proof`); the null is the head tree, `ALL 20 CM PASSED`.
- `D=$(mktemp -d); python3 tests/closure.py select --diff a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0 --workdir "$D"`: `MODE: SCOPED -- 7 script(s) run, 26 scoped out.`
- `PYTHONPATH=tests/hastub GATE_SCOPE=auto GATE_SCOPE_BASE=a7dd7f50d67e GOLDEN_MODE=drift GOLDEN_REF=a7dd7f50d67e bash tests/run.sh`: `9 TEST SCRIPT(S) PASSED; 25 SCOPED OUT AND NOT RUN`, `ALL 2499 ENTITY CHECKS PASSED`. An earlier run at `8742f1f`'s parent (the head before the cap fix) failed one check, `the template arm turns the acceptance red ... (and the real template keeps it green)`: `policy_lint.mjs` refused `.claude/rules/claim-files.md` at 57 lines against its 53-line cap. The rule paragraph was cut back to the base's line count (`8742f1f`), not raised; `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `git diff --quiet a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0 HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo "CLAIM FILES BYTE-IDENTICAL"`: `CLAIM FILES BYTE-IDENTICAL`.
- `python3 tools/pr/ci_predict.py --base origin/main --apply-inert`: applied one `inert_reads` entry (`tests/harness_headers.py` reads the new harness), then, re-run after the merge, `CI PREDICT: no closures, fast, governance or instrument red predicted against a7dd7f50d67e`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0`: `Architecture score: dS +0.0000 NULL`.

## Red checks

none

## Forward-carry

- Carry 3 (P214): the merge-main bot should relay `merge_claim_refusal`'s text, which now names each refused scenario with both sides' reasons. It waits on its own `edit-brief` taking `tools/pr/merge_main_bot.py` into this group's `files`, and stays on the roster as written. Carry: R10-996-RUNNER-CLAIMS

## Friction

- claim-files.md: contradiction: carry 2 (P209, s6-batch39) keeps "the refusal for a deletion" while carry 1 (P196, s6-batch34) rules that a scenario one side deleted and the other left alone stays deleted. Resolved here by P196's rule, since P209's stated reason (a union reinstates the deletion) does not hold for a three-way merge. Carry: dismissed: resolved in this PR's driver and pinned by `a claim one side deleted and the other left alone stays deleted`
