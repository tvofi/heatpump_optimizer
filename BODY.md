Triage batch 46 rules V146-V148 as P232-P234: **V146 → P232 REJECT**, **V147 → P233 ACCEPT narrowed → `R10-FLOW-BODY-ONLY`**, **V148 → P234 ACCEPT narrowed → `R10-PREPR-CAP`** (reopened first). Nothing is deferred. Headings carry no proposal id (P219).

**P232 / V146 — REJECT.** The premise is false. The 0 finding items is the review packet's line, and the packet runs `carry_audit.py check --body` on the pull-request body alone (`review_packet.py:327`). These bodies have `none` under Forward-carry and Friction, so 0 is correct. The merge guard reads the verdict comments (`queue_pre_flight.py:192`, `finding_rows(body, comments)`). On #2900's live body and two verdicts it reads `4 finding item(s): 4 routed`, and the three verdict files on this host read 1, 2 and 2 items. A packet relabel would prevent this one misreading, a marginal trade, so it is not carried.

**P233 / V147 — ACCEPT narrowed → `R10-FLOW-BODY-ONLY`** (not-started, 13 carries, owns `cloud_relay.sh`/`update_pr.sh`/`pr_args.sh`). `body_push.sh:40` forces code before body, and the relay's handoff arm (`cloud_relay.sh:409-428`) updates from whatever body tip exists, so every re-cut opens a stale-body window. Instances: #2890, #2891, #2894 and #2887. Separately, #2900's relay failure at 03:43:15Z today kept its `STALE CHECKOUT` reason only in stdout. Narrowed: `body_push.sh` writes a `Code: <sha>` trailer, which it has already proved at `:40`. The arm updates only when that trailer names the handoff sha; a mismatch is level-only (`handoff-body-stale`), and a body with no trailer updates as today. A failed update's level line carries its `REFUSE` line. Widening the group's `files` to `body_push.sh` is the roster seat's call.

**P234 / V148 — ACCEPT narrowed → `R10-PREPR-CAP`** (done, 1 carry; reopen queued). `copies_line` (`prepr.sh:1034`) runs a bare `python3`. Reproduced at `53c4b9cb0`: Python 3.11.5 prints `SyntaxError: f-string: f-string: expecting '}'`, and the seat venv's 3.14.7 prints the ok line. `recorder_python` (`:519`) already exists and step 6a uses it (`:716`). Narrowed to this step, with the interpreter resolved once per run (one `recorder_parses` costs 5.30 s here).

The diff is one markdown file under `dev/programme/triage/`. Nothing is implemented and no roster file is edited. The roster ops are queued for the roster seat and held until this file is on main.

## Head

`81ee429e7ef76be2012b250df97cea03408d4658`; one file, `dev/programme/triage/s6-batch46.md` (156 lines), the whole diff against `53c4b9cb0`.

## Mutation proof

The gate this file feeds is `tools/audit/seat/roster_edit.py`'s `triage_refusal`. On the committed tree, with the seat library on `sys.path`, the two carry texts the queued ops append (each ending `triage: dev/programme/triage/s6-batch46.md#P<n>`):

```
P232 REJECT / P233 ACCEPT / P234 ACCEPT / P999 None
carry P233 None
carry P234 None
mutant heading -> dev/programme/triage/s6-batch46.md#P234 is not an ACCEPT ruling (no such entry)
mutant DEFER -> dev/programme/triage/s6-batch46.md#P234 is not an ACCEPT ruling (DEFER)
```

Both mutants are applied in memory. The heading mutant renames `## P234:` to `## P234 (V148):`, and the verdict mutant turns `ACCEPT` into `DEFER`. Each makes the gate refuse the same carry, so the gate reads this entry's heading and verdict.

## Null control

```
REJECT cited -> dev/programme/triage/s6-batch46.md#P232 is not an ACCEPT ruling (REJECT)
missing file -> the triage ruling dev/programme/triage/s6-batch46.md is not on the roster branch or origin/main
uncited -> proposal-sourced text cites no triage ruling (`triage: dev/programme/triage/<file>.md#P<n>`): 'proposal V148 text, triage P234'
```

## Figures

- `carry_audit.py --roster-ref origin/main sweep --prs 2900 --from-dir <scratch>` over #2900's body and comments 6458631147 and 6459350190: `CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`. `check --comments` on the verdict files of 2900, 2891 and 2899: 1, 2 and 2 items, all routed.
- `review_packet.py`: the body-only call at 327, the refusal text at 31, the heading at 308. `queue_pre_flight.py`: `findings_gate` at 176, `finding_rows` at 192.
- `cloud_relay.sh`: `level_line` at 165, `handoff_arm` at 390-458, the failed-list write at 444, the self-test fixture at 711-749. `body_push.sh:40` is the code-first refusal and `:73` is `commit-tree`.
- `prepr.sh` (3,927 lines): `copies_line` bare `python3` at 1034, `recorder_python` at 519-533, used at 716, fixtures at 2383-2392. `recorder_parses` takes `real 5.30` (`/usr/bin/time -p`, seat venv). The 3.11.5 run prints `SyntaxError: f-string: f-string: expecting '}'`; the 3.14.7 run prints `closure: no test file defines a symbol production also defines`.
- Roster at `origin/handoff/audit-r10-roster` `5704c4048` (213 groups): `R10-FLOW-BODY-ONLY` not-started, 13 carries; `R10-PREPR-CAP` done, 1.

## Red checks

none

## Forward-carry

none

## Friction

none
