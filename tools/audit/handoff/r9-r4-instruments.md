_Requested by **tvofi**_

Readiness PR **R4** of audit round 9 (plan row R4). It adds the round-8 judge's instrument notes that `main` still lacked, and two items owed after v6.7.0.

Each item was checked against `origin/main` at `81f2c18c` first:

| # | item | at `81f2c18c` | here |
|---|---|---|---|
| 1 | seat temp roots from `TMPDIR` (judge note 2) | not done: `TMPDIR` does not appear in the harness contract or in `prepare_baseline.sh` | harness contract bullet; `BASELINE.md` line |
| 2 | perturb in memory, or keep an on-disk edit away from other runs (note 3) | not done: nothing in the harness contract | harness contract bullet (see the design choice below) |
| 3 | `orjson` pinned in `BASELINE.md` (note 1) | not done: `orjson` does not appear in `prepare_baseline.sh`, and `tests/requirements-ci.txt` does not pin it | `prepare_baseline.sh` reads the pin from `tests/requirements-typing.txt` (Home Assistant's own, hash-pinned). It refuses an interpreter whose `orjson` differs and prints a hash-pinned install. `BASELINE.md` records the version |
| 4 | `pip download` out of the cwd (note 9) | not done | the same contract bullet and `BASELINE.md` line as item 1. The refusal's install reads a requirements file under `mktemp -d` |
| 5 | `prepare_baseline.sh` keeps the `round4/` files `tests/entities.py` opens | **already done** by #1507 (`strip_earlier_rounds` keep-set plus the `finders_can_start` refusal). Dropped | nothing |
| 6 | stale `playwright@1.49.0` (#1629 moved the lane to the lock in `tests/pwlane/`) | `tools/audit/briefs/D4.md`, and the `prepare_baseline.sh` line that writes `BASELINE.md` | both now install with `npm ci` from `tests/pwlane/`'s lock, so they no longer carry a version number that can go stale again |
| 7 | steward S6 and `tools/audit/README.md` stale against `gate-scoping.md` (the FIFO lease, v6.7.0) | S6 tells a seat to take the lease by hand before any run that selects `stress.py`. The README requires the lock for `MODE: FULL` and passes `HPO_GATE_LOCK_LABEL` into `run.sh` | both cite `gate-scoping.md`: `run.sh` leases each `stress.py` run itself. The README says a direct `stress.py` run takes no lease and shows the `auto-lease` wrap. The generator's `BASELINE.md` gate paragraph (fixer step 10) says the same |

**A design choice in item 2.** The plan's wording was "hold the lease for on-disk edits". That no longer protects anything. Since v6.7.0, `run.sh` leases only its `stress.py` runs (`tests/run.sh` `leased()`, `gate_lock.py needs-lease`), so an unleased `entities.py` run in the same tree still imports the edited file. The contract therefore says: perturb in memory, or put an on-disk edit in a worktree of its own. This matters for round 9: box B8 runs D14-s1..s3, all three in the one `audit-r9-D14` worktree.

**A consequence of item 3, stated in `BASELINE.md`.** The stub's `json_bytes` (`tests/hastub/homeassistant/helpers/__init__.py`) takes `orjson.dumps` whenever `orjson` imports, and CI's gate job installs none. So on a finder box with the pin, a gate check on that path can read differently than on CI.

This diff touches code-owned paths: `tools/audit/README.md`, `tools/audit/briefs/D4.md` and `.claude/skills/steward/SKILL.md`. Those three are also policy files under `CLAUDE.md`. **It needs tvofi's code-owner approval.** `prepare_baseline.sh` is neither code-owned nor policy. The delivery row (`docs/delivery/<N>.md`) is written by the Mac seat once the pull request number exists.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Approval

This is a policy change (`tools/audit/README.md`, `tools/audit/briefs/D4.md`, `.claude/skills/steward/SKILL.md`, all code-owned by tvofi), so tvofi's approving review is owed before the merge. It is not a budget raise: no cap in any `*_budgets.json` moves, and `policy_lint --budgets` shows the aggregate `corpus` falling.

## Head

`2bf7faafaed16fdc08a9e36a3a9192e12b8c5f87`, measured on merge base `81f2c18c96636ce85006a2ef61fa0731f0813ba0`. That merge base was also `origin/main`'s tip at 2026-09-26 04:39 UTC. The handoff commit after this head only carries this body.

## Mutation proof

The one behaviour a check can pin is the `orjson` refusal in `prepare_baseline.sh`.
- **The refusal holding.** At this head, with an interpreter that has no `orjson` (`/home/claude/venv314`), the script refused with rc=2 and wrote nothing: `refusing: … has orjson none, tests/requirements-typing.txt pins 3.11.9`.
- **The predicate deleted.** I replaced `[ "$ORJSON_HAVE" != "$ORJSON_PIN" ]` with `false`. The same run then went on to `RESULT export=…` with rc=0, so an export was built with no `orjson`. Restoring the file restored the refusal.

The rest of the diff is prose, and no check can pin it cheaply. `tools/audit/` is on `tests/closure.py`'s `INERT` list, so a gate check that read these files would need an `INERT_EXCEPT` entry in code-owned `tests/closure.py` and a closure re-recording. The playwright seam is closed by construction instead: both sites now install from the lock `#1629` bumped, so the next bump moves them too.

## Null control

I ran the merge base's own `tools/audit/prepare_baseline.sh 99 81f2c18c` from a detached worktree at `81f2c18c`, with the same `orjson`-less interpreter.
- It **did not refuse** (rc=0).
- Its `BASELINE.md` carried `npm i --prefix /tmp/pw playwright@1.49.0` and `gate lock: take it only when tests/closure.py select reports MODE: FULL or names`.

At this head, with `orjson` 3.11.9 installed hash-pinned into a private `--target` under `$TMPDIR`:
- the run finished rc=0, with `finders_can_start=ok` for the export and all six worktrees;
- `grep -c "1\.49"` on the emitted `BASELINE.md` printed `0`.

Item 5, confirmed rather than assumed. Every `tools/audit/round4/…` literal in `tests/*.py`, `*.mjs` and `*.sh` exists in the head's export. The null control is `tools/audit/round4/RESUME.md`, a round-4 file no test names: it was stripped and reported MISSING by the same test.

## Figures

- items 1–4 absent at the merge base, one command per item, each rc=1 (no match): `git grep -n -i TMPDIR 81f2c18c -- tools/audit/README.md tools/audit/prepare_baseline.sh`, then the same with `orjson`, `"pip download"` and `"in memory\|in-memory"`
- the refusal at this head: `PYTHON=/home/claude/venv314/bin/python tools/audit/prepare_baseline.sh 99 81f2c18c`
- the generator at this head: `PYTHON=<interpreter with orjson 3.11.9> tools/audit/prepare_baseline.sh 99 81f2c18c`. The control is the same command run from a worktree at `81f2c18c`
- the round-4 keep-set: `git grep -oh "tools/audit/round4/[A-Za-z0-9_./-]*" -- 'tests/*.py' 'tests/*.mjs' 'tests/*.sh'`, each path tested with `test -e` in the export
- policy budgets (aggregate `corpus` falls, no per-file cap moves): `node .claude/workflows/policy_lint.mjs --budgets`
- the scoped gate's mode line (`MODE: SCOPED -- 0 script(s) run`): `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`
- rc=0 for each of: `python3 tests/structure.py`, `node .claude/workflows/policy_lint.mjs`, `node .claude/workflows/rules_sync.mjs --check`, `node .claude/workflows/check-wave-script.mjs` (it reads `prepare_baseline.sh`'s `ISOLATED_DIMS`), `node .claude/workflows/brief_lint.mjs`
- playwright seams, enumerated as `git grep -n -E "playwright@[0-9]|[Pp]laywright 1\.49" -- ':!tools/audit/round*'`. Each seam it returns and its disposition:
  - `tools/audit/briefs/D4.md` and `tools/audit/prepare_baseline.sh`: **closed here**.
  - `tests/entities.py` (`_PIN_ARMS`): synthetic workflow text for the #1548 hash-pin barrier's red arm, where the version is inert data. Left as is.
  - `docs/audit-2026-09.md` and `.claude/workflows/carry-1320.json`: measurement records written at 1.49.0. They recount a measurement and do not instruct (fixer step 10). Left as is.
  - `tests/card_browser.mjs` (the coarse-pointer comment): a measurement record that says "this job's own Chromium", which is now 1.56.1's Chromium. **Open**: re-measurement needs Chromium, and this container has none (`BASELINE.md` printed `chromium: not found`). It goes to the orchestrator as a lead, not carried, because it is unmeasured (`finding-propagation.md`).
  - `tools/audit/round*/`: round records. Left as is.
- lease seams, enumerated as `git grep -n -E "HPO_GATE_LOCK_LABEL|TAKE THE LOCK|take it only when|take the lock only when" -- ':!tools/audit/round*' ':!docs/superpowers'`. Each seam it returns and its disposition:
  - `tools/audit/README.md` and the steward skill: **closed here**.
  - `.claude/rules/gate-scoping.md`, `tests/README.md` and `tests/run.sh`: the source, and it is current.
  - `.claude/workflows/web-fragments.md` and its synced copies `web-{fix-wave,stamp,triage,decomp-stage}.js`: **open**. They still say `run.sh` "holds flock for the gate run and renews the lease before every script", which has been false since v6.7.0. The file is code-owned policy, synced by `fragments_sync.mjs`, and outside this PR's assignment. Handed to the orchestrator.
  - `tools/audit/briefs/orchestrator.md` §12: says "take it only when", which is redundant but not false, since `gate-scoping.md` still permits holding the lease by hand. Handed to the orchestrator with the one above.
  - `.claude/workflows/audit-find.js` and `audit-verify.js`: the quiet-window measurer and the judge hold the lease across commands, which `gate-scoping.md` permits. Left as is.

## Red checks

none

## Forward-carry

- `tools/audit/README.md` (the harness contract), which every round-9 finder, verifier and judge reads: TMPDIR-derived roots, `pip` out of the cwd, and in-memory perturbation or a private worktree.
- The round's `BASELINE.md` generator, `tools/audit/prepare_baseline.sh`: the `orjson` pin and its CI divergence, `TMPDIR`, installing playwright from the lock, and the lease.

## Friction

- `orchestrator: stale: PLAN.md R4 says "hold the lease for on-disk edits", but since v6.7.0 run.sh leases only stress.py (tests/run.sh leased()), so the lease cannot keep an import away from an edited file`
