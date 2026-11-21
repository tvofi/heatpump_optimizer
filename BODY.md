Group R11-HOTFIX-CODEQL-PERMS. Main is red on the required `codeql / Analyze (python)`, and so on `gate`: main 0ae95e4c9b's python job (136736442455, run 44868101509) started 04:52:17Z and was cancelled at its 75-minute cap, `2026-11-21T06:07:17.7955071Z ##[error]The operation was canceled.`, with query evaluation at 35 of 52 (`[35/52 eval 31m40s] ... CWE-730/ReDoS.bqrs`, 06:02:16Z) after about 38 minutes of extraction.

Part A, the main red. `.github/workflows/codeql.yml`'s python matrix cap goes from 75 to 120 minutes. Re-derived over the 40 newest ci.yml push runs on main (2026-11-18T13:09Z to 2026-11-21T04:51Z): 22 python jobs were capped at 75.1 minutes and 18 ran uncensored from 57.0 to 74.2 minutes, so the worst case is censored above 75. The enumerator: `gh api "repos/<repo>/actions/workflows/ci.yml/runs?branch=main&event=push&per_page=40"`, then `gh api repos/<repo>/actions/runs/<id>/jobs?filter=all` per run, duration = completed_at - started_at of `codeql / Analyze (python)`. 120 is that censored bound plus 45 minutes, which the 17 queries unfinished at the cap have to fit in. The workflow's comment carries the measurement and the enumerator. `tests/entities.py`'s `_PY_WORST_CASE_MIN` moves from 51 to 76, the first whole minute past the old cap, so a cap at the measured-capped 75 is refused. The actions and javascript-typescript legs stay at 45, which is the pin's null control.

Part B, carried from the handoff at 036cb18339 (alerts 57 and 58, `py/overly-permissive-file`): `tools/audit/seat/postmerge.py`'s `enqueue` and `tools/audit/seat/roster_lib.py`'s `writer_lease` create `roster-drain.queue` and `roster-writer.lease` `0o600` instead of `0o644`. Readers, by `rg -n "roster-drain\.queue|roster-writer\.lease|WRITER_LEASE|writer_lease|postmerge\.QUEUE"`: `beat_jobs.py` and `carry_fold.py`, both run by the operator against the same `HPO_STATE_DIR`, so owner-only loses no reader. Swept over `tools/` and `custom_components/` with `rg -n "os\.open\(|os\.chmod\(|\.chmod\(|mktemp\(|0o6[0-7][0-7]|0o7[0-7][0-7]"`: these two are the only sites creating a non-executable file group- or world-readable.

## Head

e227b49065262f5364526b56b7b763d3cd51cb6a

## Mutation proof

Part A, `tools/audit/seat/mutant_run.py --spec <spec> --cmd 'python3 tests/entities.py'` (PYTHONPATH=tests/hastub), each mutant one line of `.github/workflows/codeql.yml`:

- `python_cap_back_to_75` (`- { language: python, timeout: 120 }` to `75`, main's value): `KILLED python_cap_back_to_75`.
- `blanket_raise_actions` (`- { language: actions, timeout: 45 }` to `120`): `KILLED blanket_raise_actions`.
- The unmutated copy prints `SURVIVED NULL`, and at the head `tests/entities.py` prints `ok   codeql.yml's analyze cap is per leg: python clears the measured worst case, the others stay at 45`.

The command (`--cmd`) exits 0 exactly when `tests/entities.py` prints that check `ok`, so a timing check elsewhere in the file on a loaded host cannot kill the null.

Part B, from the handoff (036cb18339, unchanged here): `postmerge.py`'s `MUTANTS` entry `queue_world_readable` reverts the mode to `0o644`, and `python3 tools/audit/seat/postmerge.py --self-test` prints `ok   mutant queue_world_readable killed by: the queue enqueue creates is owner-only under umask 022`. Through `tools/audit/seat/mutant_run.py --spec`, `--cmd 'python3 tools/audit/seat/roster_lib.py --self-test'` prints `KILLED lease_world_readable` and `--cmd 'python3 tools/audit/seat/postmerge.py --self-test --no-mutants'` prints `KILLED queue_world_readable`, each with `SURVIVED NULL`.

## Null control

Part A: on main's workflow (python cap 75) every capped push job ends on the same `##[error]The operation was canceled.` at 75.1 minutes, 22 of the 40 measured. The entities pin's own null control is the `blanket_raise_actions` mutant above: moving a leg that reads about 40x under 45 is refused. A pull request's own python leg ignores `tests/**` and `dev/**` and runs far under either cap, so this PR's `pull_request` run cannot show Part A; the first main push run after the merge finishing `Analyze (python)` under 120 does.

Part B: main's code with the two pins added and the modes still `0o644` fails `writer_lease: the lease file is owner-only under umask 022 (got: 0o644)` and `the queue enqueue creates is owner-only under umask 022 (got: 0o644)`; at the head both self-tests report 0 failed.

## Figures

<!-- figure-block: scope-line mb=18a60ea5f66223c3948738a6be284f035c5f9bac head=e227b49065262f5364526b56b7b763d3cd51cb6a -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `codeql / Analyze (python)` and `gate` on main 0ae95e4c9b: this PR is the fix (Part A). Cheaper detector: none ran. The 75 cap's own comment said to re-derive it from the job list, but no instrument reads the python leg's duration against its cap, so the first signal was main going red; the measurement above shows capped jobs on main since 2026-11-18, three days before this red was owned. The countermeasure candidate (an advisory line when the p90 of main's python leg passes 90 % of its cap, standing cost one jobs listing per main push) is an instrument, which the round's instrument freeze routes to the round-end proposal triage, not this hotfix.
- code-scanning alert 57 (py/overly-permissive-file) and code-scanning alert 58 (py/overly-permissive-file): this PR is their fix (Part B). The next CodeQL run on main closes them; neither is dismissed. Cheaper detector: the self-test pins Part B adds, which each instrument's `--self-test` lane runs; standing cost one `os.stat` per run.

## Forward-carry

- The structural cure for the python leg's duration (splitting `tests/features.py`, or narrowing what main's push leg extracts) is named in `.github/workflows/codeql.yml`'s cap comment as an owner ruling, not a cap. Carry: dismissed: an owner ruling, not a fix; the orchestrator puts the question to the owner with this PR's measurement

## Friction

none
