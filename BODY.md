Triage batch 127 rules on the six queue lines after batch 126, P393 to P398.

- **P393: ACCEPT narrowed**, to R10-TRAIN-MERGE-LOOP-2. The train admits a superseded merge verdict, which is an instrument defect. The measured rule refuses a merge verdict when a blocked verdict at the same head carries a later-dispatched nonce. Over 59 instances, 26 are resolvable: 1 is refused (PR 3232) and 25 are admitted (21 later dispatches, 4 same-nonce revisions). The cheaper "any earlier blocked" form would refuse all 25.
- **P394: DEFER.** The replan figure measures the forecast, not a bar metric.
- **P395: ACCEPT (route only).** The DHW tank-seed carry is a finding's fix, so it keeps its route. It goes to a new size-S fly-in, or to R10-COMBI-TANK.
- **P396: REJECT.** An uncited proposal carry appears in 2 of 400 merged bodies, 0.5 %, under the bar for a new mechanism.
- **P397: DEFER.** The augmented-assignment operator gap is unmeasured.
- **P398: ACCEPT.** This is the owner directive on the subagent discovery line, ruled on form. It goes to R10-POLICY-ROLE-PACK.

The diff is three files against the merge base. This repair commit changes only `dev/audit/harnesses/r10_triage_p393.py`: the inlined `ROOT = Path(__file__).resolve().parents[3]` walk becomes the canonical `repo_root(start)` helper that `tests/harness_headers.py` names and the other harnesses carry. The three files:
- `dev/audit/harnesses/r10_triage_p393.py`, the harness that prints every figure (INERT under `dev/audit/`);
- `tests/closures.json`, one line recording that `tests/harness_headers.py` reads it (written by `tools/pr/ci_predict.py --apply-inert`);
- `dev/programme/triage/s6-batch127.md`, the ruling.

No product behaviour changes.

## Head

`1f2ab016f73d7bac88db90a1c17812548581e2a6` is the repaired code head: it merges origin/main `f2a015142714383722bf49d7ab20d8398ec9674c` and the step ref, adds the `repo_root` repair, and removes the superseded BLOCKED.md. The previous authored code head was `2e84abd9c662e6dc3d21d55b0b2b390ca3542de6`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`. `ruling_verdict` reads P393, P395 and P398 as `ACCEPT`, P394 and P397 as `DEFER`, P396 as `REJECT`, and P399 as `None`. A carry citing P393 passes `triage_refusal`. With P393's verdict flipped to DEFER, the same carry is refused as "not an ACCEPT ruling (DEFER)". Citing P394 or P396 is refused the same way. The harness is evidence and has no consumer in the gate.

For the repair: `tests/harness_headers.py` check "every inlined walk matches the canonical helper and no depth root remains" is red at the old head (`r10_triage_p393.py:35: ROOT = Path(__file__).resolve().parents[3]`) and ok after the change.

## Null control

P399 reads `None`, and a carry citing it is refused as "no such entry". A batch file that is absent is refused as "not on the roster branch or origin/main". Uncited text naming `triage P393` is refused as proposal-sourced text that cites no ruling.

For the repair, the null control is the same harness_headers run with the change stashed (the base): 57 of 112 checks failed including the depth-seam check; with the change 56 of 112 fail and the depth-seam check passes. The remaining 56 fail identically at both ends with `ModuleNotFoundError: No module named 'scipy'` in this seat's environment, so 112/112 was not reached here; CI is the authority for that figure.

## Figures

- `git diff --stat f2a015142714...1f2ab016f73d`: 3 files (harness, `tests/closures.json`, `dev/programme/triage/s6-batch127.md`).
- Every ruling figure is printed by the harness arm the ruling names, at `3a45ec251`. The harness's `stale` arm (1 stale, 21 later, 4 same) was not re-run in this repair: its input `EVENTS.tsv` is the host-local bus ledger and is not in the repository or the cloud seat. The change touches only how ROOT is found, and the ROOT value is the same directory.
- Scoped gate: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`; `env_drift --claims-only` and `closure.py selftest` ok. `tests/entities.py` did not complete in this seat (no output past its start line, and run directly it needs `paho`, absent here), so CI is the authority for it. `tests/structure.py` passes.
- No capped file is touched; claim files and VERSION are byte-identical to origin/main.

## Red checks

`tests / fast (3.14)` was red on `tests/harness_headers.py` at `dev/audit/harnesses/r10_triage_p393.py:35`, where the harness inlined a depth-root walk instead of the canonical repo-root helper. Fixed in this head. The detector, `tests/harness_headers.py` itself, already exists, which is why this was caught; no cheaper detector is owed. Cause and process state: the fixer's pre-push run missed it because the scoped gate skips `tests/harness_headers.py` for a record diff with no changed file in its closure (the closure entry was only recorded afterwards by `ci_predict --apply-inert`). Countermeasure: none new; `ci_predict --apply-inert` already records the reader, and a recorded refusal to build more applies, since a record-only diff that adds a harness is rare and CI catches it at the same cost.

## Forward-carry

none

## Friction

none
