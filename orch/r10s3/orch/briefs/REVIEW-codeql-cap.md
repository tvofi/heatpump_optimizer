# Fix review — R10-CODEQL-PR-CAP (analyze timeout 30 → 45)

Role: **fix reviewer**, adversarial. Read `dev/governance/roles/fix-review.md` and
`dev/governance/roles/COMMON.md` first. Repository `tvofi/heatpump_optimizer`. **LOCAL seat only — no cloud.**

Pull request: **#2516** (`handoff/r10-codeql-cap`), head `fccae47c41e773125960912cc74f34e70f91cb06`.
Body: `handoff-body/r10-codeql-cap` = `da8542d26d35f1b9af0ceab8d9d7042d52a23d1a`.
**The head will move once**: the orchestrator is adding the delivery row and recarrying main. Review the change now,
re-run only the delta at the post-update head (`gh pr view 2516 --json headRefOid`), and **hold the verdict** — the
`bus-nonce` follows at the final head, and `push-verdict` refuses without one.

Work in a detached worktree at the head you measure, under `/Users/timmalmstrom/hpo-seats/r10s3/r10-codeql-cap-review/`
(scratch, evidence and verdict there; absolute paths). `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`.
Long runs detached via `tools/audit/seat/daemonize.py --log`; the gate lease is shared and the box is loaded (load1
60+): prefer counts, state load1 beside any wall-clock figure.

## What this is

`.github/workflows/codeql.yml`'s analyze step `timeout-minutes` goes **30 → 45**, with a comment carrying the four
measurements that justify headroom against runner variance. `tests/entities.py` parses the YAML and refuses a cap
below 45.

## What to verify

1. **The change and its guard.** Diff the workflow; read the new entities.py check; confirm the check reads the
   workflow's YAML (not a copy of the number) and that 45 is the asserted floor.
2. **The mutation proof.** Set the cap to 30 in a detached copy and run `tests/entities.py`: the body claims
   `1 of 2360 ENTITY CHECKS FAILED`, rc=1. Restore 45: `ALL 2360 ENTITY CHECKS PASSED`, rc=0. Re-run both and
   show the counts from your own run.
3. **The null control.** The other caps (`cancel-superseded` 2, `scope` 5) unchanged at both ends; `structure.py`
   passes; `harness_headers.py` 109/109; archscore `dS +0.0000`. Re-run at least structure and the archscore
   diff and report what you measured.
4. **The four cited measurements.** The body names 30:19 (`2bd5e90f`), 30:09 (`4e5801eb` attempt 1), 30:07
   (`916431ae`) and success 21:31 (`4e5801eb` attempt 2, job 118701134345). Verify each against the run/job it
   cites, or say you could not and what that costs the claim. A timeout raised on one slow run without the other
   three is not the same justification as the four together.
5. **The body's honesty.** It records that the nine-minute extraction quiet stretch was not established (no local
   probe can time CodeQL's extractor) under Friction. Confirm nothing claims it was measured, and confirm the
   prepr re-run used `PREPR_SKIP_CLOSURES=1` legitimately (same head already green in the prior full run).
6. **Ownership.** The diff touches `.github/workflows/codeql.yml` — code-owned, so tvofi's approving review is
   required at merge; confirm the body says so. This is not a `*_budgets.json` raise.

Post the verdict with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>` once the nonce
arrives. No host path in the verdict (#2310) — write `~/…`. Report under 200 words: verdict line, each item
confirmed/not, what you could not establish.
