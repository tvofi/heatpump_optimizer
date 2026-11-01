R10-996-RUNNER-CLAIMS, second PR (the first, #2843, landed the shape-claim grammar): carries 1 (P196/V116) and 2 (P209/V129). The `claimnotes` driver in `tests/env_drift.py` refused every merge where both sides changed the bare claim list. It now merges that list three-way per scenario (`merge_claim_decision`). A scenario one side changed takes that side's lines. One neither side changed keeps its lines. One a side deleted while the other left it alone stays deleted. It refuses, naming the scenarios, when both sides changed one scenario's lines, or changed claims under different `claims-for:` stamps.

**Round 2, answering the first review's block (`verdict/3066` at `b1a0be47d`).** The review found that the note union decided `may-drift` lines. On an overlapping hunk `git merge-file --union` keeps both sides, so a `may-drift` line one side suspended came back beside a neighbour the other side reworded (its row D2). `merge_claim_defect` checked only for lost lines. The claim was stronger than the check, and the check is now strengthened rather than the claim narrowed:

- The claim file has three kinds of value-bearing line: claim lines, `may-drift` lines, and the `claims-for:` stamp. The seam census in `## Figures` names them. The stamp and each `may-drift` line now merge by the claim rule, one key per stamp and per fixture (`merge_marker_decision` over the shared `_decide_per_key`). The union's copy of those lines is cut to that decision.
- The stamp was the same defect, found by that census and closed here. A bump beside the other side's adjacent note left both stamps, and `_parse_claims` reads the first one, so a bump made on this branch read as the old stamp.
- `merge_claim_defect` compares the result's stamp and `may-drift` lines with the decision exactly, in both directions, so a lost line and a reinstated line both refuse.
- A key both sides changed differently is refused and named, like the claim rule's delete-against-edit. That covers the review's D3 (one side deletes a `may-drift` line, the other rewords it), which resolved before. It also covers a stamp both sides bumped to different releases.

**Policy, under mandate 6329234399.** `dev/governance/rules/claim-files.md` used to say the driver refuses "when both sides rewrote the bare claim list". It now says the driver merges claims per scenario and `may-drift` lines per fixture, three-way: "a side's change or deletion wins over the other's silence". It refuses "where both sides rewrote one scenario's claims or one fixture's `may-drift` line, or stamped differing `claims-for:`". The generated `.claude/rules/claim-files.md` and `.cursor/rules/claim-files.mdc` copies come from `node tools/policy/rules_sync.mjs` (`--check` ok).

**One rule beyond the carry's text, and why.** On the brief's seven recorded refusals, the per-scenario claim rule alone resolves 2 of the 5 disjoint ones. The other three (#2745 twice, e438816e3) each had one side delete a `may-drift` line, the R8-P3 suspension that claims the fixture for the release, while main left that line alone. Under the per-fixture rule that deletion stands. The alternatives lost: (a) a two-way survival check resolves 2 of 5, which misses the carry's own count; (b) reinstating the suspended line re-exempts a fixture the branch deliberately claimed, and `may_drift_error` then refuses it as `CLAIMED AND MAY-DRIFT` (the review's D2c).

**Carries 1 and 2 disagree on one case, and carry 1 decides it.** Carry 2 (P209) says "the deletion shape keeps refusing", because "a union would reinstate a claim a side deleted". Carry 1 (P196) rules that a scenario one side deleted and the other left alone stays deleted. A three-way merge reinstates nothing, so P209's stated reason does not hold for that case. Its pinned control is kept as the refusing shape only where a deletion meets a rewrite. Both carries' disjoint-addition control passes. `_CM_UNION_IS_SILENT` still pins why a two-way union stays forbidden.

**Carry 3 (P214, the bot's refusal message) is not in this PR.** Its own text says an `edit-brief` taking `tools/pr/merge_main_bot.py` into this group's `files` lands first, and "no fix touches the bot before it lands". At the base, the group's `files` are `tests/env_drift.py` and `tests/golden/claimed_drift.txt` only.

`dev/audit/harnesses/claim_merge_mutants.py` is new. It runs the mutation proof below, applying each mutant to a temporary copy of `tests/`, never to the tree. It is classified beside the census in `tests/closures.json`. Both claim files are byte-identical to the merge base.

## Approval

Pending. This diff changes `dev/governance/rules/claim-files.md` and its generated copies, which is policy. It is drafted under mandate 6329234399, as carries 1 and 2 direct. The owner has not approved it, and it merges only on `tvofi`'s approving review at its head (`main-protect-checks`' code-owner rule). The rule change: the driver refuses where both sides rewrote one scenario's claims, one fixture's `may-drift` line, or the `claims-for:` stamp, where it used to refuse when both sides rewrote the bare claim list. A side's deletion of a claim or a `may-drift` line wins over the other side's silence.

## Head

`30a7a59a520779df8c55192a437bac3cda1ff1d4`, measured against merge base `2b6bef7453a8bdaf97d42f382a116ce226b35ccc`. `origin/main` was `c89de2f62` when this was written, and `git merge-tree --write-tree origin/main HEAD` exited 0, so the branch was not merged forward (it is frozen past the handoff unless that check conflicts). Round 2 adds four commits on the reviewed head `b1a0be47d`. Every figure below was re-taken at this head.

## Mutation proof

`python3 dev/audit/harnesses/claim_merge_mutants.py` runs one mutant per rule against the merge-driver section of `tests/entities.py`, now 30 checks. The unmutated copy, run first, is the null control (`RESULT baseline_pass=1`). The result is `RESULT killed=15`, `RESULT survived=0`, `RESULT stale=0`. The two the review left alive:

- M3-main-deletion-undone (the review's M3, `our_blocks.get(name) or their_blocks.get(name)`): 4 red, first `a claim main deleted and this branch left alone stays deleted`.
- R-mine-eq-main-only (`if mine == was:`): 1 red, `a claim both sides added identically resolves, kept once`.

The new stamp and `may-drift` rules:

- N1-no-union-cut (the union's copy left uncut): 5 red, first `a may-drift line this branch suspended beside a reworded neighbour stays suspended`.
- N2-marker-refuse-nothing: 3 red, first `a may-drift line deleted against rewritten is refused and named`.
- N3-file-ignores-marker-refusal: 2 red, the same check first.
- N4-defect-no-marker-check: 2 red, first `the merge verification catches a lost stamp, a lost may-drift line, a smuggled claim and surviving markers`.
- N6-refusal-unnamed: 3 red, first `a may-drift line deleted against rewritten is refused and named`.
- N7-stamp-not-a-marker: 3 red, first `a stamp this branch bumped beside an adjacent note is the one stamp kept`.
- N8-maydrift-not-a-marker: 6 red.
- N9-maydrift-key-ignores-name: 5 red.

The review's other mutants are each killed again: M1 10 red, M2 6, M4 1, M6 1, R-keep-deleted 5. Its M5 mutated the two-way survival check, which this round replaced.

Two mutants of an earlier cut of this round survived, and I removed the code they showed was redundant rather than adding tests for it. A separate lost-line arm was subsumed by the exact comparison. A refused-key arm in `merge_claim_defect` duplicated `merge_claim_file`'s early refusal. Both are gone (commit `9c172b507`).

Failing first: I ran the new checks with the reviewed head's `tests/env_drift.py` (`b1a0be47d`) in place, and 8 of 30 failed:

- both `a may-drift line ... suspended beside a reworded neighbour stays suspended`
- both `a may-drift line ... is refused and named`
- both `a stamp ... bumped beside an adjacent note is the one stamp kept`
- `a stamp both sides bumped differently is refused and named`
- `the merge verification catches a suspended may-drift line put back`

The two claim-rule checks pass there. They pin mutants, not a defect at `b1a0be47d`.

## Null control

The seven recorded merges are the null: the fix should not change them. The reviewer's replay (`replay.sh`, blob `78d03a90ad914c5f751e0b6ddfef002d69c6b375`, its checkout path pointed at this worktree) runs the driver CLI as git invokes it. At `b1a0be47d` and at this head it gives `resolved` for #2841, #2745a, #2745b, 3a07c2eaa and e438816e3, and `refused` for #2834 and 5bf232eac. `cmp` of each of the seven result files between the two heads prints `SAME` for all seven. One-sided merges are unchanged: `a claim list only one side touched is carried, not refused` and `merging a file with itself returns it byte-identical` pass. A merge with no overlapping hunk keeps the union's output, because the cut drops only lines the decision dropped. The reviewer's disjoint row I and the identical-add rows resolve at both heads.

## Figures

- The finder's harness is the reviewer's adversarial driver `adv.py` (blob `c1c04b1aef6c2815cf02586bdc57769ac372e300` under `ev/reviewer-instruments/` on `probe/rev-3066-e2ba7157`, out of the tree), run at both ends. At `b1a0be47d` it gives 15 OK and 2 FAIL. The FAILs are `D2-ours-del-flat-theirs-edit-wood` (resolved, with the suspended `flat_prices` line reinstated) and `D3-widen-theirs-del-ours-reword` (resolved). At this head it gives 17 OK and 0 FAIL. D2 resolves with one `may-drift` line, `wood_coil -- machine-sensitive (reworded)`. D3 refuses with `CONFLICTING MAY-DRIFT OR STAMP` and names `may-drift: flat_prices`.
- The reviewer's `adv2.py` (blob `83189519c80876e06cf86adeb48fb9edc23980f9`, D2 with its claim) at `b1a0be47d` gives `may_drift_error: CLAIMED AND MAY-DRIFT ... flat_prices`. At this head it gives `may_drift_error: None`.
- The reviewer's `m3probe.py` (blob `82fb8fdd254f554f3eae6fc85212dbb7ef92006e`) gives `['beta', 'gamma']` at both heads (no defect at either). M3 is now pinned by a committed check (`## Mutation proof`).
- The seam census is the rule that enumerates every value-bearing line kind a reader takes from claim-file text: `grep -nE "startswith\((CLAIM_VERSION_MARKER|MAY_DRIFT_MARKER|SHAPE_CLAIM_MARKER)\)" tests/env_drift.py`. It returns 8 sites in three kinds:
  - `SHAPE_CLAIM_MARKER` (three sites) tests a claim line's name, so it is a claim line, already decided per scenario.
  - `CLAIM_VERSION_MARKER` in `_parse_claims` (the stamp) was decided by the union. It is closed in this diff by `_marker_key`, which is the fourth hit.
  - `MAY_DRIFT_MARKER` in `_may_drift` and `_is_may_drift` was decided by the union. It is closed in this diff by `_marker_key`, which is the fifth hit.
  No returned seam is undispositioned.
- A scratch stamp-seam probe ran three shapes at both ends. The committed checks named `a stamp ...` in `## Mutation proof` reproduce all three shapes. At `b1a0be47d`:
  - `ours-bumps theirs-edits-adjacent`: `stamp=7.0.4 want=7.0.5 FAIL`, with both stamp lines kept.
  - `both-bump-differently`: `stamp=7.0.6 want=None FAIL`.
  - `theirs-bumps`: `OK`, but with two stamp lines.
  At this head all three are `OK`, with one stamp line each, and the different bumps refuse.
- `python3 dev/audit/harnesses/claim_merge_census.py 2b6bef745` (the base driver): `RESULT resolved=0`, `RESULT refused=7`. At `b1a0be47d` and at this head it gives `RESULT resolved=5`, `RESULT refused=2`, `RESULT hand_same=1`, `RESULT hand_differs=1`. The per-row counts at this head are each side's changed scenarios against the merge base, and their overlap: #2841 5/1/0, #2745 41/1/0 and 41/5/0, #2834 5/5/5, 3a07c2eaa 3/1/0, e438816e3 4/41/0, 5bf232eac 45/50/42. e438816e3 `hand=differs` is unchanged from round 1. It concerns four lines inherited from main, which are inert at a PR's three-dot diff.
- `D=$(mktemp -d); python3 tests/closure.py select --diff 2b6bef7453a8bdaf97d42f382a116ce226b35ccc --workdir "$D"`: `MODE: SCOPED -- 7 script(s) run, 26 scoped out.`
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 2b6bef7453a8bdaf97d42f382a116ce226b35ccc`: `NO UNCLAIMED DRIFT: 56 scenario(s) checked`, `NO STALE FIXTURE: 56 committed fixture(s) still match`.
- `git diff --quiet 2b6bef7453a8bdaf97d42f382a116ce226b35ccc HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo "CLAIM FILES BYTE-IDENTICAL"`: `CLAIM FILES BYTE-IDENTICAL`.
- The same `git diff --quiet` over `VERSION`, `custom_components/heatpump_optimizer/manifest.json` and `RELEASE_NOTES.md`, with `&& echo`: `VERSION MANIFEST NOTES UNTOUCHED`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`. In `--budgets`, `.claude/rules/claim-files.md` is at 53 lines against a 53-line cap, the same line count as the base paragraph.
- `python3 tools/pr/ci_predict.py --base origin/main --apply-inert`: `CI PREDICT: no closures, fast, governance or instrument red predicted against 2b6bef7453a8`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 2b6bef7453a8bdaf97d42f382a116ce226b35ccc`: `Architecture score: dS +0.0000 NULL`.

## Red checks

none. No check went red at the reviewed head `b1a0be47d`: the review's `get_check_runs` read 55 runs, all success or skipped. This head has had no CI run yet.

## Forward-carry

- Carry 3 (P214): the merge-main bot should relay `merge_claim_refusal`'s text, which now names each refused scenario, fixture or stamp with both sides' lines. It waits on its own `edit-brief` taking `tools/pr/merge_main_bot.py` into this group's `files`, and stays on the roster as written. Carry: R10-996-RUNNER-CLAIMS
- The review's two non-blocking findings are closed in this diff, not carried. R-mine-eq-main-only is pinned by `a claim both sides added identically resolves, kept once`. D3 (delete against reword of a `may-drift` line) now refuses by the per-fixture rule. Carry: dismissed: fixed in this PR

## Friction

- claim-files.md: contradiction: carry 2 (P209, s6-batch39) keeps "the refusal for a deletion" while carry 1 (P196, s6-batch34) rules that a scenario one side deleted and the other left alone stays deleted. Resolved here by P196's rule, since P209's stated reason (a union reinstates the deletion) does not hold for a three-way merge. Carry: dismissed: resolved in this PR's driver and pinned by `a claim one side deleted and the other left alone stays deleted`
