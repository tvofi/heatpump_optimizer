Adds `dev/programme/triage/s6-batch2.md`: eight proposals from the s6 orchestrator's `proposals.md` (the s5 items I-M that `s5-batch2.md` never ruled, and s6's Q, R and S6-S) ruled as P45-P52 under `dev/governance/roles/proposal-triage.md`. The file is under `dev/programme/`, which `tests/closure.py` lists as INERT, the route the earlier batches took.

Verdicts: P45 ACCEPT, P46 ACCEPT narrowed, P51 ACCEPT narrowed (all three to the existing `R10-ORCH-BEATD`; the file says the work may later be split into its own group); P49 ACCEPT (measure first) to `R10-FLOW-RECORD-PITCH`; P47 and P48 DEFER; P50 and P52 REJECT.

## Head

`d0492904ea98b9b828b6f653efcb977b8490226d`, on origin/main `50af6174f`; roster read at origin/handoff/audit-r10-roster `4c54758d7`.

## Mutation proof

n/a: no code or check changes; the file is a ruling record. Its consumer is the triage gate: `roster_edit.ruling_verdict` reads the eight entries (P45 to P52).

## Null control

`roster_edit.ruling_verdict` on a pid the file lacks (`P53`) returns None, and a carry citing a DEFER entry (`#P47`) is refused by `triage_refusal`, so the gate distinguishes the verdicts this file states. (The earlier draft named `P52` as the absent pid; P52 is ruled REJECT in this file.)

## Figures

- Verdicts per class: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' -r '$1' dev/programme/triage/s6-batch2.md | sort | uniq -c` (4 ACCEPT, 2 DEFER, 2 REJECT).
- Entries: `rg -c '^## P' dev/programme/triage/s6-batch2.md` (8).
- P49 share of record merges: the `git log ... | grep -c record/autofix` line in P49's `Instances:`, run at origin/main `50af6174f` (14 of 48).
- P52 commit times: `TZ=UTC git log -1 --format=%cI <sha>` for `69a26d2a2`, `bd0d4d603`, `168365196`, `d5dc3e26a`, `b927f431a`; the class row: `python3 -c` over `dev/audit/config/bugclasses.json` at origin/main, key `N-postreview-merge-red`.

## Red checks

- `governance / instrument-self-tests` (job 120823664203, run 40077385335, PR head `44ee0e5f`, merge ref `1a41588b`): red in step 22, `ref_privacy.py --check`: `REFUSE dev/programme/triage/s6-batch2.md:14: host-path in an added line`. It was this pull request's own defect, not main's: the same job is `success` on main `50af6174f`. The cause was a host path in the ruling's header, pushed with a plain `git push` instead of `handoff_push.sh`, whose `ref_privacy.py guard` (handoff_push.sh line 128) would have refused it. The cheaper detector exists and runs in 0.5 s (`ref_privacy.py --check`, measured with `time`); it was bypassed, so no new check is owed. Fixed: `ref_privacy.py --check` prints `0 refused` at this head. `gate` and `pr-contract` were red downstream.
- `s6-batch1.md` carried the same line and is fixed on `handoff/r10-triage-s6-batch1`.
- Code scanning, read on 2026-10-24 (`gh api repos/<repo>/code-scanning/alerts?ref=refs/pull/2689/merge&state=open`): 0 open alerts; `codeql / Analyze (python)`, `(actions)` and `(javascript-typescript)` were `success` at `44ee0e5f`; main has 0 open alerts. The file is a markdown ruling record that no analyzer reads.

## Forward-carry

- P45, P46 and P51 (the standing seats' sweep template, `pulse.py --seat-alive` arm and Wait paragraph), cite `dev/programme/triage/s6-batch2.md#P45`. Carry: R10-ORCH-BEATD
- P49's carry (record chain: measure whether a record-only merge owes a row, then end the chain; the step is in `.github/workflows/nightly.yml` lines 492-515 today and moves with `R10-CI-LAYOUT-P1`), cites `#P49`. Carry: R10-FLOW-RECORD-PITCH

## Friction

none
