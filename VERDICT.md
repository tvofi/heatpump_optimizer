Fix review: merge 388960818889ed424e1b662ae0bd6682e1c519ce

bus-nonce: 865793f08f4b7abf1b8e81019da07903

Resolution-delta review (round 2), per fix-review.md step 12: R1 (#2131)
landed on main and this PR returns as its resolution delta. I judged the
delta alone, from a detached worktree at 388960818889ed424e1b662ae0bd6682e1c519ce
(merge base = origin/main tip 5c02e2bab, so three-dot equals two-dot here).

(e) IS GONE. `git diff origin/main -- tests/derive_closures.sh` at the head
is EMPTY -- 0 bytes; the file is R1's, byte for byte -- and derive_closures.sh
does not appear in the branch's three-dot diff at all (6 files: tests.yml,
delivery/2129.md, closure.py, entities.py, a1_dispatch_arms.sh, prepr.sh).
No residual #2129 (e) hunk survives.

(a2) IS UNCHANGED TEXT AND STILL PROVEN AT THE NEW BASE. The bodies of
`inert_read_owners` (sha 090fc4ebdb…) and `affected` (sha 1387a3163b…) are
identical between the round-1 head 156fe40a1 and this head. All three mutants
re-run at this head, each restored with `git checkout -- tests/closure.py`:

- RESULT A (consultation loop deleted): #2109-style probe and LICENSE BOTH
  answer SKIP -- both arms collapse to the defect.
- RESULT B (parent level `allowed.add(dirs[-2])` removed): round20
  new_probe.py SKIPs (the hole) while the #2109 probe stays SCOPED
  (distinguishes B from A); entities.py under the mutant fails exactly
  `1 of 2262` -- the `_A_IR_NEWDIR` pin, `case=skip rederive=[]`.
- RESULT C (unbounded ancestors, `allowed.update(dirs)`):
  dev/governance/roles/fixer.md answers SCOPED for entities+harness_headers
  (the over-trigger `_A_IR_BOUND` pins); restored, it SKIPs again.

Null controls re-taken at the head: SECURITY.md SKIP, NOTICE SKIP,
const.py SCOPED 30 (identical to base), docs/new_page.md SCOPED 1,
handoff/r9-x/note.md SKIP.

(a1) IS GENUINELY COUPLED TO THE RUNNER. The landed harness
(a1_dispatch_arms.sh, HEAD vs origin/main, seat venv): inert-only=skip,
closure-touching=scoped, diff-underivable=full; BASE arm shows
`closure-scope runs on workflow_dispatch: False`. The workflow's
"Re-record the closures" step consumes SCOPE_SCRIPTS through ONE
`derive_closures.sh --scripts-from` lane run -- no `--single` loop, no
event gate. The new coupling pin's null control, run under the pin's own
extraction rule: FAILS on pre-R1 a74520020 (serial `--single "$s"` loop),
PASSES on origin/main and on the head. The closure-scope job block is
sha-identical to round-1's head, so round-1's dispatch-branch-deleted
mutant (5d1546383) carries: no branch, no case derived, every dispatch
FULL.

CHECKS AT THE HEAD, run by me (evidence/checks_at_head.txt):
entities ALL 2262 PASSED; STRUCTURE RATCHET PASSED (all 16 metrics ok);
policy_lint 0 errors / 40 files; closure.py selftest ALL 76 PASSED;
throwaway_git 0 refused, 0 stale; env_drift --claims-only origin/main ok.
Red checks: none -- confirmed on the commit check-runs API at
388960818: zero failure/cancelled/timed_out (closures, coverage, fast
(3.14), Analyze (python) still in_progress at review time). VERSION,
manifest, RELEASE_NOTES.md heading, both claim files and every
*_budgets.json are byte-identical to main.

RULE 1 END-TO-END, answered explicitly: no path where a wrong closure
survives longer than one merge remains or was added. A push to main still
takes the FULL arm (closure-scope's `if` excludes push events, SCOPE_CASE
is empty, the closures job's full derivation runs untouched in the diff's
`else` branch), so a wrong table reddens main within one merge exactly as
before. (a2) moves the #2109 class onto the pull request itself; (a1)
gives batch dispatches the same scoped derivation, fail-closed on an
underivable diff (empty list -> `affected` answers FULL -- re-verified at
the head); the coupling pin keeps a scoped dispatch paying the lane MAX
through the same re-derivation, so the detector actually runs. The
residual hole (a subtree no recording reaches, e.g. a new round20/) is
unchanged from before and keeps main's full arm as its one-merge detector.

The prepr.sh self-test fixture change is honest and necessary: (a2)
correctly derives docs/delivery/9999.md scoped (doc_claims' recorded
reach), so the skip arm now branches dev/governance/rules/9999.md, which
I measured SKIP at both ends -- the arm's intent (record nothing) holds.

Evidence: /Users/timmalmstrom/hpo-seats/r9rev-2129b/evidence/ (HEAD-sha
names the head; a2_mutants_and_e.txt, mutantB_entities.txt,
a1_arms_runner.txt, coupling_pin_null_control.txt, checks_at_head.txt,
entities_head.txt, null_probes.txt, quick_checks.txt, a1_arms.txt).
