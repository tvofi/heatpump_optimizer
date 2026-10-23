## Unit

U11 kernel-points, stacked on U0c `d22b5f303`. Owns `.github/workflows/kernel-points.yml` only.

```
 .github/workflows/kernel-points.yml | 69 +++++++++++++++++++++++++------------
 1 file changed, 47 insertions(+), 22 deletions(-)
```

- `on:` is `workflow_call` (inputs `pr`, `base`, `head`, each `type: string`, `default: ""`) plus `workflow_dispatch` (input `pr`).
- The `pull_request` trigger, the job's label `if:` and the `concurrency:` group (`cancel-in-progress`) are removed. Not ported (A2 item 3).
- The caller's `if:` on the workset decides when it runs (`prelude.py`: `labeled` with the label is kind `kernel-points`; `synchronize` with the label adds it to the code run). The callee re-derives none of that (A2 items 1-2).
- New first step `Ref guard`: fails when `github.event_name == 'workflow_dispatch' && github.ref != 'refs/heads/main' && inputs.pr == ''` (A2 item 4, 4.3 item 5). Under `workflow_call` the event and `inputs.pr` are the caller's, so one condition covers a direct dispatch and a `ci.yml` dispatch.
- The matrix, checkout, setup-python, install and harness steps are untouched. Top-level `permissions: contents: read` stays, matching the caller's grant.
- No new files, so no `closure.py` classification. No production Python.

## Interface

Consumes U0c's `kernel-points` caller row: `with: pr, base, head` from `needs.prelude.outputs.*`, grant `contents: read`, runs when the workset names `kernel-points`. Declares exactly those three inputs. Check name stays `kernel-points / kernel-points (<coretype>)` (job `name:` unchanged). It is never in `REQUIRED`. Exports nothing.

## Static map

`python3 -I unitcheck2.py static <main's kernel-points.yml> <this file> --map kp_map.json`, with

```
{"renames":{},"dropped":[],"gained":["kernel-points|Ref guard"],"changed":["kernel-points|","|triggers"],"after":{"kernel-points|Ref guard":"kernel-points|^"}}
```

gives `STATIC rows 8->9 lost 0 gained 0 changed 2 (mapped 2) misplaced 0 rc 0`. Against the same file with no map: `gained 1 changed 2 ... rc 1`. The `if` of the job is the changed row (label test removed); `|triggers` carries the `on:` and `concurrency` change.

## Controls

- Input contract (`inputs_ctl.py`: the caller's `with:` keys in U0c's `ci.yml` must all be declared, each `string` with default `""`). Null: `passed ['base','head','pr'] declared ['base','head','pr'] BAD []`, rc 0. Plant (the `head` input deleted): `BAD ['head']`, rc 1. This is the control for the "undeclared input breaks the caller" risk, which unitcheck2's static half cannot see (it hashes no `inputs`, only the mapped `|triggers` row).
- Guard step. Plant (step deleted): unitcheck2 with this map still prints rc 0 (see UNCERTAINTIES); the control is the presence check of the `Ref guard` step in the diff. Not asserted by any repo test.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `selftest_wiring.py --check`: `87 self-testing, 87 wired, 0 unwired`.
- Scoped gate: `MODE: FULL` (the stack carries U0c's `ci.yml` edit, which forces it), venv-ci Python. 3 scripts red:
  - `tests/entities.py`, 2 of 2400. (a) "the template arm ..." is U0c's recorded, inherited red (`policy_lint` deadlock, U0c's Forward-carry). (b) "a red that lands after pr-contract ran re-runs it ..." is **caused by this unit**: `_PR_WORKFLOW_NAMES` no longer contains `Kernel points` (the file has no `pull_request` trigger), while `pr-contract-rerun.yml` still lists it. U0c's body already says this reader goes when U10 deletes `pr-contract-rerun.yml`; not fixed here (entities is not this unit's file). See Wiring.
  - `tests/stress.py`, `tests/harness_headers.py`: `gate_lock: flock-wrap refused, u11 holds no lease` -- my run did not hold the lease; environment, not the tree. Not re-run.
  - Everything else (features, structure, closure selftests, ...) green.

## Live checks owed

All on `ci-probe/all`, via `tools/audit/seat/ci_probe.py label`:
1. A `labeled` event with the `kernel-points` label: a `CI kernel-points pr=<n> ...` run whose prelude workset names `kernel-points` and whose 4 `kernel-points / kernel-points (<coretype>)` jobs run; the `Ref guard` step is skipped (event is `pull_request`).
2. Any other label: empty workset, `kernel-points` caller skipped, `gate` re-judges only.
3. `synchronize` with the label present: workset gains `kernel-points`. Without it: not present.
4. A `workflow_dispatch` of `ci.yml` at a PR branch with `-f pr=N`: guard passes. Without `pr`, on a non-main ref, if the dispatch workset reaches `kernel-points`: guard step fails. Direct dispatch of `kernel-points.yml` off main without `pr`: fails at the guard.
5. A2 item 5 (not done here, read-only live measurement): the `labeled` events per PR head over the last 7 days, for A1's projection.

## Wiring

- Assembly order: `entities.py`'s follower check (b above) is red whenever U11 lands without U10 (`pr-contract-rerun.yml` deleted, with `_PR_WORKFLOW_NAMES`/`_crr_defects`). The coordinator must cut U10 and U11 together, or U9b drops `Kernel points` from the follower pin.

## Uncertainties

- `unitcheck2.py static` does not refuse a mapped `gained` step that is absent (plant: Ref guard step deleted, map still lists it: rc 0), and hashes no workflow_call `inputs`. The input control above and the guard's presence are checked by hand only.

## Red checks

At `origin/main` `fef4a1351`, per U0c's body: no check run concluded `failure`; 27 `rerun-stale-contract` runs `cancelled` by design. No red check is carried by this unit. U0c's known local `policy_lint`/template-arm red (its Forward-carry) is inherited from the stack and not touched here.
