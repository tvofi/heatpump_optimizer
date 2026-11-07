Fix review: merge 96987ab3d7224b04803106ae4366c5a02bb91b51

bus-nonce: 2c1b06518a61d24f9ab98fc57e2c3838

## Round

This is a merge-resolution delta review of #3241 (R10-CARRY-RESIDUE), done after the round-3 `merge` at de1a371e2ed49c742ef690d605fbc8e605b853f3 (probe/rev-3241-1a35ee25, read in full). It is not a fourth blocked round, so no re-cut is owed. I ran it from a detached worktree at the head 96987ab3d7224b04803106ae4366c5a02bb91b51, with origin/main 355d9965a7a14ec45ef8cd25fb9c75c5ced044f1 as the null control. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.

## Head

- I measured 96987ab3d7224b04803106ae4366c5a02bb91b51. It was still the PR head at the last read, both in pull_request_read `get` and in the check-runs listing.
- The body's `## Head` names this SHA as the head.

## Findings

None. The resolution delta settles everything the brief asked about.

## Evidence

- (1) review_carry: `review_carry.py de1a371e2 96987ab3d` printed `review_carry: FRESH-REVIEW`, because `49feb621c06987143872795f502b2c72a2549c6e is not the automatic merge of its parents` (ev/review_carry.txt). So the scope of this review is the resolution delta.
- (2) Hand-resolved merges: I diffed each merge in de1a371e..96987ab3 against `git merge-tree --write-tree` of its parents.
  - bb33e6807, 1d5a5ce7f, 87b00d3ec and 96987ab3d are identical to git's automatic merge (ev/resolution_vs_auto_96987ab3d.txt).
  - Only 49feb621c differs, and only in tools/audit/seat/r10_ledger_mutants.py, where it removes the conflict markers (ev/resolution_vs_auto_49feb621c.diff). The resolution keeps the branch's `T3_review_owed_silent`, anchored on `lg.git_recarry(...)` and `flag=not text.startswith("CARRY:")`, and main's `T4_no_escalation`, anchored on `aging, group_of, last_open)`. Main's T3 anchor and the branch's old T4 anchor are dropped. That matches the body's account of the resolution.
  - At the head, both anchors exist once in orchestrator_tick.py, at lines 758-759 and 1075-1076. Main's former T3 anchor (`getattr(rr, "RECORD_BRANCH", None)):` plus `flag=True`) no longer exists at the head: line 757 now ends `None),`. Dropping it was therefore correct.
- RESULT mutant=T3_review_owed_silent rc=1 fails=6. RESULT mutant=T4_no_escalation rc=1 fails=4. Output: `plants: 2, without a FAIL line: none`, run by me at the head (ev/plants_T3_T4.txt). T3 still plants and is killed.
- Self-test at the head: `r10_ledger_mutants self-test: 194 checks, 0 failed` (ev/selftest_head.txt).
- Self-test at origin/main 355d9965 (null control): `r10_ledger_mutants self-test: 149 checks, 0 failed` (ev/selftest_main.txt). The 45 extra checks at the head are the branch's own plants.
- (3) Nothing rode in under the resolution: I compared the PR's patch at de1a371e (against merge base dc0a170b) with the patch at 96987ab3 (against merge base f2a01514), with index and hunk-header lines removed (ev/patch_interdiff.txt). Both touch the same 8 files. They differ in exactly two places:
  - the tests/replay.py carry-4 comment sentence (0b1a4bb6f);
  - the T4 anchor in r10_ledger_mutants.py, which is now main's.
  - No other line moved.
- (4) The 0.249 figure (ev/budget_0249.txt, ev/commit_0b1a4bb6f.txt) checks out:
  - The owner `loop_cpu_ratio` budget was 0.249 from 37bafc867 ("replay: record the owner fixture's cost budget") until 6715d9733 re-derived it to 0.2154. That is R10-REPLAY-COST-BUDGET round 3, so the past tense ("under that recording's 0.249 budget ... round 3 below re-derives that budget") is accurate.
  - sqrt(2) x sqrt(0.137 x 0.227) = 0.2494, the recording's rule applied to the cited spread.
  - The floor is 0.249/2 = 0.1245. The ref30 reading 0.128 is 2.8 % over it (0.128/0.1245 - 1 = 0.028). The highest CI reading 0.189 (ref24) sits 24.1 % under the ceiling (1 - 0.189/0.249). Both match the sentence.
  - Not re-derived: I did not re-open the logs of the cited jobs 125240101580, 125160076828, 125097530406, 125316010511 and 125461180429 to re-read 0.128 / 0.1339 / 0.1418 / 0.1433 / 0.189. Those readings are unchanged from the de1a371e text that round 3 verified, and 0b1a4bb6f moves none of them (ev/patch_interdiff.txt). The commit changes only a comment.
- (5) Red checks:
  - The live head has 68 check-runs, read in one page (total_count 68): 0 failure, 0 cancelled, everything else success or skipped. `gate` succeeded in runs 42332985078 (job 128293783122), 42333513736 (job 128293945477) and 42332985466 (job 128294118593). `pr-contract / pr-contract` (job 128293626552) succeeded after the last code-run job concluded.
  - The live head has no red, so R10-HOTFIX-GATE-BUSY-DEFER does not arise: no gate is red by mutual deferral.
  - The body's `## Red checks` answers the reds at the prior head 87b00d3: `tests / replay`, `tests / nightly-status`, `pr-contract`, `gate`.
- CI: `merge_train.py classify 96987ab3d --pr 3241` exited 0 with `GREEN 96987ab3d7224b04803106ae4366c5a02bb91b51 pending: none red: none` (ev/classify.txt).
- Merges with main: `git merge-tree --write-tree origin/main 96987ab3d` (origin/main 355d9965, 2 commits past the PR's base f2a01514) exited 0 with tree 0b22ec89849692fa275747426692bbbd383b4754 and no conflict (ev/merge_tree.txt).
- Review packet: it rendered with rc 0 and `## Refusals: none`. The advisory `hot-file: HPO_BUS_TRAIN_STATE is unset` is a seat-environment notice. Its carry_audit line at the head read `1 finding item(s): 1 routed` (the body's R10-CARRY-RESIDUE-2 forward-carry). The packet is in ev/review-packet.md.
- VERSION, the manifest and the release notes are outside the patch: the 8 files in ev/patch_interdiff.txt do not include them.
- Instrument disclosure: I built no harness of my own. The plants, the self-test and classify are the committed instruments.
- Closing self-audit: `carry_audit.py check` ran on this verdict with the body's `## Forward-carry` and `## Friction` sections copied verbatim from the live PR body, and exited 0 with `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`.
