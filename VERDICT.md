Fix review: blocked 3580acc051e8b7f8ad5fba1ce8827891111f6ba9 mutation-vacuous: check's python3-is-venv-ci predicate removed, --self-test 8 checks 0 failed

bus-nonce: 68ee7f105bcd4b226f6957d2b225de4f

Round: first review of #2709. Head measured: 3580acc051e8b7f8ad5fba1ce8827891111f6ba9 (code head eec03e0ee, merge of origin/main 2cdf7adca at e64d99786, plus the delivery row). Role file current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` empty.

## Block

- Mutant M9 deletes `[ "$py" = "$1/venv-ci/bin/python3" ] && ` from `check()` in `tools/audit/seat/cloud-setup.sh`, leaving only the `-x "$HPO_TYPING_PYTHON"` half. `bash <M9> --self-test` prints `cloud_setup self-test: 8 checks, 0 failed` (ev/mutants.txt). This predicate is the one the body says `--check` measures ("OK when `python3` is venv-ci's") and the one the Forward-carry asks `cloud_dispatch.py` to rely on. Under M9, `env -i PATH=/usr/local/bin:/usr/bin:/bin HPO_TYPING_PYTHON=/opt/hpo/venv-ha/bin/python bash <M9> --check` answers `cloud-setup check: OK python3 is /usr/local/bin/python3`, rc 0. That is the defect state (system python3) read as OK. The head answers `REFUSE`, rc 1 (ev/m9_demo.txt). Why no arm kills it: every refusing arm leaves `HPO_TYPING_PYTHON` unset. No arm sets an executable `HPO_TYPING_PYTHON` with a non-venv `python3`. The body's table lists M2 (whole condition) and M3 (the `-x` half) but not this half, and `## Unpinned sites` does not disposition it. Repair: add an arm where `HPO_TYPING_PYTHON` is executable and `python3` is the system stub, expecting rc 1 and `REFUSE`. Then show M9 red.

## Findings

- Mutant M12: `--check) check "$PREFIX"; exit 0 ;;` (the dispatch's exit code) survives the self-test with 8 checks, 0 failed. Every arm calls the `check` function through `declare -f` and never calls `cloud-setup.sh --check`. So the body's "exit 0 or 1" for the mode a seat runs is not pinned. Under this mutant, a seat that stops on a non-zero exit would carry on. Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN
- Mutants M7 and M10 each replace one export of the written profile with `:` (`OPENBLAS_CORETYPE`, `HPO_TYPING_PYTHON`), and both survive at 8 checks, 0 failed. Only the profile's PATH line is pinned. `## Unpinned sites` names only the `write_profile` call site, not these lines. They need an arm or a written triage. Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN
- `OPENBLAS_CORETYPE` appears in `--variables` and in the refusal text. No self-test pattern includes it, and `check` does not test it. A seat missing it (BLAS core-type pinning for golden floats) gets `OK`. This needs a disposition: pin it, or state why `--check` ignores it. Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN

## Evidence

- The body's mutants M1 to M6 re-run at the head. Each fails exactly the arms the body's table names (ev/mutants.txt). The baseline gives `8 checks, 0 failed` on 4 runs in this seat (ev/selftest.txt).
- Harness `dev/audit/harnesses/r10_cloud_setup_toolchain.py` (sha1 b377aeae…, the fixer's rebuild of the finder's control, disclosed as such under fixer.md step 18). Base copy 145bfe197 (sha1 de099837…): `bare`/`remedy` `/usr/local/bin/python3 numpy-missing`, `remedy-nul` `numpy-ok`, `variables` `n/a`, `nested` `/opt/hpo/venv-ci/bin/python3`, verdict `no`. Head (sha1 40fdfa19…): `variables` `/opt/hpo/venv-ci/bin/python3 numpy-ok`, `nested` `<tmp>/stub/python3`, verdict `yes`. Every figure matches the body (ev/harness.txt). The harness reads M9 as `yes` too, so it does not separate the M9 defect either.
- `--check` in this seat: `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`, rc 0.
- The merge base the body quotes (145bfe197) differs from the current merge base (2cdf7adca). `cloud-setup.sh` has the same blob at both (sha1 de099837…).
- `git merge-tree --write-tree origin/main 3580acc051e8b7f8ad5fba1ce8827891111f6ba9` (origin/main e97f5749b): rc 0, no conflict (ev/merge-tree.txt).
- `VERSION`, `RELEASE_NOTES.md`, the manifest, `tests/structure_budgets.json` and `tests/golden`: untouched in the three-dot diff. The class rule's `git grep` was not re-run.
- CI at this head (check-runs API): 6 runs, of which only one `refresh` has concluded (success). `prelude` and `cancel-superseded` are queued. No gate has concluded, so step 11 (red-check answers) cannot be judged at this head. I did not judge it, and I did not read the earlier heads' runs.
- I did not re-run the gate or the mutation table (step 11: cite CI's heavy runs).
