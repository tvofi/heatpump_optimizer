Fix review: blocked 30c940e5b5e009ebe95004235cbab8536ea14799 ci-unconcluded: gate and pr-contract red on the GitHub installation rate limit, not on content; re-run owed, every content check passes

bus-nonce: 81bcd2478c31deaac2f0ee96f0942284

Round 1. PR #2864 "roster: round-10 batch 21", head `30c940e5b5e009ebe95004235cbab8536ea14799` (authored code head `94d14569ea32889e228c54fc082c62d968f254e0`), measured from a worktree detached at that head; merge base with origin/main `fe47636fbd03d5384880badca8691f9bb4add715`; origin/main at review `149ce54a36bcf9e794d357e0ef69dc8af62f8eb8`. Head re-read with `git ls-remote` before publishing: unchanged. Role contracts current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.

## Why blocked

Both red checks at this head failed on the rate limit before judging anything:

- `gate` (check run 121645482028, CI code run 40340824427): `RATE-LIMITED reset_epoch=1793026483 repos/tvofi/heatpump_optimizer/actions/runs/40340824427/jobs`, exit 3. The earlier `gate` (121644195406, CI edit run 40340824539) also failed with exit 3, after its `prelude` failed the same way.
- `pr-contract / pr-contract` (121645202051): `gh: API rate limit exceeded for installation` while fetching the body, then `FIGURES: /tmp/pr-body.md is unreadable` and `carry_audit.py` `FileNotFoundError: /tmp/pr-body.md`. So no `pr-contract` run has checked this body.

The reset epoch passed at 14:54:43Z. At 15:40Z no re-run of either job existed. Under `fix-review.md` step 11 I cannot grade the root-cause trigger while `pr-contract` refuses, and the body's `## Red checks` does not answer either red. I found no cheaper detector: the cause is outside the diff. Owed: re-run the failed jobs of run 40340824427 (and 40340824539). If `gate` goes green on the re-run, nothing in this review stands in the way of `merge`. That re-review only needs to read the re-run's checks, because the head and every content result below stay valid while the head is unchanged.

All other checks at the head are success or skipped (`ev/check_runs_head.tsv`), including `tests / briefs`, `governance / wave-script`, `governance / delivery-status`, `tests / closures`, `tests / fast (3.14)` and `governance / instrument-self-tests`.

## Content: passes

RESULT diff-scope: `git diff --stat <merge-base>...HEAD` touches only `dev/programme/rosters/wave-r10-groups.json` (+81 -243) and `dev/programme/delivery/2864.md` (+1). VERSION, the manifest version, the RELEASE_NOTES heading and both claim files are untouched (their three-dot diff is 0 lines). `git merge-tree --write-tree origin/main HEAD` exits 0 (tree `02a525c202330b258248eb0fe1bfc0f1f9db9ecc`).

RESULT commit-count: `git log --no-merges c8d51c464e84..94d14569ea32 -- dev/programme/rosters/` gives 166 subjects: 151 `roster: drop brief carry`, 2 `roster: drop carry`, 7 `append-carry`, 3 `set-resume`, 3 `roster_sync`. This matches the body.

RESULT provenance-drops 151 groups 68 bad 0. The instrument is mine, `ev/check_drops.py`; it is not the finder's, and this group has no committed harness. It is an independent re-derivation of the body's rule. For each drop commit it diffs parent against child, then requires four things:
- exactly one carry left;
- the dropped text, whitespace-normalised, is in that group's carry list at the first roster revision containing the group (topological walk over all 1510 revisions);
- `resume.stage` is `done` at the drop commit;
- `Merge pull request #<N>` is on origin/main.

Every row is in `ev/drops.tsv`. Controls:
- The two R10-RCA-ORCH-CONTINUITY drops come out `provenance False`, so the provenance test separates.
- The unmerged #2864 tests absent from the merged set (1143 PR numbers) and #2817 present, so the merged test separates.

RESULT delivered-sample: I read 23 drops in full, one per group: R10-FAHRENHEIT, VENT-DETECTOR, INPUT-STALENESS, TARIFF, DEEPLINK, LOOP-CPU, ADVISOR, LIVESTATE, PARAMS-OWNER, SOLVER, POLICY-LINT-STATS, STRUCTURE-BLIND, TICK-DRIVERS, REPLAY-LOOPNORM, REPLAY-SCOPED, DEAD-RATE-LIMIT, FLOW-ANDON, FLOW-DISPATCH, FLOW-RECORD-PITCH, FLOW-ARCH-PLANNER, ARCH-DOCS-FIRST, FLY-YIELD-GUARD and STRUCTURE-ALIAS. I also read every one of the 151 dropped carries that matches an obligation pattern (`owed|follow-up|once this lands|deferred|residual|later PR|next PR`); there are 21. Most carries are seat instructions consumed by the group's own merged PR (null controls, reviewer, merge order). For each obligation-bearing carry, I checked where it was delivered or is still held:
- FAHRENHEIT "a test with the target attribute absent is owed": #2285's body names the check "a degF climate with no target attribute is still written in degF".
- FEEDS D1 step 3, NIGHT-FOLDS D2 step 5, STALE-PATHS "35 evidence-only seams": #2631 lists all three ("D1 step 3", "D2 step 5", "R10-N-move-stale-path RCA records the owner's confirmation of the 35 evidence-only seams").
- LIVESTATE and PARAMS-OWNER "mutation-ledger re-key and quiet-window stress re-take": #2675 item 12 and #2817 Carry 3 discharge them.
- PARAMS-OWNER P1b seal and UX-SETUP / RATIO-ANCHOR "leads, not owed": recorded as not owed.
- VENT-DETECTOR G-ID-5: still held by the roster's top-level `G-ID-5` deferral entry at the head.
- I1 "RCA owed by the class issue": #2219 is CLOSED, and `fold_ledger.py check` at origin/main prints 0 violations across 46 classes and 123 rca entries, so that mechanism still enforces the barriered class.
- FLOW-BODY-PATCH revision 14 ("run the body contract before the PR is created"): `tools/pr/app_push.sh` runs `prepr.sh` before it POSTs `/pulls`.
- FLOW-DISPATCH R15 "three standing trigger prompts": the harness's seat definitions (opus-fixer, sonnet-seat, haiku-seat) exist and this seat runs as one. This is out of tree, so it is evidence of delivery, not a tree record.
- FLOW-PULL "owner rulings owed": #2628 carries the policy under the owner gate and mandate it names.
- FLY-ENVMATRIX-NOREMOTE, FLY-NO-FOOTERS-EMITTERS, STRUCTURE-ALIAS: the group's own scope. #2711's title and body cover the getter plant ("census bare getters").

No drop removes an unlanded finding.

RESULT non-provenance-drops 2, both justified in the body:
- `503685300ee4` (RCA carry 0): the same text, prefixed "From R10-RCA-ORCH-CONTINUITY (rerouted to R10-ORCH-BEATD, orchestrator ruling 2026-10-26):", was appended to R10-ORCH-BEATD by `f082177a4d88` (an ancestor of the drop). It is present at the head.
- `7a56d6b3f15d` (RCA carry 1): decision 0012 is revoked. `0012-process-diet-and-round-cadence.md` line 4 reads "Revoked by decision `0014-...`", and 0014 line 26 reads "0012 is revoked". R10-RCA-ORCH-CONTINUITY is `done` with 0 carries.

RESULT resume-edits 3, of which 2 overwrote a note. The body names both prior notes, and neither loses information:
- R10-FLOW-JIDOKA's `rca: topic r10-rca-body-check-parity`: the RCA is on main (`dev/audit/rca/R10-RCA-BODY-CHECK-PARITY.md`, 11 lines naming JIDOKA), and a JIDOKA carry at the head cites it.
- R10-FLY-ROW-HEAD-CARRY's mandate-6319294694 registration: the group's `owner_gate` still reads "mandated approval under 6319294694".

R10-996-RUNNER-CLAIMS's prior note was `null`, so nothing was overwritten.

RESULT roster_sync: the three commits change only what the body lists. Stages: R10-MERGE-SUBJECT-HARDEN, R10-FLY-DEPGRAPH-STALE, R10-996-RUNNER-CLAIMS and R10-RCA-RATELIMIT-RECUR move to done; the others move to in-progress. Carries: R10-MERGE-SUBJECT-CASEARM +4, R10-ARCH-SHAPES-CLASSIFIER +2, R10-RECORD-API-O1 +3, each a `Carry:`-marked forward-carry of a merged PR.

RESULT brief_lint: `node tools/policy/brief_lint.mjs <head roster>` exits 0 with "TOTAL: 0 error(s) across 1 file(s)", both from an origin/main checkout and from the head checkout (`ev/brief_lint_*.txt`).

RESULT body-check: `tools/pr/prepr.sh --body-check` on the body as read exits 0: "PR-BODY: 0 error(s)", "CARRY-AUDIT: 0 finding item(s)", "preflight ok" (`ev/body_check.txt`).

Steps 1-4, 6 and 14: not applicable. The diff writes no production, test or instrument code and moves no budget, closure, golden or claim; it is roster state only.

## Non-blocking

- R10-ARCH-SHAPES-CLASSIFIER now holds the same two #2843 findings twice. `roster_sync` commit `1ec8c7259144` added them as carries 0-1 (suffix "Carry: R10-ARCH-SHAPES-CLASSIFIER"). Appends `32d783569a2a` and `c39e46bc6e47`, made after it, added them again as carries 2-3 (prefix "From #2843 ..."). The texts agree, so no reader gets two versions, but the body's "0 to 4" reads as four findings where there are two. `roster_edit.py append-carry` did not refuse a carry whose text an existing carry already contains. Carry: R10-ARCH-SHAPES-CLASSIFIER
