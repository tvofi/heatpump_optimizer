Fix review: blocked d7b25eca474f4edde0cad8eb284c27c977a0157c architecture-unsound: pr-contract would run the PR's own merge_train.py owed-reds, unpinned, so a diff can silence its required reds; and the fail-closed rc check in requiredFromTrain survives its mutant

bus-nonce: f554c34869b7c965caf87c0497bb9090

## Block

Round 1. Measured head d7b25eca474f4edde0cad8eb284c27c977a0157c, merge base 70c15830b94a758357faa0b35f9011229a0d6a9c. The head was re-read before this verdict and has not moved.

1. **The required set's owner is read from the change under check (architecture-unsound).** `pr-contract.yml` restores its check source from the base commit, "so this job runs no pull-request program at all" (#1515, decision 0013). The restored pathspecs cover `tools/policy/*.mjs` but, under `tools/audit/seat/`, only `roster_lib.py`. After this merge, the base's `policy_lint.mjs --pr-body` spawns `python3 <ROOT>/tools/audit/seat/merge_train.py owed-reds` (`requiredFromTrain`, where ROOT is the checkout). That file, together with `gh_read.py` and `tests/fixtures/required-contexts.json` which it imports, is the **pull request's** copy. The step also has `GH_TOKEN` in its environment.
   - Drive (`ev/drive-unpinned-owner.txt`): I left `policy_lint.mjs` as shipped and edited only `merge_train.py` so that `owed-reds` prints one bogus name. A body silent on the reds `tests / typing`, `tests / fast (3.14)` and `gate` then gives `PR-BODY: 0 error(s)`. The required reds go unanswered, which is the opposite of what the ruling keeps.
   - This also contradicts the PR's own claim that the set is "read through that one owner and never copied". In CI the owner read is whatever the diff makes it.
   - Fixes that keep the architecture: pin `tools/audit/seat/merge_train.py` and what it imports in pr-contract's restore list, or have the workflow compute the set in a pinned step and pass it as `--required-file`. Either way, add an entities or self-test pin that the program pr-contract runs is base-restored.
2. **Fail-closed on an unreadable set is unpinned on its live path (mutation-vacuous at the brief's FOCUS).**
   - Mutant: `if (r.status !== 0 || !names.length)` becomes `if (!names.length)` in `requiredFromTrain`.
   - It survives `node tools/policy/policy_lint.mjs` (rc 0), `review_packet.py --self-test` (rc 0) and `bash tools/pr/prepr.sh --self-test` (514 passed, 0 failed) (`ev/mutant-drop-status-check.txt`).
   - Driven (`ev/drive-unreadable.txt`): with a `gh` that fails (403), `owed-reds` prints `REFUSE proof: ...` on stdout and exits non-zero. As shipped, that leaves every red owed (2 errors). Under the mutant, the REFUSE line becomes a one-name "set" and every red, required ones included, is owed nothing (`PR-BODY: 0 error(s)`).
   - Every fail-closed fixture drives a thunk or `--required-file`. None drives `requiredFromTrain` over a non-zero `owed-reds`.
   - The body's diff-mutant run (`mutant_run.py --cmd` over three Python self-tests only) cannot reach `.mjs` lines. So "24 mutants, 0 SURVIVED" does not cover policy_lint's new code. A fixture should run `requiredFromTrain` against a stub `merge_train.py` (or an injectable command) that exits 2 with a REFUSE line, and assert every red is owed.

## Findings

none

## Evidence

- CI: `merge_train.py classify d7b25eca474f4edde0cad8eb284c27c977a0157c --pr 3305` gave `GREEN d7b25eca474f4edde0cad8eb284c27c977a0157c pending: none red: none`, rc 0 (`ev/classify.txt`). No red check on the head, so step 11 owes nothing, and `## Red checks: none` is correct.
- Merge: `git merge-tree --write-tree origin/main d7b25eca` exits 0, tree d5ea3809abbeed7811e1b2affd741beecb057916. `LEDGER-MERGE: resolved tests/closures.json`.
- Body mutant (`return true` as the first line of `redOwed`) goes red: policy_lint acceptance rc 1 with `FIXTURE VACUOUS: with the required set known ...`, and review_packet self-test 2 failed, as the body says (`ev/mutant-returntrue-*.txt`).
- My mutants that die:
  - dropping the code-scanning alert arm: policy_lint rc 1
  - dropping the job-half arm: rc 1
  - the CLI thunk returning an empty Set on an unreadable set: review_packet self-test 4 FAIL
  - the unreadable set skipping every red: policy_lint rc 1 plus review_packet 4 FAIL
  
  Logs: `ev/mutant-*.txt`.
- Live drive at the head with the set read (`ev/drive-live.txt`): of `tests / typing`, `docs / links`, `tests / nightly-status`, `mutation` and `code-scanning alert 9 (py/y)`, the owed reds are `tests / typing`, `mutation` (the job half of `tests / mutation`) and the alert. Null control at base 70c15830 (`ev/drive-base.txt`): every red but `tests / nightly-status` is owed, which is the pre-ruling P282 exemption for a diff touching only `tests/x.py`.
- Harness `dev/audit/harnesses/r10_nonrequired_reds.py` at `--base` 70c15830 (merge base) and at dee8b413 (`ev/harness-*.txt`): rows A, B, C and D match the body exactly. This is the fixer's own instrument, disclosed as such. The finding is an owner ruling with no finder's harness, so I used my own drives above as the independent measure.
- Figures re-derived at this head:
  - `merge_train.py --self-test`: 475 checks, 0 failed
  - `review_packet.py --self-test`: 72 checks, 0 failed
  - `record_row.py --self-test`: all checks passed
  - `node tools/policy/policy_lint.mjs`: TOTAL 0 errors, rc 0
  - `merge_train.py owed-reds`: 23 names, rc 0, omitting `tests / nightly-status` and `governance / delivery-status` (`ev/owed-reds.txt`)
  - `rules_sync.mjs --check`: RULES-SYNC ok, so the `.claude` and `.cursor` copies are in sync
  - prepr `--self-test`: 514 passed. This was taken with one `requiredFromTrain` line mutated that no prepr fixture reaches, so it is not a pristine-head run.
- Not re-derived, heavy (CI is cited instead): the `entities.py` 3-failure claim and the 1018 s `mutant_run` of 24 mutants.
- VERSION, the manifest and RELEASE_NOTES.md are untouched.
- The policy files change, so this PR merges only on tvofi's approving review. This seat posted nothing.
