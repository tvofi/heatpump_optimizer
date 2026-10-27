Triage batch 43 rules V130 and V131 together, because they are two answers to the same merge-train step: **V130 → P217 REJECT (superseded)**, **V131 → P218 ACCEPT narrowed → `R10-TRAIN-UPGRADE`**.

**P217 / V130 — REJECT.** The refusal is sound and costs little, but it spends the resource the instances actually lost. No merge was ever attempted on a draft; #2854 — green on every check, `gate` green twice, `policy_lint` and `structure.py` green against main, approved by the app — read `BLOCKED`/`REVIEW_REQUIRED` for the single reason that `isDraft` was true, and sat in the live batch for hours as the v7.0.5 critical path. A `Stop` phase turns that into a batch slot plus a human round trip to perform a metadata write that changes no tree. Its one durable part, the add-time `draft: true` note, is carried inside P218's carry, so rejecting the stop loses nothing.

**P218 / V131 — ACCEPT narrowed.** The five settled conditions are kept as written: a posted `merge` verdict at the current head or one `app_approve.sh --carry` says carries to it, a clean merge tree against main, a delivery row at the head, no failing or pending required context, and the approval the step posts; undrafting writes no commit and moves no head, so the verdict still names the tree being merged.

The narrowing answers the question the ruling was asked to test — whether an arm exists where a deliberate draft passes those conditions. It does: an author who holds a head by flipping it to draft **after** admission, with a `merge` verdict already posted, satisfies all five. The conditions cannot see intent; they can see history. So the train records `draft: true` at `add` (V130's note) and undrafts only a head that was **already a draft when admitted** — a flag set later, the only flag an author sets to say "stop", is respected. That is one recorded boolean and one comparison, and it makes the add-time note load-bearing.

Binding details: one `UNDRAFT #<pr> <head>` line; re-read `isDraft` after the call and continue only if false, so a re-draft between the call and the merge stops the run; a failed `gh pr ready` is a `Stop` with its own phase; the non-draft path prints nothing. Null controls: a non-draft head behaves identically; a draft whose verdict names an older head is not undrafted; a draft with a pending required context is not undrafted; and — this ruling's addition — a head drafted after admission is not undrafted.

The diff is one markdown file under `dev/programme/triage/`; nothing implemented, no roster edit.

## Head

`5a21779de67be08974152b844725013c610174d9`; the file is the whole diff against `ea36188c3`.

## Mutation proof

The gate this file feeds is `tools/audit/seat/roster_edit.py`'s `triage_refusal` (`ruling_verdict` at 456, `triage_refusal` at 464): a roster text naming a proposal must cite `triage: dev/programme/triage/<file>.md#P<n>`, and the cited entry must read `Verdict: ACCEPT`. On the committed file:

```
P217 REJECT | P218 ACCEPT
carry -> None
mutant heading None | dev/programme/triage/s6-batch43.md#P218 is not an ACCEPT ruling (no such entry)
mutant defer DEFER | dev/programme/triage/s6-batch43.md#P218 is not an ACCEPT ruling (DEFER)
missing the triage ruling dev/programme/triage/s6-batch43.md is not on the roster branch or origin/main
```

Both mutants are on the committed text in memory — the heading renamed to `## P218 (relay P1):`, and the verdict changed to `DEFER` — and both refuse, so the carry is read against this entry and verdict rather than the file's presence. P217's REJECT is not cited by any carry, which is the intended shape.

## Null control

Missing file and uncited-proposal text both refuse; the positive control is `carry -> None` on the unchanged carry.

## Figures

- `tools/audit/seat/merge_train.py` — the merge step and its phases: `app_approve.sh` at 1523-1530, `--carry` at 1740 and 2047, the docstring's phase list at 54 and 75; the train already reads `isDraft` by hand today.
- roster at `origin/handoff/audit-r10-roster` `9aed78e0e`: `R10-TRAIN-UPGRADE` `done`, `M`, 1 carry, files include `tools/audit/seat/merge_train.py`; `R10-FLOW-AUTOTRAIN` carries 7 and its brief is the queue-writing pitch, not this step.
- #2854 and #2878 as the instances, quoted from V130/V131 and not re-derived here; #2854 merged at main `ea36188c3`.

## Red checks

none

## Forward-carry

none

## Friction

none
