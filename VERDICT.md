Fix review: merge d4ab722b919b0b07917122bfe0479247bf3b989a

Round 1 (there are no earlier verdicts, reviews or comments on #2544). Measured at head `d4ab722b919b0b07917122bfe0479247bf3b989a`, detached worktree. The head is unchanged at 10:42Z. Merge base `0cc148b2f`. `dev/governance/roles/` matches origin/main.

**Group.** R10-PIP-BUMP is not on `handoff/audit-r10-roster`. The PR's delivery row names R10-DEPENDABOT-AIOHTTP (#2504). That group's brief supplies the finder's controls, and I ran those, not the fixer's.

RESULT finder-install head rc=0 aiohttp=3.14.5   (python3.13 venv, `pip install --require-hashes --build-constraint tests/requirements-build.txt -r tests/requirements-ci.txt`)
RESULT finder-install base rc=0 aiohttp=3.14.4   (the merge base's own lock and build constraints)
RESULT finder-install planted-wrong-aiohttp-hashes rc=1 THESE PACKAGES DO NOT MATCH THE HASHES   (all 161 aiohttp digests altered in the full CI lock; null control: the hash list is read)
RESULT mutation pillow-typing fixed rc=0 / mut1 (version reverted to 12.3.0, 13.0.0 hashes kept) rc=1 / mut2 (every digest altered) rc=1   (`pip download --require-hashes --no-deps`, cp314 manylinux_2_28)
RESULT pypi-hashes: every bumped block's hash set equals PyPI's file digests: CI aiohttp 3.14.5 161/161, typing aiohttp 161/161, certifi 2/2, pillow 83/83, uv 19/19, all True
RESULT diff: CI lock 14 pins and typing lock 112 pins, with none added or removed. Exactly five version lines move: CI aiohttp, typing aiohttp, certifi, pillow and uv. No other block changes in either version or hashes. Pillow goes from 87 to 83 hashes, matching PyPI.
RESULT class: no other tracked requirements, lock, pyproject or manifest file pins aiohttp, pillow, certifi or uv. The class is these two locks, and both are in the diff.
RESULT merge-tree origin/main (43f79c08b, newest at posting) rc=0. It also merges cleanly with 6961f0663.
RESULT VERSION, manifest and RELEASE_NOTES are untouched. No golden, claim, budget or closures file changed.
RESULT cheap checks at head: STRUCTURE RATCHET PASSED; layout self-test ok; claims hygiene ok; ALL 124 closure shrink pins PASSED; closure select gives MODE: FULL (requirements-ci.txt changes the gate itself); typing_ruler: ALL 11 source checks PASSED, including "the typing job's hashed lock installs the recorded pins".

**CI on this head** (from the check-runs API, every run: ev/check_runs.tsv). Every gate check is green. That includes typing (the lane #2534 failed on hashes), fast (3.14), coverage, closures, mutation, env-matrix, pr-contract (twice) and budget-raise-gate. `composed-proof` is still queued, but it is not a required context and does not block the PR (tests.yml:2775).
`nightly-status` is red, and that belongs to main, not this PR. The job reports the last scheduled run of tests.yml (the scheduled runs of 10-19 and 10-20 failed). It runs the base's pinned stdlib-only script with no pip install, so this diff cannot reach what it reads. The body names it and answers it, so step 11 is satisfied.

**Figures I could not re-derive** (step 8):
- The 27 open Dependabot alerts and their first-patched versions: the alerts API returns 403 to this seat. They are not verified.
- "ALL 12 typing-ruler checks": I get 11 here. The twelfth is the mypy census, which runs only with HPO_TYPING_PYTHON set. CI's green `typing` job is that check, so I cite it rather than confirming 12 locally.
- The "112 of 112 blocks" download sweep and the 3.13.15/3.14.7 byte-identical compile: I did not re-run them. CI's typing install and my PyPI digest comparison cover the same property.
- `tests/entities.py` needs homeassistant installed, so I did not run it here. CI `fast` ran it in FULL mode and it is green.

**Steps not applicable.** Step 2 (a baseline-to-head harness metric): the finder's install control is the measure, and it is run at both ends above. Step 4: there is no fixture drift and no claim files were touched. Step 10: the body says forward-carry none, and I found no later-stage finding. Step 14: no instrument number moves. Step 15: the added lines are lock data plus a header comment recording the uv/pillow overrides and when to drop them, which is sound.

**Notes for the orchestrator.**
- The roster's R10-DEPENDABOT-AIOHTTP still shows a resume at `fix/r10-dependabot-aiohttp`. This PR supersedes the brief's 3.14.4 target with 3.14.5.
- The brief asks for a post-merge check that the GHSA alerts closed, which still has to be done.
- The body's step-7 head chain (code head a758413a, merged with main 0cc148b2f as 1b87eb40, plus a delivery row as d4ab722b) matches `git log`.

bus-nonce: 9bb2f26885d4acc59d4a6edd5dcf6555
