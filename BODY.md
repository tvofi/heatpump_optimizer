Root-cause seat for #2883's red-check trigger (R10-FLOW-BOARD). This PR runs beside the fix and never inside it (`dev/governance/roles/root-cause.md`). The full analysis is `dev/audit/rca/R10-RCA-CLOSURE-ARGV.md`, and it is registered in `dev/audit/config/bugclasses.json` `_rca`.

**Defect.** `tests / closures` went red twice on #2883. Both times it was `INERT READS UNDER-APPROXIMATED` for `tests/entities.py`:

- run 40548660478 at `8f05b74d4`, on `tools/audit/merge_throughput.py`;
- check-run 122599859589 at `71987ff1e`, on `dev/programme/rosters/critical-path.json` and `wave-r9-groups.json`. That run was FULL scope and took 35 min 10 s, `closures-autofix` answered `skip-manual-repair-owed`, and the round-3 review blocked on it.

`tools/pr/ci_predict.py` was quiet on both heads.

**Cause.** `tests/entities.py` runs the self-tests of `state_docs.py` and `roster_lib.py`. `closure._exec_record` records what those runs read, including every argv token that names a repo file:

- in round 1, `state_docs.py` spawns `merge_throughput.py`, so the read was real;
- in round 3, `roster_lib.blob_at`'s self-test passes two roster paths to `git ls-tree` in a temp repo, so the read was an over-approximation.

The predictor's unit is the static top-level import edge, so it cannot see any read a run makes.

**Process state: (c).** Step 6d ran and passed on both heads, but its unit does not reach a run-time read. The cheaper detector that existed was `--single`, at 868 s to 913 s, and the heavy-scripts rule keeps it out of every local path.

**Countermeasure.** `ci_predict.py` gains the arm SELF-TEST READS, turned on by `--record-self-tests`. `prepr.sh` step 6d passes the flag through `predict_line`'s fifth argument. `body_push.sh` and every other caller stay static. For each changed file that carries `--self-test`, and each host script whose `closures` entry lists that file (never `inert_reads` alone, never the file itself) and whose source runs its self-test:

1. It records `<file> --self-test` with CI's recorder, `closure._exec_record`, with a 180 s timeout. A timeout prints a `NOTE` and never a red.
2. It grades that record as the host's with CI's own `closure.check(partial=True)`.
3. Each pair `check` names prints as `PREDICT tests / closures SELF-TEST READS ...`. The repair line names INERT_EXCEPT plus `--single`, the route #2883 took.

**Cost test** (`dev/audit/rca/R10-RCA-CLOSURE-ARGV.md` section 5):

- One recurrence costs about 85 min: a 35 min red run, a 15 min `--single` and a 35 min review round.
- In 300 R10 PR merges over 7 days, 4 reds had this shape and 2 are demonstrated catchable.
- The standing cost is 0.5 s to 29 s for each changed hosted file. Measured over the same 300 PRs, it was 63.4 s in total, spread across the 15 PRs that touched one.
- With the closures-only rule, no false red occurs. Round 1's rule would have refused 4 merged PRs falsely (review 1's count).

Verdict: build it.

No policy text changes, no budget changes, and no claim file, `VERSION`, manifest or `RELEASE_NOTES.md` is touched. The new file `dev/audit/rca/R10-RCA-CLOSURE-ARGV.md` is classified: `closure.is_inert` returns True, which is the `dev/audit/` prefix.

## Head

`43e474b3a7c598d68d789247baf38f64dfc555a8` merges origin/main `71fe1f7fcaeadd448a3e2213744f68b3e680e24e` into `7f29ac144`. That commit merges the PR's previous head `0d6c82965f056081c30e2cf1938597fde42dc643` (the delivery row) into `d2e0d88f7`. Both merges are automatic: main's delta touches none of the PR's files. Everything marked round 2 below was measured at `8ad983385` and `d2e0d88f7`, three-dot over `71fe1f7fcaeadd448a3e2213744f68b3e680e24e...43e474b3a7c598d68d789247baf38f64dfc555a8`.

**Round-2 delta (review 1, `blocked 0d6c82965 null-control`).**

- `8ad983385`. `self_test_hosts` counts a host only when its `closures` entry lists the file, never `inert_reads` alone, and never the file as its own host. Review 1 measured round 1's rule at 10 pairs, not 8. The two extra were `budget_raise_gate.py` and `selftest_wiring.py`, which sit in `tests/entities.py`'s `inert_reads` only, and each gave a false red on a green tree.
- `8ad983385` also adds:
  - three null arms to the arm's self-test: an inert_reads-only host, a self-test named one line past the window, and the file as its own key;
  - a host that names the self-test on the next line, which kills window 0;
  - two `prepr.sh --self-test` pins on 6d's wiring;
  - the quiet line under `--only self-test-reads`, and `notes` kept across `--apply-inert`'s re-predict.
- `d2e0d88f7` updates the RCA's sections 4 to 6: the null sweep re-run over the shipped code, the cost test with false reds counted, and the mutation proof.

## Mutation proof

Round 2 (`ev/mutants-r2.txt`). The seat's driver asserts each replacement matched once, runs `self_test_reads_self_test` and restores the file, and `cmp` with a pre-run copy is identical afterwards. **8 of 8 are killed, including review 1's three survivors:**

- R2, window 0: 4 FAIL.
- R3, round 1's closures-or-inert_reads host rule: 3 FAIL.
- R6, a file may be its own host: 2 FAIL.
- M1, the host rule always true: 2 FAIL.
- M2, a failing `check` skipped: 2 FAIL.
- M3, a recorder failure graded: 1 FAIL.
- M4, the INERT header unparsed: 1 FAIL.
- M5, an unchanged file recorded: 1 FAIL.

The unmutated run exits 0.

**The 6d wiring pins.** The two new `prepr.sh --self-test` pins check that 6d passes `record` and that `predict_line` maps `${5}` to `--record-self-tests`. Their predicates (`ev/pin6d.sh`) print `6d-record=0 predict_line-maps=0` on this prepr.sh. With 6d's `record` removed they print `6d-record=1`, and with `$rec` dropped from the predictor's command line they print `predict_line-maps=1`. `prepr.sh --self-test` itself was not run under this load; it is CI's.

**The detector shown on the defect, re-run with the round-2 rule.** Head `ci_predict.py` was copied into detached worktrees of #2883's heads, then `--only self-test-reads --base 00ab2e97b^1` (`ev/demo-r2.txt`):

- At `8f05b74d4`: rc 1, `SELF-TEST READS INERT tests/entities.py: tools/audit/merge_throughput.py`, via state_docs.
- At `71987ff1e`: rc 1, `critical-path.json` and `wave-r9-groups.json`, via roster_lib, the pair CI named.
- At the repaired `7b071dbd7`: rc 0.

## Null control

**Round 2, over what the code ships.** This figure has no command a reader can run: it rests on the seat's driver `nullsweep2.py`, outside the tree, and its log `nullsweep-r2.txt` in the seat scratch `ev/`. The driver calls the head's own `ci_predict.self_test_hosts` and `self_test_reads`. At this branch's tree on merge base `6d86acc90`, the head's own `self_test_hosts` and `self_test_reads` ran over every tracked `.py` carrying `--self-test`, each treated as the only change. The result is `self-testing=95 pairs=8`, and each of the 8 prints `preds=0`:

- `ci_ratchet.py`, `archscore/gate.py`, `record_row.py`, `roster_lib.py`, `state_docs.py`, `tools/ci/gate.py`, `ledger_merge.py` and `stamp.py`;
- each hosted by `tests/entities.py` or `tests/arch_score.py`.

`budget_raise_gate.py` and `selftest_wiring.py` are no longer hosted.

**Round 1's sweep** at `6349205b6` graded 38 file-host pairs from `closures` listings. The 11 rc-1 pairs are scripts that list a file as text and never run it, which is why the host rule exists.

**The self-test's null arms** all pass:

- `null control: a record inside the host's closure is not`;
- `null control: a file the diff does not change is never recorded`;
- the inert_reads-only, past-the-window and own-host plants inside the first arm.

## Figures

- three-dot diffstat, 5 files changed, 480 insertions(+), 17 deletions(-): `git diff --stat 71fe1f7fcaeadd448a3e2213744f68b3e680e24e...43e474b3a7c598d68d789247baf38f64dfc555a8`
- the arm's self-test, 5 `ok` lines and rc 0: `python3 -I -c "import sys; sys.path.insert(0, 'tools/pr'); import ci_predict as c; from pathlib import Path; sys.exit(c.self_test_reads_self_test(Path('.').resolve()))"`
- the new file is INERT, `True`: `python3 -c "import sys; sys.path.insert(0, 'tests'); import closure; print(closure.is_inert('dev/audit/rca/R10-RCA-CLOSURE-ARGV.md'))"`
- round 1, at `c68b62203`: `ci_predict.py --self-test` prints 32 `ok` lines and the 5 AGREEMENT FAILs the base `6349205b6` prints too, and CI's instrument-self-tests job 122773548310 prints `ci_predict self-test: 0 failed`: `python3 -I tools/pr/ci_predict.py --self-test`
- the cost-test and class-search figures are each named with their command in `dev/audit/rca/R10-RCA-CLOSURE-ARGV.md` sections 4 and 5

## Red checks

none

## Forward-carry

none

## Friction

none
