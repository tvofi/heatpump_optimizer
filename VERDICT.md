Fix review: merge c3fa2b58fda798284ee4ae335989bb3cb5ab9616

bus-nonce: 8c8e6407303cb41aec61c94b02f449fd

## Findings

none

## Evidence

- Round: second review, at the handoff. Scope is the delta 7d55d16d97..c3fa2b58fd (tests/throwaway_git.py, tests/throwaway_git.sh only) plus the prior verdict's findings. `review_carry.py 7d55d16d c3fa2b58` prints FRESH-REVIEW, so this is a delta review. No production (custom_components/) line is in the delta, so the scope does not widen.
- Head: c3fa2b58fda798284ee4ae335989bb3cb5ab9616 (ev/HEAD.txt). It matches BODY.md's `## Head` and the tip of handoff/r10-suite-env-residue-p2, re-read by ls-remote just before writing this verdict. `git merge-tree --write-tree origin/main HEAD` exits 0, so the head merges cleanly.
- No pull request exists yet, so there is no review packet and no CI run to read. `merge_train.py owed-reds` prints tests / mutation, tests / typing and validate / validate-hacs, and none of them has run on this head. `## Red checks` none is not contradicted.
- Prior block, now resolved:
  - (1) Shell residue: the mktemp, the trap-less file and the `_HPO_EMPTY_GITCONFIG` reuse are gone. A fresh TMPDIR run of the self-test, `--check`, `stop-selfcheck.sh --self-test` and `tmp_paths.py --check` leaves 0 files (ev/figures.txt).
  - (2) Truncation of an inherited path: nothing reads a path from the environment or writes one. The self-test's "never written" check pins this, and the R1/N5 inherit mutants die.
  - (3) M4 and M5: their sites no longer exist. The same class, re-planted as R2 (sh `$(mktemp)`) and R3 (py mkstemp), is killed with 2 and 3 failed (ev/mutants.txt). I did not re-derive the body's claim that M4 and M5 die on 7d55d16d plus the new tests.
- Leak class: with the ENOTDIR path, neither side creates a temp file, so no residue can come from either helper, including under SIGKILL. `git grep` at the head for `GIT_CONFIG_GLOBAL`, `empty_global_config` and `_HPO_EMPTY_GITCONFIG` outside the two helpers finds only prose in dev/audit/rca/R9-RCA-stamp-race.md:51, so the removed symbol has no remaining importer. The one `git config --global` site, dev/audit/harnesses/hpo_ci_container_setup.sh:28, does not use the throwaway env. The class is closed at its two seams, both in the diff.
- ENOTDIR semantics, measured on git 2.43.0 under `unshare -m` with a 10-byte file bind-mounted over /dev/null (ev/repro_bindmount.txt).
  - At the base 8c10361eb1, the py init fails (128), and the sh env + `git init` exits 128 with `bad config line 1 in file /dev/null`. `git config --global --get` and `git commit` also exit 128.
  - At the head, py init 0, sh env + init 0, `config --list` 0, `config --global --get` 1 (key absent, not an error) and `commit` 0. Residue is 0.
  - Separately, the base's shell `throwaway_git_init` (not the env + `git init` form) exits 0 under the bind mount. The body's sh 128 figure uses the env + `git init` form, which reproduces.
- Prior Follow-up (the self-test has no non-empty-/dev/null arm): the body dismisses it, on the grounds that the junk-file null control plus the ENOTDIR create probe pin it seat-independently. I accept that. The bind mount was re-run here at both ends, as recorded above.
- Mutation at the head (ev/mutants.txt): N1, N2, N3 and N5 from the body are killed, 1 failed each. My extra R1 (py inherit) is killed with 1 failed. N4 and N6 were not re-run. After every mutant the tree is clean and no `tests/no-global-config` file was left.
- Body figures re-derived at the head:
  - self-test: 49 checks, 0 failed.
  - `--check`: 0 refused.
  - stop-selfcheck: 29 passed, 0 failed.
  - tmp_paths: 0 refused.
  - STRUCTURE RATCHET PASSED.
  - `closure.py select --diff 8c10361eb1fe`: MODE: SCOPED -- 4 script(s) run (arch_score, doc_claims, entities, layout).
  - layout exit 0; doc_claims: ALL 343 checks PASSED. The body says "all checks passed" and quotes no count.
- Figures not verified: arch_score (280 checks) did not finish inside my 200 s bound, and entities (2709 checks) and `prepr.sh` rc=0 were not re-run. These are heavy runs that CI will carry once the PR opens.
- VERSION, the manifest and the release notes are untouched, and no claim file changed. The diff against the merge base is the two test files only, so no fixture can move and no budget moved.
