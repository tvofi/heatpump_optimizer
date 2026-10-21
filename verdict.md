Fix review: blocked 044edcc2b32ef6fb9172b79bfc169c7beeb0dc38 carry-missing: not carried to R10-CI-LAYOUT (PR 1/PR 2) -- this round's new finding, that every main merge into the PR 1/PR 2 branches must re-run selftest_wiring.py --check and that neither prepr.sh nor the orchestrator's merge path runs it, is only in the PR body; roster handoff/audit-r10-roster 31e162fd3a1207db596539b2330af1d274c36c85 holds neither line

Round 2 for this head series. The fixer's round 4 body; the previous verdict blocked 38ec7c60 for ci-red. I measured head 044edcc2b32ef6fb9172b79bfc169c7beeb0dc38 (ev/HEAD.txt). It was still the PR head and the branch tip when I wrote this. Roles directory: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so my contract is current.

## The blocker (step 10, finding-propagation.md "Enforcement")

The fix is right. What blocks the merge is the carry. This round's red produced a finding that changes how later stages must work. The body records it in two places:
- Forward-carry, third bullet, with a new sentence: "Every main merge into those branches must re-run `selftest_wiring.py --check`, because main can add a self-testing program at any time (this round's red)."
- Friction, a new line: "defect-root-cause: unenforced: a merge of origin/main into a branch that widens `selftest_wiring`'s rule can bring in a newly self-testing program, and neither `prepr.sh` nor the orchestrator's merge path runs `selftest_wiring.py --check` ..."

Neither text is in the tree's roster. handoff/audit-r10-roster at 31e162fd3a1207db596539b2330af1d274c36c85 (re-fetched just before writing):
- R10-CI-LAYOUT's carry list (27 entries, ev/roster-group-carries.txt) has the third bullet only in its older form, ending "...or the drift this PR closes reopens. Carry: R10-CI-LAYOUT". The main-merge re-check sentence is missing.
- No group's carry or brief contains the new friction line. A grep for "selftest_wiring.py --check`, because main" and "newly self-testing program" over the roster file returns 0 hits.
- R10-CI-LAYOUT-P1 (2 carries) and R10-CI-LAYOUT-P2 (1 carry) are both not-started. They are the stages that move instrument-self-tests and do the main merges this precondition binds, and they hold nothing about it.
- The body names no roster SHA for these lines.

finding-propagation.md says: "The producing PR does not merge until the carry is in the tree". This finding is established by measurement (control below). It narrows what PR 1/PR 2 must do, so it must be carried. Not a defect in the code.

Remedy: append the amended bullet and the friction line, with its control, to R10-CI-LAYOUT (or to -P1/-P2, the stages it binds) on handoff/audit-r10-roster. Then name that SHA in the body. The control, stated as a precondition: `python3 -I tools/audit/seat/selftest_wiring.py --check` after every main merge prints `N self-testing, N wired, 0 unwired`, rc=0. Deleting any wired line turns it rc=1 (my M-del below). No code change is needed, so a pure carry fix should qualify for the merge carry.

## What I verified (Linux cloud container, bash 5, CPython 3.11, node 22)

RESULT selftest_wiring_check before(7b43b1b4e) self_testing=71 wired=70 unwired=1 (tools/pr/gate_priority.py) rc=1   (ev/wiring_before_7b43b1b4e.txt)
RESULT selftest_wiring_check head self_testing=71 wired=71 unwired=0 rc=0   (ev/wiring_head.txt)
RESULT selftest_wiring_check merged_with_origin/main_3688cf259 self_testing=71 wired=71 unwired=0 rc=0   (ev/wiring_merged_with_main_3688cf25.txt)
RESULT gate_priority_selftest checks=12 failed=0   (ev/gate_priority_selftest.txt)
RESULT offline_spy gate_priority network=0 remote_git=0 refused=0 rc=0   (ev/offline_spy.txt)
RESULT agreement_py_restore closure=13 covered=13 missing=0 rc=0   (ev/restore.txt)
RESULT finder_harness(head's r10_seat_selftests_mutants.py) M0_red=0 killed=38 survivors=0 rc=0   (ev/harness_head_version.txt)
RESULT finder_harness(main's r10_seat_selftests_mutants.py, run at head) M0_red=0 killed=33 survivors=1 rc=1   (ev/harness_main_version_at_head.txt)
RESULT merge_tree origin/main=3688cf259 rc=0 tree=147c4bab0 (no conflict)   (ev/merge_tree.txt)
RESULT version_manifest_notes_golden untouched   (ev/version_untouched.txt)

- The check that fired fails before the fix and passes after it: 71/70/1 rc=1 at 7b43b1b4e, then 71/71/0 rc=0 at the head.
- The fix does not weaken the check. Between 38ec7c60 and this head, the blobs of tools/audit/seat/selftest_wiring.py, tools/policy/agreement_py.py and tests/closure.py are identical (292dc67d, 0d4a76b3, e876e458). The authored delta is fdf471c55's one added line in governance.yml. The rest of 38ec7c60..head in tools/tests/.github is main's mutation-ledger killed_by JSON plus delivery rows. Merging the newer origin/main 3688cf259 brings in no new self-testing file.
- Mutants on the new line (ev/mutants.txt). Each one reddens the check, and the restored file is clean:
  - M-del (line deleted): 71/70/1, rc=1. KILLED.
  - M-comment (`# python3 -I tools/pr/gate_priority.py --self-test`): 71/70/1, rc=1. KILLED.
  - M-noflag (`--self-test` dropped from the line; my own, not in the body): 71/70/1, rc=1. KILLED.
  - Restored: 71/71/0, rc=0.
- Finder's harness. The roster brief names "#2444's selftest_wiring.py --check and mutant harness". I ran two versions, each in its own worktree:
  - The head's version: M0 green and 38 KILLED, which matches the body's 38.
  - main's version (the finder's, unedited) run at head: 33 KILLED. Its one "survivor" is S08: `NOT RUN rc=-1 | PATTERN FOUND 0 TIMES`. This PR rewrote handoff_push.sh's --self-test wrapper, and the head's harness re-targets S08 to the new dispatch line with a stated reason. S08 is KILLED there. A pattern that no longer matches is not a mutant that survived, so I count it as harness maintenance, not a survivor.
- Step contents (ev/step_programs.txt): the "Show the self-tests outside tools/audit/seat/" step has 15 non-comment lines. 13 are distinct self-test programs (11 + replan.py + gate_priority.py), plus agreement_py's --self-test and --restore (item B). That matches the body's "13 programs" read that way. I re-derived this count myself.
- Body figures re-taken at fdf471c55 (ev/figures_at_fdf471c55.txt), all reproduced:
  - structure: STRUCTURE RATCHET PASSED.
  - layout --guard --base 265d3bf1a: 0 refusal(s).
  - tmp_paths --check: 0 refused, 0 stale.
  - policy_lint: TOTAL 0 error(s) across 41 policy file(s).
  - ci_predict --base 265d3bf1a: no closures or fast red predicted.
  - agreement_py --self-test: 7 checks, 0 failed.
  - `grep -n selftest_wiring tools/pr/prepr.sh` prints nothing, as the body says.
- Not reproduced exactly: the cheaper detector's cost. I measured 0.101, 0.106 and 0.109 s against the body's 0.064-0.066 s (ev/wiring_timing.txt, date-based wall clock). It is still sub-second and the answer stands; the figure is host-dependent.
- Not re-run: prepr.sh's FIGURES line, and the agreement.mjs --py-json null.

## CI on this head (check-runs API)

- All gate checks concluded success: instrument-self-tests (119209062047, the check that fired last round), closures, fast (3.14), coverage, Analyze (python), wave-script, policy-docs, pr-contract and the rest. Every other run is skipped.
- nightly-status (119209062914) is failure. It grades main: the body names it and answers it (the slow lane, tests.yml, which this diff does not touch). Not this PR's red.
- Red-check answers (step 11): instrument-self-tests at 38ec7c60 is named with a cheaper detector and its cost. policy-docs at e9d54acd is named and answered. Both pass the trigger.

## Not verified / disclosed

- I did not re-run the gate (FULL by item E) or the mutation table. Those are CI's runs.
- I built no instrument of my own beyond the M-noflag mutant and the YAML step-line count.

bus-nonce: 5a067b503faa6da9926b251336626c65
