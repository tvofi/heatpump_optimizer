Six open Dependabot alerts on `main`, three advisories times the two manifests that pin `aiohttp==3.14.3`; each advisory is first patched in 3.14.4. Both test locks now pin 3.14.4 with the complete index hash list for the version, so the alerts' manifests no longer name the vulnerable version.

The typing lock also moves `yarl` 1.24.5 to 1.25.1: aiohttp 3.14.4 requires `yarl>=1.25.1,<2.0`, and `homeassistant==2026.9.3` pins `aiohttp==3.14.3` and `yarl==1.24.5` exactly, so the lock cannot resolve the bump without both. Both override the homeassistant pins, the mechanism the file's header already uses for `cryptography` and `PyJWT`, and the header now records the pair and the drop condition. CI installs this lock with `--no-deps` (`.github/workflows/tests.yml:680`), so the lock, not homeassistant, decides what is installed.

## Head

`1a9b90965c31c6fd0093f623ec623e319fd6d3be` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2487.md`. The authored code head is `d7241ed4fcb4a578f6fc1df6ca4b977cfd379058`.

`9e39a47187f234c4e6977d127538e2c17b05c2ce` merges origin/main `76bb45628` into the authored code head `d7241ed4fcb4a578f6fc1df6ca4b977cfd379058` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

d7241ed4fcb4a578f6fc1df6ca4b977cfd379058

The second commit is comment-only (a header paragraph). Both lock bodies are byte-identical to the compiled bodies every control below ran against.

## Mutation proof

The version line and the hash list are one predicate: `--require-hashes` binds the artifact set to the digests in the file. Two mutations of the fix, both red.

1. Version line reverted to `aiohttp==3.14.3`, 3.14.4 hash list kept:
   `ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE`, `Expected sha256 019587c7...`, `Got 11fb37ef...`, rc=1.
2. All 161 aiohttp hash lines altered one hex digit, version line at 3.14.4:
   `Expected sha256 00134dc8...`, `Got fac247d0...`, rc=1.

Both ran on scratch copies; the tree was unmodified and control 1 (below) is green at the head.

## Null control

Unmodified tree (`origin/main` a2b25bbc5): the same install command, against `aiohttp==3.14.3` and its own 119 hashes, exits 0 and installs `aiohttp-3.14.3`. The environment is not what turns the mutants red.

The planted-hash run is also the hash-list control, and it corrected its own design: planting one hash — the arm64 wheel's — PASSED, because pip selected `aiohttp-3.14.4-cp313-cp313-macosx_10_13_universal2.whl` on that run instead of the arm64 wheel, whose digest was still listed. The control must plant every hash for the package; only then does a green install mean the list went unread.

## Figures

- 6 open alerts before the change, numbers 85-90, all `state=open`, `fixed_at=null`: `gh api "repos/tvofi/heatpump_optimizer/dependabot/alerts?state=open" --paginate`
- alert disposition: every alert the enumerator returns names one of the two manifests this diff bumps (`tests/requirements-ci.txt` 85-87, `tests/requirements-typing.txt` 88-90); it returns no aiohttp pin outside them and no other package
- aiohttp 3.14.4 hash set equals the 161 files PyPI publishes for the version; yarl 1.25.1 equals its 138: `python3 -c "import json,re,urllib.request as u;t=open('tests/requirements-ci.txt').read();b=t[t.index('aiohttp=='):t.index('aiosignal==')];hs=set(re.findall(r'sha256:([0-9a-f]{64})',b));idx={x['digests']['sha256'] for x in json.load(u.urlopen('https://pypi.org/pypi/aiohttp/3.14.4/json'))['urls']};print(len(hs),len(idx),hs==idx)"` (and the same over `tests/requirements-typing.txt` for `yarl==1.25.1` against `https://pypi.org/pypi/yarl/1.25.1/json`, 138/138)
- version lines changed: one in the CI lock (`aiohttp`), two in the typing lock (`aiohttp`, `yarl`): `git diff HEAD~2 -- tests/requirements-ci.txt | grep -E '^[+-][a-zA-Z0-9]'` and the same for `tests/requirements-typing.txt`
- the CI lock compiles to one body on both installed interpreters (the header's own claim), and that body is the committed body: `uv pip compile tests/requirements-ci.txt --python-version 3.13.15 --python-platform x86_64-manylinux_2_28 --generate-hashes --no-header --no-annotate -o <a>` and the same with `--python-version 3.14.7 -o <b>`; `diff <a> <b>` empty and `diff <a> <(tail -n +27 tests/requirements-ci.txt)` empty
- control 1, install green: `python3 -m pip install --require-hashes --build-constraint tests/requirements-build.txt -r tests/requirements-ci.txt` exits 0 in a Python 3.13.15 venv (pip 26.2.1), `Successfully installed ... aiohttp-3.14.4 ...`
- null control, baseline install green: same command against `git show origin/main:tests/requirements-ci.txt`, `Downloading aiohttp-3.14.3-cp313-cp313-macosx_11_0_arm64.whl`
- mutation 1 red: same command against a scratch copy of the CI lock with the version line at 3.14.3
- mutation 2 red: same command against a scratch copy with every aiohttp digest altered
- typing ruler: `python3 tests/typing_ruler.py` -> `ALL 12 typing-ruler source checks PASSED`, including `the typing job's hashed lock installs the recorded pins`; the run also drove the pinned mypy arm, `ALL 9 typing-ruler checks PASSED`
- gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: FULL`, `reason: tests/requirements-ci.txt changes the gate itself, so every closure is suspect`
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`
- `python3 tests/closure.py selftest` -> `ALL 124 closure shrink pins PASSED`
- `python3 tests/layout.py` -> `layout self-test: ok`
- `python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)` -> `claims hygiene: a2b25bbc5518b5cb212429fdd623b5d33634fd08 ok`
- `python3 tests/harness_headers.py` -> `ALL 109 HARNESS HEADER CHECKS PASSED` (run with its docstring's `PYTHONPATH=tests/hastub:custom_components:tests`)

## Red checks

`nightly-status` is red at this head and it grades `main`, not this tree: its failing step reports the last scheduled run's conclusion on `main`, and this diff touches no reporter input, so it stands red whatever this branch does. `pr-contract` was red at the previous head because `## Head` still named the pre-row head while CI ran on the row commit, and again at this head because the two `## Friction` bullets ended their `Carry:` markers inside a code span, which `carry_audit.py` reads as a quoted example rather than a marker; both markers now stand bare, and the carrier passes locally with 0 findings. The cheaper detector is `python3 -I tools/audit/carry_audit.py check --body <body>` — under a second, local, and already wired into `prepr.sh`.

Two local reds are answered here.

- `tests/harness_headers.py` exited 1 with `12 of 109 HARNESS HEADER CHECKS FAILED` on a first run that set `PYTHONPATH=tests/hastub` only. The script's own docstring specifies `PYTHONPATH=tests/hastub:custom_components:tests`; rerun at the same head with that path, it prints `ALL 109 HARNESS HEADER CHECKS PASSED`. The invocation, not the tree, was the defect; the cheaper detector is the docstring line the run skipped.
- `tests/entities.py` did not complete locally: stopped at 46 minutes while three other seats ran the same script concurrently (load average 66). It is not a `run_always` script; the gate's `MODE: FULL` runs it in CI, and no local result is claimed.

## Forward-carry

none.

## Friction

- `fixer-brief: contradiction`: the brief scopes the bump to "the version line plus every hash line for the package", but the typing lock cannot hold aiohttp 3.14.4 beside `yarl==1.24.5`, aiohttp 3.14.4's resolver floor is `yarl>=1.25.1`, and `homeassistant==2026.9.3` pins both exactly. Fixed inside the same group and the same advisory closure, as `yarl==1.25.1` under the file's existing override mechanism. Carry: dismissed: same group, same two files; the header carries the drop condition
- `null-control: unenforced`: a single planted hash can pass because pip selects among a package's published artifacts (universal2 and arm64 both listed, one chosen per run), so the control must alter every hash for the package. Carry: dismissed: group-local technique, recorded above and in the seat report

