## Re-cut

Round 5. This body replaces the earlier one and carries nothing from it. Its scope is only the round-4 block: `tests/replay_cost_draws.tsv` was in no audit universe and not excluded, so `governance / instrument-self-tests` went red on it, and `## Red checks` did not name that red. The code under review (the replay cost budget, as handed off at 130769e1) is not changed here; the only change since the round-4 head is one line in `dev/audit/config/scopes.json`.

The classification: `tests/replay_cost_draws.tsv` is added to D3's universe, beside `tests/replay/**`. It is test input, the recorded CI draws that `tests/replay.py` and `tools/audit/seat/replay_draws.py` read to derive and grade the replay budgets, so a finder checking the test suite for gaps should read it. D3's `s3` seat owns it through `rest`. An exclusion was the other option; it was not taken because `_coverage_excluded` is for records no seat acts on (`tests/golden/**`, past-round evidence), and this file drives a live budget.

## Head

8de8ada94587281c7c0efec290862266ae73d87c

## Mutation proof

The change is a data classification, so the mutant is reverting it. With the line removed from `dev/audit/config/scopes.json`, `python3 -I tools/audit/check_scopes.py --repo .` prints `FAIL coverage tracked=9105 in_universe=1417 excluded=7687 unclassified=1` naming `tests/replay_cost_draws.tsv`, and `--self-test` prints `SELF-TEST FAILED` with `the default verdict passes the live scopes` and `the default invocation exits 0 on the live scopes` False. With the line, both pass (below).

## Null control

The unmodified tree (this branch merged with origin/main, before the one-line edit) is the null: `check_scopes.py --repo .` exits non-zero with the one unclassified file, and `--self-test` fails on those two arms. Its other arms, which perturb the scopes (drop D10's universe, exclude a covered path, an exclusion naming nothing), are True there and at the head, so the self-test still refuses what it should.

## Figures

- `python3 -I tools/audit/check_scopes.py --repo .` at the base (merged tree before the edit): `FAIL coverage tracked=9105 in_universe=1417 excluded=7687 unclassified=1`. At head 8de8ada9: `ok coverage tracked=9105 in_universe=1418 excluded=7687 unclassified=0`.
- `python3 -I tools/audit/check_scopes.py --self-test --repo .` at the base: `SELF-TEST FAILED` (two arms False, as above). At head: `SELF-TEST passed (every perturbed scope refused)`.
- `PYTHONPATH=tests/hastub python3 tests/replay.py` at head: `ALL 197 replay checks PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/audit/seat/replay_draws.py grade --job 127046649273` at head: clean passes, cpu doubled `cpu_ratio 4.444 over its budget 3.342`, loop doubled `loop_cpu_ratio 0.2063 over its budget 0.1527`, memory doubled `peak_kib 3861 over its budget 2686`; rc 0. With `--ruler 51.5` the doubled arms are refused on ref53's 2.076.
- Draw set at head: 565 runs, 116 jobs (`tests/replay_cost_draws.tsv`, counted with a csv reader).
- `bash tools/pr/prepr.sh` at head 8de8ada9, origin/main 33e60b5b already merged: `PRE-PR: 8de8ada94587 ... rc=0`.

## Red checks

Check runs of PR head 4512d770, read over both pages (107 check runs):

- `governance / instrument-self-tests` (job 127916728606, run 42214980826) is red. Cause: this PR's new `tests/replay_cost_draws.tsv` was in no universe and not excluded, so `check_scopes.py --self-test --repo .` found `FAIL coverage ... unclassified=1`. Repaired by the D3 classification in this diff. Cheaper detector: `python3 -I tools/audit/check_scopes.py --repo .`, 1.2 s, which `tools/pr/prepr.sh` does not run (it runs only in governance.yml). Standing cost of adding it: one 1.2 s step in prepr.sh. Not built in this PR, which changes no code beyond the classification; the follow-up is in `## Forward-carry`.
- `pr-contract / pr-contract` (job 127916741200) is red for the same check, refused by the body that left it unnamed. This body names it.
- `gate` in runs 42216249923 and 42214982575 failed after that red and follow it.

## Forward-carry

- Follow-up: `tools/pr/prepr.sh` does not run `tools/audit/check_scopes.py --repo .` (1.2 s), so a new tracked file in no audit universe reaches CI and turns `governance / instrument-self-tests` red after the handoff; this PR is an instance. Carry: R10-REPLAY-COST-2
- Residual: the grading unit is still one number per job. A job whose pooled ruler reaches >= 51.12 but whose runner is a ref47 runner is graded on ref53's 2.076 and goes red. The nearest ref47 job sits at 50.07, 1.05 ms under the border; ref53's lowest is 52.17. Carry: R10-REPLAY-COST-2

## Friction

none
