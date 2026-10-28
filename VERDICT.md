Fix review: merge 14388f6f09e33dc98a315da7ff8d33ef905a31ff

bus-nonce: c38c9974a189b460d633cca6a15ee506
round: 1 (first review at this head; fresh dispatch)
measured-head: 14388f6f09e33dc98a315da7ff8d33ef905a31ff (re-read at post: unchanged)
base: aaf8af512c1fb9aeabdf58dbb5131928f432d4d1

RESULT diff-vs-dependabot-6ee3e4d4f tests/requirements-build.txt: 0 lines (6ee3e4d4f is authored by dependabot[bot])
RESULT three-dot diff: tests/requirements-build.txt (3 out, 3 in) + dev/programme/delivery/2905.md (row); VERSION/manifest/notes untouched
RESULT pypi 84.1.0 sha256: whl 5231689c6ac8156cd155cfb98c3fd6fb252c3e7e9bd3d78b64d3c55f132624c9, sdist 23657205b63d4d31395ab917815247f694aafad28cd21316bf5fd45a51048ea0 == both --hash lines in the file
RESULT install arm=head  rc=0 build-env setuptools-84.1.0 (pip 26.2.1, py3.14.7, pip wheel --require-hashes --no-binary pyyaml --build-constraint)
RESULT install arm=main  rc=0 build-env setuptools-84.0.0 (null control)
RESULT install arm=mut2 (both digests 000../111..) rc=1 "DO NOT MATCH THE HASHES", Got 5231689c... -- mutant killed
RESULT install arm=mut1 (wheel digest only) rc=0 -- one-hash plant vacuous, as the body states (sdist fallback)
RESULT closure select: MODE: FULL, reason "tests/requirements-build.txt changes the gate itself" -- justified; CI ran full, gate success
RESULT open alerts: 1 (145 GHSA-xmj3-9gf7-h52w setuptools tests/requirements-build.txt, patched 84.1.0); git grep setuptools== finds only this file -- class is one seam
RESULT closingIssuesReferences: [] ; body says Refs #2722 (depgraph-stale issue, OPEN) -- correct not to close it
RESULT merge-tree vs origin/main: rc 0
RESULT live check-runs at head: 55, 0 failed, 0 pending

Notes: harness is the body's install command (no finder's harness exists for a Dependabot bump; I ran it myself in my own venv, arms logged in evidence). Mutation proof re-run: removing the correct digests turns the build red; null and head arms green. Post-merge alert re-read is owed by R10-DEPENDABOT-SETUPTOOLS, as the body's Friction says.
