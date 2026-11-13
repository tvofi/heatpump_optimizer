Fix review: merge f172a9ce91e18cbb4cfa2af5b2bbd3706d06a88b

bus-nonce: 93da9103f017de7ead7908ace630eedd
pending-ci: gate

Round 2, a delta review over the reviewed head 740e6074cf5bace0302c7f2896b72149c918f010 (packet `## Review scope: delta`). Measured head f172a9ce91e18cbb4cfa2af5b2bbd3706d06a88b. It matches the PR body's `## Head` line and is a merge of 740e6074 with the authored head 7d09eae1ba3ab2ab5a7ed2b84a087d6c5d6ef128.

## Evidence

- Delta: `git diff 740e6074cf5bace0302c7f2896b72149c918f010 f172a9ce91e18cbb4cfa2af5b2bbd3706d06a88b` touches only `tools/audit/seat/cloud_relay.sh` (12 insertions, all inside `--self-test`). It changes no production text and adds no predicate, so it has no new predicate to mutate. As an instrument and test delta, it does not widen the scope (step 12). `git diff 7d09eae1 f172a9ce` is empty, so the merge resolution is trivial.
- Round-1 block resolved. I took the four surviving mutants from round-1 ev/mutants.json (probe/rev-3541-7c9edde1, commit 74136516fa7cc14c4f31b2cb8dba595ea51fdfbd) unchanged into ev/mut-r2.json. Each anchor matches exactly once at this head. I ran `python3 tools/audit/seat/mutant_run.py --spec ev/mut-r2.json --cmd 'bash tools/audit/seat/cloud_relay.sh --self-test' --copy-tree` from a detached worktree at this head (ev/mutant_run.r2.log, rc 0):
  - SURVIVED NULL
  - KILLED redsecs-validate-off
  - KILLED nr-rev-window-off
  - KILLED nr-rev-revt-off
  - KILLED nr-rev-lsremote-fail-continue
- This matches the body's `## Review block answered` (four SURVIVED -> KILLED, NULL SURVIVED). Each new arm carries a null control in the same pass: the numeric bound at GREEN posts, and the in-window unreturned #3339 fires.
- RESULT: `bash tools/audit/seat/cloud_relay.sh --self-test` at the head printed `cloud_relay self-test: 488 checks, 0 failed` (ev/selftest-head.log). That re-derives the body's head figure (482 -> 488, 6 checks for the four arms). The merge-base figure of 452 was re-derived in round 1 and is unchanged by this delta.
- RESULT: `python3 tests/structure.py` at the head printed `STRUCTURE RATCHET PASSED` (ev/structure.log). The delta touches no budget file.
- Carried from round 1 unchanged, because the production text is identical to 740e6074: the 16 kills, the spec conformance to Carries 7, 21, 23 and 30, and the PROMPT.md n8 parse.
- Merge with main: `git merge-tree --write-tree origin/main f172a9ce91e18cbb4cfa2af5b2bbd3706d06a88b` exited 0 with empty stderr (ev/merge-tree.out, ev/merge-tree.err), so there is no conflict.
- CI: `python3 tools/audit/seat/merge_train.py classify f172a9ce91e18cbb4cfa2af5b2bbd3706d06a88b --pr 3541` read `WAIT ... pending: gate red: none` (exit 3) at the last poll, 09:40:56Z (ev/classify.txt, ev/classify-poll.log). The dispatch said not to wait on CI, so this verdict carries `pending-ci: gate`. The packet's `introduced-red` refusal was `governance / instrument-self-tests` still in progress at render. Its `gate` failure read while lanes ran, and classify (which decides) reads no red.
- Red checks: classify reports none at this head. The body's `## Red checks: none` stands pending the relay's GREEN read.
- tests/entities.py did not run here, as in round 1: `env -u BASH_ENV python3 tests/entities.py` raised ModuleNotFoundError for homeassistant (ev/entities.log). The delta adds no tracked file, so the check has nothing to classify.
- No finder's harness is named. This is instrument work built from roster carries (round 1's evidence applies).
