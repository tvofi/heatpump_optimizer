Fix review: blocked b63829d1c163aff58823157d7691894f46301ae5 ci-red: governance / instrument-self-tests fails selftest_wiring --check on this diff's own instrument page (MISMATCH cancel_superseded.py.md), and the body says the red is not this program's

bus-nonce: fec93b3aefb0b6478b701e34a8a73f3b

Round 3. Previous reviewed head 4cd6cac6495a2d7ac1a452fad6bc8e9eceef1c75 (blocked at verdict/3004 07f1ef8e3, mutation-vacuous on sweep-main-skip). I reviewed from a detached worktree at b63829d1c163aff58823157d7691894f46301ae5, and the delta 4cd6cac6..b63829d1 is the fixer's 041e2c80f plus two automatic merges. The empty three-dot diff on dev/governance/roles/ shows the contract is current. From round 4, fixer.md owes a re-cut rather than a repair. The fix this block needs is a single line in a doc page, though, and the orchestrator decides whether that counts as a re-cut.

## Block

`governance / instrument-self-tests` was red at the previous head 4cd6cac6 (run 41106825228, job 124238884919). The failing step was "Refuse a self-testing seat instrument that no step runs" (governance.yml:494-499), which runs `python3 -I tools/audit/seat/selftest_wiring.py --check`. The cause is this diff, and it reproduces deterministically:

- `selftest_wiring.py --check` exits 1 with `MISMATCH tools/audit/seat/instruments/cancel_superseded.py.md: the index line's name is not the one its entry opens with`. It does this at this head, at 4cd6cac6, and on the merge tree with origin/main (5f065ed1ac).
- It exits 0 with `0 index gap(s)` at origin/main 437f1ba9b (ev/selftest-wiring.txt).
- The index rule (selftest_wiring.py `index_gaps`, lines 110-134) compares the first backticked name of the label on the new index line, INSTRUMENTS.md:89 (`cancel_superseded.py sweep`), with the name its entry file opens with. The entry file opens its first bullet with `python3 -I tools/pr/cancel_superseded.py sweep ...`, so the two names differ.

Nothing in the round-3 delta touches either file, so the same step will fail at this head when the job reaches it. The job was still in progress when I read it (ev/checks-at-head.txt). The brief requires this red to be green or answered at this head. It is neither:
- The body's `## Red checks` says "Cause not established ... Not shown to be this program ... Cheaper detector: none identified".
- `## Prepr` says "No red check at this round".
- The first two statements are factually wrong. The cause is this PR's own page, and a cheaper detector exists: `python3 -I tools/audit/seat/selftest_wiring.py --check`, which takes seconds, is deterministic, and has no network cost. The scoped prepr evidently did not reach it.

The fix needs two things:
- Make the entry file and the index line agree, for example by matching the index label's first backticked name to the name `cancel_superseded.py.md` opens with, or the reverse. Then re-run `selftest_wiring.py --check` to `0 index gap(s)`.
- Rewrite `## Red checks` with that cause and the cheaper detector, per defect-root-cause.md.

No production change is needed.

## Findings

- defect-root-cause.md owes a root-cause answer for the instrument-self-tests red. The red is detectable by a check that costs seconds (`selftest_wiring.py --check`), yet the scoped `prepr.sh` passed "all ok" without running it, because a new file under tools/audit/seat/instruments/ plus an INSTRUMENTS.md line did not draw it into the scoped run. The fixer's body has to name this, and the countermeasure, or record a refusal, goes beside the fix in its own seat. Carry: R10-FLY-CANCEL-SWEEP
- tools/pr/cancel_superseded.py is code-owned, so @tvofi's approving review is needed at merge. This is flagged as the brief asks and does not block. Carry: dismissed: the merge gate is the code-owner review, not this seat
- The body's figure in `## Red checks` is stale: it says "now 43 checks, 0 failed here", but this head gives 44 checks, 0 failed (`## Figures` gives 44 correctly). It should be corrected in the same body rewrite. Carry: R10-FLY-CANCEL-SWEEP
- The round-2 non-blocking finding `commit-only-cancel-prs` (commit-read cost bound unpinned) is carried by the body to Part 2, as the brief scopes it. I did not re-litigate it. Carry: R10-FLY-CANCEL-SWEEP

## Evidence

- RESULT: the round-2 survivor is now killed. At this head, dropping the `b == "main"` disjunct from sweep_plan gives `44 checks, 1 failed`, and the failing arm is "sweep: a PR-event run on main is skipped by the branch test alone, not a ghost, never cancelled" (got (0, [93, 94], [101, 102]), want (2, [], [101, 102])). The same mutant at 4cd6cac6 gives `43 checks, 0 failed`. The restored tree gives `44 checks, 0 failed`, and the worktree is clean after the restore (ev/mutant-main-skip.txt). The body's round-3 mutation claim matches these numbers.
- RESULT: `selftest_wiring.py --self-test` gives 26 checks, 0 failed at every tree checked. `--check` exits 1 at head, at the old head and on the merge tree, and exits 0 at origin/main (ev/selftest-wiring.txt).
- Merge: `git merge-tree --write-tree origin/main b63829d1c163aff58823157d7691894f46301ae5` exits 0 with tree 5f065ed1ac, no conflict, and no claim-file driver invoked. The remerge-diffs of 9800ed8ca and b63829d1c are empty, so both are clean automatic merges. review_carry 4cd6cac6 -> head prints FRESH-REVIEW, as expected for a new branch commit (ev/merge.txt).
- VERSION, the manifest, RELEASE_NOTES.md, the claim files and every *_budgets.json are untouched in the three-dot diff.
- Head: the body's `## Head` names b63829d1c163aff58823157d7691894f46301ae5, the head I measured.
- Part 2 disposition: the body still routes roster carry 9e7ba7aae (tier module, config file, train pause/resume) to R10-FLY-CANCEL-SWEEP PART 2 under mandate 6329234399, unchanged from round 2. I accept it as round 2 did. The packet's carry_audit reports 1 routed, 0 unrouted.
- Review packet: no refusals and no advisories. figure_lint resolves 3 of 3 figures. The finder's harness is "none named" (an instrument group), and I built no harness beyond the mutant and the selftest_wiring runs (ev/review-packet.md).
- CI at head, read from the check-runs API (ev/checks-at-head.txt): no run had concluded red yet. instrument-self-tests, env-matrix, browser, fast, closures, coverage, codeql python and the edit-run prelude were in progress, so I did not see their conclusions at this head. The instrument-self-tests outcome above is my local reproduction on the merged tree, not CI's conclusion. No prelude or pr-contract red from an HTTP 502 was seen.
