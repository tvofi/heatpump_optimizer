Fix review: blocked c8219f601f85f881ae8fe3c38a9c218ffececeb4 ci-red: tests / fast (3.14) fails harness_headers on the PR's own harness depth root, and the R10-FLOW-AUTOTRAIN carry at roster 4937d60fe is a host path, not text

bus-nonce: 31d3fc7de5f180d85a07b9955ef13e39

Round: 1 (first review of #2772). Measured head: c8219f601f85f881ae8fe3c38a9c218ffececeb4, re-read from origin just before the return; still the head.

## Block

1. **Red gate check from this PR's own file.** `tests / fast (3.14)` concluded failure at this head: `tests/harness_headers.py` (run_always) fails "every inlined walk matches the canonical helper and no depth root remains", naming `dev/audit/harnesses/r10_train_upgrade_mutants.py:23: ROOT = Path(__file__).resolve().parents[3]`. The file is new in this diff (absent at merge base c176ee55d), so this red belongs to this PR. The fix: use the canonical `repo_root(start)` helper (tools/audit/repo_root.py, inlined the way the other dev/audit/harnesses/*.py files do), not `parents[3]`. The body's `## Red checks` says "none", and its Scope figure lists only `tests/entities.py`, but harness_headers runs on every gate. A cheaper detector existed: `python3 tests/harness_headers.py`, run_always, about 105 s on CI. Some head workflows (closures, coverage, instrument-self-tests) had not concluded when this was read. So I am not assigning the root-cause-detectable/unrecorded class (step 11). I am blocking on the red itself, which needs a code push.
2. **carry-missing: not carried to R10-FLOW-AUTOTRAIN.** The body's Forward-carry cites "Roster SHA: 4937d60fe (on `handoff/audit-r10-roster`)". That commit (`roster_edit append-carry R10-FLOW-AUTOTRAIN`) appends one carry entry. The entry is the literal string of an absolute host file path ending `carries/carry-train-upgrade-autotrain.md`, not that file's text. The `@file` form of `roster_edit.py append-carry <group> <text | @file>` was not used. At 4937d60fe, which is still the roster tip, no entry of the group names `admit_add`, `launch_detached` or `queue.open` (grep count 0). The body's four items are therefore not in the stage's brief, and neither is the precondition "its `live_train` must read `queue.open` as well as `train.pid`". The earlier carry entry covers only "pitch() should `train.sh add`" (finding-propagation.md: a carry states its control as a precondition, in the brief). The roster also now holds an account-bearing host path, which the brief forbids in pushed content. Replace it with `append-carry R10-FLOW-AUTOTRAIN @<file>` (and `drop-carry --match` the path entry), then cite the new roster SHA.

## Findings

- Reviewer mutant R2 SURVIVED: in `Train.policy_approve`, flipping the fail-closed `except` branch to `live, why = True, ...` (an unreadable mandate posts the approval) fails no self-test check. The "in force" condition is pinned only on a readable mandate (out-of-window, scope code-owned). Under this mutant, an approval as the owner's `gh` account citing an unverified mandate would sit at the head, even though `policy_gate` would still refuse at the merge. The fix: one `policy post null:` arm where `_mandate_read` raises. Carry: R10-TRAIN-UPGRADE
- Reviewer mutants R3 and R4 SURVIVED on the "no owner approval at the head yet" condition. Dropping `commit_id == h` (R3: an owner approval at another head suppresses the post) or dropping `_is_owner` (R4: any account's approval at the head, e.g. hpo-approver's P86 admission approval, suppresses it) fails nothing. Both fail closed: `policy_gate` then refuses and nothing merges. But R4 is the realistic shape, because admission now approves via app_approve before the batch's policy post can matter, and no arm pins that the owner-only filter is what lets the policy post through. The fix: one arm each, (a) an owner approval at a stale head still gets the post, and (b) an hpo-approver approval at the head still gets the post. Carry: R10-TRAIN-UPGRADE
- The harness `dev/audit/harnesses/r10_train_upgrade_mutants.py` is the fixer's own instrument (the finding is the owner's ask, with no finder harness), and the body does not say so in those words (fix-review.md step 9). I also built my own mutants: ev/reviewer_mutants.py, disclosed here as mine. Carry: R10-TRAIN-UPGRADE

## Evidence

- Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Finder harness per brief, at head: `MUTANTS: 28 run, 0 not as required`. M0 PASS, M1-M27 KILLED (ev/mutants_summary.txt). This matches the body.
- `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 283 checks, 0 failed`, rc 0. This matches the body's 283.
- `bash tools/audit/seat/train.sh --self-test`: `train.sh self-test: ok (...add takes no pidfile)`, rc 0 on this Linux host. The body's arm-9 host note does not reproduce here, and the test passes.
- Race: arm `RACE: two concurrent adds with no train live start exactly ONE train (one launch, one train.pid) and spool exactly the other entry` ok. Two threads take separate `open()` descriptions, so `fcntl.flock` excludes them (queue_lock). M15 (lock replaced by nullcontext) is KILLED by this arm.
- policy_approve guard, reviewer mutants (RESULT lines in ev/reviewer_mutants.txt):
  - R0 null PASS.
  - Exactly one mandate: R6 (take the first of several cited ids) KILLED by `mandate_id:`.
  - In force: R1 (scope widened to code-owned) KILLED by `policy post null: ... scoped code-owned`; R2 SURVIVED (see Findings).
  - No owner approval yet: R3 and R4 SURVIVED (see Findings). The harness's M5 (re-post when the owner approved) is KILLED.
  - No budgets file: R5 (guard reads `pol` instead of `files`) KILLED by `policy post null: a budget file beside the policy`.
  - Head re-check before post: R7 KILLED.
  - Null control where all conditions hold: arm `policy post: a policy head with no owner approval at it, under --mandate <id> in force ... gets ONE approval citing \`mandate comment <id>\`` ok.
- `git merge-tree --write-tree origin/main c8219f601f85f881ae8fe3c38a9c218ffececeb4`: rc 0, tree 31529a355189424572610161c969be4aed8fa5ae, no conflict (origin/main = merge base c176ee55d).
- Claim files, VERSION, manifest, RELEASE_NOTES.md and every *_budgets.json are untouched by the diff (three-dot; ev/untouched.txt is empty).
- CI at this head (ev/ci_checks.txt): fast red as above. tests/entities.py passed all 2425 checks on CI. Several lanes were still in progress at read time. Heavy runs are cited, not re-run.
- Body figure "Scope: MODE: SCOPED -- 1 script(s) run": not re-derived here (no homeassistant module in this container for tests/harness.py). CI's own run shows entities.py scoped in, plus the run_always harness_headers and layout.
- ev/depth_seam_repro.txt applies harness_headers' own root_name and `.parents[` rule to the new file and matches line 23. The file is absent at the merge base.
