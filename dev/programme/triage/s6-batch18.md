# Proposal triage, session s6, batch 18 (P87)

One proposal from the s6 `proposals.md`, S6-V22, filed 2026-10-24. Numbering
continues after `s6-batch17.md` (P86, #2761, unmerged at this base). GitHub calls: 0
for this ruling.

## P87: a dispatch row commit on a triage PR stales its body's Head (S6-V22)
Verdict: ACCEPT (no code) -> the orchestrator's triage-seat and dispatch-seat briefs: add the row through the existing `tools/audit/seat/update_pr.sh <branch> - <body>`, which already writes the matching `## Head` note. Candidate (a), a tool change, is unneeded because the tool exists. Candidate (b), triage writing its row before it opens, is REJECTED because the row needs the PR number.
Source: s6 `proposals.md` `## V22`.
Instances: 3, all on triage PRs opened by a bare `tools/pr/app_push.sh`, each followed by a dispatch commit `record: the delivery row for #<n>` that left the body's `## Head` naming the pre-row head:
- #2755: row commit 06cb984b; the review was blocked "body-head-stale" (verdict comment 6388572020) and the body was re-taken.
- #2758: row commit 7f91e684; pr-contract was red with "`## Head` does not name 7f91e68", and the body was re-taken on 2026-10-24 at about 20:45Z.
- #2759: row commit 5c824098; masked, because the triage seat pushed an amendment on top.
That is the third instance, so this is a barrier, not a note.
Cause, read in the tree at origin/main 0810d5b8f. The row has one writer, `delivery_row.sh` (`commit_row`, `ensure_row`), and the tracked openers pair it with the Head note:
- `open_pr.sh` opens, then commits the row and prefixes `## Head` through `head_note.py`'s `prefix` ("adds one commit to the previous head, containing only this PR's own row").
- `update_pr.sh <branch> - <body>` adds a missing row (`ensure_row`), prefixes the note, and pushes through `app_push.sh --row-only`, whose verdict accepts exactly "the live body under one new `## Head` note".
The triage seat opens with a bare `app_push.sh`, as its brief says, so its PR has no row, and the dispatch step then added one by a path that does not write the note. Every piece needed already exists; the slip is which instrument the two briefs name.
Cost: none in code. Two brief lines in the orchestrator's out-of-tree dispatch prompts:
- triage seat: "after `app_push.sh` opens the PR, run `tools/audit/seat/update_pr.sh <branch> - <body-file>` once, then cite the head it prints";
- dispatch seat: "a PR missing its row gets it through `update_pr.sh <branch> - <body-file>`, never a hand commit".
The row push costs one `--row-only` push (the body contract, not the full prepr).
Risk: low. The pushed head still moves after the opener, but the body moves with it in the same push, so pr-contract stays green. A review dispatched before the row lands would still be stale, which is why the row comes from the opener, before dispatch (`bus.sh dispatch` already refuses a head without its row).
Binding: 3 instances in one day, each a red pr-contract or a blocked review plus a body re-take (one cost a full review cycle), against two brief lines and no code. Candidate (a) would duplicate `update_pr.sh`'s note inside another writer. Candidate (b) cannot work, because `write_row` and `row_line` key on the PR number, which exists only after the open. If a fourth instance follows the brief change, the next step is mechanical: `app_push.sh` refuses to open a PR without then calling the row path, or the triage seat moves to `open_pr.sh`'s handoff route.
