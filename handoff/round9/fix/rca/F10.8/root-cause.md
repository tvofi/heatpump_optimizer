# R9-F10.8 root cause: "merging main erases another lane's claims"

Seat: root-cause (`tools/audit/briefs/root-cause.md`), opus, beside the R9-F10.8 fixer.
Measured at main `f67f598a` (#1806 F6.4 merged). Roster entry read at `2eaa8c77`.
Reproduction: `repro.sh` and its output `repro.out` sit next to this file. They run in a
scratch worktree and touch nothing remote.

## Verdict

**The reported defect does not exist. The claimed cause is wrong in the direction that
matters** (root-cause.md §1, second trap). A solver-claimable branch that merged a
claiming `main` *must* drop that main's claim lines. Main's own push run requires it,
and dropping them loses nothing any consumer reads. The class's real harmful variant,
a branch that cannot move a claimable fixture rewriting the list, was closed by #662
and #747 and stays closed (R5 below). The roster's prescribed fix ("a branch whose claim
files are byte-identical to the main it merged must pass") would turn main red at the
next merge, and it would reopen the carried-claim hole that `inherited_claims_error`
exists to close.

What actually failed is the diagnosis, not the gate. The refusal text and the rule
wording describe a mandatory step in the language of a loss. That is process state (c),
and the countermeasure is a zero-cost message and wording change (§5).

## 1. Mechanism, reproduced

A claim line describes **one diff**: the PR's diff against its merge base, then the
merge commit's diff against `HEAD^1` on main's push run (`tests.yml` "Resolve the golden
comparison ref": a PR uses `git merge-base origin/<base> HEAD` plus `CLAIM_HEAD`, and a
push to main uses `HEAD^1`). The stamp states the lifecycle in the file it writes
(`tools/release/stamp.py` `rewrite_claims`): *"The stamp empties the list; the next
branch restates its own footprint."*

So once #1806 lands, main's list describes the step `f67f598a^1 → f67f598a`. A branch
that merges `f67f598a` gets a new merge base, `f67f598a`, and with it a diff that does
not contain F6.4's step. F6.4's lines are not claims about that diff.

| run | shape | result |
|---|---|---|
| R1 | solver branch cut at `f67f598a^1`, merges `f67f598a`, keeps the 5 lines; PR check (`CLAIM_HEAD`, ref = merge base) | `INHERITED CLAIMS` |
| R2 | R1's branch merged `--no-ff` into `f67f598a`; main push check `--claims-only HEAD^1` | `INHERITED CLAIMS` (**main red**) |
| R3 | R1 after `--drop-inherited f67f598a`; PR check | ok |
| R4 | R3 merged into main; main push check | ok; the delta to main is `claimed_drift.txt` −5, card file untouched |
| R5 | null control: docs-only branch that merged `f67f598a` | PR check ok; autofix `skip-moves-nothing-claimable` |

R4 also shows that the per-file-kind rule (#747, `claim_kinds`) holds: a solver-only
branch leaves F6.4's five card claims exactly as found.

**What the drop costs, by consumer.** I checked each place that reads the claim files
after a merge:
- **Main's push run of #1806** already ran at `f67f598a` and does not re-read the file
  at a later commit.
- **The stamp** deletes every bare claim regardless (`rewrite_claims`), and stamp rule 7
  checks `--claims-only HEAD^1`, which is R2/R4's shape.
- **The goldens** are not a to-do list kept in the claim file: #1806 committed its own
  re-recorded `coord_*.json` (`git show f67f598a --stat`).
- **The record** stays in git at `f67f598a`.

Nothing in that list loses information.

**Base rate.** This is routine, not an incident. Since 2026-09-17, **43 of 351**
first-parent commits on main added claim lines (enumerator:
`count_claimers.sh f67f598a`, next to this file). Branches carried **47** commits matching
`drop.*inherited|inherited claims`, **17** of them the `claims-autofix` bot's
`ci: drop inherited claims`:

```
git log --all --since=2026-09-17 --oneline -i --grep='drop.*inherited\|inherited claims' | wc -l
git log --all --since=2026-09-17 --format=%s | grep -c '^ci: drop inherited claims'
```

## 2. Why the prescribed fix is wrong

"A list byte-identical to the merged main's passes" fails on both of the gate's
invariants:

1. **Main's push run.** After merge, `HEAD`'s list equals `HEAD^1`'s, so R2 is red. A
   rule that also exempts that shape cannot tell "carried by merge" apart from "written
   for this diff". On main, every commit's list is "byte-identical to what it merged".
2. **The carried-claim hole (#213; v4.0.7, v4.2.0 and v4.3.0 failed main with inherited
   lists).** A claim excuses drift **by scenario name**. F6.4's carried
   `coord_minimal`/`coord_dhw`/… lines would silently excuse any drift #1808 or #1809
   causes in those fixtures. That is the exact failure `inherited_claims_error`'s
   docstring names: "whatever it excuses here, it excuses by accident". *Inferred from
   `_claimed`/staleness code. Not run: it needs an `--all` capture, about 20 min, which
   the brief forbids repeating.*

In the same `--all` run, carried lines also match no drift against the new merge base.
They are stale, and `stale_claims_judged` judges them for a solver branch, so the PR
goes red there too. This is also inferred from the code and was not captured.

## 3. Why the earlier fixes "didn't close the class"

They did close it. The roster mixes two cases that the code already treats differently:

| case | correct action | fixed by |
|---|---|---|
| a branch that **cannot** move what a claim file excuses (docs/roster/policy, or a solver branch facing the card file) rewrites or empties that file | refuse; leave the file exactly as found | #662 `2d06e065` (`record_pr_claims_error` "left exactly as found", autofix `skip-moves-nothing-claimable`); #747 `0e43448b` (`claim_kinds`, `foreign_claim_file_error`); `66998520` |
| a branch that **can** move what the file excuses merged a claiming main | drop the carried lines (`--drop-inherited`, or the bot) | working as designed, 47 times since 09-17 |

#608 (`2b5e4167`, policy linter) and #635 (`dda71933`) were the first case, and so was
#658, which was stopped in time. The 2026-10-01 events on #1808/#1809 (`c447cf9d`,
`5ef09d8a`, "claims: drop claims inherited from main f67f598a (#1806)") are the second
case. **They are not instances of the #634 class**, so the class count stays at the two
real instances plus one stopped, all barriered by #662/#747. No new barrier is owed
under `defect-root-cause.md`'s audit-class clause.

## 4. Process state: (c), followed and misled

The process: a seat reads the gate's refusal and the rule text, then classifies.
Both were followed, and both pointed at "loss":

- The `INHERITED CLAIMS` message says the list was "written for the baseline's diff
  and carried forward". It never says that a merge of the baseline is how a list gets
  carried, or that dropping is safe and required.
- `apply_inherited_claims`'s comment ("the emptied file squashes onto the baseline and
  deletes another lane's claims (#608, #635)") and `record_pr_claims_error`'s docstring
  call deletion harmful. Neither says this holds only for a branch that cannot move the
  file's fixtures. `claim-files.md` and `ci-autofix.md` never state the lifecycle.
- The roster entry (`2eaa8c77`) then cited those same instances, #608 and #635, as
  precedent.

This is not state (b). Nobody skipped a step, and a firmer instruction to "check the
premise" would change nothing, because the text the seat checked against says the
wrong thing. It is not state (d) either. Nothing changed underneath the process: merge
commits, `CLAIM_HEAD` and merge-base re-pointing (#1359–#1361) all predate the 43 routine
cases.

## 5. Invariant and countermeasure

**The invariant the gate already enforces, and should state:** *the bare claim lines
at any commit X describe exactly X's diff against the commit it is judged against (its
merge base on a PR, `HEAD^1` on main), restricted to the file kinds that diff can
move.* Corollaries:
- Lines from an earlier merge are dropped by the next branch that can move that kind.
- A branch that cannot move that kind leaves them untouched.
- The stamp clears them all.

**Countermeasure (addresses state (c)). Rescope R9-F10.8 to this, and drop the
byte-identical fix:**

1. **Message.** When `inherited_claims_error` fires and the claim file's blob at
   `CLAIM_HEAD`/`HEAD` equals the baseline's blob, so the branch never authored it,
   print a distinct lead line: `CARRIED BY MERGE: these are <baseline>'s own claims,
   brought in by merging it. They describe that merge's diff, not this branch's. Run
   tests/env_drift.py --drop-inherited <ref>; main's push run requires the drop and no
   consumer loses anything.` Keep the exit code at 1. R2 proves passing would only move
   the red to main.
   - It must still refuse a branch that **copies** main's list as its own, which has a
     different blob or authored commits. That refusal is the null control.
   - Demonstrate: R1 prints the new line, R3 passes, and a copied list keeps the old
     message.
2. **Wording.** Reword the comments in `apply_inherited_claims` and
   `record_pr_claims_error` to scope "deletes another lane's claims" to the
   cannot-move case. Add the lifecycle invariant above to `claim-files.md` in one
   paragraph.
   - This is policy text and needs tvofi's approving review, under the mandate.
   - `ratchet-budgets.md` caps the policy corpus, so pay for the paragraph by cutting
     elsewhere first.
3. **Propagation (`finding-propagation.md`).** Amend the R9-F10.8 roster `brief`
   before any F10.8 PR merges, and record in `docs/HANDOVER.md` that a solver branch
   dropping carried claims after merging main is routine. #1808 and #1809 keep their
   drop commits as they are.

**Cost test.** Both sides are in wall-clock per occurrence.
- **Standing cost.** One extra blob comparison per `--claims-only`, which is
  milliseconds and well under 1 s per run. The wording adds no runtime.
- **Defect cost.** One misdiagnosis this cycle cost one roster entry, an opus fixer
  seat, this opus RCA seat and a pending opus review. That is several seat-hours; I
  did not measure the seats' wall-clock. Each routine manual drop also costs a seat a
  refusal and a re-push. The rate is one misdiagnosis in 47 drops over 14 days.
- **Result.** A cost near zero beats any positive expected loss, so build it.

**Alternatives considered and refused:**
- *Auto-drop inside the claimnotes merge driver.* The driver cannot know whether the
  branch's diff can move the file's kind, and dropping on a docs branch is exactly
  #662's refusal.
- *Pass carried lists.* §2.
- *Move claims out of the tree.* Too large for the bound in `defect-root-cause.md`.

## 6. Class search

I checked whether the same message-versus-lifecycle gap exists elsewhere. `UNDER-SCOPED`
and unpinned-mutant autofixes (`ci-autofix.md` table) are also "routine repair, alarming
text", but each one's message already names the bot and its subject line, and none
asks a seat to delete another PR's lines. I found no other instance.
