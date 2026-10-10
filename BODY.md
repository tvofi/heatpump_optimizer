**R9-RC-RECARRY-READBACK.** `tools/pr/app_push.sh --recarry` refused a push that had succeeded, and `merge_train` read the refusal as fatal and stopped a whole batch pass. This makes the read-back settle a race instead of refusing it, and the train re-read the head once before declaring a stop.

## The defect, re-derived

2026-10-09 ~21:4xZ, the batch pass over five verdicted heads recarried #2071: the clean merge of the judged `1f9d606d` with main `23d35497` produced `61617145f`. `app_push.sh` printed `RECARRY: prepr SKIPPED: HEAD 61617145 is the clean merge of the live head 1f9d606d and origin/main's 23d35497, and the body is the live one` (so it minted and pushed) and then `REFUSE: the pull request did not read back; its state is above -- re-read it by hand before touching anything`. `merge_train.py`'s recarry step keys on the literal `PUSHED` in the push output (`tools/audit/seat/merge_train.py`, the `if "PUSHED" not in o` branch); `die` at the read-back printed no `PUSHED`, so the train raised `Stop("recarry", "the main merge pushed nothing: …")` and the pass died with `RESULT pr=2071 head=61617145f4a2cc254f90b53ba683ea74f13100d4` (`/Users/timmalmstrom/hpo-seats/merge-train-0118/logs36/batch-1.log`) — the head WAS `61617145f`, i.e. the push had landed and only the read-back had raced GitHub's index. The same run's next attempt recarried #2072 (`head 04d10721`, no refusal), so it is a race, not a systematic failure.

## The repair: three outcomes, not two

The read-back exists on purpose (comment-readback.md; decision 0011's #1256 incident, where a mint returned 201 then 404 and left a branch wedged), so it is **kept and made to distinguish**, not deleted. `confirm_readback` polls `GET /pulls/{n}` over a stated budget (`APP_PUSH_READBACK_TRIES` default 6, `APP_PUSH_READBACK_SLEEP` default 2s → ~10s) and resolves to three outcomes:

- **pushed and confirmed** — a read answers open at the pushed sha with the body: exit 0, prints `app_push: PUSHED …`.
- **pushed and not visible within the budget** — every read answered, none at the pushed sha: refuses with its own wording, `… pushed and not visible within the budget … a race GitHub had not indexed, not a refused push`.
- **refused** — no read could be performed (the API refused it): refuses with `the read was refused …`.

The clean case confirms on the first read and never sleeps (the loop breaks on `ok`); every settle it spends is printed (`app_push: read-back 1/6: …; sleeping 2s`), so the budget is in the output, not implied. A silent retry-forever is the opposite failure — a genuinely refused push would read as slow success — so the budget is bounded and stated. The clean-carry condition is unchanged: `prepr` still runs before anything reaches the remote (#678), and nothing but that condition skips it. A body mismatch at the right sha is settled, not a race, so it still refuses at once.

## merge_train's decision, by measurement

app_push now confirms a race inside its own budget, so a non-`PUSHED` recarry output is a real refusal — or a lag that outran app_push's budget. The blast radius of a false stop is the whole pass (#2071: five verdicted pull requests down, rc=1), so the train re-reads the head once after a settle (`RECARRY_RESETTLE` = 2s) before declaring a stop: a recarry moves the head, so a head that is no longer the pre-recarry sha proves the push landed, and the train carries on; a head that did not move is the real refusal and still stops. No train-side retry loop: the push has already happened, and the one open question — did the branch advance — is a single read. One `GET /pulls/{n}` measured TTFB 0.06–0.36s on this host, so 2s is ~6× the worst observed; the settle is paid only on a refusal, never on the common path.

## A second gap, found by measurement: the self-test was run by no check

The brief states "the gate runs that self-test". Measured, it does not. `tests/closure.py select` on this diff prints `MODE: SCOPED -- 0 script(s) run` (both changed files are INERT), and `governance.yml`'s `instrument-self-tests` job drives `prepr.sh`, `push.sh`, `app_approve.sh`, `app_comment.sh`, `merge_main_bot.py`, `bus.sh`, `budget_raise_gate.py`, `contract_rerun.py`, `merge_fastpath.py`, `tmp_paths.py`, `throwaway_git.py` and `merge_train.py` — but not `app_push.sh`. Without a step the arms below would be run by nothing on the pull request. This PR wires `bash …/app_push.sh --self-test` into that job (the sibling of the `push.sh` step); the diff then reaches two scoped scripts (`MODE: SCOPED -- 2 script(s) run`: `tests/entities.py`, `tests/harness_headers.py`). The other half of the fix, `tools/audit/seat/merge_train.py --self-test`, was already wired there.

## Head

`48d47ab19`

## Mutation proof

Three mutants of the fix's production lines, each restored (grep for the mutation marker returns 0 afterwards). Commands are the two self-tests.

M1 — the poll reduced to a single shot (the original #2071 defect): `[ "$attempt" -lt "$RB_TRIES" ] || break` → `break`. `bash tools/pr/app_push.sh --self-test` reports **7 failed**, every one a read-back arm, e.g.:
`FAIL read-back race: the push confirms once the head becomes visible, so it succeeds (got '1', want '0')`,
`FAIL at the SECOND read (the first answered the old head) (got '1', want '2')`,
`FAIL with the settle it spent printed, so the budget is visible (got '0', want '1')`,
`FAIL after the whole budget of reads and settles (got '10', want '32')`.

M2 — the third outcome collapsed (the `not visible` branch deleted, folding it into the generic refusal): **2 failed**:
`FAIL with its OWN wording, so a race is told from a wedge (got '0', want '1')` and
`FAIL and it is NOT reported as a refused read (got '1', want '0')`.

M3 — the train's re-read never lands on a moved head (`moved != h` → `False`): `python3 tools/audit/seat/merge_train.py --self-test` reports **1 failed**: `FAIL a recarry refusal whose head nonetheless moved is treated as landed, not a stop`.

## Null control

The **unmodified** tree. `git show origin/main:tools/pr/app_push.sh` → run its self-test: **91 checks, 0 failed** — it has no read-back race arm, so the single-shot refusal is the defect the three outcomes close. The unmodified `merge_train.py` self-test is **95 checks, 0 failed** and stops on any no-`PUSHED` recarry (its `heads: [H0, H1]` recarry case read `a recarry that pushed nothing stops it`, which this PR re-keys to `heads: [H0]` so the same check still proves a real refusal stops it). The fix's own null control is the clean path: the `rok` case, a `--recarry` whose head is already current, prints **no** settle (`settles rok` = 0) and reads back once (`get-n` = 1) — a fix that looped on the clean path would fail it.

## Figures

- The App push self-test at this head: `bash tools/pr/app_push.sh --self-test`.
- The merge train self-test at this head: `python3 tools/audit/seat/merge_train.py --self-test`.
- The unmodified self-tests (the null control above): `git show origin/main:tools/pr/app_push.sh`.
- The ratchet, which this diff does not move: `python3 tests/structure.py`.
- The scope selection: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`.
- The read-back endpoint's latency, one unauth GET: `curl -sS -o /dev/null -w '%{time_starttransfer}\n' https://api.github.com/repos/tvofi/heatpump_optimizer/pulls/2071`.

## Unpinned sites

none: the diff adds no Python mutation site under a graded closure (both files are INERT).

## Red checks

none.

## Forward-carry

none: the fix lands its own two instruments (app_push.sh's read-back and merge_train's re-read) in the same pull request, and no later stage's brief changes.

## Friction

- `gate-scoping: unenforced: tools/pr/app_push.sh --self-test was wired into no CI job, so a fixer's arms there are run by nothing on the pull request (the diff is MODE: SCOPED -- 0); this PR wires it into instrument-self-tests`.
