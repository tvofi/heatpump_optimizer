Fix review: merge 1d0d17d78cc7bb20bd40c143c6831dede52f8693

bus-nonce: a4f814db6b343db6190c69114f88dd3d
reviewer: local-reviewer-s10
round: 2 (round 1 blocked carry-missing at 3d8f7c378)
measured: 1d0d17d78cc7bb20bd40c143c6831dede52f8693 (detached worktree); base origin/main eab04d0eb. Delta over round 1: six roster_edit set-stage ops 7c4acca07..86e101084 plus merge 1d0d17d78; 6 lines in the roster, each "done" -> "carries-open" (ev/delta.txt).

## Round-1 block: resolved
R10-FLY-OPENPR-ATOMIC, R10-FLOW-MAIN-GATE, R10-ORCH-REVIEW-PACKET, R10-TRAIN-OVERLAP-GRADE, R10-PREPR-CAP and R10-FLOW-BOARD read `carries-open` at the head, a stage roster_sync.py lists in PROTECTED_STAGES (self-test "a carries-open group with a merged PR is never overwritten"), so the next sync cannot re-derive them to done. The ACCEPT carries P227/P228/P229/P231/P234 and FLOW-BOARD's root-cause carry now sit on live groups.

## Re-run at the head
- merge-tree origin/main HEAD: rc 0, tree 72e4c9429 (head already contains main). brief_lint: rc 0, `TOTAL: 0 error(s) across 1 file(s)`, no error lines.
- Done commits on main: 138 done groups (144 less the six), 0 NOT-ON-MAIN under merge-base --is-ancestor (ev/done_check.txt).
- Triage citations unchanged from round 1 (ev/carry_triage.txt identical in citations): P223, P227, P228, P229, P231, P233, P234, P236 are "Verdict: ACCEPT narrowed" on origin/main.
- V149 (FLOW-BOARD): not blocking. Its ruling is a DEFER in s6-batch47.md, on open PR #2906 only, re-read at #2906's current head fb2f3de86: "DEFER -- owned by the red-check root-cause route on #2883 (R10-FLOW-BOARD ...)". The carry implements nothing from the proposal: it records the root cause #2883's second red check already owes under defect-root-cause.md's red-check trigger, which binds with or without a triage ruling, and the DEFER routes to exactly this group. Residual: the citation does not resolve on main until #2906 merges; if #2906 is re-cut to another route, this carry's "Source:" line must follow.
- Two live destinations: no carry has two destinations. Issue lists: the reopen puts #2717 (R10-ORCH-REVIEW-PACKET + R10-POLICY-ROLE-PACK) and #2719 (R10-FLY-OPENPR-ATOMIC + R10-FLOW-POSTMERGE) on two live groups each, as #2715 is on main. Each is a multi-arm issue whose groups own distinct arms (review packet vs per-role pack; open_pr atomicity vs post-merge bookkeeping), neither group lists either in `fixes`, and the new carries route to one group apiece -- so not one finding routed twice. #2505 stays an umbrella. (ev/dup.txt)
- Body: names head 1d0d17d78 and code head 86e101084; figures 212 215 3 0 25, 201/43 numstat, blob d1a915b7d, merge-tree fbfe4ade7 for eab04d0eb 86e101084 re-derive. Six-done/seven-carries-open stage account matches ev/done_check.txt.
- CI at the head: 6 queued, 1 skipped, none red (ev/checkruns.txt). This verdict carries the content; the required gate still has to go green before merge.

## Advisories
- The body's Head section has a second paragraph naming `4fd9402678030982d59cd708fe9088a2ee44155d` as a merge into the previous head; that commit exists but is not an ancestor of 1d0d17d78cc7bb20bd40c143c6831dede52f8693 (merge-base --is-ancestor rc 1). It reads as a leftover from an update attempt that was not pushed (the orchestrator's update script appends one per attempt). Not load-bearing -- the head and every figure re-derive -- but the line is false; drop it on the next body re-take. Instrument note for whoever owns the update script, not this PR.
- Cross-PR, #2896's reviewer: #2896 (head 73b1b4048) still adds carry-2733.json with the two items this batch moved into R10-ORCH-ROSTER-SCHEMA.
- R10-TRIAGE-S6 is done while #2906 is open, so that batch PR has no live group; its resume.pr / next_step are stale.
- Draft: content is ready; mark ready once the gate is green.
