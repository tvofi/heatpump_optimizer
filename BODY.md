R10-CONFIGFLOW-PAGES (Product UX, L), arm B, the second of the group's pull requests in the approved design's order (`design/R10-CONFIGFLOW-PAGES` `32892dc67`, `dev/programme/designs/R10-CONFIGFLOW-PAGES.md`; approve verdict `design-verdict/R10-CONFIGFLOW-PAGES` `3af84d776`). Finding D7-s2-55 of #2238, fixed here. Arm A (D7-s2-56 and A3') is its own pull request, and arms C/C2 and D follow, so this one closes nothing.

**The finding (D7-s2-55).** `_options_suggested_numeric(current, key)` and `_suggested_entity(key, current)` were two copies of one rule, with the argument order swapped: an optional key that suggests the stored value and never defaults it, because voluptuous refills a `default` for a key the submission left absent. `_suggested_entity`'s own docstring called it "the same two-armed rule as `_options_suggested_numeric` beside it".

**The fix (the finder's patch 04, unchanged).** `_suggested_optional(current, key)` replaces both helpers at their three call sites: `_field_marker` (the `_SUGGESTED` arm) and `_quick_setup_schema`'s two wood probes. No behaviour moves. The two `killed_by` ledger rows, `_options_suggested_numeric RETURN_DEL fcaa22f1` and `_suggested_entity RETURN_DEL fcaa22f1` (both `return vol.Optional(key)`), collapse into the one site the helpers now share, `_suggested_optional RETURN_DEL fcaa22f1`. B is hygiene, so it has no failing test. Its evidence is the architecture score plus the existing `_field_marker` and quick-setup checks in `tests/config_flow_steps.py`, which pass unchanged.

**Conflict with arm C2, for the merge.** Arm C2 (the next pull request) rewrites the value side of the same two wood-probe lines (`_entity_of(["sensor"])` -> `_prefill_row(K).widget`), while this one rewrites the marker side. The design resolves it by keeping both sides on each probe: `_suggested_optional(current, K): _prefill_row(K).widget`. That combined tree is the one the design reviewer measured at dS +3.3700.

## Head

`ad4dd15a5b49915b525effad1f0ac9991988e681`, branch `handoff/r10-configflow-b`, merge base `6d86acc909f7fc465e5736771daf8fa45c1373a4` (origin/main tip at 2026-10-28T10:23Z). Everything below was measured on this branch over that base, three-dot, with the seat interpreter (Python 3.14.7, `~/.local/state/hpo/venv-ci`, first on `PATH`).

## Mutation proof

Each mutant edits one line of `config_flow.py` in a fresh `git archive HEAD` copy and runs `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py`:

- `_suggested_optional`'s `if key in current:` -> `if False:` (every stored suggestion dropped): `1 of 505 checks FAILED`, `and every one of them re-renders its stored value as that field's pre-fill` (quick_setup's `wood_tank_top_entity` and `wood_tank_bottom_entity` lose their suggestion), at `58e2d6953`, whose `config_flow.py` is this head's.
- the ledger's own mutant on the collapsed row, `RETURN_DEL fcaa22f1` (`return vol.Optional(key)` -> `pass`): `python3 tests/mutation_table.py --anchor 'custom_components/heatpump_optimizer/config_flow.py:_suggested_optional RETURN_DEL fcaa22f1' --scripts tests/config_flow_steps.py`: `PIN RE-VERIFICATION: 1 reproduced, 0 not reproduced, 0 not re-verified`, `killed by tests/config_flow_steps.py`, beside a baseline `rc=0 failed=0` and the comment-only null control `NULL_COMMENT survived tests/config_flow_steps.py`, at `58e2d6953`.

## Unpinned sites

none: `python3 tools/pr/ci_predict.py --base origin/main` lists no unpinned site the diff adds (the guard and return lines of `_suggested_optional` are `_options_suggested_numeric`'s, kept as context).

## Null control

The unmodified tree: `tests/config_flow_steps.py` passes at the merge base and at this head with the same check count (`ALL 505 checks PASSED`, rc 0). The helper's two arms are pinned by those checks. The finder's harness reads the patch at its own base with a perturbation that reverses it: `perturbed_delta_S=+0.0000` and `perturbed_vector_equals_baseline=1`, so the patch file is the whole delta. `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical to the base, so nothing is claimed.

## Figures

- `tests/config_flow_steps.py` at this head: `ALL 505 checks PASSED`, rc 0: `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py`.
- architecture score: `Architecture score: dS +0.3628 IMPROVES`, `duplication_copies 35 -> 34 +0.3628`: `python3 tools/audit/archscore/score.py --diff 6d86acc909f7fc465e5736771daf8fa45c1373a4`. The design's arm-B row is +0.3628 (duplication_copies 35 -> 34).
- the finder's harness at the finder's base `554e2ecfa`, from a standalone clone at `01d9d0be2`: `bash dev/audit/rounds/round10/D7/arch-s2/run_findings.sh 04_suggested`. It reads `RESULT delta_S=+0.1880`, `duplication_copies=68->67`, `perturbed_delta_S=+0.0000`, `perturbed_vector_equals_baseline=1`, which is #2238's figure for D7-s2-55.
- structural ratchet: `STRUCTURE RATCHET PASSED` after re-recording `duplication_copies` 15 -> 14 (`python3 tests/structure.py --record`; the reason is in commit `ad4dd15a5`'s message): `python3 tests/structure.py`.
- the class's seams: `git grep -n '_options_suggested_numeric\|_suggested_entity\b' -- custom_components` prints nothing at this head. At the base it prints the two definitions and three call sites. The other hits in the tree are records (round-10 evidence, an archived roster, `dev/audit/harnesses/r10_mutant_skip/matrix.tsv`), which recount and are left as written.
- the gate: `PRE-PR: ad4dd15a5b49915b525effad1f0ac9991988e681 000000000000000000000000`, `clean no refusal`: `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>`.
- three-dot diffstat: 5 files changed, 20 insertions(+), 33 deletions(-): `git diff --stat 6d86acc909f7fc465e5736771daf8fa45c1373a4...HEAD`.
- the branch touches none of `VERSION`, `RELEASE_NOTES.md`, the manifest, `tests/golden/claimed_drift.txt`, `tests/golden/card_claimed_drift.txt`: `git diff --name-only 6d86acc90...HEAD -- <those five> | wc -l` prints 0.

**#2238's findings, each dispositioned** (no closing keyword here; the group's last pull request carries #2238's): D10-s1-51 fixed by #2290; D2-s2-01 by #2365 and #2368; D7-s2-01 by #2527; D7-s2-51 (weakened), D7-s2-52, D7-s2-53 and D7-s2-54 by #2379; D7-s2-55 fixed here; D7-s2-56 by this group's arm-A pull request (`handoff/r10-configflow-a`); D7-s2-57 by #2819; D7-s2-59 by #2282; D8-s1-01 by #2819.

## Red checks

none: no check has run on this head yet. `ci_predict.py --base origin/main` prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 6d86acc909f7`.

## Forward-carry

- `dr1-b-c2-conflict`: the B/C2 resolution above goes to arm C2's pull request, which lands after this one. It lands in `dev/programme/rosters/wave-r10-groups.json`, group R10-CONFIGFLOW-PAGES. Carry: R10-CONFIGFLOW-PAGES

## Friction

none
