Fix review: blocked 7e197a6fd2af676203ee5ed30fc97f8214c2de87 null-control-unpinned: stress.py timing_check's env read survives a mutant that exempts the gate; body-false: ## Approval says no CODEOWNERS file, three are code-owned

bus-nonce: 5b430c1bb707f61bdd7ec6bac9c69ae9

Reviewer seat r9c-rev-2018, round 1. Measured head 7e197a6fd2af676203ee5ed30fc97f8214c2de87, which is still the live head at posting. Merge base 59b5ac6e. The review ran from a detached worktree at that head. Load was about 215 to 250, so no heavy run was made locally, and every heavy figure below comes from CI check-runs at this head.

## Blocking

**1. The guard that keeps the exemption out of the gate is not pinned.** The body's null control says stress.py's pin `(1, 0, 1)` means "the exemption cannot make a graded run green". The pin does not test that. All three of its calls pass `recording=` explicitly. The one line that decides grading versus recording, `recording = os.environ.get(CLOSURE_RECORDING_ENV) == "1"` (tests/stress.py:790), is never executed by any pin.

I used my own harness, `timing_check_mutants.py`. It extracts `timing_check` from the head, replays stress.py's pin against each mutant, and adds a gate-shaped call with the env absent and `recording` omitted.

```
RESULT mutant='T2 env read inverted'        stress_pin=pass gate_miss_fails=False -> SURVIVES
RESULT mutant='T3 env default to recording' stress_pin=pass gate_miss_fails=False -> SURVIVES
```

T3 (`recording = True`) makes every gate run print, rather than fail, all six timing verdicts. That is exactly the leak this PR has to rule out. Neither the closure.py selftest, which checks only the constant's spelling, nor the mutation lane, which mutates only `custom_components/`, reaches that line.

The fix is a few lines in the same pin. Call `timing_check("probe", False, results=X)` with `recording` omitted, twice: once with `HPO_CLOSURE_RECORDING` popped from `os.environ`, where it must count a failure, and once with it set to `"1"`, where it must count none. Then restore the environment.

**2. `## Approval` is false.** It says "This branch changes no file under `CODEOWNERS`". On origin/main (f060cb4c), `.github/CODEOWNERS` lines 138, 140 and 150 assign `/tests/closure.py`, `/tests/derive_closures.sh` and `/tests/stress.py` to @tvofi. GitHub has already requested tvofi as reviewer. The body must say these paths need the owner's approving review, so the orchestrator routes the PR correctly.

## Verified (re-derived, not taken from the RCA seat)

- **Scope of `HPO_CLOSURE_RECORDING`.**
  - `git grep` shows exactly one setter: `record()` in tests/closure.py writes to a copied `env` dict, never to `os.environ`, so the selftest process does not inherit it.
  - It has exactly one reader: stress.py's `timing_check`.
  - run.sh's `lane_stress` runs stress.py directly. No workflow sets the variable, and it is not in my shell.
  - Only derive_closures.sh, through tests.yml's `closures` job, reaches `record()`, and nothing grades from a recording's verdicts.
  - CI at this head bears this out. `fast (3.14)` (job 112782299434) printed 0 `not graded under` notes, and all six timing verdicts appeared as counted `ok` lines. stress.py's new pin passed, and the run ended `ALL 105 STRESS CHECKS PASSED`.
  - The exemption covers exactly the six `timing_check` sites (AST count at head: 6). The memory-peak checks stay counted.
- **rc capture.**
  - `rc_semantics.txt`: `false; echo "[$(date)] (exit $?)"` prints 0, and `local rc=$?` on its own line prints 1.
  - `closures_37564484318.log`: all 33 `done` lines read `exit 0`, while the artifact's `stress.py.json` has rc 1.
  - At this head, the `closures` job (112782396363) logs `done tests/stress.py (exit 0)`, which is now the real exit, and the job is green.
  - Mutation proofs from `mutants_closure.txt`:
    - Reverting derive_closures.sh fails the `exit 3` pin.
    - Dropping the env assignment fails the probe pin.
    - Renaming stress.py's constant fails the name pin.
    - The head passes 36 of 36.
- **Replay claim, reproduced with my own `replay.py`** at #1987's head 95ad5034, on freshly downloaded artifacts:
  - All 3 runs give `skip-failed-recording` in the before arm and `changed` in the after arm, and the after arm adds `quiet_windows.py`.
  - Every stress FAIL line is one of the 6 timing_check names.
  - Caveat, which the PR discloses: the after arm forces rc to 0. It is a simulation of the countermeasure, not a recording made under it.
- **Cost test.**
  - The 5 attributable runs fall between 2026-10-05T19:01Z and 2026-10-07T02:57Z. 5 / 2.1 days × 70 min ≈ 167 min a day. That matches the body's 165.
  - Over the whole 10.4-day window it would be about 34 min a day, and the test still holds.
  - The standing cost depends on load. At load 216 I measured selftest medians of 1.96 s at the base and 2.55 s at the head, or +0.6 s. The body gives +3.7 s at load 450.
  - Either way the countermeasure costs far less than the defect, so the verdict on the cost test stands. I did not re-derive the 700-run census and use its figures as quoted.
- **Policy.** This changes nothing `ci-autofix.md` promises. The rule says `skip-failed-recording` means the named script stopped. The PR makes that true for stress.py by removing a false positive, and makes the `closures` log name the script. No policy file is in the diff, and `policy-docs` is green. `## Approval` is owed for CODEOWNERS (finding 2), not for policy.
- **Red checks.** `delivery-status` is OVERDUE on #2001, which is main's. `nightly-status` reports last night's main lanes. Neither reads this diff, and the body answers both.
- **Other checks.**
  - `merge-tree --write-tree origin/main HEAD` exits 0.
  - `VERSION`, the manifest, the notes heading and both claim files are untouched.
  - The body names head 7e197a6f.

## Not checked

- The 700-run class census.
- `coverage`, which was still in progress at posting.
