The nightly `nightly-ha` lane went red on both images at `816547ef` (scheduled Tests run 37753990323, 2026-10-08 09:03Z). The same two jobs were red on the workflow_dispatch at PR #2024's head (run 37756420882). The last green nightly-ha on main was workflow_dispatch run 37682446929 at `f637d24a`. Of the first-parent merges since then, only #2041 touched `tests/nightly_ha.py`.

The cause is the A16 container check that #2041 added (R9-DBG-2). It is not production code. Three checks failed on each image: `a16:debug_inline`, `a16:debug_capped` and `run:exit_status`. `ha_download_writer` in `tests/nightly_ha.py` called Home Assistant's private `diagnostics._async_get_json_file_response` with five positional arguments, then took `len()` of `response.body`. Each image broke a different one of those two assumptions:

- **`2025.2.0`**: the call bound correctly, but the writer returns `web.Response(body=<str>)`. aiohttp wraps that body in a `StringPayload`, which has no `len()`. The log line was `TypeError("object of type 'StringPayload' has no len()")`.
- **`stable`**: Home Assistant inserted a `data_issues` parameter after `data`, so the five positional arguments left `d_id` unbound. The log line was `TypeError("_async_get_json_file_response() missing 1 required positional argument: 'd_id'")`. `a16:debug_capped` then read the writer's refusal as a `-1B` download.

The fix binds the writer by parameter name: `data`, `data_issues`, `filename`, `domain`, `d_id`.

- `data_issues` is passed as `[]`, the list Home Assistant itself passes for an entry with no issues. So on the newer images the file carries its `issues` section, as the real download does.
- A required parameter that neither name covers stays unbound, and Python's own `TypeError` names it.
- The body is read as bytes when it is bytes, or through the aiohttp payload's `write()` otherwise. aiohttp never leaves `.body` a str, so there is no str branch.
- A non-200 response or a missing body is refused with its status.

The host half is now pinned in `tests/debug_collect.py`. It drives `ha_download_writer` itself against stand-ins with the 2025.2.0 and current upstream signatures, each returning a body with no `len()`. It also drives a bytes body, a status-500 response and a writer with an unknown required parameter.

The CI oracle is the lane itself, dispatched on this branch at the code head: both arms green, `ALL 64 checks PASSED`. A16 now measures what #2041 claimed. The bundle carried inline gives a real Home Assistant download of about 8.08 MB against the 8 MiB (8388608 B) cap. The bundle past the cap gives a summary download of about 13 kB.

## Head

`7e74470795173adfb52c2824bf489938272dbb28`

## Mutation proof

Each mutant was applied to `tests/nightly_ha.py` at `7e744707` in a scratch worktree, then `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` was run (seat venv-ci). Each is named by the check(s) it turns red:

- M0, unmutated: exit code 0, `ALL 64 DEBUG COLLECT CHECKS PASSED`.
- M1: the positional call restored (`_async_get_json_file_response(hass, payload, "a16", domain, entry_id)`). Exit code 1, 2 of 64 failing: `FAIL A16's download writer returns the bytes of HA's 2025.10 writer, whose body is a payload with no len()` and `FAIL A16 passes data_issues as the list HA passes, so the file carries its issues section`, both from `TypeError ... missing 1 required positional argument: 'd_id'`.
- M2: `return response.body` in place of `await _body_bytes(response.body)`. Exit code 1, 3 of 64 failing: the 2025.2.0 and 2025.10 writer checks and the `data_issues` check.
- M3: the status guard turned off (`if False:`). Exit code 1, 1 of 64 failing: `FAIL A16's download writer refuses a response HA's writer failed (status 500, no body)`.
- M4: `"data_issues": None` in place of `[]`. Exit code 1, 1 of 64 failing: `FAIL A16 passes data_issues as the list HA passes, so the file carries its issues section`.
- M5: the bytes branch of `_body_bytes` deleted. Exit code 1, 1 of 64 failing: `FAIL A16's download writer returns a bytes body as it is` (`AttributeError("'bytes' object has no attribute 'write'")`).

Earlier heads removed two branches whose mutants survived. One was an explicit `raise` for an unbindable parameter, which duplicated Python's own `TypeError`. The other was the str branch of `_body_bytes`, which no aiohttp response reaches. The behaviour behind the first is still pinned by `A16's download writer refuses a writer parameter it cannot bind, naming it`.

## Null control

At the base `816547ef`, with the new checks and the unmodified `tests/nightly_ha.py`, `debug_collect.py` exits 1 with 4 of 64 checks failing:

- The two CI errors, reproduced on the host: the 2025.2.0 stand-in hands back the `_StringPayload` object, and the 2025.10 stand-in gives `missing 1 required positional argument: 'd_id'`.
- The `data_issues` check, with the same `d_id` error.
- The status-500 response, which is returned instead of being refused.

At the head, all 64 pass. In CI, the unmodified tree fails `a16:debug_inline` and `a16:debug_capped` on both images (runs 37753990323 and 37756420882), and the code head passes them (run 37768894718).

## Figures

Measured at code head `7e744707` against merge base `816547ef`, on 2026-10-08.

- **CI oracle**: run 37768894718, a workflow_dispatch of `tests.yml` at `7e744707` (`gh workflow run tests.yml --ref handoff/r9-nightly-ha -f recheck=false`). The jobs API (`gh api repos/tvofi/heatpump_optimizer/actions/runs/37768894718/jobs`) reports job 113283232227 `nightly-ha (stable)` success and job 113283232260 `nightly-ha (2025.2.0)` success. Each job's log prints `ALL 64 checks PASSED`. These are CI's results.
- **A16 lines** in those logs (`gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs`):
  - stable, job 113283232227: `a16:debug_inline [the download 8077011B against the 8388608B cap; 63707 row(s) inline]` and `a16:debug_capped [bundle 9376014B against the 8388608B cap; the download 12945B]`.
  - 2025.2.0, job 113283232260: `a16:debug_inline [the download 8077018B ...]` and `a16:debug_capped [... the download 12952B]`.
- **Red baseline**: from the jobs API logs of run 37753990323, job 113233890376 (2025.2.0) and job 113233890742 (stable). On each image, `FAILED: 3 of 64 checks: ['a16:debug_inline', 'a16:debug_capped', 'run:exit_status']`, with the two `TypeError`s quoted above.
- **Scoped gate**: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` reports `MODE: SCOPED -- 3 script(s) run, 30 scoped out`. Each of the three was run at `7e744707` with `PYTHONPATH=tests/hastub` in the seat venv-ci:
  - `tests/config_flow_steps.py`: `ALL 496 checks PASSED`.
  - `tests/debug_collect.py`: `ALL 64 DEBUG COLLECT CHECKS PASSED`.
  - `tests/entities.py`: `ALL 2210 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- **Class seams**: `grep -nE "from homeassistant[.a-z_]* import .*\b_[a-z]" tests/nightly_ha.py` lists every private Home Assistant name the lane imports. It returns one seam, `_async_get_json_file_response`, closed in this diff.

## Red checks

None on a commit of this branch from its own diff. Two reds appear on the dispatch runs at its heads, and the diff touches neither:

- **`closures`** (job 113255056308 of run 37760373214) prints the same refusal as main's own job 113233890832: `tests/harness_headers.py: dev/audit/harnesses/git_auto_maintenance_race.sh`. That is main's red after #2051, fixed by #2055 (merged 2026-10-08T10:40Z).
- **`mutation-nightly`** (job 113255117017 of run 37760373214) is red on a NULL_COMMENT timeout in `custom_components/heatpump_optimizer/__init__.py` under `boost_drift_replay.py`. That is a production site this diff does not change.

`nightly-status` and `delivery-status` grade `main`.

The red this pull request fixes is on `main`, in the nightly lane: `nightly-ha (stable)` and `nightly-ha (2025.2.0)`, scheduled run 37753990323. The root-cause question, per `dev/governance/rules/defect-root-cause.md`:

- **Cause.** #2041's A16 assumed one Home Assistant writer signature and a bytes body. Both assumptions sit in the container half, which only the nightly lane executes.
- **Process state: (a), the process did not exist.** `nightly-ha` runs only on `schedule` and `workflow_dispatch` (its `if:` in `tests.yml`). No policy file obliges a pull request to run the container half of a changed nightly check before merge. #2041's fix reviewer recorded the gap in round 2, writing "The container half runs on schedule or dispatch only", and noted that they did not run it. The 2026-10-07 seat block's instruction to dispatch a workflow on one's branch is a convention, not policy.
- **Cheaper detector, built here.** `tests/debug_collect.py` drives `ha_download_writer` host-side against both signatures, at seconds' cost inside a script the scoped gate already runs for this file. It catches this instance, but not the next unknown upstream change to a private name.
- **Countermeasure.** It is built as a separate pull request in group R9-CI-2, on the orchestrator's decision: `nightly-ha`, still unrequired, runs on a pull request whose three-dot diff touches what `tests/nightly_ha.py` reads outside the package.
  - Standing cost: both arms run in parallel at about 3 minutes each (`started_at` to `completed_at` in runs 37753990323 and 37760373214). Only such pull requests pay it.
  - Frequency: 22 first-parent merges to `main` touched `tests/nightly_ha.py` since 2026-08-01 (`git log --since=2026-08-01 --first-parent origin/main --format=%h -- tests/nightly_ha.py | wc -l`).

## Forward-carry

none

## Friction

- fix-review.md: unenforced: #2041's round-2 verdict recorded that A16's container half was never run, and no contract made an unexecuted new check in a schedule-only lane a blocking finding.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
