# blocked 2de73776 wording: step 11 forbids cheap re-runs

# Fix review: PR #1792 at 2de73776da2c9f1d88f08a36e528394e4e749a68 (base 5dfa6684)

Round 1. Measured head 2de73776; policy prose only, no production or test line.

## Steps 12 and 13 compression (diff_5dfa6684_2de73776.patch)
- Step 12: "Step 7 is not this check ... compares the SHA in the body ... a branch that moved after the body was written passes it ... this one compares the live head at posting time" -> "Step 7 compares the body's SHA, which a later move passes; this compares the live head at posting time against what you measured." Same distinction, same obligation. Kept.
- Step 13: the descriptive "classifying by line shape instead is what fails" becomes the imperative "Never classify by line shape" (stronger). Kept: may-drift line is a # comment to `_comment_lines`, `merge_claim_defect` refuses when one is lost, the "only comment notes conflict" rule waves a real refusal through, the `claim-files.md` pointer. Dropped only explanation: the `_is_may_drift` name, the "everything before # is blank" mechanism, and "on a file with no bare claim lines on any side". None states a requirement; the absolute "never" covers that last case. Symbols verified at head: tests/env_drift.py:1516 `_comment_lines` (blank-before-# test), :1618 `merge_claim_defect`.

## Step 11 against tvofi's rule
- cite the head's CI run for gate and mutation table: present.
- only own targeted mutants and blocker checks: present (step 1 mutation proof stays, consistent).
- merge seat merges only on CI green at a head containing current main; if main moved, merge main and wait: present.
- "old local re-run exception removed": the 5dfa6684 file had no such text (grep for re-run/whole-tree/mutation_table finds only steps 1, 3 and the #713 control), so nothing to remove in the tree; the local re-run practice lived in seat memory (now marked superseded). The body's "Before" line describes practice, not this file's text. Not blocking.
- Nit (not blocking): the rule says cite the *green* run; the text says "the head's CI run". The red-check paragraph above already governs a red one.

## Merge state
git merge-tree --write-tree origin/main 2de73776: rc=0 (origin/main = 5dfa6684, head contains it).

## CI at head (cited, not re-run)
See CI section appended below.

## Blocker (tvofi clarification 2026-09-30T20:14Z: cheap checks may still be re-run)
Step 11 reads "Cite CI; never re-run it ... run only your own targeted mutants and the blocker checks". "Never re-run it" plus "only" forbids re-running cheap checks (brief_lint, one targeted test, claims, lint), which tvofi allows. The ban should cover only the full gate and the mutation table.

One-paragraph fix, same four lines (proposed_step11_fix.patch):

    **Cite CI's heavy runs** (tvofi, 2026-09-30): never re-run the gate or the
    mutation table; cite the head's CI run. Cheap checks (seconds: a lint, one
    test, claims) and your targeted mutants stay yours. The merge seat merges
    only on CI green at a head containing current main; if main moved, it merges main and waits.

policy_lint --budgets with the fix applied: rc=0, fix-review.md 140/140 lines, 2391/2393 tokens.

## CI at head 2de73776
Run 36770925905 (Tests): typing, briefs, mutation, browser, closures, closure-scope, nightly-status green; fast (3.14) gate, coverage, env-matrix still running at verdict time. policy-docs, pr-contract, delivery-status, budget-raise-gate green. Not re-run locally.
