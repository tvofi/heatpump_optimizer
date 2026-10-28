Triage batch 41 rules the four proposals appended to `proposals.md` at 2026-10-27T20:20Z: V125 REJECTED because the mechanism it proposes cannot see the one instance it was written for, and V126/V127/V128 ACCEPTED (two narrowed) into three carries. This is the re-cut after the first review returned `blocked` (`claim-false`); the verdicts are unchanged and the four corrections are listed below.

**P212 / V125 — REJECT.** The candidate makes `bus.sh dispatch` digest the ruling documents a packet cites and makes `confirm` refuse a head whose digests moved. On the instance — #2886 merging a triage ruling its author had already withdrawn — the ruled text was *inside* the head: the digest at dispatch and the digest at confirm are the same bytes, nothing in the tree moved, the verdict confirms, and the stale merge happens exactly as it did. What changed was the author's judgement, written to a seat's state and to a message, never to a file; a digest of files records files. The candidate's second half is worse than idle: it digests `dev/programme/rosters/*`, and that ref is the programme's fastest-moving file. Measured on committer timestamps (`git log --format='%cI' origin/handoff/audit-r10-roster`), twelve commits landed between `2026-10-27T18:31:07Z` and `20:23:46Z` — 1 h 52 m 39 s, about 6.4 an hour — and the three tips this seat read were `32b938f3e` (18:32:41Z), `8f7e252fe` (19:35:59Z) and `d61e2834c` (20:17:47Z), 1 h 45 m 06 s end to end. The first cut said "45 minutes", which no window holds; the honest figure is larger and it understates the argument. A verdict citing any roster path would be refused at confirm about six times an hour — routine churn paid by every reviewer to catch a class no instance records. A DEFER trigger is stated in the entry: the first instance where a cited document *outside* the head moves under a live verdict and the stale reading is what merges.

**P213 / V126 — ACCEPT narrowed → `R10-ORCH-REVIEW-PACKET`.** #2883 and #2889 were both refused within ten minutes, after green work, with `head-note: ## Head does not name the dispatched head <sha>` — the text at `tools/audit/seat/review_packet.py:289` names the fault and no repair. The command that fixes a body already exists (`tools/audit/seat/update_pr.sh <branch> - <body>`), so the carried change is one line: the refusal names the head the body must name, the branch, and that invocation. The trigger `head_note_ok(body, head)` does not change. The proposal's second half — an in-place `## Head` rewrite in `tools/pr/head_note.py` — is not carried: its benefit is the unmeasured half (no instance distinguishes "did not know the command" from "knew it and wanted a one-liner"), and the file is unowned, so carrying it would need an `edit-brief` as well as a fix. P214's fix has a measured benefit and pays that cost explicitly; this one does not.

**P214 / V127 — ACCEPT → `R10-996-RUNNER-CLAIMS`, with one `edit-brief`.** #2872 is DIRTY at `fe964895e`, the bot answered `skip-driver-refused tests/golden/claimed_drift.txt`, and the owner had to diff both sides to learn that main added `negative_prices`/`summer_dhw_only` while the branch deletes them and rewrites `config_flow`. The decision text the proposal asks for already exists: `tests/env_drift.py`'s `merge_claim_refusal` (1844-1857) prints both claim sets and the rule. It is dropped in transit — `tools/pr/merge_main_bot.py:139` emits `"skip-driver-refused " + ",".join(...)`, a filename list with the reason stripped. The fix is to carry the driver's own message through, with the filename list as the fallback when the driver cannot run. Because the fix lives in `tools/pr/merge_main_bot.py`, which no group among the 212 owns, the carry takes that file into `R10-996-RUNNER-CLAIMS`'s `files` by `edit-brief` first, so the fixer owns what it edits; the standing roster seat applies the brief from the queue.

**P215 / V128 — ACCEPT narrowed → `R10-ROSTER-OPS`.** This sweep's two `wire-issue` calls from the orchestrator (`2410` at `e331abfbf`, `2593` at `d61e2834c`) were correct writes from the wrong caller, and no instrument could tell. The narrow: the guard covers the structural ops (`wire-issue`, `unwire-issue`, `edit-brief`, `append-carry`, `set-after`, `drop-carry`) and leaves `set-stage`, `append-group` and `set-resume` direct-callable — `sweep_template.md:63` and `nudge.md` step 12 (`nudge.md:89`) run `set-stage` after every merge, and `nudge.md:105` runs `append-group` at dispatch ("register a fly-in at dispatch with `tools/audit/seat/roster_edit.py` append-group"), so a guard on either refuses the tree's own written procedure. `set-resume` appears in no role or template and is left direct on that weaker note. The marker is set where `roster_queue.py` builds its child environment and required before the JSON load, so a refusal writes nothing.

**Recut (after `Fix review: blocked`, `claim-false`).** Four corrections, none to a verdict: (1) `conflicting_claims_message` does not exist — the function is `merge_claim_refusal` (1844-1857); the quoted text was verbatim and the symbol was invented, and `figure_lint` passed it because it resolves paths, not identifiers, so the figures were checked and the names were not. (2) The churn figure is re-taken on committer timestamps, above. (3) P214's destination did not own the file its fix is in; it now carries the `edit-brief`, and P213 states its own exclusion as unmeasured benefit plus an unowned file, so the batch answers the ownership question one way. (4) P215 guarded `append-group`, which `nudge.md:105` runs directly; that op moved to the direct-callable set.

The diff is one markdown file under `dev/programme/triage/`. No product behaviour changes, no roster edit, and nothing implemented.

## Head

`ec7c5b8c0291fd3ae3c57f52a5cafc8876dc4538` merges the authored code head `c2cb1c5bf1b841b4c14a34700f3eb798af410120` and then merges origin/main `e8cb7e683` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`adf5ef473a74e4c25f654f01c4201244b771c147` merges the authored code head `adf011c8f6f2cedabde9e0083d887a5f0ac9a234` and then merges origin/main `ea36188c3` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`adf011c8f6f2cedabde9e0083d887a5f0ac9a234`; the file is the whole diff against `a0e7664ea`, on top of the delivery row at `54ac455ab`.

## Mutation proof

The gate this file feeds is `tools/audit/seat/roster_edit.py`'s `triage_refusal` (`ruling_verdict` at 455, `triage_refusal` at 466): a roster text naming a proposal must cite `triage: dev/programme/triage/<file>.md#P<n>`, and the cited entry must read `Verdict: ACCEPT`. On the committed file, with the seat library on `sys.path`:

```
P212 REJECT
P213 ACCEPT
P214 ACCEPT
P215 ACCEPT
b41-P213.txt -> None
b41-P214.txt -> None
b41-P215.txt -> None
mutant heading P213: None
mutant refusal: dev/programme/triage/s6-batch41.md#P213 is not an ACCEPT ruling (no such entry)
mutant2 verdict P214: DEFER
mutant2 refusal: dev/programme/triage/s6-batch41.md#P214 is not an ACCEPT ruling (DEFER)
missing file: the triage ruling dev/programme/triage/s6-batch41.md is not on the roster branch or origin/main
```

Two mutants on the committed text in memory — the `## P213:` heading changed to `## P213 (relay P1):`, and P214's verdict changed to `DEFER` — are both refused, so the carries are read against this file's entries and verdicts rather than against its presence. The re-cut changed ruling text and carry text, not the verdicts, and the gate arms are unchanged.

## Null control

`missing file` refuses above; the uncited-proposal arm refuses a text naming a proposal with no citation. P212's REJECT is not cited by any carry, which is the intended shape: a rejected proposal produces no roster text.

## Figures

- `tools/audit/seat/bus.sh` dispatch record — line 479 writes `<pr> <head> <reviewer> <nonce> <date> <model>` to `$S/dispatched`; `dispatched_to` (line 313) matches on `pr` and `head`. No document digest exists to extend.
- `tools/audit/seat/review_packet.py:289` — the `head-note` refusal string, fault only; line 411 is its self-test arm.
- `tools/pr/head_note.py` — `head_offset` (20) and `prefix` (39); no function rewrites a section.
- `tools/audit/seat/update_pr.sh` usage block — `updatepr.sh <branch> <code-sha|-> <body-file> [issues...]`.
- `tests/env_drift.py` `merge_claim_refusal` (1844-1857) — both sorted claim sets and "keep the claims that describe THIS branch's diff and delete the rest".
- `tools/pr/merge_main_bot.py:139` — `"skip-driver-refused " + ",".join(driver_conflicts or text_conflicts)`.
- roster churn — `git log --format='%cI %h' origin/handoff/audit-r10-roster` prints `5ffe924ae 2026-10-27T18:31:07Z` through `9aed78e0e 2026-10-27T20:23:46Z`, twelve commits in 1 h 52 m 39 s; the three cited tips are `32b938f3e 18:32:41Z`, `8f7e252fe 19:35:59Z`, `d61e2834c 20:17:47Z`.
- `tools/audit/seat/roster_queue.py:94-102` — the child `env` is built there; `roster_edit.py:703-705` lists the nine ops.
- `dev/governance/roles/nudge.md:105` — "register a fly-in at dispatch with `tools/audit/seat/roster_edit.py` append-group"; `sweep_template.md:63` and `nudge.md` step 12 (`nudge.md:89`) carry `set-stage`; step 18 runs none.
- roster at `origin/handoff/audit-r10-roster` `9aed78e0e` (212 groups): `R10-ORCH-REVIEW-PACKET` `done`, 10 carries; `R10-996-RUNNER-CLAIMS` `carries-open`, 2; `R10-ROSTER-OPS` `done`, 6.
- no roster group owns `tools/pr/head_note.py` or `tools/pr/merge_main_bot.py` — checked across `files` and `hot_files` in all 212 groups.

## Red checks

none

## Forward-carry

none

## Friction

none

