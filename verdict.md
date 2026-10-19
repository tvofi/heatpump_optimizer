Fix review: blocked b9f201f90efbb39422319426a7839c036b7b46af body-head-unnamed: ## Head names bef08da49, not this head b9f201f, and pr-contract run 117962608686 (started 08:28:44Z, after the body edit) refuses it with PR-BODY: 4 error(s); the same run also wants arch-score, env-matrix and validate-hacs named under ## Red checks

bus-nonce: b835f2fd79dc934f514517fb2402b581

Round 2. Head measured: b9f201f90efbb39422319426a7839c036b7b46af (ev/HEAD). At 08:31Z it was still the tip of `fix/r10-recarry-head-pr` (from `ls-remote`). Contract: fix-review.md at main. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current. Round 1 blocked this same head on carry-missing alone and verified the code. I did not re-take its RESULT lines (self-tests, M1 to M5, finder-shape rebuild, class grep): the tree has not moved.

## The block

The body edit fixed the routing. It did not fix the head the body names.

- `## Head` names `bef08da49`. The head is `b9f201f9`, two commits later:
  - `0378873ab` merges origin/main `c3530277`. Its only resolution is a set-merge of `tests/closures.json` (`LEDGER-MERGE: resolved`, `--remerge-diff`).
  - `b9f201f9` adds the record row `dev/programme/delivery/2442.md`.
- The figures probably still hold under the carry predicate, because that delta does not touch the fix. But the body records no carry note, and its text "origin/main's tip is its merge-base" is now stale.
- Local `policy_lint.mjs --pr-body ev/body.md --head b9f201f…` exits 1 (ev/pr_body_lint.txt). It reports: "`## Head` does not name b9f201f … b9f201f is not authored and committed as github-actions[bot]".
- CI's pr-contract run 117962608686 read the edited body and refuses on the same line (ev/pr_contract_117962608686_excerpt.txt, `PR-BODY: 4 error(s)`).
- Fix: a `## Head` note that names b9f201f and carries the figures. This is what `app_push.sh --recarry` or `update_pr.sh` write. It needs no code change.

## Red checks (step 11)

All six non-green completed checks are installation rate-limit or API-unreachable failures in the 08:00–08:04Z window. None is a test failure of this diff (ev/logs/):

- arch-score ×2: `gh: API rate limit exceeded for installation`.
- validate-hacs: `GitHubRatelimitException`.
- nightly-status: `NIGHTLY UNREADABLE … HTTP 403 (rate limit exhausted)`. It is unrequired.
- env-matrix: its one FAIL is `required-contexts … the GitHub API is unreachable`.
- pr-contract 117951683530 and 117953084773: rate-limited, before the body edit.

The body's `## Red checks` still says "none. No check has run on this head". That is now false, and pr-contract wants arch-score, env-matrix and validate-hacs named. The run that read the body lists only those three. nightly-status shows up in my local run only, and only because it was given no changed-path list.

I am not posting `root-cause-unanswered`: `closures` (117956369607) is still in_progress, so the head's workflows have not all concluded. The answer here is just to name each red as the rate limit, or to re-run them and drop them from the section. Either clears this part.

## Round-2 judgement of the routing

- RESULT carry_audit: `check --body ev/body.md` against `--roster-ref origin/main` (c3530277) and against `--roster-ref origin/handoff/audit-r10-roster` (f0fb8ae4) prints `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`, rc=0, in both runs. Adding `--comments` (round 1's verdict JSON) changes nothing. carry_audit.py is the same file at head and main (ev/carry_audit.txt). CI's pr-contract run agrees: `CARRY-AUDIT: 2 … 0 unrouted`.
- `## Forward-carry: none` is sound. The old item pointed to the INSTRUMENTS.md entry this diff itself adds, so it was not a finding for a later stage.
- The Friction `fixer.md` dismissal (one-off conflict) is sound. Four PRs rewrote the same lines, and no rule or wording change would have prevented it.
- The Friction `harness_headers.py` dismissal (slow locally, CI is authority) is sound for this PR. One caveat: I did not read the CI timing of harness_headers on this head, because the rate limit was in force. If one harness really runs for minutes, that is a D9/D13 question for that harness, not this group's.

## Other checks

- RESULT merge: `git merge-tree --write-tree origin/main(c3530277) b9f201f9` gives rc=0 with tree cb670a9e, the same as round 1 (ev/merge_tree.txt). No claim-file conflict.
- RESULT untouched: VERSION, manifest, RELEASE_NOTES.md, tests/golden and `*budgets.json` all have an empty three-dot diff (ev/untouched.txt).

## Notes

- Round 1's step-9 note is still open, and the body still does not address it. `r10_recarry_head.py` and the app_push arms are the fixer's own instruments, and no finder harness is committed for this group. Add one sentence saying so in the same body edit. Carry: R10-RECARRY-HEAD
- I made no GitHub writes. My last API reads hit the installation rate limit warning, so the check-run snapshot is from 08:31Z.
