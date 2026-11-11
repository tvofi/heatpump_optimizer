# BLOCKED: no pin can be measured at this head while `tests/features.py` is red on main

Code head: bf9707ae03044f329bdbc5c3ce8d3249c51f955b on refs/heads/handoff/r10-duty-switch-restart-learning, unchanged by this seat. No ledger file is written: zero of the 109 sites `--pin-killed` lists are pinned.

Question: may the head merge `origin/main` once pull request 3466 is on it, although `git merge-tree --write-tree origin/main HEAD` reports no conflict (exit 0 against 0e28afd38b353ca8e66269d9ae4be8614fcf5cfb)? That merge is the one route to a pin: with it `mutation-autofix` pins on the pull request by itself, or a seat runs `--pin-killed`. The brief allows a merge on a conflict only, so this seat did not take it, and 3466 is not on main yet (`git log --oneline origin/main | grep -c "#3466"` prints 0).

## Scope item 2: why `mutation-autofix` reports `skip-measure-failed`

Cause: `tests/features.py` is a driver of every site of this diff and its baseline is red at the head, on the `combi_type_branch` census this branch inherits from its merge base cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf (main's red, fixed by pull request 3466 at c0dec53cf1847e97cda8421352d580f49d2dceba, which touches the six lines the census names and none of this diff's). On a red baseline `tests/mutation_table.py` prints `MUTATION TABLE INCONCLUSIVE`, scores no mutant and prints no `PIN KILLED: <n> pinned` line; `measurement()` reads a missing summary line as `skip-measure-failed`, and `merge_pin_shards` ranks that status over every other but `measured`. The twelve `mutation-pins` shards are green because the measure step ends `|| echo`, and the pin run itself exits 0.

Measured here, at bf9707ae0, `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --shard 1/4 --jobs 4` (exit 0, 28 of 109 sites, `git status --short` empty afterwards):

```
  baseline tests/features.py: rc=1 failed=2 462s
MUTATION TABLE INCONCLUSIVE
  - the baseline is already red in tests/features.py, so no mutant's verdict means anything. Fix the suite first. [...]
      tests/features.py: combi_type_branch census: [...]  [slugs: []; vendor: ['const.py:812', 'const.py:1595', 'heat_curve.py:72', 'pump_arbiter.py:260', 'pump_arbiter.py:1019', 'thermal_model.py:1870']]
```

On the pull request (job 130538473389, run 43011652325, head e277df592e678982bb22fb48644482e30b5b86c7): `shards merged: skip-measure-failed`, `AUTOFIX: skip-measure-failed`. Which shard carried the status was not read from the twelve shard logs; the local run reproduces the path on shard 1 of 4.

Not fixed here, and why: the cause is main's, in lines of `const.py`, `heat_curve.py`, `pump_arbiter.py` and `thermal_model.py` this group does not own, and pull request 3466 already holds the fix. Driving with `--scripts` less `tests/features.py` would leave the run conclusive and every site the section kills unpinned as a survivor: the section's checks live in that script. Pinning from a tree other than the head is what the body rule "`pinned` only if `--pin-killed` ran on this head" refuses.

The census is the script's only red at the head: `PYTHONPATH=tests/hastub python3 tests/features.py` at bf9707ae0 exits 1 with one `FAIL` line, that check, and ends `1 of 5283 FEATURE CHECKS FAILED`. The pin run's `failed=2` for the same script is its own copy's count and its second failure was not identified; the previous body records that a `git archive` copy also fails the `recorded_at` check, which would account for it and was not re-measured here.

## The other scope items

1. Pins: owed, blocked as above. The previous body's ledger-operator run (109 `KILLED` by the section, `SURVIVED NULL`) predicts no survivor; that is `mutant_run.py`'s verdict, not the ledger's.
3. The fast red: the body on handoff-body f37dc235e already names `tests / fast (3.14)` under `## Red checks` as main's census. It does not yet name pull request 3466 as the fix, nor this cause for `mutation-autofix`; both go in at the re-take.
4. The review block at 5289e1fee: answered by round 2 (491e272a4, 4bd4edb40, 68a6ba2b3), whose body lists each of the nineteen `rv_` mutants `KILLED` at bf9707ae0. Not re-run by this seat: the head has not moved since that run.

`governance / instrument-self-tests` is red on the pull request and is not in `merge_train.py owed-reds`' set; it is owed no answer.

## Added by a second fixer seat of this round (2026-11-11, origin/main 50e4b1aa259827e0c74366bc45d065c26e3cc86c)

The Question above stands unchanged; this seat adds evidence only. Code head still bf9707ae03044f329bdbc5c3ce8d3249c51f955b, no ledger file written, nothing pushed to `handoff/` or `handoff-body/`.

- The shard that carried the status, read from the pull request's run 43011652325: `tests / mutation-pins (8)`, job 130495883117, prints `baseline tests/features.py: rc=1 failed=2 344s`, `MUTATION TABLE INCONCLUSIVE` with the `combi_type_branch census` line and its six `vendor:` sites, then `measure: skip-measure-failed, 0 anchor(s)`, and uploads a 403-byte artifact. All twelve artifacts the autofix job downloads are 403 bytes (job 130538473389's download list), so none carried a pin.
- Scope item 3's evidence: main's own failing run is 43010208881 (push, head ee64358be7eeccaec5178a923cb3b83a18a924a0), whose `tests / fast (3.14)` is job 130489628669, conclusion failure. Read from main's run list; the job's census line itself was not read from that log.
- Pull request 3466 is still not on main: `git merge-base --is-ancestor 97cb87c70 origin/main` exits 1 at 50e4b1aa2.
- A prediction, not a pin: on a scratch tree of bf9707ae0 with 3466's diff to `custom_components/` and `tests/features.py` applied (never pushed), `--pin-killed --base origin/main --scripts tests/features.py` reads `baseline tests/features.py: rc=0 failed=0` and its null control survives; shard 1 of 4 under a 55-minute budget ended `PIN KILLED: 21 pinned, 7 left unpinned (0 survived, 7 not started for the budget, ...)`. Had the census not been the cause, that baseline would have stayed rc=1. Those 20 ledger files were discarded: `ci-autofix.md` allows `pinned` only where `--pin-killed` ran on this head. Cost to expect once the head can be measured: about two minutes a mutant on four workers against that one driver, so the 109 sites need several budgeted passes or the pull request's own shards.
