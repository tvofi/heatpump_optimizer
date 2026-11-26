Fix review: merge 9003a6896342a0729a595648ca218b1d976fe925

bus-nonce: 48b413726d56e0bf21368f1b6a34cabf

## Round

First round, full scope (packet: no verdict names the reviewed head). Reviewed the three-dot diff against merge base 97026ed8cf085f318849107d2207577804043287: `.github/workflows/pages.yml` (1 line + 2 comment lines), `tests/entities.py` (+26), `dev/programme/delivery/3900.md` (+1). No `custom_components/` change.

## Evidence

- RESULT: same first line. The replaced `| head -n 1 | sed 's#.*refs/tags/##'` and the new `| awk 'NR == 1 { sub(/.*refs\/tags\//, ""); print }'` give identical output on the live `git ls-remote --tags --refs --sort=-v:refname origin 'refs/tags/v*'` listing (180 lines, both `v10.1.4`) and on edge inputs: empty listing (both empty, so the step's `-z "$tag"` warning branch still fires), one line, two lines, a doubled `refs/tags/refs/tags/` (both greedy, both `v9`), an rc suffix, a line without `refs/tags/`. A failing `git ls-remote` still fails the step under pipefail, as before. ev/equivalence.txt.
- RESULT: SIGPIPE reproduced and removed. A 20000-tag generator under `bash -e` + pipefail: old form exits 141, new form exits 0 with `v20000.0.0`. ev/equivalence.txt.
- RESULT: no other pipefail-plus-early-exit pipe remains in pages.yml. Every `|` in a run block was listed (ev/pages-pipes.txt): the only other pipe is `Stage the site`'s `git ls-files -z ... | while IFS= read -r -d '' f`, whose reader consumes all input (`continue` only, no `break`/`exit`); lines 99/101 are `||`. No `head`, `grep -q`, `grep -m`, `sed q` or awk `exit` remains.
- RESULT: mutation proof re-run. Restoring the old form in `pages.yml` at the head (ev/mutant.diff) turns the new check red: `FAIL pages.yml: the release step's tag pipeline reads its listing to the end under pipefail (run 45663211757)  [got=(141, '') plant=(141, '')]` (ev/entities-mutant.log line 2064). At the head the same check prints `ok` (ev/entities-head.log line 2064). Both runs: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 tests/entities.py`, stopped by my timeout after the check line; the full script's verdict is CI's `tests / fast (3.14)`.
- RESULT: the check's own plant is built by an exact, count-1 `replace`, and the assertion requires `_PAGES_TAG_PLANT != _PAGES_TEXT`, so a future re-spelling of the line fails the check instead of silently passing it. The stand-in runs under `_GHA_RUN` (`bash -e -c`, tests/entities.py:21344), the shell GitHub runs a step under.
- RESULT: `git merge-tree --write-tree origin/main 9003a689...` exits 0 (ev/merge-tree.txt). Role-file drift against main: none (`git diff <merge-base>...origin/main -- dev/governance/roles/` is empty).
- RESULT: VERSION, the manifest version, RELEASE_NOTES.md and both claim files are untouched (diff covers 3 files, none of them).
- Owed red: `tests / fast (3.14)` at 455e9b09 (run 45719342344) is in the `owed-reds` set (ev/owed-reds.txt) and is answered in the body's `## Red checks`, with countermeasure B named and the repair at f8decf8b.
- Finder's harness: none named; the defect is the CI run 45663211757 exit 141, re-derived above with a stand-in listing. A one-seam class: the claim covers pages.yml's pipes, and the enumeration above (every pipe in the file) returns only this seam.
- Figures: the body quotes none; 20000 and `v20000.0.0` are re-derived above.
- CI: `merge_train.py classify 9003a6896342a0729a595648ca218b1d976fe925 --pr 3900` exit 0: `GREEN 9003a6896342a0729a595648ca218b1d976fe925 pending: none red: none` (01:35:31 UTC; every poll in ev/classify.log).

## Findings

- Note: body-stale: the body's `## Head` says "The change is two files", but the diff carries three: `dev/programme/delivery/3900.md` as well (the delivery row). Paperwork, does not block. Carry: dismissed: paperwork in the body, no later stage changes

## Friction

none
