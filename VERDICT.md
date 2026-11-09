Fix review: merge 9fdf05abf58983d6d36d6bbdead3d8155fea190c

bus-nonce: ce031baecfe5bf580bfa5cb9dd467a35

Round: first review by this seat (head 9fdf05abf58983d6d36d6bbdead3d8155fea190c = the PR's authored head merged with origin/main 19865e5a86).

## Findings

- Follow-up: the owner-side settings the RCA (section 7) says are needed whatever this PR does, remove BASH_ENV from the cloud environment's variables and re-paste cloud-setup.sh into the setup script after merge, are not made by this diff; until then a cloud seat that keeps BASH_ENV runs the old profile and reproduces shape A. Carry: R10-RCA-CLOUD-ENTITIES-ENV | dev/programme/rosters/wave-r10-groups.json
- Residual: the coverage-reuse arm of shape A is known by inspection only (RCA section 2: no python on the author's Mac), and the full tests/entities.py was not re-run by the author or by me (868 s, exclusive lease; CI's heavy runs cited instead). Carry: dismissed: the barrier is the profile/arm, which I measured; the entities arm is CI's.

## Evidence

- Head measured: 9fdf05abf58983d6d36d6bbdead3d8155fea190c (ev/HEAD.txt). merge-tree against origin/main: rc 0, no conflict (ev/mergetree.txt).
- VERSION, manifest and RELEASE_NOTES.md untouched (name-only three-dot diff empty for them); no policy, budget, closures, golden or claim file in the diff (6 files, ev/diffstat.txt). dev/governance/roles/ unchanged on main since the merge base (empty diff).
- RESULT cloud-setup --self-test at head: 22 checks, 0 failed, 0.141 s (ev/selftest-head.txt); the arm prints seven names besides PATH, the control (nested bash under BASH_ENV runs the profile) passes.
- Mutation, mine: reverting only the RUNNER_TEMP line in write_profile -> FAIL "under BASH_ENV a nested bash keeps every variable its caller set", overwritten: RUNNER_TEMP, 22 checks 1 failed (ev/mutant-runner-temp.txt); reverting only GIT_AUTHOR_NAME -> the same FAIL, overwritten: GIT_AUTHOR_NAME (ev/mutant-gitauthor.txt). Restored, tree clean. (Running the base script wholesale shows 19 checks, 0 failed because it lacks the arm itself; that is not a mutant of the arm.)
- The claimed 0.24-0.39 s arm cost: I measured 0.141 s for the whole self-test on Linux; consistent with the bound, not re-derived on the author's Mac.
- Figures 4 h 20 min / 39 min / 868 s are from handoff-wip refs and tests/closures.json; the packet's figure_lint marks the two git-log ones unverified (flags unchecked), I did not re-derive them.
- Class check: BASH_ENV greps (ev/bashenv-grep.txt) show no other profile writer in tools/, .claude/ or workflows exporting caller-overridable variables; the arm derives its names from the profile, so a later export is covered. PATH keeps its own arm (#2452).
- Red checks: none on this head; body's "Red checks: none" matches. CI: merge_train classify -> GREEN, pending none, red none (ev/classify.txt, rc 0). Packet carry_audit: 1 item routed, 0 unrouted. bugclasses.json parses (ev/json.txt).
- Root-cause answer is in the diff's RCA doc (state (d), cost test, refusals recorded); not judged here beyond presence.
