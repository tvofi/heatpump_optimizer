Fix review: blocked 9ea84ecca8a8fd28c9bd8d8bdb325942a95888bd mutation-vacuous: ctx-const closeout.py:131, run-uses-const closeout.py:411, tip-no-len prune_refs.py:280

bus-nonce: 0c95b377dc2f414c36ff876e87cfa70c

Round 1 (first review of this PR; review scope full).

## Block

The PR's headline change is that `run()` uses the round's own closeout group, derived from the roster's name, in place of the `R10-CLOSEOUT-CLEANUP` constant. The self-test pins `self_group_for` and `roster_blockers` on their own. It does not pin the wiring that connects them to `run()`. Every `run()` arm in the self-test builds its roster as `tmp/wave-r10-groups.json` (`mk`, closeout.py:598-607). For that roster the derived group and the old constant are the same string. Reverting either production line below to the constant leaves all 46 checks passing:

- ctx-const: `self.self_group = self_group_for(str(a.roster_file))` -> `self.self_group = "R10-CLOSEOUT-CLEANUP"` (closeout.py:131): rc=0, SURVIVED.
- run-uses-const: `roster_blockers(c.roster, c.self_group)` -> `roster_blockers(c.roster, "R10-CLOSEOUT-CLEANUP")` (closeout.py:411): rc=0, SURVIVED.
- tip-no-len: `if read(batch) and len(batch) > 1:` -> `if read(batch):` (prune_refs.py): rc=0, SURVIVED. This one is equivalent: a failed one-sha batch is read once more and gives the same result. It is listed only because survivor_list.py requires every survivor.

What the fix owes: one `run()` (or `Ctx`) arm on a roster named `wave-r11-groups.json` that holds R11-CLOSEOUT-CLEANUP not-started and everything else done. It should assert that the dry run does not print `would REFUSE`. A null control should add R10-CLOSEOUT-CLEANUP not-started and assert that it is named. The ctx-const and run-uses-const mutants must then fail.

## Findings

- Follow-up: `dev/programme/HANDOVER.md:1643` documents the dry-run enumerator as `closeout.py --roster-file <roster> --repo ... --report-dir <dir> --verdicts-drained --successor <N>` with no `--orch-root`. At this head that command now exits 2 with `--orch-root is required`, so the documented command needs `--orch-root <dir>`. Carry: R11-CLOSEOUT-CLEANUP

## Notes

- Note: figure: the body says closure select gives "MODE: SCOPED, the two changed files". At this head it prints `MODE: SCOPED -- 0 script(s) run, 34 scoped out.` (ev/figures.txt). The changed tools are covered by the governance instrument-self-tests job, not by a closure script.
- Note: test-shape: the two `--orch-root` mutants the body names are killed, but by an uncaught `FileNotFoundError` on `wave-r10-groups.json` (relative to the cwd) that crashes the self-test, not by the named check "a run without --orch-root refuses (rc 2) naming it" failing (ev/mut-orch-refusal.log). Any kill counts, but the check would read more clearly if it ran from a temp dir with a real roster.

## Evidence

- RESULT head: measured 9ea84ecca8a8fd28c9bd8d8bdb325942a95888bd in a detached worktree (ev/HEAD.txt). The body names this head, plus authored code head c64b6c335c; the delta between them is the delivery row only.
- RESULT role currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- RESULT merge: `git merge-tree --write-tree origin/main 9ea84ecc...` exit 0, tree 9f70f68f83. Merges cleanly.
- RESULT self-tests at head: `closeout.py --self-test` 46 checks, 0 failed; `prune_refs.py --self-test` SELF-TEST PASS (82 checks). This matches the body's 46.
- RESULT mutants: 9 run, 6 killed, 3 survived (ev/mutants.txt, ev/mut-*.log). Killed: orch-refusal, orch-default, selfgroup-const, selfgroup-noraise, tip-no-retry, tip-return0. The body's two named mutants (tip_ages fallback, `--orch-root` refusal) reproduce as killed.
- RESULT figures (ev/figures.txt): the `orch-root` grep lists only tools/audit/seat/closeout.py, as the body says; `tests/structure.py` prints STRUCTURE RATCHET PASSED; VERSION, the manifest and RELEASE_NOTES.md are untouched by the three-dot diff (3 files: the delivery row, closeout.py, prune_refs.py).
- RESULT claims: no golden fixture or claim file is in the diff; production code is untouched, so env_drift is not engaged.
- RESULT finder's harness: none is named (an instrument fix built from carries); the self-test arms are the fixer's own.
- RESULT CI: `merge_train.py classify 9ea84ecc... --pr 3942` printed WAIT `pending: gate red: none` on every poll (ev/classify.log). The review packet's digest showed `governance / instrument-self-tests` and `tests / closures` still in progress at render. I stopped waiting because this block rests on test code, not on CI state. No owed red has concluded, so there is no `## Red checks` answer.
