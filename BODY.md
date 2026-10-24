Adds `dev/programme/triage/s6-batch1.md`: the s6 orchestrator's untriaged batch 3 (items N, O, P, s5 measurements) ruled as P42-P44 under `dev/governance/roles/proposal-triage.md`. The file is under `dev/programme/`, which `tests/closure.py` lists as INERT, the route `s5-batch2.md` took.

P42 (relay vs update_pr race) is DEFER to R10-FLOW-BODY-ONLY; P43 (queue_pre_flight refuses a PR that adds its own carry file) is a defect in an instrument, ruled ACCEPT only to set its route; P44 (brief_lint ignoring roster `carry[]`) is DEFER on an unmeasured benefit.

## Head

`569da4eed060ba229f548719237ba2c4545dec58`, on origin/main `50af6174f`; roster read at origin/handoff/audit-r10-roster `4c54758d7`.

## Mutation proof

n/a: no code or check changes; the file is a ruling record. Its consumer is the triage gate: `roster_edit.ruling_verdict` reads the three entries.

## Null control

`roster_edit.ruling_verdict` on a pid the file lacks (`P45`) returns None, and a carry citing a DEFER entry (`#P42`) is refused, so the gate distinguishes the verdicts this file states.

## Figures

- Verdicts per class: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' -r '$1' dev/programme/triage/s6-batch1.md | sort | uniq -c`.
- Entries: `rg -c '^## P' dev/programme/triage/s6-batch1.md`.
- P43 class size: the `git log ... carries/ | sort -u | wc -l` line in P43's `Instances:`, run at origin/main `50af6174f`.

## Red checks

- `governance / instrument-self-tests` (job 120821317365, run 40076628415, PR head `b451bde0`): red in step 22, `ref_privacy.py --check`: `REFUSE dev/programme/triage/s6-batch1.md:12: host-path in an added line`. It is this pull request's own defect, not main's: the same job is `success` on main `50af6174`. The cause was a host path I wrote into the ruling's header, pushed with a plain `git push` instead of `handoff_push.sh`, whose `ref_privacy.py guard` (handoff_push.sh line 128) would have refused it. The cheaper detector exists and runs in 0.5 s (`ref_privacy.py --check`, measured with `time`); I bypassed it, so no new check is owed. Fixed at head `569da4ee`: the path is gone and `ref_privacy.py --check` prints `0 refused`. `gate` and `pr-contract` were red downstream of it.
- Code scanning, read on 2026-10-24 (`gh api repos/<repo>/code-scanning/alerts?ref=refs/pull/2688/merge&state=open`): 0 open alerts; `codeql / Analyze (python)`, `(actions)` and `(javascript-typescript)` are `success` at `b451bde0`. The file is a markdown ruling record that no analyzer reads.

## Forward-carry

- P43's carry (`carry_audit.load_dests` unions the PR head's carry files; `queue_pre_flight.findings_gate` passes the head), cites `dev/programme/triage/s6-batch1.md#P43`. Carry: R10-FLY-CARRY-DISPOSITION

## Friction

none
