# Proposal triage, session s14, batch 187 (P609)

The bar and the denominators are batch 141's.

Sources:
- origin/main `cbd23f1c8b`. Every line number below is at that commit.
- The live train log (`merge_train` state directory, `train.log`), and its `queue-add.jsonl`.
- The merge seat's relaunch queue file, `q-relaunch.json`, read at 11:20Z.
- `gh api issues/3425/events`.

## P609: TRAIN-UNDRAFT-EVERY-ROUTE

Verdict: ACCEPT, as a carry on R10-TRAIN-RESIDUE-P2. It sits beside P608 in the same file. The
seam is distinct: P608 is the policy-refusal reader, and this is the admission draft flag and
the merge retry loop. The group is still not-started, with no `*train-residue-p2*` ref.

Source: queue line 288, 2026-11-11T11:13:55Z, orchestrator s14.

Instances:
- **Wasted merge attempts.** Command: `grep -E 'merge attempt .*still a draft' train.log`, counted
  per PR.
  - Result: 78 refused attempts over 8 PRs: #3318 16, #3381 8, #3382 8, #3387 8, #3388 8,
    #3392 8, #3400 2, #3425 20.
  - Each full loop of 8 sleeps 30 s between attempts, about 3.5 min, and re-grades the merge
    tree at each guard.
  - #3425's 20 attempts also burned 2 of its 3 MAIN-MOVED recarries.
  - If the claim were false, the count would be 0 or 1 per PR: undraft once, then merge.
- **The route that skips undraft.** `undraft()` (`:1349-1361`) acts only on `item["draft"]`. That
  flag is set in one place, `add` (`:1470`).
  - Entries from `train.sh`'s `--queue` file (`json.loads`, `:9444`) never carry it. Nor do
    `build_queue` / `admit_verdict` entries (`:3120`, which returns `{"pr", "verdict",
    "verdict_comment"}`).
  - #3425's batch `20261111-091345` ran from the merge seat's `q-relaunch.json`, whose 3 entries
    hold no `draft` key.
  - The spool line for #3425 does hold `"draft": true`. The batch did not read it.
  - The PR was drafted at 01:48:39Z and readied at 11:13:40Z, by the manual workaround. So it was
    a draft for the whole batch.
  - If the claim were false, #3425's batch entry would carry `draft`, and the log would hold
    `UNDRAFT #3425`.
- **The retry loop.** `land` (`:2726-2770`) logs the refusal. It classifies only BASE_MOVED and
  BRANCH_POLICY, so "still a draft" retries 8 times and then falls to MAIN-MOVED.

Cost:
- About 15-25 lines in `merge_train.py`, plus self-test fixtures. No new file or check.
- One `isDraft` read per entry at batch admission. The read already exists in `is_draft`.
- `merge_train.py` is not in `tests/structure_budgets.json`.

Binding: this repairs existing machinery on the critical path of every merge, measured at 78
wasted attempts, roughly 10 loops of about 3.5 min, plus burned recarries and a manual cure. The
benefit clearly outweighs a one-file change.

### Card (carry on R10-TRAIN-RESIDUE-P2)

**`tools/audit/seat/merge_train.py`.**

1. **Admission, every route.** Where a batch's entries are admitted (`preflight`, `:3014`), set
   `item["draft"]` from one `is_draft` read for every entry that lacks the key. This covers a
   `--queue` file, `build_queue`, a relaunch and the spool.
   - It keeps `undraft`'s rule, "a head drafted after admission is left alone", with admission
     meaning the batch's own start.
2. **The refusal.** In `land`'s retry loop (`:2726-2770`), "Pull Request is still a draft" is a
   state, not a retry.
   - If the entry was a draft at admission, undraft once (`undraft`) and re-attempt.
   - Otherwise `Stop("merge", "drafted after admission: left as a hold")` at once, never 8
     attempts and never MAIN-MOVED.

**Self-test.**
- **The relaunch shape.** A `--queue` entry with no `draft` key, on a PR that reads as a draft:
  one UNDRAFT, then a merge.
- **A draft after admission.** A PR readied at admission but a draft at the merge gets one
  attempt, then a Stop with that reason, with no recarry spent.
- **Null control.** A non-draft entry makes no `gh pr ready` call.
- **Mutation proof.**
  - Removing the admission read fails the relaunch-shape case.
  - Removing the refusal arm restores 8 attempts in the draft-after-admission case.
