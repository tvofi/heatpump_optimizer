R10-CI-LAYOUT-P2, sub-PR P2a "umbrella engine, inert": unit **U0a, the gate core**. Part of #2495. Offline cloud fixer seat; no PR opened, no row written, nothing posted. Base `738d950aa981` (origin/main at dispatch, measured 2026-10-22). Head: the tip of `handoff/r10-ci-layout-p2a-u0a`.

## Unit

U0a, the gate core. Files (all mine; no other P2a unit's file touched):

| file | what |
|---|---|
| `tools/ci/ghapi.py` (new) | contract item 1: the one REST client of `tools/ci/` |
| `tools/ci/prelude.py` (new) | DESIGN-P2 2.3 / 4.3: kind, pr, base, head, scope, legs, workset; dispatch verification; the verdict wait |
| `tools/ci/gate.py` (new) | the 4.1 predicate ported from `measure/rev/gate_model.py` at `1371a0a6`; `REQUIRED`; `--refresh`; `RATE-LIMITED`; `--sweep` dispatch |
| `tools/policy/fixtures/required-contexts.json` | additive `gate_required` (+ its `_gate_required` note); `contexts` stays the 17 |
| `tests/closure.py` | `GATE_FILES += "tools/ci/"` (classifies my three files; the harness is under the INERT `dev/audit/` prefix, the fixture was already classified) |
| `dev/audit/harnesses/r10_ci_gate_core.py` (new) | the driver glue: the design's oracles driving the port; B3 enumeration; predicate mutants |
| `tests/layout.json` | `tools/ci/**` joins the `tools` category: `tests/layout.py` refused my three files otherwise (every `tools/ci/` unit needs this line; the glue keeps one) |
| `tests/closures.json` | one INERT READS line, `harness_headers.py` → my harness, written by `ci_predict.py --apply-inert` |
| `dev/audit/harnesses/r10_seat_selftests_mutants.py` | 7 per-file mutants (`gate-1..3`, `ghapi-1..2`, `prelude-1..2`) in their own block; `rel()` lets an entry name a repo-relative instrument |

`git diff --stat $(git merge-base origin/main HEAD)...HEAD`:

```
 dev/audit/harnesses/r10_ci_gate_core.py           | 257 +++++++++++++
 dev/audit/harnesses/r10_seat_selftests_mutants.py |  22 +-
 tests/closure.py                                  |   4 +
 tests/closures.json                               |   1 +
 tests/layout.json                                 |   1 +
 tools/ci/gate.py                                  | 426 ++++++++++++++++++++++
 tools/ci/ghapi.py                                 | 218 +++++++++++
 tools/ci/prelude.py                               | 281 ++++++++++++++
 tools/policy/fixtures/required-contexts.json      |  24 ++
 9 files changed, 1232 insertions(+), 2 deletions(-)
```

Production lines, rule: code lines (tokenize: any non-comment token) outside `self_test()` and outside docstrings, over `tools/ci/*.py`: **ghapi 81, prelude 140, gate 229 = 450**. The plan's U0a row (EXECUTION.md §1, 400 est.) costed prelude + gate only (369 here); `ghapi.py` (81) joined U0a with contract item 1. I judge 450 within "about 400" for that reason and did not stop; the reviewer may judge otherwise.

## Interface

Contract items 1-4, exactly as exported:

**`tools/ci/ghapi.py`** (stdlib only; the only `tools/ci/` module importing urllib):
- `get(path: str, params=None) -> Resp`, `post(path: str, body=None) -> Resp`; `Resp = (status: int, headers: dict, json)`. `path` is repo-relative (`repos/o/r/...`) or a full URL. A non-2xx answer is **returned**, never raised, except:
- `class RateLimited(Exception)`: `.path`, `.reset_epoch: int`. Raised on 403/429 whose body says the rate limit was exceeded (both GitHub wordings: "API rate limit exceeded", "You have exceeded a secondary rate limit"). `reset_epoch` from `X-RateLimit-Reset`, else now + `Retry-After`, else now + 60.
- `paginate(path, params=None, get=get) -> list`: every item of every page (`per_page=100`, Link-followed, at most 50 pages); an object page contributes its one list member. Raises `class ApiError(Exception)` (`.path`, `.status`) on a non-200 page. The `get=` keyword is additive: injected modules pass their own.
- Token: `GITHUB_TOKEN`, else `GH_TOKEN`.

**`tools/ci/prelude.py`**: `python3 -I tools/ci/prelude.py [--changed-from FILE]` prints `key=value` lines for `$GITHUB_OUTPUT`: `kind`, `pr`, `base`, `head`, `scope` (`full` on push, else `auto`), `legs` (compact JSON `{"actions": "analyze"|"skip", "javascript-typescript": …, "python": …}` from `tools/pr/codeql_scope.py decide` over `--changed-from`, which the caller fills with `codeql_scope.py changed` on `pull_request`; an empty list analyzes), `workset` (space-separated units). `head` and `workset` are additive to the contract's five (the design's 2.3 table names `head`; `workset` carries A2's kernel-points for U11's guard). Exit 0; 1 with `FAIL <why>` on stderr (dispatch not verified, wait bound); 3 with `RATE-LIMITED reset_epoch=<n> <path>` on stderr. Library, for U0c's `run-name` and the gate:
- `context(event_name, payload: dict, env: dict) -> dict` (the flat ctx), `derive(ctx) -> (kind, pr, base)`, `title(kind, pr, base, sha="") -> "CI <kind> pr=<n|-> base=<b|-> sha=<sha|->"`, `parse_title(t) -> (kind, pr, base) | None`, `title_sha(t) -> str`, `workset(kind, pr, labels=()) -> set[str]`.
- Kinds: `code`, `edit`, `review`, `kernel-points` (labeled with that label: WORKSET {kernel-points}), `label` (any other label: empty WORKSET, its gate only re-judges). `synchronize` (any code kind) with the label present adds `kernel-points` to the workset. `kernel-points` is in no `REQUIRED` class.
- `POLL_S = 60` (tvofi's floor), `WAIT_MAX_S = 8700`, one runs listing per poll; waits on every lower-id run in `queued|pending|waiting|requested|in_progress`, never on a held (`action_required`) one.

**`tools/ci/gate.py`**:
- `python3 -I tools/ci/gate.py --pr N --base B --kind K`: the three are the prelude's outputs, cross-checked only (the gate derives from `GITHUB_EVENT_NAME`/`GITHUB_EVENT_PATH` itself). Reads `GITHUB_SHA`, `GITHUB_REPOSITORY`, `GITHUB_RUN_ID`, `GITHUB_RUN_ATTEMPT`; needs a `fetch-depth: 0` checkout for D-2's `git diff origin/<base>...<head> -- custom_components/` (git failure reads as reaching: fail closed). Order: event, git, then the Actions/pulls reads last (R3-1), then the summary.
- stdout first token: `PASS` (exit 0), `FAIL <reason>` (exit 1; further reasons on later lines), `RATE-LIMITED reset_epoch=<n> <path>` (exit 3) followed by the line `::error title=RATE-LIMITED::reset_epoch=<n>`. That annotation is how a sweep tells a rate-limited red gate from any other (`GET check-runs/<gate job id>/annotations`); it is not in the contract and U0b may ignore it. `$GITHUB_STEP_SUMMARY` gets the outcome, the reasons, and "Not gating:" this run's jobs that no class requires.
- `--refresh`: on `pull_request`/`pull_request_review` only; fork head → NOTICE, exit 0; head no longer live → NOTICE, exit 0; re-runs (`POST actions/jobs/<id>/rerun`) the `gate` job of every other **completed** run at the head whose latest `gate` is `success`, skipping (and printing) any run at `run_attempt >= 45`. A non-2xx re-run prints `FAIL rerun …` and exits 1; a rate limit exits 3.
- `--sweep --run ID`: `import sweep; return sweep.main(["--run", ID], get, post)` with ghapi's `get`/`post`; a `RateLimited` it raises becomes `RATE-LIMITED` (exit 3). **Until U0b's `tools/ci/sweep.py` is assembled, the guarded import prints `FAIL sweep-unavailable: …` and exits 1.** U0b must not edit gate.py, and need not.
- `REQUIRED: dict[str, tuple[str, ...]]`, keyed by event class (`event_class(event_name, pr, reaches_cc)`):
  - `"pr"`: an event naming a PR, diff missing `custom_components/`: the 17 renamed `<stem> / <job>` (17 names);
  - `"pr-cc"`: the same, diff reaching it: + `arch-score / arch-score` (D-2) (18);
  - `"no-pr"`: a dispatch naming no PR: the code units' 15 (closure-scope included, as the model);
  - `"push"`: the code units less `tests / closure-scope`, plus B3's `tests / coverage`, `tests / coverage-ratchet`, `tests / ci-ratchet` (17).
  - Not `tests / arch-instrument` (P2b's U5b adds it to `REQUIRED` and to the enumeration together).
- `gate_required() -> list[str]`: the sorted union, which the fixture's `gate_required` equals (21 names; gate.py's self-test asserts the equality, and the glue's entities pin will):

```
arch-score / arch-score
budget-raise-gate / budget-raise-gate
codeql / Analyze (actions)
codeql / Analyze (javascript-typescript)
codeql / Analyze (python)
governance / env-matrix
governance / policy-docs
governance / wave-script
hassfest / hassfest
pr-contract / pr-contract
tests / briefs
tests / browser
tests / ci-ratchet
tests / closure-scope
tests / closures
tests / coverage
tests / coverage-ratchet
tests / fast (3.14)
tests / mutation
tests / typing
validate / validate-hacs
```
- Pure layer (what the oracles drive): `UNITS`, `CODE`, `BODY`, `PUSH_ONLY`, `ATTEMPT_CAP = 45`, `judging(run)`, `gate(ctx, api) -> (ok, reasons)` with `gate_model.gate`'s `api` shape; `read_api(ctx, claim, reaches_cc, get)` builds that shape.

**B3, enumerated by command** (`python3 dev/audit/harnesses/r10_ci_gate_core.py b3`, reading `git show origin/main:.github/workflows/tests.yml`; rule: a job reddens the push run iff its `if:`, evaluated for a push to main, can be true and it is not `continue-on-error`; any term it cannot decide reads as true, an unknown token refuses; a single-dimension literal matrix names `<job> (<value>)`):

```
$ python3 dev/audit/harnesses/r10_ci_gate_core.py b3; echo rc=$?
b3: enumerated from origin/main:.github/workflows/tests.yml: ['briefs', 'browser', 'ci-ratchet', 'closures', 'coverage', 'coverage-ratchet', 'fast (3.14)', 'mutation', 'typing']
b3: REQUIRED['push'] tests / * : ['briefs', 'browser', 'ci-ratchet', 'closures', 'coverage', 'coverage-ratchet', 'fast (3.14)', 'mutation', 'typing']
b3: parity GREEN; only in tests.yml [], only in REQUIRED []
rc=0
```

## Controls

All run at this head on Linux, `python3` 3.11 for the instruments, `/opt/hpo/venv-ci` (3.14.7) for the suite.

**Oracles driving the port** (`dev/audit/harnesses/r10_ci_gate_core.py`: extracts `measure/` from `1371a0a6`, registers `gate_model` as a module whose every symbol is the port's; `gate_sim`'s `G.judging` ablations are installed into the port for each call). Pass = the oracle's own rc 0 **and** its output byte-identical to the design's recorded `.txt`:

```
$ python3 dev/audit/harnesses/r10_ci_gate_core.py replay --model | tail -1
$ python3 dev/audit/harnesses/r10_ci_gate_core.py replay | tail -1
$ python3 dev/audit/harnesses/r10_ci_gate_core.py sim | tail -1     # 8 min
gate_replay2.py over the MODEL: rc 0; output IDENTICAL to 1371a0a6:measure/rev/gate_replay2.txt
gate_replay2.py over tools/ci/gate.py: rc 0; output IDENTICAL to 1371a0a6:measure/rev/gate_replay2.txt
gate_sim.py over tools/ci/gate.py: rc 0; output IDENTICAL to 1371a0a6:measure/rev/gate_sim.txt
(sim: GATE-SIM rc 0; run at `f3a7e3553`. Its predicate, every module-level assignment and `gate`/`judging`/`event_class`/`_names`, is AST-identical at the head: `python3` comparing `ast.get_source_segment` of each between `git show f3a7e3553:tools/ci/gate.py` and the head prints `predicate identical`; later commits touch the I/O layer and the self-test only. The replay and the mutants were re-run at the head.)
```

- That covers the 22 history heads (agree 22/22), the 37 replay rows, the 42 timed sequences with END-BAD 0 under all three readings in both chain arms, the **7 planted defects refused** (the fork plant R3-4 among them), the **TAIL** arm (re-run and every-attempt tails, READ-LATE null) and the **EARLY** arm, and gate_sim's ablation rows (each design element load-bearing).
- Null for "identical": the same oracle over the model (`replay --model`) is identical too, and `--no-b3-fill` makes the port's replay differ (next item), so the comparison can fail.
- **B3 fill, and its null.** The model predates B3, so the shim adds the three B3 jobs green to a push run that lacks them (never over one it has). `replay --no-b3-fill`: exactly the two push rows go BAD, naming exactly the B3 names; nothing else moves:

```
$ python3 dev/audit/harnesses/r10_ci_gate_core.py replay --no-b3-fill | grep -E 'BAD|GATE-REPLAY2|over'
0e238c3042 FAIL     FAIL     False       agree      governance / wave-script: failure (this run); pr-contract / pr-contract: failure (this run)
6c0218b0d5 FAIL     FAIL     False       agree      codeql / Analyze (javascript-typescript): cancelled (this run); governance / env-matrix: cancelled (this run); tests / b
b0140e47bc FAIL     FAIL     False       agree      governance / wave-script: failure (this run); pr-contract / pr-contract: failure (this run)
  BAD push: closure-scope absent (never runs on push), body units not applicable ruleset FAIL gate FAIL  tests / coverage: ABSENT (this run); tests / coverage-ratchet: ABSENT (this run); tests / ci-ratchet: ABSENT (
  BAD push run as the umbrella writes it (closure-scope never runs, body rows skipped)           gate FAIL  
GATE-REPLAY2 rc 1
gate_replay2.py over tools/ci/gate.py: rc 1; output DIFFERS from 1371a0a6:measure/rev/gate_replay2.txt
```

**B3 parity, plant and null**:

```
$ python3 dev/audit/harnesses/r10_ci_gate_core.py b3 --plant; echo rc=$?
b3: enumerated from origin/main:.github/workflows/tests.yml: ['briefs', 'browser', 'ci-ratchet', 'closures', 'coverage', 'coverage-ratchet', 'fast (3.14)', 'mutation', 'typing']
b3: REQUIRED['push'] tests / * (PLANT: ci-ratchet dropped) : ['briefs', 'browser', 'closures', 'coverage', 'coverage-ratchet', 'fast (3.14)', 'mutation', 'typing']
b3: parity RED; only in tests.yml ['ci-ratchet'], only in REQUIRED []
rc=1
(null: the unplanted `b3` above, parity GREEN, rc 0)
```

**RATE-LIMITED (A1 item 4)**, in `gate.py --self-test`, through `main()` with a stubbed `get`: plant, a 403 rate-limit → `RATE-LIMITED`, exit 3, the annotation line, never PASS; null, an ordinary 403 (`Resource not accessible by integration`) → `FAIL … HTTP 403 Resource not accessible …`, exit 1. Same pair at the transport in `ghapi.py --self-test` (raised vs returned), and the prelude's dispatch read → exit 3.

**Fork plant R3-4**: gate_sim's I5 (above) and `gate.py --self-test` "a fork PR, every source green" → `FAIL PR 7: its head is not in this repository`; its null is the self-test's "every source green" → `PASS`.

**Self-tests** (each prints `<name> self-test: N checks, 0 failed`):

```
$ for f in ghapi prelude gate; do python3 -I tools/ci/$f.py --self-test; done
ghapi self-test: 11 checks, 0 failed
prelude self-test: 27 checks, 0 failed
gate self-test: 27 checks, 0 failed
```

**Mutation proof on the predicate** (`r10_ci_gate_core.py mutants`: each mutant removes or inverts one rule in `gate.py`; killed = the self-test or the replay goes red; the unmutated pair is green first):

```
$ python3 dev/audit/harnesses/r10_ci_gate_core.py mutants
mutants: unmutated self-test rc 0, replay rc 0
  M1 prelude conclusion: KILLED (self-test rc 0, replay rc 1)
  M2 prelude cross-check: KILLED (self-test rc 1, replay rc 1)
  M3 attempt cap: KILLED (self-test rc 1, replay rc 1)
  M4 unnamed dispatch at a PR head: KILLED (self-test rc 1, replay rc 0)
  M5 fork PR (R3-4): KILLED (self-test rc 1, replay rc 1)
  M6 live base: KILLED (self-test rc 0, replay rc 1)
  M7 defer rule: KILLED (self-test rc 1, replay rc 1)
  M8 judging: listed gate: KILLED (self-test rc 0, replay rc 1)
  M9 judging: owed jobs (R3-2): KILLED (self-test rc 1, replay rc 0)
  M10 skipped is not success: KILLED (self-test rc 1, replay rc 1)
  M11 source must judge the live base: KILLED (self-test rc 0, replay rc 1)
  M12 own unit always counts: KILLED (self-test rc 1, replay rc 0)
  M13 D-2 arch-score: KILLED (self-test rc 0, replay rc 1)
  M14 held run is no source: KILLED (self-test rc 1, replay rc 0)
  M15 unreadable title: KILLED (self-test rc 0, replay rc 1)
  M16 B3 on push: KILLED (self-test rc 1, replay rc 0)
RESULT mutants=16 survivors=0
```

M12 and M14 survived the first pass (the replay cannot see them); two self-test checks were added ("this run's own unit is never filled from an older run", "a newer held run is neither waited on nor a source") and both are now killed. **Disclosed inconsistency:** M4 read `KILLED (self-test rc 0, replay rc 1)` in that first pass and `SURVIVED (self-test rc 0, replay rc 0)` in a later one; three replays under M4 at the current head all read rc 0 and IDENTICAL, so the replay does not reach M4 (no row is an unnamed dispatch; gate_sim's plant does, too slow per mutant). I cannot explain the first reading. M4 is now killed by a self-test check with its null ("judged as usual at no PR's head").

**Seat-selftest mutants** (`r10_seat_selftests_mutants.py`, per-file ids in their own block). Their steps do not exist until the glue wires them, so I ran them with the three steps below added to `governance.yml` `instrument-self-tests` **uncommitted** and reverted after; the harness's baseline (the unmutated step green) ran first for each:

```
$ python3 dev/audit/harnesses/r10_seat_selftests_mutants.py gate-1 gate-2 gate-3 ghapi-1 ghapi-2 prelude-1 prelude-2
== gate-1 tools/ci/gate.py: KILLED rc=1 | gate self-test: 23 checks, 1 failed
== gate-2 tools/ci/gate.py: KILLED rc=1 | gate self-test: 23 checks, 1 failed
== gate-3 tools/ci/gate.py: KILLED rc=1 | gate self-test: 23 checks, 1 failed
== ghapi-1 tools/ci/ghapi.py: KILLED rc=1 | ghapi self-test: 11 checks, 1 failed
== ghapi-2 tools/ci/ghapi.py: KILLED rc=1 | ghapi self-test: 11 checks, 2 failed
== prelude-1 tools/ci/prelude.py: KILLED rc=1 | prelude self-test: 27 checks, 2 failed
== prelude-2 tools/ci/prelude.py: KILLED rc=1 | prelude self-test: 27 checks, 1 failed
RESULT survivors=0
(the self-test counts are those at the time of the run; the gate and prelude self-tests have since gained checks, none of which these mutants touch)
```

**Repository checks.** The gate, `PREPR_SKIP_CLOSURES=1 GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=738d950aa981 ./tests/run.sh` under `/opt/hpo/venv-ci` (python 3.14.7), `MODE: FULL`:
- run 1 (head `c7589113a`): `tests/layout.py` FAILED, `placement: tools/ci/{gate,ghapi,prelude}.py is in 0 categories of tests/layout.json` (`layout: GUARD: 3 refusal(s)`); repaired in `8bc9901bf` (`tools/ci/**` joins the `tools` category), `tests/layout.py` rc 1 → rc 0. That run was then killed by my session's 30-minute background limit, not by a test.
- run 2 (head `515d41bb7`): every script ok except `tests/stress.py` and `tests/harness_headers.py`, both refused in 0 s with `gate_lock: flock-wrap refused, u0a-cloud holds no lease` (I set `HPO_GATE_LOCK_LABEL` without taking the lease: my error, not the tree's). Re-run alone under `tests/gate_lock.py take`: `ALL 113 STRESS CHECKS PASSED`, rc 0; `harness_headers.py` rc 1, `FAIL depth seams: dev/audit/harnesses/r10_ci_gate_core.py:48: ROOT = Path(__file__).resolve().parents[3]`; repaired in `e312a70f6` (the canonical `repo_root` walk), rc 0.
- after run 2 the head moved only by `e312a70f6` (the harness, under INERT `dev/audit/`) and `06c99c0e3` (two `gate.py` self-test checks; no gate script executes `tools/ci/`). At `06c99c0e3`: `tests/layout.py` rc 0; `python3 tools/pr/ci_predict.py --base origin/main` → `no closures or fast red predicted` (after `--apply-inert` added this harness to `harness_headers.py`'s INERT READS, `515d41bb7`).

`python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`; `python3 tests/throwaway_git.py --check` → `0 raw git init or clone site(s) refused`; `python3 -I tools/audit/seat/tmp_paths.py --check` → `0 refused`; `python3 -I tests/harness_headers.py` → rc 0 (above). No new `git push` site (no `PUSHERS` row owed). Scope (fixer step 5): `MODE: FULL` (`tests/closure.py` and `tools/ci/` are gate files), as EXECUTION.md §3 says P2a is.

**Not done here**: no live call of any kind (the unit is offline). The prelude's `--changed-from` arm is only driven over `README.md` in the self-test. The fixer's "finder's harness at both ends" has no finder for a new unit; the oracles at both ends are the design's (model vs port, above).

## Propagation (what later stages must carry; the briefs are the orchestrator's to edit, I may push nothing else)

- **P2a glue (integration seat)**: three `instrument-self-tests` steps, exactly as I ran them: `python3 -I tools/ci/ghapi.py --self-test`, `python3 -I tools/ci/prelude.py --self-test`, `python3 -I tools/ci/gate.py --self-test`, one per step (the seat harness's `step_for` requires exactly one step per file). Then the 7 seat mutants run for real. The entities pins: `gate.REQUIRED`'s union == fixture `gate_required` (gate.py's self-test asserts it already), and B3 parity (`r10_ci_gate_core.py b3` is the enumeration; an entities pin has PyYAML where governance's self-test step may not).
- **Every other `tools/ci/` unit (U0b, U6-lib) and the glue**: `tests/layout.json` must list `tools/ci/**` once (this branch adds it; an assembled tree keeps one line), or `tests/layout.py` refuses each new `tools/ci/` file.
- **U0b (sweep)**: `--sweep` calls `sweep.main(["--run", ID], get, post)`; a red `gate` is rate-limited iff its job's check run carries the annotation `title=RATE-LIMITED` with `reset_epoch=<n>`.
- **U0c (ci.yml)**: `run-name` must render `prelude.title(kind, pr, base, github.sha)` for the kinds above, `labeled` included; the gate step is `gate.py --pr "${{ needs.prelude.outputs.pr }}" --base … --kind …` (an empty `--pr` is a value, not an omission); the prelude step takes `--changed-from` from `codeql_scope.py changed` on `pull_request`; the gate job needs `fetch-depth: 0`.

## Red checks

- `nightly-status`: red on main's ancestry, not this diff's: the PR-only job reports the nightly lanes' latest result on main, which no PR's diff moves; this unit touches no nightly lane, workflow or test script (`tools/ci/` has no caller until P2b). No check went red because of this branch on CI (none ran: nothing was opened); the two local reds this branch caused (`layout.py`, `harness_headers.py`) are under Repository checks, each repaired before the handoff. Cheaper detector for both: `tools/pr/ci_predict.py` predicts neither (it predicts closures and fast reds); running `tests/layout.py` and `tests/harness_headers.py` on any new file is the standing cost, about 30 s.
