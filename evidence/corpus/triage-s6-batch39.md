Triage batch 39 rules the four proposals the orchestrator relayed, in its funding order: V127 (a verdict publishes before anything checks its findings name a destination) ACCEPT to `R10-FLY-CARRY-DISPOSITION`; V128 (the body's `## Head` is checked last, after the expensive steps) ACCEPT to `R10-RCA-BODY-LINT`; V129 (the claim driver refuses a merge it can safely union) ACCEPT to `R10-996-RUNNER-CLAIMS`; V130 (the field-coverage step has no bound, so a blocked run reads as a long one) DEFER, because its cost cannot be stated until one healthy run's wall and CPU time are measured.

The three ACCEPTs are reorders or narrow additions, not new rules: V127 runs `carry_audit`'s own `audit` — the parser the train's admission gate already runs — a second or two earlier, inside `bus.sh`'s `push_verdict()`; V128 invokes the body check's existing `## Head` arm before step 1b takes the heavy slot; V129 adds one comparison arm to `merge_claim_file` and rewrites the expectation `tests/entities.py` already pins in exactly the disjoint-add shape. V130 is a DEFER because a bound below a healthy run's wall time trades a rare hang for false reds at an unmeasured rate: the one isolated run spent 52.47 s user and 15.74 s system and had not finished at `timeout 120`, while the three live instances hold a heavy slot and spend about 0.02 s of CPU in 53 s.

No product behaviour changes in this batch: the diff is one markdown file under `dev/programme/triage/`. Three carry texts are filed with the seat's roster queue (P207, P208, P209); P210 takes no roster op. `R10-RCA-BODY-LINT`'s stage is `done`, so its carry needs the reopen route (`set-stage ... fixing` first), the route P196 took. Measured corrections to the relay's own account are recorded in the file: the buffer-store log puts `REFUSE pr-body` *before* the body sub-checks, so the waste is steps 1b and 2-6f; the claims change rewrites an existing pinned expectation rather than only adding a test; and the two parked verdicts' `PRE-FLIGHT` lines are not reproducible locally, so the ruling cites the earlier recorded #2683 instance beside them.

## Head

`cd75ce70552b2b03c34b89d5680f55798f752754`; the file is the whole diff against `67178dc6a589cf95d2ce7cff36d8bbf17343e8dc`.

## Mutation proof

The gate this file feeds is `tools/audit/seat/roster_edit.py`'s `triage_refusal` (`ruling_verdict` at 456, `triage_refusal` at 464): a roster text that mentions a proposal must cite `triage: dev/programme/triage/<file>.md#P<n>`, and the cited entry must read `Verdict: ACCEPT`. On the committed file, with the seat library on `sys.path`:

```
P207 verdict: 'ACCEPT'
P208 verdict: 'ACCEPT'
P209 verdict: 'ACCEPT'
P210 verdict: 'DEFER'
P999 verdict: None
refusal, P207 cite: None
refusal, P210 cite: dev/programme/triage/s6-batch39.md#P210 is not an ACCEPT ruling (DEFER)
refusal, P999 cite: dev/programme/triage/s6-batch39.md#P999 is not an ACCEPT ruling (no such entry)
refusal, missing file: the triage ruling dev/programme/triage/s6-batch39-nope.md is not on the roster branch or origin/main
mutant P207 verdict: DEFER
mutant refusal: dev/programme/triage/s6-batch39.md#P207 is not an ACCEPT ruling (DEFER)
```

The mutant is this file with P207's verdict flipped to `DEFER` in an out-of-tree copy: the gate reads the verdict, so a DEFER cannot be laundered into a carry. The first run of this proof printed `P207 verdict: None` for all four entries: this file's headings read `## P207 (relay P1): ...`, and the gate's entry form is `## P207: ...` (its regex anchors the pid to the colon), so an ACCEPT whose heading carried the relay label could not have been carried at all. The headings were fixed in this commit and the proof re-run; the relay label stays on each entry's `Source:` line. The three carry texts this batch files were put through the same gate with the committed file as their ruling source, and each returned `None`.

## Null control

`P999` is not an entry: `None`. A missing file: the `is not on the roster branch or origin/main` refusal above. The gate's other arm, a roster text that mentions a proposal with no cite, prints `proposal-sourced text cites no triage ruling (`triage: dev/programme/triage/<file>.md#P<n>`): 'proposal P1 adds a check to bus.sh'`.

## Figures

One line per figure, with the command that printed it.

- the carry audit's cost per verdict: `/usr/bin/time -p python3 -I tools/audit/carry_audit.py --roster-ref origin/main check --body <body>` prints `real 0.64`/`0.62`/`0.60` over three runs on a body with no finding rows; the roster read alone (`/usr/bin/time -p python3 -I -c "import sys; sys.path.insert(0,'tools/audit'); import carry_audit; carry_audit.load_dests('.', '<ref>')"`) prints `real 0.64` on `origin/main` (208 groups) and `real 1.13` on `origin/handoff/audit-r10-roster` (211 groups), the ref the publication check reads.
- the admission check reads exactly this text: `sed -n '176,205p' tools/audit/seat/queue_pre_flight.py` — `findings_gate`, `carry_audit.finding_rows(body, comments)`, the empty short-circuit at 192, `carry_audit.audit(body, comments, dests)` at 199.
- `bus.sh` names no carry check: `git grep -n 'carry_audit' origin/main -- tools/audit/seat/bus.sh` prints nothing; `sed -n '200,230p' tools/audit/seat/bus.sh` — `push_verdict()`, with `append_commit review` at 228.
- the precedent for a refusal before the ref moves: `sed -n '1209,1221p' tools/audit/seat/bus.sh` — the host-path self-test arm where `review/7` does not move.
- the earlier recorded instance: `grep -n 'PRE-FLIGHT' merge-report.txt` in the session state prints `2026-10-24T10:06:03Z parked #2683 train 20261024-100534: PRE-FLIGHT carry_audit: 4 finding item(s) with no valid Carry (first: review 6379079217 item 57e267d2 unrouted)`. Session state, not the tree.
- the buffer-store refusal order: the local push log for R10-BUFFER-STORE records at line 78 "`## Head` does not name 8d0a1c3, which is the head this ran on", then `ok figures` / `ok carry` / `ok unpinned sites` at 82-85, then `app_push: REFUSE: the body did not pass tools/pr/prepr.sh` at 86. Local seat state; the seat measured the same run live at 37 minutes.
- the prepr step order: `grep -n 'heavy_run /tmp/prepr-fc\|body_line\|prepr: body' tools/pr/prepr.sh` puts the field-coverage step at 3246 (3f3) and the body check at 3435 (step 7), and `sed -n '600,615p' tools/pr/prepr.sh` shows `heavy_run()` with no wall-clock arm.
- no recorded duration for the field-coverage step: `git show origin/main:tests/closures.json | grep -n '"tools/policy/field_coverage.mjs":'` prints nothing; line 1642 is that path inside a closure's file list, not a `recorded` entry.
- the live field-coverage instances: `ps -p 64440,66073,85913 -o pid,etime,time` printed `09:15 0:00.81`, `09:11 0:00.76`, `08:46 0:00.76`, and 53 s later `10:08 0:00.83`, `10:04 0:00.79`, `09:39 0:00.78`.
- the destinations: the three groups own the files each refuse carries — `R10-FLY-CARRY-DISPOSITION` names `tools/audit/seat/bus.sh` and `tools/audit/carry_audit.py`, `R10-RCA-BODY-LINT` names `tools/pr/prepr.sh` and `tools/audit/seat/body_push.sh`, `R10-996-RUNNER-CLAIMS` names `tests/env_drift.py` and `tests/golden/claimed_drift.txt` (`python3 -c "import json; print(...)"` over `dev/programme/rosters/wave-r10-groups.json`, 208 groups).
- the pinned expectation the claims change rewrites: `sed -n '22423,22456p' tests/entities.py`.

## Red checks

none

## Forward-carry

none

## Friction

none
