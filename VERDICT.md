Fix review: merge 5bb7710c1c347a7969b2319d97575eb4f15f8151

bus-nonce: 5d5d6d21cda2ca8de409bb419b6446b2

Round 1, full review. Measured at head 5bb7710c1c347a7969b2319d97575eb4f15f8151 (merge-base with origin/main 56630e7e6, merge-tree exit 0, no conflict).

## Head

5bb7710c1c347a7969b2319d97575eb4f15f8151. Body names the same head. origin/main is the base 56630e7e6; the diff is 11 files.

## Red checks

Whole check-run set at the head (55 runs, one page): concluded failure = `budget-raise-gate / budget-raise-gate` (two runs) and `gate` (two runs; the gate log reads only `FAIL budget-raise-gate / budget-raise-gate: failure`). The body names budget-raise-gate and answers it (frozen key `ruler.mypy`, gate reads the diff alone, no cheaper detector). merge_train classify printed `RED ... red: gate` rc=1 because `gate` aggregates that one check; its only underlying red is the raise's approval, so judged APPROVAL-OWED (GREEN) as the brief instructs. pr-contract success. tests / fast (3.14), coverage, closures, typing, mutation, arch-instrument, browser, env-matrix, instrument-self-tests, CodeQL: all success.

## Unpinned sites

None added by this diff (body: prepr step 6d lists none; the diff adds no production line beyond two annotations).

## Pins versus #3088

Pin sets of the four requirement files compared name==version against #3088 head bffd45a03 (refs/pull/3088/head): identical in build, ci and coverage; typing differs in exactly one line, homeassistant-stubs 2026.9.3 here against 2026.10.0, which the body explains (deprecated empty release; census 0 -> 70 errors) and carries to #201. Against main, the package-name sets are identical in all four files: nothing added or dropped. Installs: `pip install --dry-run --require-hashes` on Python 3.14.7: ci lock with the build constraint exits 0; typing lock --no-deps exits 0; coverage lock exits 0. Null control: main's coverage lock (7.13.1) also resolves, and the body's #3088 coverage hash mismatch is the stale-hash defect fixed here. A full typing venv was built from the head's lock.

## custom_components edits

learner_progress.py and snapshots.py each add a local annotation of the loop variable before `for ... in reversed(...)` (`Mapping[str, Any]`, `dict[str, Any]`) plus a comment. No runtime behaviour change. `tests/features.py` and `tests/entities.py` run at the head: rc 0 both. Mutation: removing the snapshots.py annotation makes the ruler's mypy invocation print 1 error; restored, `python tests/typing_ruler.py --mypy` in the lock-built venv reads ALL 9 typing-ruler checks PASSED, errors did not grow (0).

## typing_budgets.json

One line: `ruler.mypy` 2.3.1 -> 2.4.1. It is the pinned toolchain version, not a cap; `census.errors` stays 0, by_code empty, type_ignores 0. Neither lowers nor raises a budget number; it is the frozen-key edit the Raise justification section names, and the brief says the approval follows the verdict. Payments: none exist in code (holding mypy at 2.3.1 would drop a clean bump). Architecture score dS +0.0000 NULL, re-run here.

## Seat scripts

seat_venv.sh and cloud-setup.sh read the homeassistant pin from the typing lock instead of a literal; no host path added (grep of added lines for /home, /Users, /root, /opt/hpo: none). Self-tests: seat_venv 25 checks 0 failed; cloud_setup 13 checks 0 failed. Mutation: replacing `$ha_pin` with the old literal in check() gives FAIL on "--check accepts a venv-ha at the typing lock's homeassistant pin (2026.10.4)", 25 checks 1 failed; restored 0 failed. `cloud-setup.sh --check` OK in this seat.

## carry-201.json

A record, not code. Parsed JSON: the first 21 carries and `_comment` and `issue` are equal to main's; two carries are appended (stubs hold-back; owner re-paste of cloud-setup.sh) and `stage` extended. See the reindent finding below.

## Standing checks

`python3 tests/structure.py`: STRUCTURE RATCHET PASSED. Scoped gate: `MODE: FULL` (requirements-build.txt changes the gate). Delivery row dev/programme/delivery/3147.md added, one line, three-dot diff. Claim files, tests/golden, VERSION, manifest, RELEASE_NOTES: untouched (empty three-dot diff). No closing keyword for #3088 (body says "Supersedes"). carry_audit in the packet: 3 items, 3 routed, 0 unrouted. Round 1.

## Findings

- carry-201.json was rewritten with one-space JSON indentation where main has two, so the three-dot diff shows 178 insertions and 164 deletions for a 15-line semantic change and hides the appended carries from a line review (content verified equal by parsing). Not blocking. Carry: dismissed: content verified equal by parsing; formatting only, no behaviour or record change

## Evidence

Files under ev/: HEAD.txt, pindiff.txt, vs3088.txt, names.txt, pip dry-run outputs, structure.txt, mode.txt, ver.txt, merge-tree.txt, seat self-test outputs, mutation outputs, typing-head.txt, features.txt, entities.txt, classify.txt. CI figures cited, gate and mutation not re-run.
