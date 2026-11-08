Fix review: merge f326fd6dc0dfe9b29d4008903a6768cefd50d4e9

bus-nonce: f962ab5e204b8f4b20a21ac00fe67429

## Scope

Later-round fix review of PR #3288 (R10-TRAIN-MERGE-LOOP-2), round 2 after `Fix review: blocked 35fc2646` (class-open, app_approve.sh carry fetch). Measured head f326fd6dc0dfe9b29d4008903a6768cefd50d4e9 from a detached worktree; refs/pull/3288/head re-read before return and still f326fd6d. Roles diff (merge base...origin/main -- dev/governance/roles/) is empty, so the contract is current. Since 35fc2646 the head carries two repair commits (0ccedc45 one git-transient rule; 022a55fd pin the diff-mutant survivors) and three merges of origin/main; I reviewed both repair commits as new work and the merges as a resolution delta.

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main(092941b7) f326fd6d` = tree 7e0259aa, rc 0, no conflict (ev/merge_tree.txt).
- Resolution delta: of the merges 624b03fd, 17b8194e, f8c4982d, f326fd6d, only 17b8194e differs from git's own automatic merge, in tools/audit/seat/merge_train.py only (7 lines: the conflict markers removed, both sides kept). Every other path in every merge is byte-identical to the automatic merge, so nothing outside merge_train.py was dropped. merge_train.py is unchanged between 17b8194e and f326fd6d, and main has not touched it since 48af0864.
- Resolution read-back, my own multiset count (ev/resolution_readback.txt): lines added against the merge base b4ec2f33 by the PR parent (364) and by main's parent (560) are all present in the merged file, 0 missing on each side.
- Merged wait_ci, read against both parents: #3290's `_gate_busy` and sweep settle run first and reclassify a red GATE as pending while gate.py's busy names a run; a lone red GATE left over then goes through #3288's `gate_deferred` sibling read and its one-poll `graced` allowance. `classify_at`, `_gate_busy` and `gate_deferred` all stay. Mutants on each side (below) show that both behaviours are pinned at the head.
- Self-tests at head f326fd6d / base d2e4d2d1 (ev/selftests_head.txt, ev/selftests_base.txt): merge_train 564/0 vs 506/0; app_approve 322/0 vs 316/0; pr_args 184/0 vs 179/0; gh_read 129/0 vs 122/0; r10_codescan_wait_race --selftest 12/0 vs 9/0. STRUCTURE RATCHET PASSED at head (ev/structure_head.txt).
- Race harness (reviewer-built, not the finder's: the previous round's evidence/gate_race.py from verdict/3288, re-run unchanged, ev/gate_race.py). At base d2e4d2d1 (which already includes #3290): `RESULT scene=race red=['gate'] checkrun_polls=1 sibling_reads=0` and null `red=['gate']`. At head: `RESULT scene=race red=[] checkrun_polls=3 sibling_reads=2`; null control `RESULT scene=null red=['gate'] checkrun_polls=1 sibling_reads=1`. The harness moves under its perturbation and the null stays red at both ends (ev/gate_race_harness.txt).
- Mutation proof, re-run by me at the head (ev/mutants.txt, ev/mutants_carries.txt; unmutated null: every suite 0 failed; tree restored clean). Every mutant was killed:
  - RESULT deferred-no-held (action_required dropped from gate_deferred's exclusion): merge_train 1 failed.
  - RESULT deferred-empty: 5 failed.
  - RESULT no-grace-poll: 1 failed.
  - RESULT drop-main-busy (main's `_gate_busy` call removed in wait_ci, the #3290 side of the resolution): 5 failed.
  - RESULT mt-no-git-retry (`_reads_retried` git arm made plain run): 2 failed.
  - RESULT aa-plain-fetch (the carry fetch reverted to plain git fetch, the blocked seam): app_approve 3 failed.
  - RESULT aa-gh-classifier: 3 failed.
  - RESULT aa-always-transient: 2 failed.
  - RESULT rm-plain-fetch (remerge_main recarry fetch): pr_args 1 failed.
  - RESULT gr-one-try (run_git_retry): gh_read 1 failed.
  - RESULT gr-refused-ignored (GIT_REFUSED bypassed): merge_train 1 failed.
  - RESULT hr-no-fallback (pages() per_page=30 fallback removed): harness selftest crashes with AssertionError.
  - Carries 1, 2 and 5, still settled after the merges: c1-runs-approved-false 1 failed; c2-started-at-filter-dropped 1 failed; c2-no-verdict-needed 2 failed; c5-undraft-unrecorded 1 failed; c5-failed-ready-ignored 1 failed.
- Class census, the body's rule re-run at head (ev/census.txt, ev/census_mt_prod.txt): 18 merge_train.py self.run/self.ok git fetch/push sites above `_self_test` (line 3930): 17 fetches and 1 push, every one with argv starting `["git", "fetch"|"push"]`, so `_reads_retried` routes every one of them to `gh_read.run_git_retry`. app_approve.sh:554 is closed (retry_with git_transient). remerge_main.sh:29 is closed (--git-retry). train.sh returns none. The body dispositions app_push.sh's push (Forward-carry, R10-FLY-GH-READ-RETRY).
- Carries settled. The parent's carries 3, 6, 7, 8, 9 and 16, and the gate-race hotfix, are each pinned by the mutants above (bot tip = c1; post-approval wait = c2; git rule = mt-no-git-retry/aa-*/rm-*/gr-*; pages fallback = hr-no-fallback; undraft = c5; remerge FAIL/full-log = pr_args 184/0, re-pinned at 35fc2646 and unchanged since).
- Figures re-derived at head: merge_train 564, app_approve 322, gh_read 129 and the 18-site census match the body. The Figures line `pr_args ... 179 checks, 0 failed at this head` is the pre-merge figure (17b8194e^1). At f326fd6d it prints 184/0, as the body's own Resolution delta says. 179 is main's count at the base, so the +5 holds. The prepr wall times (2087 s, 2878 s), the 4 diff-mutant survivors and archscore dS +0.0000 were not re-taken (heavy runs cited, not re-run; the survivors are self-test lines by the body's disposition, which I read and accept as test scaffolding).
- Files: VERSION, the manifest, RELEASE_NOTES.md, claim files and every *_budgets.json are untouched in the three-dot diff. dev/programme/delivery/3288.md is in the diff. The diff adds no other new file, and CI's closure/entities lanes are green.
- CI at this head: `merge_train.py classify f326fd6d --pr 3288` = `GREEN f326fd6d... pending: none red: none`, rc 0, taken twice, the last just before return (ev/classify.txt). All check-run pages read (filter=all, total 107, 2 pages, ev/checkruns_all.tsv). The concluded reds at this head are:
  - gate 128638659969 and gate 128642651276: failures. Each log reads `FAIL run(s) [42449977714] at this head are still being judged; their gate decides`, an edit-run deferral (ev/gate_red_logs.txt). Code run 42449977714 concluded success at 05:56:07Z, and gates 128644941507, 128645103438 and 128645105770 succeeded.
  - gate 128637938818 and arch-score / arch-score 128637736092: cancelled, both superseded. Later arch-score runs succeeded.
  - The body's `## Red checks` describes 35fc2646 and says no CI ran at 17b8194e. It does not name these four. Under the gate-deferral ruling and step 11, pr-contract 128644808143 started at 05:54:50Z, after the last red concluded (05:44:04Z), and succeeded. That run is the evidence, and none of the four is this diff's red.
  - governance / instrument-self-tests is success at this head (128637167549), so no 30-minute-timeout claim needs judging at f326fd6d.
- `## Head` names f326fd6dc0dfe9b29d4008903a6768cefd50d4e9, the head I measured. A stray `17b8194e` line follows it.
- Forward-carries are routed on the roster: packet carry_audit at head reports 5 routed, 0 unrouted, 0 bad destinations. The body's carries land in R10-TRAIN-REJOIN-NO-RECARRY, R10-HOTFIX-TRAIN-DEFER-WAIT and R10-FLY-GH-READ-RETRY.
- Merge state: draft, mergeable_state blocked (review owed). This is the second fix-review round of this group.
- handoff-wip milestone pushes were skipped. The dispatch says to push nothing but the probe ref, and that narrower instruction governs.

## Findings

- The body numbers carries against the roster as it stood at f91d0eb9e/d0c203cd (17 entries, with the gate-race hotfix at 15). dafe26ff3 later dropped the hotfix carry, so on the current roster (16 entries) the body's `Carry 16` (bot tip) is position 15 and `Carry 17` (git rule) is position 16. Every parent number in the body is right and every current carry 1-16 is settled at this head, so no work is lost. Carry: dismissed: a numbering offset in the body only; the parent carry numbers disambiguate each item and all 16 current roster carries are settled at f326fd6d.
- The gate-race hotfix still has no committed finder harness. The race harness re-run here is a reviewer's (evidence/gate_race.py from verdict/3288), not tree, as the body discloses. Carry: R10-HOTFIX-TRAIN-DEFER-WAIT

## Friction

none
