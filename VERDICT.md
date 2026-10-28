Fix review: merge e42df200774f19af6805f6a7fa2912a9318af328

bus-nonce: 5a81007884ec4c77699b2de891f56127

## Round

Round 1. Reviewed at head e42df200774f19af6805f6a7fa2912a9318af328 (PR head re-read just before writing: unchanged). Merge base beb570c81. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Findings

- The body's figure "`merge_train.py` 113" GitHub call sites "by `grep -c`" does not re-derive. The body names no pattern. Neither the plausible patterns nor the file's wrapper calls give 113: `\bgh\b` gives 132, `"gh"` 104, `gh api|gh pr|gh run|"gh"` 114, and `self.run|out|ok|head(` gives 110 in production code. The file is unchanged since the stated fact commit `0b8f8b585`. The other three counts re-derive: 24, 6 and 5. The DEFER does not turn on this figure, since the total stays at about 150 under any of these definitions. Carry: dismissed: immaterial to the ruling, and a triage record cannot be amended after merge to any effect
- The triage file cites BEATD's watch jobs as "design note §3, §6 (c)5". In `dev/programme/designs/R10-ORCH-BEATD.md` on `design/R10-ORCH-BEATD` (32e249d2e), `kind:"watch"` with its 60 s floor is in §2 (job table, line 22), and the 60 s floors for ci-watch/proof_watch are in §4, arm (c). §4 cites "round 3 §6 (c)". The substance is right but the section pointer is not. Carry: dismissed: citation imprecision only, and the claim it supports is verified

## Evidence

- RESULT mutation: the committed file makes `ruling_verdict` return DEFER and `triage_refusal` refuse a `#P248` carry. A mutant with the verdict rewritten to ACCEPT makes the same carry pass (None). A mutant with no verdict line returns `unreadable` and is refused. The null control (file absent) returns "not on the roster branch or origin/main". This matches the body's mutation proof and null control. See ev/mutation.txt and ev/mut.py.
- RESULT figures: these were confirmed at the head. `orchestrator_tick.py` has the quota read and flag at lines 1277-1287 and `RATE_FLOOR = 0.2` at line 159. Its self-test rate-headroom block is at lines 3120-3136 (it starts at 3130, and 3120 is the mandate stub's `rate_limit`). The docstring cost of 67 calls at 27 open PRs and 84 at 21 is at lines 93-94. `gh_read.py` lines 18-26 cover spent-bucket handling. Call sites are 24 (`self.gh(` in production code), 6 (proof_watch, gh-invoking sites) and 5 (ci-watch). The 113 figure is not re-derived; see Findings and ev/callsites.txt. The rate_limit snapshot at 10:40:58Z, the seat-ledger lines and `proposals.md` V162 are out of tree (no `proposals.md` exists in the repo). I could not re-derive them and did not verify them.
- The finder's harness: none. This is a proposal-triage ruling with no finding harness; the body's figures are the instrument. The mutation script ev/mut.py is my own and calls the production `roster_edit.py` functions.
- The class is one seam: a single triage entry, and the body states no class.
- Classification: both new files are under `dev/programme/`, which is INERT (`tests/closure.py` line 274). `tests/entities.py` could not run in this container: python3.12 lacks `homeassistant`, and the default python3 is older and fails on f-string syntax. CI carries that check.
- VERSION, the manifest, RELEASE_NOTES.md and the golden and claim files are untouched (ev/version.txt is empty).
- `git merge-tree --write-tree origin/main e42df2007` returns rc 0 with tree 53bc3a5be, and origin/main is beb570c81 (ev/merge-tree.txt). GitHub reports mergeable_state `blocked` (review/required checks), not dirty.
- CI on this head, read from the check-runs API: `arm` skipped, and `cancel-superseded`, `prelude` and `refresh` (two each) are still queued. No gate check has concluded and none is red, so no red-check answer is owed (the body says `none`). The workflow runs `CI edit` and `CI code` are queued. CI was not concluded when this review was written; the merge train's own required-check grading governs (ev/check-runs.txt).
- The body's Head section explains the second file (the delivery row) as the commit on top of the authored head fa3eddc47. Its line "the diff is one markdown file" refers to the authored head.
- Forward-carry: the body says none. The `orch_sweep.sh` half is routed to the orchestrator as out-of-tree, which is consistent with P230 and P236 as the body cites them (not re-read).
