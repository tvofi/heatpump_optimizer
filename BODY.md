R10-CODEQL-PR-PATHS (P606): a pull request's `Analyze (python)` leg now ignores `tests/` and `dev/`; main's push run keeps the full path set. Ruled by the orchestrator under mandate 6715477401 (scope all), not by tvofi in person. The required context `codeql / Analyze (python)` keeps its name and category and stays required; the non-gating-leg arm is declined. There is no scheduled CodeQL run (codeql.yml is a `workflow_call` callee of ci.yml), so main's push run is the only full python analysis: a finding it raises in `tests/` or `dev/` that the PR leg missed is a red on main, handled as any other.

The callee already sees the caller's event (`github.event_name` is the caller's in a reusable workflow, as its own "Restore the decision program" step relies on), so no input is passed from ci.yml: the init `config` picks the ignore list by `github.event_name == 'pull_request' && matrix.language == 'python'`. The tests/entities.py pins moved in the same diff: the old pin (ignored files must not parse) now reads the full-run list, and a new pin reads both lists out of the registered text.

Alternative rejected: a second init step per event (duplicates the step the existing pins read).

## Head

04a1f28c14cb79f61b62cfdc3c4165d1cc8204e4

## Mutation proof

Round 2 (blocked verdict: the main-push full-set pin survived M2 and M3). The check now anchors the whole config as `paths-ignore: ${{ (<GUARD>) && '<PR list>' || '<BASE list>' }}` and evaluates it for push, pull_request, merge_group and workflow_dispatch across the three legs: only pull_request on python may select the tests/dev list. Mutants of codeql.yml run against `PYTHONPATH=tests/hastub python3 tests/entities.py` (one pass, script /tmp/mut.sh, each restored after):
- M1 drop ` && matrix.language == 'python'`: rc=1, the check FAILs.
- M2 negate the guard (`!(...)`): rc=1, the check FAILs (survived at the previous head).
- M3 guard `|| true`: rc=1, the check FAILs (survived at the previous head).
After the pass `git status --short` was empty.

## Null control

Unmodified tree (M0 of the same pass, rc=0): `PYTHONPATH=tests/hastub python3 tests/entities.py` exits 0 and both codeql checks print `ok`. Before the fix of my own pin order, both printed FAIL (lists read swapped), so the pin discriminates.

## Figures

- Before/after job seconds: NOT MEASURED. This seat has no authenticated `gh`, so `python3 tools/audit/seat/ci_critpath.py --repo tvofi/heatpump_optimizer --workflow ci.yml --last 5` could not run, and a job time needs a PR run on this head. The brief's recorded before is 2173-3623 s (siblings 48-104 s); target under 900 s. Carry: dismissed: owed to the orchestrator, who has the runs; run the command above over the 5 runs before and after this merge and put both medians here.
- Whether ignored-path alerts read as fixed on a PR against main's same-category analysis: NOT MEASURED, same reason (needs a PR run with the PR alert view). I kept the shared category deliberately: a separate PR category would leave the required `/language:python` configuration missing on the PR ("1 configuration not found", per codeql.yml's stand-in comment). If the first PR run shows tests/ or dev/ alerts as fixed, the PR leg needs its own category plus an equivalent for the required context. Carry: dismissed: conditional on that measurement.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` exit 0 at the head; `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` exit 0 at 04a1f28c1 (no interpreter with homeassistant; the skip is ruled allowed), merge-tree with origin/main clean.

## Red checks

none owed by this branch. Main is red on `tests / fast` (features.py combi census) since #3398; a hotfix is in flight and that red is main's.

## Forward-carry

none

## Friction

none
