# Evidence for the round-3 review (design revision 3)

Design: `handoff/orch-machinery` at
`09174d94e24faa0a02cda531164ec55ac2c49577`. Rounds 1–2 reviewed `2b159e46` and
`14d2ac1c`. Read from a detached worktree at that SHA; live state re-read
2026-10-20T14:40Z–14:55Z, `load1` 44–52 on 8 cores. Host paths are written `~`.
Commands and the output I got.

---

## R1. What moved

    $ git diff --stat 14d2ac1c 09174d94
     dev/audit/design/orch-machinery/DESIGN.md   | 109 ++++++++++++++++++--------
     dev/audit/design/orch-machinery/EVIDENCE.md | 111 ++++++++++++++++++++++++----
     2 files changed, 176 insertions(+), 44 deletions(-)
    $ git log --format='%h %cI %s' 14d2ac1c..09174d94
    09174d94e 2026-10-20T14:35:43+02:00 design: revision 3, closing B10-R and the round-2 residuals
    $ grep -c '^| M[0-9][0-9]' dev/audit/design/orch-machinery/DESIGN.md
    50
    $ … contiguity …
    contiguous 1..50

The diff is targeted: §1 tree size, §6.2 relay-probe first cut and the seat
token grammar, §6.3 the `handoff-update` row and the three-arm import, §6.4 the
class→scope mapping, §6.7 arm-1 provenance, §6.8 the proposal count, §8 Phase 3
ordering, §10 corrections, and the new §11. No inventory row or other section is
restructured.

## R2. N1-R and N2-R

    $ git ls-tree --name-only HEAD tools/audit/seat/ | wc -l
    52
    $ ls tools/audit/seat | wc -l
    52
    $ cd ~/hpo-seats/r10s3/orch-wt; git rev-parse --short HEAD
    a2b25bbc5
    $ ls tools/audit/seat | wc -l
    53
    $ diff <(ls -A tools/audit/seat | sort) <(git ls-tree --name-only HEAD tools/audit/seat/ | sed 's|tools/audit/seat/||' | sort)
    2d1
    < __pycache__
    $ git status --short --ignored tools/audit/seat/
    !! tools/audit/seat/__pycache__/

The tree is 52; the live checkout's 53 is the ignored import cache, exactly as
revision 3 now states.

    $ grep -c 'cloud-disposed' tools/audit/seat/orchestrator_tick.py
    0
    $ grep -c 'disposed' tools/audit/seat/orchestrator_tick.py
    1
    $ grep -n 'disposed' tools/audit/seat/orchestrator_tick.py
    1693:        """Every open issue must be disposed in a record artifact: a delivery

The precise pattern is 0; the loose one hits one docstring word, as stated.

## R3. B10-R.1 — the import's three arms

    $ awk '{print $1}' ~/.local/state/hpo/cloud-disposed | sort -u |
        sed -E 's#(refs/heads/[a-z-]+/).*#\1#' | sort | uniq -c
     89 refs/heads/handoff-body/
    113 refs/heads/handoff/
      1 refs/heads/probe/
    $ wc -l < ~/.local/state/hpo/cloud-disposed; sort -u ~/.local/state/hpo/cloud-disposed | wc -l
    210
    209
    $ awk '{print $1}' ~/.local/state/hpo/cloud-disposed | sort | uniq -c | awk '$1>1'
       2 refs/heads/handoff/audit-r10-roster
       6 refs/heads/handoff/r10-rca-worktree-vanish
       2 refs/heads/probe/cloud-seat-20261018

89 + 113 + 1 = 203 distinct refs; 210 lines and 209 distinct lines mean seven
repeated ref entries, one of them an exact duplicate line and six same-ref
re-disposals (1 + 5 + 1 extra entries). The three arms classify every ref; the
last disposition per ref is the only rule consistent with the six moves.

## R4. B10-R.2 — the live kinds

    $ awk '$1=="OWED"{print ($2 ~ /^[0-9]{4}-/ ? $3 : $2)}' ~/.local/state/hpo/cloud-relay.log | sort | uniq -c
    29890 handoff-no-pr
       10 handoff-update
      151 probe-ref
        1 reviewer-fire
    $ grep -c 'logline OWED "approve-held-runs\|logline OWED "dispatch' tools/audit/seat/cloud_relay.sh
    3
    $ grep -n 'logline OWED "approve-held-runs\|logline OWED "dispatch' tools/audit/seat/cloud_relay.sh
    206:      || logline OWED "approve-held-runs $pr $br"
    209:    … || { logline OWED "dispatch $pr no new head read after the update"; continue; }
    214:    else logline OWED "dispatch $pr $nh bus.sh dispatch failed; run it by hand"; fi

The five live shapes are covered once the confirm arm is counted (it is 0 live).
The `approve-held-runs`/`dispatch` code paths exist; the grep returns 3 lines
(one and two), not the 2 E20 prints — that 2 counts code paths, not matches
(N13-R).

## R5. The relay's `handoff-update` state and its closer

    $ sed -n '180,225p' tools/audit/seat/cloud_relay.sh
      f=$state/cloud-handoff-failed
      …
      if [ -f "$f" ] && grep -qxF "$topic $hs" "$f"; then continue; fi
      … update_pr.sh … if [ "$urc" != 0 ]; then
        echo "$topic $hs" >> "$f"; logline OWED "handoff-update $pr $topic $hs"; …
      … approve_held_runs.sh … || logline OWED "approve-held-runs $pr $br"
      … bus.sh dispatch … else logline OWED "dispatch $pr $nh bus.sh dispatch failed; run it by hand"; fi

    $ head -3 ~/.local/state/hpo/cloud-handoff-failed; wc -l < ~/.local/state/hpo/cloud-handoff-failed
    r10-policy-instruments 26189a1fdf61777848fca426634bcc14b07a0f93
    r10-deeplink-handlers 8b3ea42cbd45fcb30fefe03d2e74a79876f5c1c0
    r10-setpoint-boost 890fba053bdf3b3c7611f6a860be528665278259
    10

The entry format is `<topic> <code-sha>`, written only on an update failure. A
moved ref no longer matches the stored sha, so the next pass retries — the
"moved ref supersedes" clause matches the code. A successful update can remove
the entry under the new job (the current relay does not, but the new writer can).
The approve/dispatch failures happen after a successful update and write no
entry, so folding them in as reasons has no backing state and no distinct closer
(N11-R).

## R6. N12-R — `instrument-self-tests` is not a required context

    $ gh api repos/tvofi/heatpump_optimizer/rulesets --jq '.[] | [.id,.name,.enforcement] | @tsv'
    22628467  main-protect         active
    23698884  main-protect-checks  active
    23937752  release-tags-protect active
    $ gh api repos/tvofi/heatpump_optimizer/rulesets/23698884 --jq '.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context'
    fast (3.14)
    browser
    briefs
    closure-scope
    closures
    typing
    hassfest
    validate-hacs
    policy-docs
    wave-script
    pr-contract
    env-matrix
    Analyze (actions)
    Analyze (javascript-typescript)
    Analyze (python)
    mutation
    budget-raise-gate
    $ gh api repos/tvofi/heatpump_optimizer/rulesets/22628467 --jq '.rules[].type'
    deletion
    non_fast_forward

17 required contexts; `instrument-self-tests` is not one, and no required job
`needs:` it (`grep -n 'needs:.*instrument-self-tests' .github/workflows/*.yml`
→ no match). The tree's own note (`governance.yml` above the job, and
`pr-contract.yml:85`) says a red there is "a red check at the head, which
`pr-contract` makes the body answer". The chosen ordering (wire with the
instrument) remains right; the stated reason is not.

## R7. N3-R — the gate counts

    $ git ls-remote origin refs/heads/handoff/audit-r10-roster   # 573efe68…
    $ python3 -I -   # open gates at that tip
    open gates: 14
    exact 'mandated approval under 6175172275': 6
    name the mandate in some form: 10
    neither: R10-I5-DOCS, R10-BRIEFS-FOLD, R10-REPLAY-LANE, R10-REPLAY-SCOPED

Six exact, ten naming, four neither (all still code-owned/policy). Reproduces.

## R8. N5-R, N7-R, N8-R, N10-R

    $ grep -c '^| [ivx]* | ' dev/audit/design/orch-machinery/DESIGN.md
    8
    $ grep -n 'DONE?\|STALLED?' tools/audit/seat/orchestrator_tick.py | head -6
    982:  self.line(S, f"{seat}: STALLED? no PR pushed after "
    994:  self.line(S, f"{seat}: DONE? #{pr}'s head moved since dispatch {tail}",
    1011: self.line(S, f"{seat}: STALLED? head unchanged and no new CI "
    $ grep -n 'groups\["R10-ARCH-DOCS"\]' ~/hpo-orch/r10s3/plan/gen.py
    17: groups["R10-ARCH-DOCS"] = {"group": "R10-ARCH-DOCS", "kind": "docs", "size": "M", …
    $ python3 -I -c "… print roster R10-ARCH-DOCS resume …"
    {'stage': 'not-started', …}
    $ grep -n 'MANDATE_COVERS' tools/policy/budget_raise_gate.py
    116:MANDATE_COVERS_RAISE = ("budget-raise", "all")
    123:MANDATE_COVERS_POLICY = ("all",)
    $ sed -n '117,122p' tools/policy/budget_raise_gate.py
    # What covers the merge train landing a POLICY head …: only `all`. …

Eight proposals; the existing `STALLED?`/`DONE?` tokens; the live defect-1
override is `not-started` (the fixture supplies a roster saying `done`, so the
override contradicts it); the mapping matches the gate's own constants —
`MANDATE_COVERS_POLICY` is at line 123, not the 121 E22 prints (N15-R).

## R9. N9-R — the timing anchors

    $ /usr/bin/time -p sh -c 'git ls-remote --heads origin "refs/heads/probe/*" >/dev/null'
    real 0.55   user 0.04   sys 0.03
    $ /usr/bin/time -p bash tools/audit/seat/cloud_relay.sh --self-test
    cloud_relay self-test: 74 checks, 0 failed
    real 37.87  user 9.33   sys 11.97

The design's anchors (0.99 s at load1 50; 56.54 s for the self-test) are the same
order of magnitude at a different load. The self-test does not print a fixture
count, so "~8 relay fixtures => ~7 s per relay" is inferred, not measured
(N16-R). The design labels the 120 s bound a first cut; the anchors support that.

## R10. Regressions

    $ python3 -I -   # E3 fixture
    E3 findings: 2
    E3 after dispose: 2
    $ HPO_STATE_DIR=… HPO_RELAY_PRS=true bash cloud_relay.sh pass
    E4 rc=0 retries=2
    $ python3 -I -   # E6 throwaway lock dir
    E6 stolen, A alive: True
    $ python3 -I tools/audit/seat/orchestrator_tick.py --self-test | tail -1
    orchestrator_tick self-test: 150 checks, 0 failed
    $ bash tools/audit/seat/tick_loop.sh --self-test | tail -1
    tick_loop self-test: 4 checks, 0 failed
    (cloud_relay self-test: 74 checks, 0 failed — R9)

All reproduce.

## R11. Roster counts

    $ python3 -I -
    groups: 93
    stages: {'done': 46, 'not-started': 36, 'in-progress': 7, 'queued': 4}
    open: 47
    non-40hex commits: 8

Unchanged.

## R12. §11's row count

    $ sed -n '/## 11. Corrections in revision 3/,$p' …/DESIGN.md | grep -cE '^\| (B10-R|N[0-9]+-R)'
    12
    $ … | grep -oE '^\| (B10-R|N[0-9]+-R)' | sort | uniq -c
    2 | B10-R
    1 each | N1-R … N10-R

Twelve data rows: the two B10-R clauses and ten residuals. The prose "two ledger
clauses and nine figures" undercounts by one (N14-R).
