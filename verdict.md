Fix review: merge 8445e36cfc6e5d77931f5558efedbe1c4f22db95

bus-nonce: fe8a730168342a5f454873e11e49a39a
pending-ci: gate

Round 3 (delta scope over the reviewed head 5fd0fc537375027f219394c11994cf1239624271). Measured from a detached worktree at 8445e36cfc6e5d77931f5558efedbe1c4f22db95, merge base 6aa7ddc71216c4bc357db0097839ce40ff94e263.

## Scope

`git diff 5fd0fc53 8445e36c` changes `tools/audit/enumerate.py` alone (130 insertions, 22 deletions). That is the `d1-inputs` rule rewritten as `flow_slots` united with `wiring_slots`, the planted repository widened, and new self-test arms. It is an instrument delta with no production code, so the scope is not widened. Both grounds of the round-2 block are resolved at this head.

## Prior findings

1. `d1-inputs` population: resolved. `enumerate.py d1-inputs` exits 0 and prints 51 lines, among them `input CONF_COMPRESSOR_FREQ_SENSOR` beside `input CONF_COMPRESSOR_FREQ_ENTITY`. The round-2 enumerator, run against the same tree, prints the same set less that one key. The new rule does not depend on the name's suffix: it reads `config_flow.py` `_F` rows behind an entity selector, together with the keys `entry_config.py` `FACTORY_KEPT` keeps as an entity assignment. Its arm plants `CONF_F_SENSOR` and `CONF_W_SENSOR` and fails without them (N2, N5, N10 and N11 below). Independent cross-check: every `CONF_*` name or value in `const.py` that matches entity, sensor or entities is in the universe. The only universe line outside that set is `CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY`, a multi-line declaration the grep cannot read (`ev/d1_inputs_crosscheck.txt`). No `EntitySelector` occurs in the package outside `config_flow.py`.
2. Round-1 survivors: resolved. I re-planted all ten by hand against the self-test at this head (`ev/mutants.py`, `ev/mutants_head.txt`, `ev/mutant_M3_head.txt`). NULL reads `SURVIVED` with `SELF-TEST passed (147 arms)`. M1, M2, M3, M4, M5, M8, M12, M18, M25 and M27 each read `KILLED` rc 1, and each failure names the arm the body cites for it.

## Findings

- Follow-up: round 1's finding stands unchanged. `COMMON.md` states no rule that a finder reports examined over a universe, so each brief restates the sentence. Carry: dismissed: the group owning COMMON.md is carries-open and carry_audit lists no live target; the body's payment (4) already records the alternative and the saving is a sentence per brief

## Evidence

- RESULT mutants of the delta's new code, the reviewer's own and not the fixer's N1-N15 (`ev/mutants_head.txt`): 12 mutants, 12 `KILLED`. They cover: the factory widget ignored (N1); the loop expansion dropped (N2); each of the four refusals turned off (N3, N4, N7, N8); the literal wiring entries dropped (N5); the wiring tests dropped (N6); the isinstance skip widened to any argument (N9); each half of the union dropped (N10, N11); the reason not compared (N12). N1 is killed by an uncaught `Refuse` out of the self-test rather than by an arm's comparison. Either way the self-test exits 1.
- RESULT self-test at the head: `SELF-TEST passed (147 arms)`, rc 0. This matches the body's figure at `5267332704`.
- Body's head chain: `git diff 5267332704 5b2e29e654` and `git diff 5b2e29e654 8445e36c` are both empty. `git diff 6a32d9035a 8445e36c --stat` names `tools/audit/enumerate.py` alone (`ev/delta_checks.txt`). These match the body.
- RESULT `--briefs` at the head: rc 0 (`ev/figures_head.txt`).
- RESULT `score.py --diff 6aa7ddc712`: `Architecture score: dS +0.0000 NULL`, matching the body. Against the current origin/main `f9b680fee4`: `dS +0.0006 IMPROVES` (`coord_footprint 2496 -> 2495`). That comes from main's movement, not this diff.
- RESULT `tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`.
- `git merge-tree --write-tree origin/main 8445e36c` with origin/main at `f9b680fee43bb519996fc107c5f1c65df02683d7`: exit 0, tree 4d4bf6e4fc9014975e0a6473ccae5e3b1794b4d7, no conflict. The head is behind main and merges cleanly.
- `git diff 6aa7ddc712...origin/main -- dev/governance/roles/` is empty. The three-dot diff touches none of `VERSION`, `custom_components/`, `RELEASE_NOTES.md` or `tests/golden/`.
- Not re-derived: the body's figures for brief prose and budgets taken at `fb9b921b98` and `6a32d9035a` (policy_lint, check-wave-script, closures, prepr). This delta moves no brief or config file, and round 1 checked those figures.
- CI: `merge_train.py classify 8445e36cfc6e5d77931f5558efedbe1c4f22db95 --pr 3625` read `WAIT 8445e36cfc6e5d77931f5558efedbe1c4f22db95 pending: gate red: none` (rc 3) on every run from 05:46:30Z to 06:16:36Z (`ev/classify_poll.txt`). No required check was red at any reading, so no `## Red checks` answer is owed. This verdict waits on `gate` through `pending-ci`.
