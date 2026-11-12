Fix review: blocked 7d55d16d97926797c5cdaf33eea2b6a981ee75b2 residue-leak: the shell twin leaves one temp file per sourcing process and truncates any file an inherited _HPO_EMPTY_GITCONFIG names; its truncation and the python cleanup are untested (M4, M5 survive)

bus-nonce: 300c4cd9b6ec2c2c49542b3a4e84bc53

## Block

- `tests/throwaway_git.sh:30-34`: `throwaway_git_env` makes a `mktemp` file and never removes it. There is no trap, and `_HPO_EMPTY_GITCONFIG` is not exported, so every process that sources the twin leaves a 0-byte `hpo-empty-gitconfig-*` in `$TMPDIR`. Running the self-test, `--check`, `stop-selfcheck.sh --self-test` and `tmp_paths.py --check` once against a fresh TMPDIR left 3 files. 32 non-record files source the twin. The dispatch asked for a temp file that cannot outlive the run, and on the shell side it does outlive it. That is new residue on a topic named suite-env-residue.
- Same lines: the twin reuses whatever `_HPO_EMPTY_GITCONFIG` it inherits whenever that names a regular file, and then runs `: >"$g"` on it. Setting it to a populated gitconfig emptied that file (size 0 afterwards, ev/runs.txt). Nothing in the tree sets the name, but a hostile-environment helper should not truncate a path that comes from outside.
- Untested lines: M4 (the shell truncation removed) and M5 (the python `atexit` unlink removed) both leave the self-test at 45/0. One possible cut that fixes all three: point both sides at the file the mkstemp returns only after checking it is the one this process made, and remove it in the shell too, or use a tracked empty file classified INERT so that no temp file exists at all. Either way, add checks that kill M4 and M5.

## Findings

- Follow-up: neither side's self-test runs git with a non-empty `/dev/null`. M1 and M2 die only on the twin comparison's `isfile` assertion, not on a failed `git init`. The bind-mount reproduction in ev/repro_bindmount.sh (`unshare -m`, root) shows the real failure at the base and its absence at the head, and could become the both-ends check where the seat is root. Carry: R10-SUITE-ENV-RESIDUE

## Evidence

- Head reviewed: 7d55d16d97926797c5cdaf33eea2b6a981ee75b2 (ev/HEAD.txt). It matches BODY.md's `## Head` and the handoff tip. Merge base 8c10361eb1fe. `git merge-tree --write-tree origin/main` exits 0, so it merges cleanly.
- No pull request exists yet, so there is no review packet and no CI run to read. `## Red checks` none is not contradicted.
- Reproduction: in this container `/dev/null` is the normal empty char device, and `GIT_CONFIG_GLOBAL=/dev/null git init` exits 0. That matches the body and contradicts the dispatch's premise that this image fails. Bind-mounting a file that holds bytes over `/dev/null` reproduces `fatal: bad config line 1 in file /dev/null`, exit 128, for both the py and the sh helper at the base. At the head both exit 0 (ev/runs.txt).
- Host-config leak: none. `GIT_CONFIG_GLOBAL` names a 0600 mkstemp file that is emptied on each call, and `GIT_CONFIG_NOSYSTEM=1` is set, so git reads neither `~/.gitconfig`, XDG nor system config. The only exception is the inherited-variable case under Block.
- Callers: 32 shell sources and every python importer reach the change through `throwaway_git_env`/`throwaway_git_init`. `git grep GIT_CONFIG_GLOBAL` at the head finds no other site outside the two helpers. The one hit is prose in dev/audit/rca/R9-RCA-stamp-race.md:51. The class is closed at two seams, both in the diff.
- Body figures re-derived at the head: self-test 45 checks, 0 failed; `--check` 0 refused; stop-selfcheck 29 passed, 0 failed; tmp_paths 0 refused. I did not re-run `prepr.sh` (PREPR_SKIP_CLOSURES), so its exit 0 is not verified.
- Mutation: the body's mutant (truncation dropped) is killed, and so are M1 to M3. M4 and M5 survive (ev/runs.txt).
- VERSION, the manifest and the release notes are untouched: the diff is tests/throwaway_git.py and tests/throwaway_git.sh only. No claim-file change, and no fixture can move.
