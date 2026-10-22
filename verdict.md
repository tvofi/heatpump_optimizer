Fix review: merge 9ebc80551588c69ebd607c1fd8f9fdb6de993512

bus-nonce: b31bf36ebe541343b0a71be5b4004b50

## Round

Second fix review of PR #2558 (R10-PLAN-ARTIFACT), after `blocked mutation-survivor` at `59c5b20ef0d7beef377fe2580bd87f9fdb783ff7` (`origin/review/2558`, `probe/rev-2558-e98d4b97`). The fixer's own count puts this at fix round 3 plus the orchestrator's main merge, so it is not yet the fourth round that owes a re-cut. Measured at head `9ebc80551588c69ebd607c1fd8f9fdb6de993512`, from a detached worktree. The PR's base and merge base are `b0f134142de15b37dcada9accc7dff19ed185d3b`. origin/main was `46e3681276f99e8d3e4d12e9d316a46946f666d7` at measurement. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current. The PR head was still `9ebc8055` when I read it for this verdict.

## Findings

- The body's prose has two unclosed parentheticals. In `## Head`, "(see `## Red checks" never closes, so the round-3 narrative ("Every figure below was re-taken ...") renders under a first `## Red checks` heading, and the real `## Red checks` appears again further down. In `## Figures`, "(see `## Forward-carry` (`python3 ...`" also never closes. No figure or answer is lost: `pr-contract` is green at this head and every figure is re-derived below. Carry: dismissed: prose formatting only, contract check green (item F1)
- The body states its figures at `6d981d0d`, not at this head. I re-took each one at `9ebc8055` and every one matches. The only difference is `ci_predict.py`'s named base, `b0f134142de1` here against `5a755f53efda` in the body, which is expected after the main merge. Carry: dismissed: re-derived equal at head (item F2)
- The live-page figures (108 rows, the stage counts, 11 of 14 open PRs) are not re-derived. They rest on an uncommitted, hand-assembled GitHub snapshot, and the body says so. Production code is unchanged since round 1. Carry: dismissed: disclosed in body, no committed snapshot (item F3)
- There is no finder harness. On the roster, R10-PLAN-ARTIFACT is a tooling group with `findings: []`, `issues: []` and an empty `architect_note`. Every arm here is the fixer's or a reviewer's, and my driver (`ev/reviewer_mutants_driver.py`) is my own instrument, extending the round-1 reviewer's anchors. Carry: dismissed: tooling group without finder (item F4)
- Work owed after the merge, on R10-ORCH-MACHINERY item (3): drive the page from `state_docs.py`, add an UNAVAILABLE page if the design still wants one, add the generator-defect fixtures, and retire the out-of-tree `gen.py`/`tpl.html`. This is carried on `origin/handoff/audit-r10-roster` `2ce05426410f8606267d3e4ce1857fcb0e61294a` as "From #2558 (R10-PLAN-ARTIFACT ...) ... Control: plan_page.py --self-test re-measured at that stage's merge base, as a precondition." (`ev/roster_carry.txt`). Carry: R10-ORCH-MACHINERY (item F5)

## Evidence

- Mutation proof (step 1), with my own driver `ev/reviewer_mutants_driver.py` and output in `ev/reviewer_mutants.txt`. Each mutant is applied alone at this head, both self-tests run, and the file is restored byte for byte (`git status` clean afterwards).
  - RESULT mutant=M0 verdict=null rc=0/0: `plan_page self-test: 41 checks, 0 failed`, `self-test: 0 failed`. This is the null control, the unmutated tree passing the same tests.
  - RESULT mutant=B-model-record-refusal verdict=killed rc=1/0. `FAIL a fresh plan recording no duration model is refused, nothing written (got: ('raised KeyError', False, False))`. The arm treats the crash as a failed refusal, so its assertion is what goes red.
  - RESULT mutant=C-check_plan-dropped verdict=killed rc=1/0: `FAIL a fresh plan that check_plan refuses is refused, nothing written (got: (0, True, False))`, plus the knock-on `FAIL a stale plan is refused, nothing written (got: (1, True))`.
  - RESULT mutant=D-caption-drawn-count verdict=killed rc=1/0: `FAIL the caption counts the links drawn (none drawn, one left) (got: ['1 of 1 critical-path links'])` and `FAIL the caption counts the links drawn (one drawn, none left) (got: ['0 of 1 critical-path links'])`.
  - RESULT mutant=E-ref-override-ignored verdict=killed rc=0/1: `FAIL an explicit ref is read instead of generated.roster_ref`, `FAIL --check --roster-ref passes the plan at the ref it names: rc=1`.
  - RESULT mutant=A-blobless-accepted verdict=killed rc=0/1: `FAIL a plan pinning no roster blob is refused as unknowable`.
  - Mutants of my own, which test the body's claim that a constant caption fails: RESULT mutant=D2-caption-constant-0 killed by `(one drawn, none left)`; RESULT mutant=D3-caption-constant-1 killed by `(none drawn, one left)`; RESULT mutant=C2-check_plan-truncated (`check_plan(plan)[:0]`) killed by the check_plan arm.
- The fixer's driver `python3 dev/audit/harnesses/r10_plan_page_mutants.py` at this head printed M0 null, then 18 rows killed and `RESULT survived=0`, the body's "18 mutants plus M0" and "19 rows" (`ev/figures.txt`).
- Figures re-measured at `9ebc8055` (`ev/figures.txt`):
  - `plan_page self-test: 41 checks, 0 failed`; `replan.py --self-test` `self-test: 0 failed` with 41 `ok` lines.
  - `selftest_wiring: 73 self-testing, 73 wired, 0 unwired`; `STRUCTURE RATCHET PASSED`; `ALL 124 closure shrink pins PASSED`; `layout self-test: ok`; `claims hygiene: origin/main ok`.
  - `CI PREDICT: no closures or fast red predicted against b0f134142de1`; `Architecture score: dS +0.0000 NULL`.
  - `throwaway_git: 0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`.
  - `ALL 2382 ENTITY CHECKS PASSED` (venv-ci, `PYTHONPATH=tests/hastub`).
  - `ALL 109 HARNESS HEADER CHECKS PASSED` (venv-ci); `closure: no test file defines a symbol production also defines` (`no-copies`); `closure.py select --diff b0f134142`: `MODE: FULL`, reason `tests/closure.py changes the gate itself`, as the body states.
- Step 5: `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden` are untouched in the three-dot diff from `b0f134142`. No claim file is touched, so step 4 has nothing to compare.
- Step 13: `git merge-tree --write-tree origin/main 9ebc80551588c69ebd607c1fd8f9fdb6de993512`, with origin/main at `46e3681276f9`, exited 0 with tree `5e475ec6f538527d82b635b302a0ad49ddd1e986`. It is clean and no MERGE-CLAIM line was emitted.
- Step 10: the forward-carry is on the roster with its control stated as a precondition, as quoted in item F5. The round-1 `carry-missing` block is settled.
- Step 14: the diff moves one instrument, `tests/closures.json`, by one INERT READS entry for the new file `tools/audit/seat/plan_page.py`. That entry is the classification CLAUDE.md requires of a new tracked file, and `ci_predict` predicted the closures red without it. No budget file changes.

## Red checks

Read per commit from the check-runs API for `9ebc80551588c69ebd607c1fd8f9fdb6de993512`: 46 runs, all concluded (`ev/ci_check_runs.txt`). `closures` (job 119556985403) was in progress at my first read and is now `success`.
- The only `failure` is `nightly-status` (job 119547580705). Its log grades main's scheduled run 39563978649 (`mutation-nightly failure`, `slow failure`), which is the run the body's `## Red checks` names and answers as main's, owned on main. This diff does not reach `tests.yml` or `tests/nightly_status.py`. The log itself says it is not one of the required contexts on `main-protect` and does not block. A `pr-contract` run (job 119547753712) started at 23:35:33Z, after that red concluded at 23:35:31Z, and passed. So the body was checked against it. Carry: dismissed: grades main, answered in body (item R1)
- `mutation` is green. The diff writes no production line under `custom_components/`, so no mutant is drawn. The lane's conclusion is evidence only, and the step-1 proof above rests on my local mutants. Carry: dismissed: no production line drawn (item R2)
- The `ci-ratchet` red on main named in the brief (runner-speed variance, R10-CI-LAYOUT) is not on this head's runs, and this diff does not touch its inputs. Carry: R10-CI-LAYOUT (item R3)
