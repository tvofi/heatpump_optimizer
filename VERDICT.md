Fix review: merge 4cf5a2e6f0c8eb23031cd89e67b809bbbdcaeeca

bus-nonce: d7072715d824d6e9692d95fe9c4113e4

Round 1. Measured head 4cf5a2e6f0c8eb23031cd89e67b809bbbdcaeeca (reviewed from a detached worktree at that head).

## Evidence
- Role file on main is current (empty diff of dev/governance/roles/ against the merge base).
- RESULT: codeowners_gap.py --self-test at head: 55 probes, 15 nulls, 0 wrong. --check: uncovered_files=0 (enforcement_surface_files=174, covered_by_an_owner=61, pinned_by_base_restore=113).
- SHAs re-verified with git ls-remote on the upstream tags (all lightweight): checkout v7.0.1=3d3c42e5, setup-python v7.1.0=6d4fd22b, setup-node v7.1.0=949feb24, download-artifact v8.0.2=9000827c. They equal the four SHAs in ALLOWED_USES and the saved-work ref handoff-wip/r10-deps-actions-bump (6c46b09f) was reachable for comparison.
- Null control: the nulls for current and bumped revisions of all four actions pass (PINNED); the four one-character-off probes refuse.
- Mutants (clean head green as null control): dropping the checkout, setup-python, setup-node or download-artifact bumped SHA each turns the self-test red (1 wrong each, a NULL at its bumped pin). A prefix-wildcard on the membership check at line 644 turned 5 probes red (4 one-off probes plus unpinned setup-python). The literal string "actions/*" added to the set is inert (0 wrong) because membership is exact; that is an equivalent mutant, not a gap. All restored; worktree clean.
- Scope: three-dot diff is codeowners_gap.py (+28) and dev/programme/delivery/3160.md (+1) only; no workflow, no claim file, no tests/entities.py, no VERSION/manifest/RELEASE_NOTES change. The entities.py graders-head-copy literal still reads the current revisions (fbc6f399/ece7cb06) and tests.yml at this head still carries them, so it stays true; the body states Part 2 changes both together.
- git merge-tree --write-tree origin/main (3dd36972) against the head: clean, exit 0.
- tests/structure.py: STRUCTURE RATCHET PASSED. Scoped gate: MODE: SCOPED -- 2 script(s) run, 31 scoped out.
- carry_audit in the packet: 0 finding items. Body: Head names the head, Red checks is none, Part 2 is named as following and not opened.
- CI: every check in the live digest had concluded success, skipped or neutral except codeql / Analyze (python), in_progress for the whole review (over 40 minutes). merge_train.py classify stayed rc=3 WAIT (gate red: none) on that one run; no check was red. I could not obtain GREEN; the merge train should re-run classify before merging.
- The body's figure "origin/main = 94d8b47f" does not match the base 8247a1ed1 recorded in the packet; a stale remark that does not affect the diff, not a required check.
