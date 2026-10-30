Roster group R10-ERREXIT-COUNTERMEASURES: the four carries of #2849 (R10-RCA-HOTFIX-BATCH-ERREXIT), landed as checks, not as one-call barriers. The diff touches `tests/entities.py`, `tests/closures.json` (the `tests/entities.py` entry, re-recorded), `tests/arch_score.py`, one line of `.github/workflows/gate-sweep.yml`, and one registry entry in `tools/policy/agreement.mjs`. There is no production code in it.

- **(1) Countermeasure A.** `tests/entities.py` scans every errexit `run:` block in `.github/workflows/*.yml` and `.github/actions/*/action.yml` and refuses a `$?` read whose producer is a bare simple command, an arithmetic `(( $? ))` test among them. It replaces `_RAF_BARE_GREEN`, the one-call barrier that let I3 through.
- **(2) gate-sweep.yml, the 4th instance.** `out=$(python3 -I tools/ci/gate.py --sweep ...) || true`; `_gs_step_verdict` runs the step under `_GHA_RUN` (`bash -e -c`).
- **(3) Countermeasure B.** `_GHA_RUN = ["bash", "-e", "-c"]` is GitHub's default step shell. A pin keeps it: every `-c` list literal whose shell is `bash` or `sh`, in a tracked non-INERT `.py` under `tests/` and `tools/`, carries an errexit flag or is listed in `_SHELL_NOT_A_STEP`.
- **(4) Class proposal:** under Forward-carry. This PR mints nothing.

### This round: the `tests / fast (3.14)` red, fixed at the root

At the previous head `5e7d8865f`, `python3 tests/entities.py` printed `1 of 2482 ENTITY CHECKS FAILED`: countermeasure B's pin, `sites=12 without errexit=['tests/entities.py:_o1_window']`. The site is main's (R10-RECORD-API-O1, commit `3122bc41d`, merged by #2964/#2966): `_o1_window` ran the nightly `Choose the window` step under a bare `["bash", "-c", script]`, which is exactly the shape B refuses, because GitHub runs the step under `bash -e` and a harness that does not reads a different step. The two branches were each green alone; the merge of `origin/main` brought the second site in. The fix routes that call through `_GHA_RUN`. The step runs clean under `-e` (the check itself passed at the new head), so no behaviour of the step moved.

## Roster carries

- Carry 1: countermeasure A, landed in an earlier round; unchanged this round.
- Carry 2: gate-sweep.yml fixed under `_GHA_RUN`, landed in an earlier round; unchanged this round.
- Carry 3: countermeasure B, landed and narrowed to non-INERT files in an earlier round; this round it caught `_o1_window`, which is fixed here.
- Carry 4: the class proposal, under Forward-carry.
- Carry 5: the arithmetic `(( $? ))` arm of A, landed in an earlier round; unchanged this round.
- Carry 6: each runner main moved to `_stub_path_env` keeps its env; only the argv moved to `_GHA_RUN`, unchanged this round.

## Head

The head is the code head: `6c123f469` (the fix) merged with `origin/main` `c0a1d4635`, which gives the tip named below. A figure that names no tree was taken at that tip.

793658cd4400be4398f73b57670e9df101617b84

## Mutation proof

The mutant is the fix deleted (`["bash", "-c", script]` restored in `_o1_window`), which is the tree `5e7d8865f` reds on: `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` printed `1 of 2482 ENTITY CHECKS FAILED`, the failing check being "every `bash -c` / `sh -c` a check runs carries errexit ... (countermeasure B)" with `without errexit=['tests/entities.py:_o1_window']`. With the fix restored the same command printed `ALL 2482 ENTITY CHECKS PASSED`, rc 0. The earlier mutants M1–M7 of the previous rounds read lines this round does not touch.

## Null control

The null control for the claim that B names every bare site is B's own plants, which pass unchanged: a bare `["bash", "-c", s]`, `["sh", "-x", "-c", s]`, `["/bin/bash", "-c", s]` and `["/usr/bin/env", "bash", "-c", s]` each yield exactly their own defect, and the failing site above is the live one B found without a plant. The finder harness `dev/audit/harnesses/r10_errexit_capture.py` reads flat by design (I3 was fixed on main before the cut, I4 is a `$(...)` read), and the companion that reads I4 is the tree's executed check under `_GHA_RUN`.

## Figures

- `python3 tests/entities.py` at the code head: `ALL 2482 ENTITY CHECKS PASSED` (rc 0), after the merge of `origin/main`; at `5e7d8865f`: `1 of 2482 ENTITY CHECKS FAILED` (rc 1).
- B's read: `git ls-files -z -- 'tests/*.py' 'tools/*.py'` less `closure.is_inert`. The census of sites is the check's own output (`sites=` and `without errexit=` in its failure line), run at the head; the `_o1_window` site is the only one it reported, and it is closed in this diff.
- The scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` reports `MODE: FULL`, because `.github/workflows/gate-sweep.yml` changes the gate itself. `tests/entities.py` was run in full; the rest is left to CI.
- `tests/closures.json` is unchanged this round: `_o1_window` reads nothing new.

## Red checks

- `tests / fast (3.14)` at `5e7d8865f`: red on `tests/entities.py` (above). It was this branch's in the sense that its pin (B) is the check that went red, on a site main had added; it is fixed here. The cheaper detector was running `python3 tests/entities.py` after the last merge of `origin/main`; the previous seat's merge was automatic by the orchestrator and no seat re-ran the closure of a merged tree. The standing cost is about nine minutes on a seat box, and `GATE_SCOPE=auto` already selects it for any diff that reaches the entry, so no new countermeasure is built: the merge train's own gate caught it before it merged.
- `pr-contract / pr-contract` at `5e7d8865f`: red on the body check "`tests / fast (3.14)` is red and `## Red checks` does not name it". It is answered by the entry above; nothing else in the job was red.
- `tests / nightly-status`: grades main's scheduled Nightly, which this diff does not reach. It is not this PR's.
- `tests / closures`, `tests / closures-autofix`: red at an earlier head (the INERT-reads refusal), fixed at the root in the previous round by narrowing B's read to non-INERT files.

## Forward-carry

- The verdict's `## Evidence` item 158ad202 records a measurement at the earlier head, not a finding: nothing in it is owed. Carry: dismissed: evidence measurement, not a finding (item 158ad202)
- **Class proposal (carry 4), for the judge or the orchestrator to mint.** "A workflow step's meaningful nonzero exit ended by errexit before the step reads it." Instances: I1 (`718c94c84`), I2 (`bc2ad6964`), I3 (#2848, `e0ffb1213`), I4 (gate-sweep's `out=$(...)`, fixed here). Carry: R10-ERREXIT-COUNTERMEASURES (this group's carry (4) in dev/programme/rosters/wave-r10-groups.json; the class mint is the judge's or orchestrator's, in dev/audit/config/bugclasses.json)
- **A's unguarded domain.** `export X=$?` and `${?}` are bare-producer reads that A and its finder harness skip, with no live instance in the tree. Carry: R10-ERREXIT-COUNTERMEASURES (the same carry (4) entry, for whoever mints the class)

## Friction

none
