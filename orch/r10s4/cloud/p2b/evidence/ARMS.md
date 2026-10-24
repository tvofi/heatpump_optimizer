# P2b live arms for the probe-runner (coordinator: p2b-coord seat)

Binding: plan `1011d6b2f:plans/ci-layout/EXECUTION.md` §2 (rows 4-7, 9, 10 and 12 are yours), DESIGN-P2 §10 (tag `archive/probe/design-ci-rev4`).

Rules for every arm:
- At most 4 probe PRs open at once. All drafts. Topic `r10-ci-layout-p2-probe-<arm>`. The body says "PROBE, throwaway draft, closed unmerged" and "Part of #2495" (no closing keyword).
- Poll no faster than every 60 s. Stop and tell me on any 403 or 429, or when the rate limit is under 20 %.
- Held runs: `tools/pr/approve_held_runs.sh` (it lives under tools/pr, not tools/audit/seat). Run it after every App push. FIRST, for M-3(a), list `actions/runs?head_sha=<H>&status=action_required` before approving, and record the count.
- Write one `probe-runner-<arm>.txt` per arm here. Record the PR number, each push SHA, each run id, its `display_title`, and every job's name and conclusion (`jobs?filter=latest`). For each `gate` job, also record its step-summary line (PASS or FAIL and the reason).
- Close every probe PR when its arm has been read (row 12).
- Review submits and dismissals are NOT yours. They are owner-account writes under row 11. When an arm needs one, write `probe-runner-<arm>.REVIEW-NEEDED` naming the PR and head, and SendMessage me. I relay it to main.
- I do the dispatch-only arms myself (U0 perturbations by dispatch, U1-U3 and U5 dispatch pairs). Do not duplicate them.

## Arm A: U0 events on a draft PR (ref `ci-probe/u0c`, already pushed = `65f112ec51dfa1f3d1617dda2bac74adab394eda`)
Cut ci.yml: prelude + one `probe` unit + refresh + gate. The base restores are removed, so the probe runs its own `tools/ci/`. Its gate requires only `probe / probe`. Main's standalone workflows also fire on this PR; ignore them except for M-3.
1. Open a draft PR from `ci-probe/u0c` to `main`. Expect: the `CI code pr=<N> base=main sha=<merge sha>` run's `gate` is success with summary PASS. Record whether the `sha=` token equals `refs/pull/<N>/merge`'s commit (item 7).
2. M-3(a): the count of held `action_required` runs at the head after the App push, before approval.
3. Edit 1 s after a push (item 5). Push a trivial commit (a comment line in `.github/workflows/probe.yml`), then within about 1 s patch the PR body (`body_patch.sh`). Expect two runs, `CI code …` and `CI edit …`, both completed and neither cancelled. The edit run's `gate` PASSes and its summary names the code run's id as the `probe` source.
4. M-5(b): while a newer code run is in progress at the head, re-run a COMPLETED run's `gate` job (`ci_probe.py rerun-job <job id>`). Expect the newer run unaffected (conclusion read back), and the re-run attempt in its own `CI-<run_id>` group.
5. M-7: during step 3's code run, list `jobs?filter=latest` once while `probe` runs. Record whether `gate` appears before its needs finish.
6. M-4: record the check names (`probe / probe`), and whether a SKIPPED `uses:` caller writes a bare `probe` check run. To get one, use an edit run, whose workset omits `probe`.
Record everything in `probe-runner-A.txt`, then close the PR.

## Arm B: the combined control (DESIGN-P2 §10 "final combined null control")
- AFTER: draft PR from `ci-probe/all`. I will name the exact SHA when U10 and U9b+U9p are assembled. Do NOT open it before I send the SHA.
- BEFORE twin: draft PR from `ci-probe/all-before` = origin/main plus one comment line in `tests/closure.py`, so FULL scope fires as it does on AFTER. I push this ref and send you its SHA.
- Steps 1-4 of §10's combined control, as I list them when I send the SHAs. They include U6 cases 1-7, U7's D-2 plant, the U8 review submit and dismiss (owner, via me), a retarget (`ci_probe.py retarget`), and the bot-head dispatch.
Wait for my message before opening anything in Arm B.

## Not yours
- The U0 dispatch perturbations (forced red, `if: false`, unit removed): already running from `ci-probe/u0c-red`, `-skip` and `-absent`.
- The U1-U3 and U5 dispatch pairs.
- sweep_driver arms M-6: I run them on Arm A's PR after step 3. Tell me the PR number as soon as it is open.

## Arm B -- the final combined null control (DESIGN-P2 section 10, "The final combined null control")
Refs (coordinator-pushed; do not edit them): AFTER `ci-probe/all` = ff7244ac0 (was 4319b06a0; prepr refusals fixed) (the full assembly on current main);
TWIN `ci-probe/all-before` = 69a9279a5 (main 57b7b4994 + a comment in tests/closure.py; FULL scope on both).
Open: two DRAFT probe PRs via open_pr.sh, topics r10-ci-layout-p2-probe-B (AFTER) and r10-ci-layout-p2-probe-Btwin.
Body: "PROBE, throwaway draft, closed unmerged", "Part of #2495", no closing keyword; delivery row as for Arm A.
No probe cut: AFTER carries the full REQUIRED. Expect prepr to run the full gate set; report any refusal verbatim, no bypass.
Coordinator runs sweep_driver --nochain against the AFTER PR before the first event (step 3), --chain for M-6's rerun.
Step 3 events on the AFTER PR, in order, each logged (UTC, run ids) to evidence/armB-events.txt:
  3a body edit 1 s after a push (App path) -- both runs complete, no code run lost
  3b review submit then dismiss on a budget-raising branch: relay to coordinator (owner write; U8's probe)
  3c retarget (base -> ci-probe/base and back) -- refresh turns the old green gate red, new code run decides
  3d a commit that breaks `briefs` -- gate FAIL naming `tests / briefs`; then revert it
  3e a review while a retarget's code run is in flight, then a second review after the first review run's gate is green (relay)
  3f an edit and a review 1 s apart during a code run -- every gate at the head ends green
  3g M-6's sequence again (push, edit, review relay)
Step 4 (bot head): coordinator dispatches `ci.yml --ref <AFTER branch> -f pr=<n> -f base=main`.
The TWIN gets the same push(es) as 3a only; its pull_request runs are the BEFORE union for step 1.

### Arm B split (main, 2026-10-23 ~08:05Z): two AFTER drafts, one twin
Both drafts are cut from the SAME ci-probe/all head (ff7244ac0) and pair against the SAME twin ci-probe/all-before (69a9279a5).
B1 topic r10-ci-layout-p2-probe-B1: 3a, 3c, 3e, then 3b.   B2 topic r10-ci-layout-p2-probe-B2: 3d, 3f, 3g. Step 4 (bot head) on B2 last.
Independence -- no event in one group reads state an event in the other writes:
  3a (B1) push + edit 1 s apart: writes B1's head and body; reads only B1's runs at B1's new head.
  3c (B1) retarget and back: writes B1's base; refresh reads B1's own gate runs; B2's base is untouched.
  3e (B1) review during 3c's in-flight code run, then a second review: DEPENDS ON 3c, so it stays on B1 after 3c.
  3b (B1) budget-raising commit, review submit then dismiss: writes B1's head and reviews; reads B1's budget-raise-gate only.
  3d (B2) a commit breaking `briefs`, then its revert: writes B2's head; reads B2's gate (FAIL names tests / briefs).
  3f (B2) edit and review 1 s apart during a code run: needs a run in flight on B2 (3d's revert push supplies it); reads B2 only.
  3g (B2) M-6's sequence (push, edit, review): writes B2's head, body and a review; reads B2's runs only.
SHARED STATE, the one coupling: until each draft's first push both PRs head the same SHA, and check runs attach to the commit, so each PR's
merge box reads both PRs' suites. Each group therefore starts with a push (3a on B1, 3d on B2), which diverges the heads before any judged event.
The opening runs at the shared SHA are the same_sha_dup_heads reading (carry 1), not an event.
#2649 is closed right after M-5b/M-7 so at most 4 probe PRs are open (B1, B2, Btwin + one).
