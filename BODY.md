One open Dependabot alert on `main`: GHSA-xmj3-9gf7-h52w (setuptools, low, vulnerable `>= 38.2.2, < 84.1.0`, first patched 84.1.0) against `tests/requirements-build.txt`, which pins `setuptools==84.0.0`. This PR moves that pin to 84.1.0 with both of its index hashes. It supersedes Dependabot #2678, closed 2026-10-27T04:26:34Z because a `tvofi` merge commit on its head (`d08cb515b`) fails `tools/policy/dependabot_contract.mjs` condition 2, and Dependabot answered both `rebase` and `recreate` with a refusal. The file at this head is byte-identical to Dependabot's own commit `6ee3e4d4f`, so nothing here departs from what #2678 proposed.

Refs #2722 (the roster group's listed issue; it covers the stale dependency graph under `R10-FLY-DEPGRAPH-STALE`, which this PR does not touch, so it is not closed here).

## Head

683965206e678d2107f27871cc533d7b89930446

One commit over `origin/main` `aaf8af512c1fb9aeabdf58dbb5131928f432d4d1`, touching `tests/requirements-build.txt` only: three lines out, three in (the version line and its two `--hash` lines).

## Mutation proof

The version line and the hash list form one predicate: `--require-hashes` binds the build-constraint artifact to the digests in the file. Mutant: both setuptools 84.1.0 digests replaced (`0000…`, `1111…`) in a scratch copy, version line kept. Installing PyYAML 6.0.1 from source against it (the sdist build that consumes this file) exits 1 with `ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE`, `Expected sha256 0000…`, `Got 5231689c6ac8156cd155cfb98c3fd6fb252c3e7e9bd3d78b64d3c55f132624c9`, then `Failed to build 'pyyaml' when installing build dependencies for pyyaml`. The tree was unmodified; the head arm below is green.

Planting only one digest (the wheel's) PASSED: pip fell back to the listed sdist, built a setuptools 84.1.0 wheel from it, and installed. A one-hash plant is a vacuous control here; only planting every digest for the version shows the list is read.

## Null control

Unmodified tree (`origin/main` `aaf8af512`): the same install against main's `tests/requirements-build.txt` exits 0 and uses `setuptools-84.0.0`. The environment does not turn the mutant red, and the head arm differs from it only in the setuptools version the build environment installs.

## Figures

- open alerts on `main` before the change: one, number 145, GHSA-xmj3-9gf7-h52w, `tests/requirements-build.txt`, first patched 84.1.0: `gh api 'repos/tvofi/heatpump_optimizer/dependabot/alerts?state=open&per_page=100' --jq '.[]|[.number,.security_advisory.ghsa_id,.dependency.package.name,.dependency.manifest_path,.security_vulnerability.first_patched_version.identifier]|@tsv'` (read 2026-10-28; a re-read after the merge is owed, below)
- alert disposition: the enumerator above returns one alert, and its manifest is the one file this diff edits; it returns no other package and no other manifest
- the committed lock body equals the header recipe run with `--upgrade-package 'setuptools==84.1.0'` over main's body as `-o` preferences: `printf 'setuptools>=61\nwheel\nCython<3.0\n' | uv pip compile - --python-version 3.13.15 --python-platform x86_64-manylinux_2_28 --generate-hashes --no-header --no-annotate --upgrade-package 'setuptools==84.1.0' -o <body>`, then `awk 'f;/^$/&&!f{f=1}' tests/requirements-build.txt | cmp - <body>` prints nothing (exit 0); only the setuptools stanza differs from main's body
- the two hashes equal PyPI's published sha256 for the version's two files (`setuptools-84.1.0-py3-none-any.whl` 5231689c…, `setuptools-84.1.0.tar.gz` 23657205…): `curl -s https://pypi.org/pypi/setuptools/84.1.0/json | python3 -c "import json,sys;[print(u['filename'],u['digests']['sha256']) for u in json.load(sys.stdin)['urls']]"`
- byte identity with Dependabot's commit: `git diff 6ee3e4d4f83b362001647b2d433d56c96cd20843 -- tests/requirements-build.txt | wc -l` prints 0
- head arm, install green: `pip install -v --no-cache-dir --require-hashes --no-binary pyyaml --build-constraint tests/requirements-build.txt -r <pyyaml stanza of tests/requirements-ci.txt>` in a fresh Python 3.14.7 venv (pip 26.2.1), exit 0, build env `Successfully installed Cython-0.29.37 packaging-26.3 setuptools-84.1.0 wheel-0.48.0`, then `Successfully installed pyyaml-6.0.1`
- null control: the same command against `git show origin/main:tests/requirements-build.txt`, exit 0, `setuptools-84.0.0` in the build env
- mutant red: the same command against a scratch copy with both setuptools digests altered, exit 1 (quoted under `## Mutation proof`)
- not taken: 84.2.1, which the header's recipe yields without `--upgrade-package` today. 84.1.0 is the alert's first patched version, the roster brief's target and Dependabot's bytes; a later version is Dependabot's next weekly proposal, not this alert's fix
- gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: FULL`, `reason: tests/requirements-build.txt changes the gate itself, so every closure is suspect`; CI runs every script, and nothing below claims the full suite locally
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`
- `python3 tests/closure.py selftest` -> `ALL 117 closure shrink pins PASSED`
- `python3 tests/layout.py` -> `layout self-test: ok`
- `python3 tests/harness_headers.py` (with its docstring's `PYTHONPATH=tests/hastub:custom_components:tests`) -> `ALL 112 HARNESS HEADER CHECKS PASSED`
- `python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)` -> `claims hygiene: aaf8af512c1fb9aeabdf58dbb5131928f432d4d1 ok`; no golden and no claim file is touched

## Unpinned sites

none: the diff adds no code.

## Red checks

none at this head before CI. `tests / nightly-status` and `governance / delivery-status` grade `main`, and this diff touches nothing they read.

## Forward-carry

none.

## Friction

- `roster-brief: stale`: the brief says land Dependabot #2678 and forbids adding commits to its head, but #2678 closed on 2026-10-27, before dispatch, and Dependabot refuses to rebase or recreate it; the brief's own target and bytes are delivered here as an `hpo-author` PR instead. After the merge, re-read the open alerts and confirm GHSA-xmj3-9gf7-h52w closed; if it does not, that is #2722's stale dependency graph, not this pin (`R10-FLY-DEPGRAPH-STALE` is `done`, so the post-merge read stays with this group). Carry: R10-DEPENDABOT-SETUPTOOLS
