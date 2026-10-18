Group R10-MERGE-PR-MANDATE. No issue is filed, so this body closes none.

On 2026-10-18 at 16:43Z, `tools/audit/seat/merge_pr.sh 2401 <sha> <evidence> owner` printed `MANDATE EXPIRED` and stopped. The mandate in force (#201 comment 6175172275, scope `all`, valid until 2026-10-28T18:14Z) was invisible to it. Before it refused, it had already re-posted a fix-review comment.

**Cause.** The owner branch hard-coded round 8's mandate. One line held that mandate's window (`expires 2026-09-25T08:40Z`) and the line after it held that mandate's text, copied into the approval body. The window test also called BSD `date -j -f`. GNU `date` rejects `-j`, which empties the test operand, so on Linux the branch printed `MANDATE EXPIRED` whatever the date. The test also ran after `app_comment.sh` had posted the verdict, so every refusal came after a GitHub write.

**What changes.**

- **The live mandate read.** `merge_pr.sh` `owner` mode now needs `--mandate <#201 comment id>`, the same argument `merge_train.py` takes. It reads the comment through `budget_raise_gate.py`'s own reader, imported and never copied: `_mandate` fetches the comment and the thread where a revocation would sit, and `mandate_state` judges them at the current instant. Both readers share the rules on grammar, the pinned owner, the window, edits and revocation. `merge_pr.sh` holds no date, scope or mandate text.
- **The approval body.** It cites the mandate by id (`under mandate <id> (scope …, from … until …)`, a `MANDATE_CITE` shape) and states when it was read.
- **The scope set lives in the gate.** `budget_raise_gate.py` gains `MANDATE_COVERS_CODE_OWNED = ("code-owned", "all")`, next to its raise and policy sets, so every scope set stays in that one file. `merge_train.py`'s docstring already requires this ("its scope sets … live in no other file").
- **Refusal order.** Every refusal now runs before the first GitHub write: the mode, a missing `VERDICT.md`, a moved head, and in `owner` mode a missing or out-of-force mandate.
- **The self-test.** `merge_pr.sh --self-test` builds a throwaway repository holding the script, the real gate and its move map, with a logging `gh` and `app_comment.sh`. `governance.yml`'s `instrument-self-tests` runs it and greps the tally line, as it does for `merge_train.py`.
- **`proof_watch.py`.** It is the one caller that can pass `owner`. It now takes `--mandate`, forwards it, and refuses `--mode owner` without one at launch, not after a watch of several hours.

**Alternatives considered.**

1. **Replace the date with the current mandate's date.** This repeats the defect: the next mandate needs another edit.
2. **Search #201 for the newest mandate comment, as `orchestrator_tick.py` can.** This would make the script pick a mandate on the operator's behalf. An explicit id is the citation the approval body owes, and it is the train's interface. No search was added.
3. **Define the scope tuple inside `merge_pr.sh`.** That would be a second reading of the scope sets. The gate is the one owner of the concept.
4. **Pre-check the `app` path's code-owned refusal before the comment.** `app_approve.sh` reads the posted verdict comment, so its refusal cannot run first. See Forward-carry.

**Ownership.** `tools/policy/budget_raise_gate.py` and `.github/workflows/governance.yml` are code-owned by `@tvofi`. No policy file changes: `policy_lint.mjs --corpus-filter` returns none of the five changed files. No budget file changes.

## Head

`6219325ca20928f82c80880b1ed7fadf3e1c93b2`, branched from origin/main `c8cc75ea90a3bb38dbc6b8dbb7d27d9cce74cdd0` with no merges. Three commits: the merge_pr.sh fix, the proof_watch.py forward, and dropping the retired `.claude/workflows/` gate path, which prepr's layout guard refused. The mutation proof and the self-tests were re-run after that third commit. The scoped-gate script runs and the archscore line were taken at `aa01d527`, whose `tools/` tree differs only by that fallback.

## Mutation proof

Each mutant was applied to the head's file, the self-test was run, and the file was restored.

- **M1: the gate's verdict is ignored** (`sys.exit(0 if ok else 1)` becomes `sys.exit(0)`). `bash tools/audit/seat/merge_pr.sh --self-test` prints `11 checks, 4 failed`:
  - `an expired mandate refuses`
  - `an expired mandate refuses before any GitHub write`
  - `a mandate whose scope does not cover code-owned paths refuses`
  - `a mandate comment that does not exist refuses before any write`
- **M2: the code-owned scope set is dropped**, so `mandate_state`'s raise default applies. `11 checks, 2 failed`:
  - `a mandate whose scope does not cover code-owned paths refuses`
  - `null: scope code-owned in force reaches the approval`
- **M3: owner mode no longer requires `--mandate`** (`[[ "$MID" =~ … ]]` becomes `true`). `11 checks, 1 failed`: `owner with no --mandate refuses on code-owned paths`.
- **M4: the mandate check moves after the verdict comment**, into the approval block. It is moved, not deleted. `11 checks, 4 failed`:
  - `an expired mandate refuses before any GitHub write`
  - `null: the mandate is read before the verdict comment is written`
  - `a mandate whose scope does not cover code-owned paths refuses` (its `! wrote` clause)
  - `a mandate comment that does not exist refuses before any write`
- **M5: `proof_watch.py` drops the `--mandate` argv append.** `python3 tools/audit/seat/proof_watch.py --self-test` prints `36 checks, 1 failed`: `(a3) owner mode passes --mandate <id> to merge_pr.sh`.
- **Failing first.** The same self-test, with base `merge_pr.sh`'s body after it, prints `11 checks, 10 failed`. Only `a moved head refuses before any write` passes, because base already read the head first. The expired arm fails on `MANDATE EXPIRED` printed after `WRITE comment`, which is the incident's order.

## Null control

- **Each refusal arm has a paired arm that differs in one input and reaches the approval write**, so the `! wrote` detector can see a write when one happens:
  - expired (`until` 1 minute ago) against in force (`until` 60 minutes ahead)
  - scope `budget-raise` against scope `code-owned`
  - no `--mandate` against `--mandate <id>`
- **The live mandate, read by the gate's own `mandate_state` with `MANDATE_COVERS_CODE_OWNED`.** At 2026-10-18T16:48Z it returned `(True, 'mandate 6175172275 (scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z)')`. The same comment and thread, judged at 2026-10-29T00:00Z, return `expired at 2026-10-28T18:14Z`. Thread read: 188 #201 comments since the mandate was created, fetched page by page.
- **The unmodified tree.** Base `merge_pr.sh` refuses this mandate on any date, and only after its comment write (Failing first above).

## Figures

- `bash tools/audit/seat/merge_pr.sh --self-test`: `merge_pr self-test: 11 checks, 0 failed`, rc 0.
- `python3 tools/audit/seat/proof_watch.py --self-test`: `proof_watch self-test: 36 checks, 0 failed`.
- `python3 tools/policy/budget_raise_gate.py --self-test`: `budget_raise_gate self-test: 235 checks, 0 failed`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. The two scripts are `tests/entities.py` and `tests/harness_headers.py`, run locally with `PYTHONPATH=tests/hastub`: `harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED`; `entities.py` prints `1 of 2347 ENTITY CHECKS FAILED` at head and at base, run the same way in a worktree of origin/main `c8cc75ea9`. A `diff` of the two runs' FAIL lines (durations and temp names stripped) differs only in one negative arm, `a8:register_once`, whose fixture names are randomised. The one failure is the base's and is not this diff's. It is `graders-head-copy's delivery_status step is red only when …`. Every case returned 0, so the step under test ran the container's real `python` instead of the test's stub. This container exports `BASH_ENV=/etc/profile.d/hpo-toolchain.sh`, which prepends `/opt/hpo/venv-ci/bin` to PATH in every `bash -c` and shadows the stub directory. Probe: the step's own `run:` text with a head-only stub returns rc 1 with `BASH_ENV` unset and rc 0 with it set. CI has no such `BASH_ENV`.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok`. `python3 tests/closure.py selftest`: `ALL 115 closure shrink pins PASSED`. `node tools/policy/policy_lint.mjs`: `FIXTURE ok`. `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- **Class seams.** The rule is every site that posts an approval as the owner, or that tests a mandate window: `git grep -n -E 'pr review[^|]*--approve|"--approve"|2026-09-25T08:40Z|expires 2026' -- tools .claude dev/audit/harnesses ':!*.md'`. At base it returns four production sites:
  - `merge_pr.sh` (the hard-coded window, the hard-coded text, and the review): closed in this diff. At head the grep returns only that file's review line, which now sits behind the live read.
  - `merge_train.py` `_post_carry`: already guarded. Its caller `_carry_owner_approval` re-reads the cited mandate through `mandate_state` at the merge.
  - `merge_train.py` `approve`, the code-owned branch: **a distinct finding**, R10-TRAIN-MANDATE-LABEL. For a code-owned head that is not a raise, it posts an owner approval under `--mandate LABEL` and reads nothing: the label is free text, and no window or scope is checked. The `*_budgets.json` and policy branches do read it live. Not fixed here: it is outside this group's file scope, and the train's argument is a label, not an id. See Forward-carry.
  - The self-test stub in `merge_train.py`: not a production site.

## Red checks

none

## Unpinned sites

Every changed line is under `tools/audit/seat/`, `tools/policy/budget_raise_gate.py`'s constant block or `governance.yml`, all outside the mutation inventory. Behaviour is pinned by the self-test rows M1 to M5 turn red. CI runs `merge_pr.sh --self-test` through `instrument-self-tests`. `proof_watch.py --self-test` has no CI step, at base or here. `merge_pr.sh` past the approval (CI wait, merge, issue states) is unchanged and is driven by no hermetic test.

## Forward-carry

`merge_train.py`'s code-owned approval under an unread `--mandate LABEL` (R10-TRAIN-MANDATE-LABEL, above) is a finding for the orchestrator's next dispatch. This seat may write neither a delivery row nor an issue. The fix would have the train take the comment id and route that branch through the same `mandate_state` read its policy and raise branches use.

## Friction

- `fixer.md`: cost: on this container `tests/entities.py` fails one check at base and at head (`graders-head-copy's delivery_status step …`): the container's `BASH_ENV` (`/etc/profile.d/hpo-toolchain.sh`) prepends `/opt/hpo/venv-ci/bin` to PATH in every non-interactive bash, which shadows the test's PATH stubs. So prepr's `closures` step refuses (`failed while being recorded: tests/entities.py (exit 1)`) on any branch whose scope includes `entities.py`. It is reported here and was not worked around; the fix is the container recipe, or the test clearing `BASH_ENV` in its `env`.
- `brief`: contradiction: the brief says merge_pr.sh should read the mandate "the way merge_train.py does (its --mandate argument … read live)". The train's `--mandate` is a free-text label that its code-owned branch never reads; only its policy and carry paths read the cited id live. This fix follows the gate's reader, not the train's label.
- `environment`: cost: through this container's proxy, `gh api --paginate` on the #201 thread fails (`Numeric-ID repository paths … are not supported through this proxy`). So a live `merge_pr.sh owner` run here fails closed (`could not be read`). The live read above was taken page by page instead. On a seat with a direct `gh`, the gate's own `_mandate` is unchanged.
