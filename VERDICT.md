Fix review: merge b00a5d3ef97bc343a09116217b74a82b2c4190c9
bus-nonce: 5911fe815ebb26be3f0acbdd33d61656

Measured at `b00a5d3ef97bc343a09116217b74a82b2c4190c9` from a detached worktree at
`~/hpo-seats/r10s6/review-2888/wt`. Head re-read immediately before posting and unmoved. The PR is
a draft, base `a0e7664ea`. Cost run: reads, greps, one local Python driver, the API; no `prepr.sh`.

## The central claim — verified, not taken from the body

The file at this head says exactly what the body says it says. `## P211` now reads "The second arm
splits. The threshold raise alone is REJECTED", then "The lease half is ACCEPTED narrowed, into a
second carry of **R10-PREPR-CAP**", and the first arm is still "the one carried into
**R10-UPDATE-PR-SIGNALS**". No leftover of the old ruling survives: `grep -n 'twice over|resume.stage.*done|reopens it first'`
prints nothing and `grep -c updatedAt` prints 0.

The first carry is untouched in destination and in carried arm. Only its roster-state clause moved,
from `resume.stage done`/reopen to `fixing`/plain `append-carry`, and that re-derives: at
`origin/handoff/audit-r10-roster` (tip `8f7e252fe`) both `R10-PREPR-CAP` and `R10-UPDATE-PR-SIGNALS`
read `resume.stage: fixing`, and `R10-PREPR-CAP`'s `files` list holds `tests/gate_lock.py`.

## Citations — cited against measured at this head

| cited | measured | verdict |
|---|---|---|
| `tests/gate_lock.py:577` | 577 is `raise RuntimeError("no live gate lease to renew")` | exact |
| `:1119-1124` | 1119 `def _cmd_flock_wrap`; 1123 the `print(...file=sys.stderr)`; 1124 `return 1` | exact |
| `:53-56` | 53 "A pool slot is held for the LIFE of its run, not for its lease"; the quoted sentence at 55-56 | exact |
| `:861-877` | 865 `def flock_wrap`; 873 `except RenewRefused` | both inside; range opens 4 lines before the def and closes 1 before `return run_group` at 878 — precise enough, boundary loose |

The `:53-56` quote matches word for word; the source is RST (` ``LEASE_SECONDS`` `) and the entry
renders it in markdown single backticks. No line fails to say what it is cited for.

## #2854's body, read live

`gh pr view 2854 --json body` contains the quoted sentence verbatim — "were refused by
`tests/gate_lock.py` when the 30-minute lease lapsed inside the 85-minute run" — and the refusal
string verbatim: `gate_lock: flock-wrap refused, fix-2854-conflict holds no lease: no live gate
lease to renew`. Each appears exactly once. `updatedAt` appears 0 times in the entry.

## The gate that makes the entry load-bearing — re-derived

I drove `tools/audit/seat/roster_edit.py`'s `triage_refusal` myself; the driver is mine, at
`~/hpo-seats/r10s6/review-2888/probe/drive_triage_refusal.py`, and the gate it calls is the tree's.
Carry text: `triage P211 (V124): … triage: dev/programme/triage/s6-batch40.md#P211`.

| arm | body claims | measured |
|---|---|---|
| corrected file, P211 ACCEPT | `None` | `None` |
| same file, verdict changed to DEFER | refused naming DEFER | `'…/s6-batch40.md#P211 is not an ACCEPT ruling (DEFER)'` |
| same file, heading renamed | `no such entry` | `'…/s6-batch40.md#P211 is not an ACCEPT ruling (no such entry)'` |
| null control, text naming no proposal | `None` | `None` |
| unmodified main (pre-fix) | gate passes | `None` |

All five cells re-derive; none is a cell that had to be rebuilt to fit.

## Figures and controls

`git diff --stat origin/main...1ca755414` prints 1 file changed, 47 insertions(+), 14 deletions(-);
`git log --no-merges --oneline origin/main..1ca755414` prints the three named commits;
`git diff --stat 1a6365f16:<file> a0e7664ea:<file>` is empty; `grep -c R10-PREPR-CAP` is 0 on main
and 2 at this head. Every figure the body states re-derives.

## Delivery row

`dev/programme/delivery/2888.md` exists and equals `record_row.open_row_line(2888, "<PR title>
(R10-PREPR-CAP)")`. `GROUP_TAIL` (` \([A-Z][A-Z0-9.-]*\)\.`) fullmatches the suffix, so the merged
rewrite `_row_refusal` will judge at record time passes; the row names `R10-PREPR-CAP`, the live
group the ruling carries.

## Mergeability once undrafted

`git merge-tree --write-tree origin/main b00a5d3e` exits 0 with no conflict. `VERSION`, the manifest
and `RELEASE_NOTES.md` are untouched, and the diff carries no claim file, golden, budget, closure,
mutation-ledger or archscore file — it is two record files. The touched paths match no
`.github/CODEOWNERS` rule, so `hpo-approver` suffices and no owner review is owed. At the head read,
no check is red; `governance / delivery-status` and `tests / mutation` concluded success, and three
were still running. Nothing in the tree or body keeps this from merging once undrafted.

## Residual findings


- The body's Head paragraph says `b00a5d3e` "merges the authored code head `1ca755414` and then
  merges origin/main `a0e7664ea` … into this PR's previous head". Measured: its parents are
  `99ffeb11e` and `1ca755414`; `a0e7664ea` is only an ancestor, the parent of `2a92dd656`, and no
  commit in the branch merges it. The head SHA and all four figures still re-derive.
  Carry: dismissed: body provenance only, every number was re-taken
- The triage entry says "The first cut reached `main` as PR #2886 at `ee5816b1`". `ee5816b1` is the
  pre-image *blob* of the file, not a commit; #2886's merge commit is `a0e7664ea` (19:41:20Z, which
  the body's "19:41Z" matches). The blob does resolve to the first cut's text.
  Carry: dismissed: the blob resolves to the first cut's text, the merge commit is a0e7664ea
- The forward-carry to `R10-PREPR-CAP` is not yet on the roster at the cited tip `8f7e252fe`:
  `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json | grep -c P211`
  prints 0, and no first-arm text is there either. The body discloses this ("holds both of this
  batch's append-carry ops until this file is on main"), and it matches the demonstrated sequencing
  of batches 34 and 39, whose roster carries landed after their rulings merged. The carry text with
  its preconditions and null control is in this PR's tree, so the held op is the mechanical copy.
  Carry: R10-PREPR-CAP

## Not established

The three `updatedAt` readings the body quotes (18:23:17Z, 19:09:27Z, 19:39:04Z) are historical and
cannot be re-derived here; what is verified is the removal (count 0), not the sequence. I did not
re-read `R10-UPDATE-PR-SIGNALS`'s whole brief beyond the two files the entry names.
