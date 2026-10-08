The nightly `nightly-ha` lane went red on both images at `816547ef` (scheduled Tests run 37753990323, 2026-10-08 09:03Z). The same two jobs were red on the workflow_dispatch at PR #2024's head (run 37756420882). The last green nightly-ha on main was workflow_dispatch run 37682446929 at `f637d24a`. That leaves `816547ef`, the merge of #2041, as the first main head the lane ran on afterwards.

The cause is the A16 container check that #2041 added (R9-DBG-2). It is not production code. Three checks failed on each image: `a16:debug_inline`, `a16:debug_capped` and `run:exit_status`. `ha_download_writer` in `tests/nightly_ha.py` called Home Assistant's private `diagnostics._async_get_json_file_response` with five positional arguments, then took `len()` of `response.body`. Each image broke a different one of those two assumptions:

- **`2025.2.0`**: the call bound correctly, but the writer returns `web.Response(body=<str>)`. aiohttp wraps that body in a `StringPayload`, which has no `len()`. The log line was `TypeError("object of type 'StringPayload' has no len()")`.
- **`stable`**: Home Assistant inserted a `data_issues` parameter after `data`, so the five positional arguments left `d_id` unbound. The log line was `TypeError("_async_get_json_file_response() missing 1 required positional argument: 'd_id'")`. `a16:debug_capped` then read the writer's refusal as a `-1B` download.

The fix binds the writer by parameter name: `data`, `data_issues=None`, `filename`, `domain`, `d_id`. A required parameter that neither name covers stays unbound, and Python's own `TypeError` names it. The fix reads the body as bytes, as a string, or through the aiohttp payload's `write()`. A non-200 response or a missing body is refused with its status. The host half is now pinned in `tests/debug_collect.py`. It drives `ha_download_writer` itself against stand-ins with the 2025.2.0 and current upstream signatures, each returning a body that has no `len()`, plus a status-500 response and a writer with an unknown required parameter.

The CI oracle is the lane itself, dispatched on this branch. Both arms are green, and A16 now measures what #2041 claimed. The inline bundle's real Home Assistant download is about 8.08 MB against the 8 MiB (8388608 B) cap. The capped bundle's download is about 13 kB.

## Head

`1a7eebad28fde79f5b93d51f7fa575fc5ce8b11a`

## Mutation proof

Each mutant was applied to `tests/nightly_ha.py` at the head in a scratch worktree, then `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` was run (seat venv-ci):

- M1: the positional call restored (`_async_get_json_file_response(hass, payload, "a16", domain, entry_id)`). Exit code 1. `FAIL A16's download writer returns the bytes of HA's 2025.10 writer, whose body is a payload with no len()` [`TypeError ... missing 1 required positional argument: 'd_id'`].
- M2: `return response.body` in place of `await _body_bytes(response.body)`. Exit code 1. Both `FAIL A16's download writer returns the bytes of HA's 2025.2.0 writer ...` and `... 2025.10 writer ...` fail.
- M3: the status guard turned off (`if False:`). Exit code 1. `FAIL A16's download writer refuses a response HA's writer failed (status 500, no body)`.
- M0, unmutated: exit code 0, `ALL 62 DEBUG COLLECT CHECKS PASSED`.

A fourth mutant at the first commit, `74689d11`, replaced an explicit `raise` for an unbindable parameter with `pass`, and it survived. Python's own `TypeError` already names the unbound parameter, so the branch was dead and `1a7eebad` removes it. The check `A16's download writer refuses a writer parameter it cannot bind, naming it` still pins the behaviour.

## Null control

At the base `816547ef`, with the new checks and the unmodified `tests/nightly_ha.py`, `debug_collect.py` exits 1 with 3 of 62 checks failing. Two of the failures are the two CI errors, reproduced on the host: the 2025.2.0 stand-in hands back the `_StringPayload` object, and the 2025.10 stand-in gives `missing 1 required positional argument: 'd_id'`. The third is the 500 response, which is returned instead of being refused. At the head, all 62 pass. In CI, the unmodified tree fails `a16:debug_inline` and `a16:debug_capped` on both images (runs 37753990323 and 37756420882), and this head passes them (run 37760373214).

## Figures

All figures were measured at head `1a7eebad` on 2026-10-08, against `origin/main` at `816547ef`.

- The CI oracle is run 37760373214, a workflow_dispatch of `tests.yml` at `1a7eebad` (`gh workflow run tests.yml --ref handoff/r9-nightly-ha -f recheck=false`). Its jobs, as GitHub's jobs API reports them, are `nightly-ha (stable)` success and `nightly-ha (2025.2.0)` success. Each log prints `ALL 64 checks PASSED`. These are CI's results, read with `gh api repos/tvofi/heatpump_optimizer/actions/runs/37760373214/jobs`.
- The A16 lines in those logs (`gh api repos/tvofi/heatpump_optimizer/actions/jobs/113255055681/logs` and `.../113255056233/logs`):
  - `a16:debug_inline [the download 8076990B against the 8388608B cap; 63707 row(s) inline]` on 2025.2.0, and `8077011B` on stable.
  - `a16:debug_capped [bundle 9376008B against the 8388608B cap; the download 12930B]` on 2025.2.0, and `12951B` on stable.
- The red baseline lines are from the jobs API logs for jobs 113233890376 (2025.2.0) and 113233890742 (stable) of run 37753990323. On each image, `FAILED: 3 of 64 checks: ['a16:debug_inline', 'a16:debug_capped', 'run:exit_status']`, with the two `TypeError`s quoted above.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` reports `MODE: SCOPED -- 3 script(s) run, 30 scoped out`. Each of the three was run at the head with `PYTHONPATH=tests/hastub` in the seat venv-ci:
  - `tests/config_flow_steps.py`: `ALL 496 checks PASSED`.
  - `tests/debug_collect.py`: `ALL 62 DEBUG COLLECT CHECKS PASSED`.
  - `tests/entities.py`: `ALL 2210 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Class seams. The rule is `grep -nE "from homeassistant[.a-z_]* import .*\b_[a-z]" tests/nightly_ha.py`, which lists every private Home Assistant name the lane imports. It returns one seam: `_async_get_json_file_response`, closed in this diff. `grep -nE "\.body\b" tests/nightly_ha.py` returns only the two lines in the new `download`, also closed here.

## Red checks

None on this branch. The red this pull request fixes is on `main`, in the nightly lane: `nightly-ha (stable)` and `nightly-ha (2025.2.0)`, scheduled run 37753990323.

The root-cause question, per `dev/governance/rules/defect-root-cause.md`:

- **Cause.** #2041's A16 assumed one Home Assistant writer signature and a bytes body. Both assumptions sit in the container half, which only the nightly lane executes.
- **Process state: (a), the process did not exist.** `nightly-ha` runs only on `schedule` and `workflow_dispatch` (its `if:` in `tests.yml`). No rule or job runs the container half of a changed nightly check before merge. #2041's fix reviewer recorded the gap in round 2, writing "The container half runs on schedule or dispatch only", and noted that they did not run it. Nothing turned that into an obligation, so `merge` was a correct verdict under the contracts as written.
- **Cheaper detector, built here.** `tests/debug_collect.py` now drives `ha_download_writer` host-side against both signatures, at seconds' cost inside a script the scoped gate already runs for this file. It catches this instance and the class "the writer's argument shape or body type changed". It cannot catch the next unknown upstream change to a private name.
- **Countermeasure proposed, not built in this pull request.** On a `pull_request` whose three-dot diff touches `tests/nightly_ha.py`, run `nightly-ha`: `closure-scope` emits a flag, and `nightly-ha` gets `needs: closure-scope` with `!cancelled()`. It would stay unrequired.
  - Standing cost: both arms run in parallel at about 3 minutes each (`started_at` to `completed_at` in runs 37753990323 and 37760373214). That is beside `fast`, so about zero added wall-clock, and only on such pull requests.
  - Frequency: 22 first-parent merges to `main` touched `tests/nightly_ha.py` since 2026-08-01 (`git log --since=2026-08-01 --first-parent origin/main --format=%h -- tests/nightly_ha.py | wc -l`).
  - Cost of the defect: one red night on `main`, this fixer seat, and a confounded dispatch on #2024.
  - It changes `.github/workflows/tests.yml`, which is code-owned, so it is left to a separate pull request on the orchestrator's decision rather than slowing this fix.

## Forward-carry

none

## Friction

- fix-review.md: unenforced: #2041's round-2 verdict recorded that A16's container half was never run, and no contract made an unexecuted new check in a schedule-only lane a blocking finding.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
