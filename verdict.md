Fix review: merge d4ab722b919b0b07917122bfe0479247bf3b989a

bus-nonce: 131f9c75894cd6cae3b827dfe76bca93

Round 1. Measured head d4ab722b9 (re-read at post time: still the PR head d4ab722b919b0b07917122bfe0479247bf3b989a). Merge base with origin/main 0cc148b2f; origin/main is now 6961f0663.

Contract copy: `git diff merge-base...origin/main -- dev/governance/roles/` empty (current).

RESULT three-dot diff: 3 files only (tests/requirements-ci.txt, tests/requirements-typing.txt, dev/programme/delivery/2544.md); VERSION, manifest, RELEASE_NOTES untouched. Exactly 5 version lines move (ev/versionlines.txt): aiohttp 3.14.4->3.14.5 in both locks, certifi 2026.7.22->2026.10.19, pillow 12.3.0->13.0.0, uv 0.12.5->0.13.4 (typing). Per-block comparison (ev/blocks.txt): CI lock 14 blocks, only aiohttp changed; typing lock 112 blocks, none added/removed, only aiohttp/certifi/pillow/uv changed. Header text change matches the body (uv/pillow added to override set, drop conditions).
RESULT PyPI hashes (my own script, ev/hashes.txt, hash set == PyPI release file digests): CI aiohttp 3.14.5 161/161 True; typing aiohttp 161/161 True, pillow 13.0.0 83/83 True, certifi 2026.10.19 2/2 True, uv 0.13.4 19/19 True.
RESULT mutation (ev/mut.txt, pip download --require-hashes on the CI lock's aiohttp block, py3.13): unmutated rc=0 (aiohttp-3.14.5 saved, null control); version reverted to 3.14.4 with 3.14.5 hashes rc=1 "THESE PACKAGES DO NOT MATCH THE HASHES"; every digest first-nibble altered rc=1 same error.
RESULT CI lock full install: python3.13 venv, pip install --require-hashes --build-constraint tests/requirements-build.txt -r tests/requirements-ci.txt rc=0, aiohttp 3.14.5.
RESULT typing lock FULL install (what the fixer could not do): python 3.14.6 venv (uv-provided), pip install --require-hashes --no-deps --build-constraint tests/requirements-build.txt -r tests/requirements-typing.txt rc=0 (ev/typing-install.log); installed aiohttp 3.14.5, certifi 2026.10.19, pillow 13.0.0, uv 0.13.4, PyRIC built from sdist under the build constraints.
RESULT merge: `git merge-tree --write-tree origin/main d4ab722b9` exit 0, no conflict, no claim-file involvement.
RESULT typing_ruler.py: ALL 11 typing-ruler source checks PASSED, including the hashed-lock-installs-the-recorded-pins check. NOTE: the body says "ALL 12"; both this head and origin/main print 11, so the body's 12 is a misquote (not load-bearing, nothing moved it).
RESULT CI on this head (check-runs API, ev/checkruns*.txt): every completed run success or skipped except nightly-status=failure. At my last read fast (3.14), browser, coverage, instrument-self-tests were still in progress; env-matrix and typing had concluded without red. pr-contract (both runs), closure-scope, mutation, arch-score, budget-raise-gate, hassfest, policy-docs all success. Heavy lanes cited, not re-run.
RESULT step 11 (red checks): the only red is nightly-status, which grades main; this diff touches nothing it reads (lock files and one delivery row), and the body names it with the separate r10-replay-cap fix. Not this PR's. No other red check, so no root-cause-unanswered. The body's account of #2534's reds (typing hash mismatch, pr-contract author) is answered there.
RESULT steps 14/15: no budget, closure, golden, claim, ledger or score file moves; nothing for metric-gamed. Pure lock content; no added code lines, so architecture-unsound does not apply. Forward-carry "none" is consistent (no finding changes a later stage).
RESULT PyPI vulnerability metadata (ev/pypi-vulns.txt): new pins aiohttp 3.14.5, pillow 13.0.0, certifi 2026.10.19, uv 0.13.4 list 0 vulnerabilities; the old pillow 12.3.0 (8), uv 0.12.5 (2), certifi 2026.7.22 (2) list advisories. Consistent with the body's claim that those alerts are fixed.

NOT VERIFIED: the body's alert table against `dependabot/alerts?state=open`. This seat's token gets HTTP 403 "Resource not accessible by integration" on that endpoint, so I could not re-derive the 27-alert list or each first-patched version. I substituted only the PyPI vulnerability metadata above, which is my own proxy and not the alert API. The orchestrator's machine can confirm the table with the body's command; nothing else in the verdict depends on it.

Round-trip caveat: in-progress CI lanes (fast 3.14, browser, coverage, instrument-self-tests) had not concluded at my read; a red among them after this verdict would be new information outside it.
