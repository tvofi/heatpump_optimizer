# R10-RCA-CI-RATCHET-RUN-NAME: the ci-ratchet grade keyed on a run's `.name`, which the umbrella's run-name rewrites

The root-cause seat for the red `tests / ci-ratchet` on `main` from `d5dc3e26a`. It ran beside
the fix (`handoff/r10-ci-ratchet-artifacts`) and not inside it (`dev/governance/roles/root-cause.md`).
Every time below is UTC. Every log was read from the Actions API at 2026-10-24 08:35Z.

**Defect.** `tests/ci_ratchet.py` took a run for the umbrella's only when `.name == "CI"`
(`run_minutes`, `gather_runs`). `ci.yml` sets `run-name:`, so a push run's `.name` reads
`CI code pr=- base=- sha=<sha>`. Each umbrella run therefore read as another workflow's run.
Once the newest 8 push runs were all umbrella runs, the window held no measurable run and
`critical_path_minutes` refused: `ci-ratchet: no completed push CI or Tests runs in runs.json;
cannot derive critical_path_minutes (fail closed)` (job 120755282204, run 40052726602).

## 1. Cause, reproduced

- **Latency is exactly the window arithmetic.** `PUSH_WINDOW` is 8 and the window is sorted by
  `created_at` across `ci.yml` and `tests.yml`. The first umbrella push run on `main` is
  `b927f431a` (23:53 on 10-23). The pre-umbrella `Tests` push runs stopped at 23:20. At the
  `ci-ratchet` job of `d5dc3e26a`'s run (created 02:05, grade at 02:36) the 8 newest were the 8
  umbrella runs `b927f431a`..`15f0b5924`, the last two created 02:20 and 02:22 while that job
  ran. Earlier jobs still saw 1 or more `Tests` runs and passed: job 120752118657 (run
  40051607763, 6 umbrella and 2 `Tests` runs in its window) is green. `tests.yml`'s runs carry no `run-name`, so `.name == "Tests"` kept
  working.
- **Reproduced against the API shape.** `gh api repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?event=push&branch=main`
  returns `name` = `CI code pr=- base=- sha=...` and `path` = `.github/workflows/ci.yml` for
  every umbrella push run (10 runs listed). The base `run_minutes` returns `None` for such a
  run (`name` not in `("CI", "Tests")`), and `critical_path_minutes` refuses on an all-`None`
  window. The fix keys on `path`, which `run-name` does not rewrite.
- **Which side moved.** `git log -S'run-name'` shows `run-name` entered `ci.yml` in `85d13b859`
  (U0c, 23:18:40 on 10-22). The reader's change is `9262e6f43` (U9a, 23:16:49), a cherry-pick of
  `77f97545c`. In `77f97545c`'s tree `ci.yml` has 0 `run-name:` lines (`git show
  77f97545c:.github/workflows/ci.yml | grep -c run-name`). So U9a was written, gated and
  self-tested against a `ci.yml` whose run `.name` was `CI`; U0c, a sibling unit, changed that
  afterwards. The reader did not misread the tree it was written against.
- **The self-test could not see it.** `ci_run()` in the self-test built `"name": "CI"` by hand.
  The stub restated the reader's assumption, so it pinned the stub.
- **The artifacts listing is a second, independent cause and was intermittent.** The repo-wide
  `actions/artifacts?per_page=100` listing returned 0 bytes (`unexpected end of JSON input`)
  from 03:14 on. It was not "every attempt of every push run": job 120791448344 (05:33) failed
  attempts 1 and 2 and read a 43-artifact window on attempt 3, and then failed on the name. Jobs
  120752118657 (02:21) and 120755282204 (02:36) read windows of 43 and 41. The ratchet's own
  retry and refusal behaved as designed on it (a failed fetch refuses, it is never an empty
  window). That cause is the fixer's per-lane listing, not this document's; it did not turn
  `d5dc3e26a` red.

**Cost of the defect, measured.** `main` push runs failed at `d5dc3e26a` (02:05),
`94bec976b` (02:20), `15f0b5924` (02:22), `88744e573` (04:58) and `50af6174f` (05:00): 5 red
`CI` push runs, `gate` and `tests / ci-ratchet` the only failing jobs of `50af6174f`'s run.
`main` has been red from 02:36 to at least 08:35, 6.0 h, and nothing merged after `50af6174f`.
Detection lag from the cut-over (23:53 to the first red grade at 02:36) was 2 h 43 min.

**Class search** (the same shape elsewhere: a reader keyed on a run's `.name` or title).
`git grep` over `tools`, `tests/*.py`, `tests/*.sh` and `.github` for run-name or workflow-name
keys finds three kinds:

| reader | keys on | affected |
|---|---|---|
| `tests/ci_ratchet.py` (`run_minutes`, `gather_runs`) | `.name == "CI"` | yes, this defect |
| `tools/ci/gate.py`, `codescan_wait.py`, `alert_list.py` | `display_title` parsed for `kind pr base sha=` | no, they read the run-name on purpose |
| `tools/ci/ruleset_cutover.py:187` | `.path in MAIN_RUN_PATHS`, or `.name == "Tests"` | no, `.path` is checked first and `tests.yml` has no `run-name` |

The search found one affected reader. `autofix_statuses.sh`, `ci_critpath.py` and `nightly_status.py` read runs by id or
by workflow file. Hand-built stubs of `display_title` in `codescan_wait.py` restate the run-name
format in their own text. They are not tied to `ci.yml` either, but they parse the shape the
run-name pins, and `tests/entities.py` pins that text.

The same-day neighbours of this defect are `bd0d4d603` (a gate-at-head precondition read one
check suite), `69a26d2a2` (a required-contexts record accepted one shape) and `168365196` (two
prepr refusals). Each is a defect where a reader written against one unit's tree met another
unit's change in the assembly. Together with this one, 4 defects in the P2b assembly are on `main`.
I did not check whether they share a cause beyond that shape.

## 2. Process state: (d), sound in its unit, precondition changed underneath

The process was unit-level gating: each U-unit is written, self-tested and gated in its own
tree, and the assembly (#2673) is gated on the sum. Each step ran and passed. U9a's self-test was
correct for U9a's tree, where a run is named `CI`. The change that broke it was U0c's `run-name`,
which landed 2 minutes earlier in the assembly and not in U9a's tree.

Not (a): a self-test of `run_minutes` existed. Not (b): nothing was skipped. The stub is not the
whole story, so this is not (c): a stub modelling the API faithfully would have been correct for
U9a's tree too, because in that tree `.name` was `CI`. The unfaithfulness only became wrong when
U0c changed the API's answer. (c) holds if the stub should have been API-shaped from the start;
the first unit could not have known the second would rewrite the name. The countermeasure for (d)
is "the process notices its own precondition change", which is what the options below test.

Why the assembly's gate did not notice: the ratchet's window is the **push** runs on `main`. On
the assembly PR those were all pre-umbrella `Tests` runs, which the old key read correctly. The
precondition (push runs titled by `run-name`) did not exist until the first umbrella push run,
and the grade needs 8 of them to fail. No PR-time run can see it.

## 3. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock per occurrence.

- **cost(defect)** = 6.0 h of red `main` = 21 600 s (measured above; the fix has not merged, so
  it is a floor).
- **Candidate A: the ratchet job classifies its own run.** In the `ci-ratchet` job, one `gh api
  repos/<repo>/actions/runs/$GITHUB_RUN_ID` call asserts `run_kind(own run)` is not `None`. On a
  PR run `name` is `CI code pr=N ...`, so on the assembly PR the old `.name == "CI"` key would
  have refused at PR time, before merge. Standing cost: 1 API call per job. The existing
  `--gather-runs` step took 1.14 s for its 2 listing calls and up to 5 job calls (job 120752118657,
  02:21:30.8 to 02:21:32.0), so I take 1.14 s as an upper bound. `ci.yml` ran 113 times in the 24 h
  to 2026-10-24 06:00 (`gh api .../workflows/ci.yml/runs?created=...`, `total_count`). 113 x 1.14
  = 129 runner-seconds per day, about 1 s on each run's wall.
  Break-even: 129 s/day < 21 600 s x P, so P > 0.006 per day, one occurrence in 167 days.
- **P(recurrence) after the fix.** The fixed reader keys on `.path`, the file name
  `ci.yml`. `gather_runs` builds its list URL from the same file name
  (`workflows/ci.yml/runs`), and `api()` refuses on a nonzero `gh` exit or empty output, so a
  renamed `ci.yml` is a loud named failure at the listing, not a silent `None`. By reading the
  code (not run) the only silent route left is a `path` change that still lists runs, and I found
  no such route. The measured class frequency is 1 occurrence of this shape among the readers
  listed in section 1, in the 13 days since `ci_ratchet.py` first landed (`e3511b221`, 10-11).
  The condition that made it possible, a unit assembly that changes what an earlier unit reads, was
  a one-off: P2b is complete, and `tests/entities.py` already pins `ci.yml`'s `run-name`, so
  changing it is a reviewed edit. My estimate of recurrence is well below once per 167 days, but
  it is an estimate, not a measurement.

**Verdict: Candidate A fails the cost test as stated.** Its standing cost is paid every run
and the recurrence it guards was closed structurally by the fix. Building it would be a
countermeasure that fails the test and is built anyway.

## 4. Recorded refusal, and what is not refused

**No new check, test or hook is proposed.** The fix already carries the one change that maps to
(d) at no standing cost: the self-test's stubs are API-shaped (`name` = a rendered run-name,
`path` = the workflow file) and an all-umbrella window is a self-test case with `Tests` as its
null (`run_kind` returns `None` for `card.yml` whatever its title). That is not a new
countermeasure and I do not count it as one.

**What I leave to the owner, not to build:** an assembly of independently-gated units has no
gate at the seam where a sibling's change meets a reader. This defect and its three same-day
neighbours are that shape. It is a P2b-specific shape, and P2b is done, so I record the finding
and build nothing. If a later layout round assembles units again, `plan-review.md`'s brief for it
should name the readers of workflow runs and check each against the post-assembly API answer. That
is policy-adjacent, so it is a proposal and not a change.

## 5. What I did not establish

- Whether 4 assembly defects in 2 days make an audit class that owes a barrier
  (`defect-root-cause.md`). They are not registered in `bugclasses.json`; I did not register them.
- The artifacts listing's own cause (why the server returned 0 bytes from 03:14). The fixer's
  per-lane listing answered in under a second per its comment; I did not measure it.
- Whether `ci-ratchet` runs on PR events with a window; I read only the push-run logs.
