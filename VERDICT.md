Fix review: merge dba7f86b1da529a59bc9b15b6f3641bcfc2c8891

bus-nonce: 016a7230ddedbace841a48354f35d2f4

## Round

Round 1 (no earlier verdict on #2714). Measured head dba7f86b1da529a59bc9b15b6f3641bcfc2c8891 (authored code head aa5b7e069; the head commit adds only dev/programme/delivery/2714.md). Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` empty.

## Findings

- Surviving mutant: deleting the lost-race retry clause `or ("failed to push" in out and "lint gate: TOTAL: 0" in out)` leaves the self-test at 14 checks, 0 failed. The documented "push lost a race with a clean lint" retry is unpinned; the stub editor only emits the moved-main message. Carry: dismissed: seat-side instrument, the body claims no proof for this clause; pinning it is one stub mode, worth taking if the file is touched again.
- Surviving mutant: removing `git worktree remove --force` between attempts leaves 14 checks, 0 failed. Without it roster_edit's prepare_worktree would refuse the retry ("HEAD ... is on no origin ref") after a lint-gate refusal left a local commit, so the retry the docstring promises would become a refusal. Carry: dismissed: the stub editor never builds a worktree, so only a real-roster_edit integration fixture could pin it; out of proportion for a seat tool whose failure mode is a reported refusal, not a wrong write.
- Success is recognised only by `pushed handoff\S* at <sha>`; with `--branch` naming a branch not under `handoff` (an option this runner exposes), a successful push from roster_edit ("pushed <branch> at <sha>") is reported `refused rc=0` and an append-carry read-back is skipped. Traced from code, not run. The default branch (roster_lib.round_branch, `handoff/audit-r<N>-roster`) matches. Carry: dismissed: no caller passes a non-handoff branch today; a misreport is visible as rc=0 and never writes.
- `run_queue` returns 0 even when ops are refused, so a caller keying on the exit code sees success. The docstring says refusals are reported in the report file, which is where the seat reads. Carry: dismissed: documented contract, the report line is the signal.

## Evidence

- Mutation proof, re-run at the head with `python3 -I tools/audit/seat/roster_queue.py --self-test`: `attempt < 0` -> 2 failed ("moved main retried", "pushed + readback"); `hit = [0]` -> 3 failed, including the null control "absent text is no match"; dropping `extra` from the editor command -> 1 failed ("drop-carry --match reaches the editor as a flag"); reverting the parser to a bare positional -> 1 failed ("parse: drop-carry --match keeps the flag"). All four match the body exactly.
- Extra mutants of my own: dropping the MOVED condition -> 2 failed; alive touch removed -> 1 failed; line-number strip removed -> 4 failed.
- Null control: unmodified tree, `roster_queue self-test: 14 checks, 0 failed`; counted by hand 4 parse + 3 readback + 7 run = 14.
- Figures in the body re-derived at the head: selftest_wiring 94 self-testing, 94 wired, 0 unwired; throwaway_git 0 raw git init or clone sites refused; STRUCTURE RATCHET PASSED. See ev/figures.txt.
- Not re-derived: `tests/entities.py` cannot run here (no homeassistant module; also `layout` under -I), same as the fixer's host; the INERT classification is checked by eye only (one line added to the INERT READS list in tests/closures.json, alphabetical).
- VERSION, manifest version and RELEASE_NOTES.md heading untouched (three-dot diff empty). No golden or claim file moved, so step 4 is vacuous. No budget file touched.
- Merge: `git merge-tree --write-tree origin/main dba7f86b1da529a59bc9b15b6f3641bcfc2c8891` exit 0, no conflicting path.
- CI on the head (check-runs API): no check concluded red. prelude and refresh succeeded; hassfest, tests, governance, codeql, validate and kernel-points concluded skipped (the PR is a draft), so the new governance.yml self-test step has not run in CI at this head; arch-score, budget-raise-gate and cancel-superseded were still queued or in progress when read. No pr-contract run was listed. Red checks: none, which matches the body's "none".
- Harness: the finding is the roster seat's own queue runner, moved into the tree per decision 0013; the self-test is the fixer's, and it is the only harness that exists. I built none beyond mutants planted in that file.
- Class: one seam (one tool moved into the tree); the body names no enumeration rule and its issue states one seam.
- Forward-carry: body says n/a; nothing in the diff changes a later stage.
- Head re-read before return: origin/fix/r10-roster-runq is dba7f86b1da529a59bc9b15b6f3641bcfc2c8891.
