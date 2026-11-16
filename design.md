# R11-INTAKE-R10-RESIDUE: no design; a holding group stops at step 2 (two or more owners)

Designer seat, round 1. Outcome: **stop, reported** (designer.md step 2 and "Stops you"). No
shape, no alternatives, no evidence plan: each would design around the stop.

- Base: f9b680fee43bb519996fc107c5f1c65df02683d7 (`origin/main` at dispatch). No predecessor
  handoff head: the group's `after` is empty on the round-11 roster, so code was read at the base.
- Roster read: `dev/programme/rosters/wave-r11-groups.json` on `handoff/audit-r10-roster` at
  1427bf2ac0e07385ade7fbef6fc41804a68fc87f (the base carries no round-11 roster; on the base's
  `dev/programme/rosters/wave-r10-groups.json` the group is size S with no dispositions, and on the
  roster branch's round-10 file its `resume.note` reads "cut over to
  dev/programme/rosters/wave-r11-groups.json").

## Why this stops

1. **The brief says it is not a work unit.** Verbatim: "Not a work unit as it stands: the
   round-11 architect (architect-planner.md) triages each carry below and re-homes it to the group
   that owns its seam, or refuses it with a reason; this group closes when it holds no carry." The
   roster's `resume.next_step` is "round 11 architect triage", and `dev/programme/HANDOVER.md`
   section "R11-INTAKE-R10-RESIDUE and the carries" says the same. Re-homing a carry is
   `architect-planner.md`'s act; a design note that picks owners would pre-empt it.
2. **The open carries need many owners (step 2: "A change that needs two owners is a design
   finding: report and stop, never split the concern").** The open carries name, among others:
   product code (`custom_components/heatpump_optimizer/config_flow.py`, `services.py`,
   `presets.py`, `setpoint_check.py`, `price_tiles.py`, the services.yaml examples); the test suite
   (`tests/features.py`, `tests/entities.py`, `tests/card.mjs`, `tests/doc_claims.py`); the pre-PR
   gate (`tools/pr/prepr.sh`); the merge and seat instruments (`tools/audit/seat/mutant_run.py`,
   `record_row.py`, `review_packet.py`, `pulse.py`); the policy linter
   (`tools/policy/brief_lint.mjs`); and policy text (`fixer.md`, `design-review.md`,
   `finding-propagation.md`, which the owner approves before merge). These share no seam; one
   design over them would split each concern across one fixer.
3. **The roster's `size` and `files` do not describe the work.** `size` was set S -> L (its
   `resume.note` cites `handoff/audit-r10-roster@8b730d82ba8bf58cd5664863c6f74d59cb9fb413`), and
   `files` names only `tools/audit/seat/merge_train.py` and `tools/audit/seat/orchestrator_tick.py`,
   the seam of the two round-10 carries the group was created for; those carries (2 and 3 in the
   current numbering) are marked `[moved: R11-PRE-PARALLEL-PIPELINE]`. The L that dispatched this
   seat is the sum of unrelated residue, not one change.

## Measurements (re-measured at the reads above)

Enumerator, run alone, prints the figures in this section:

```
git show 1427bf2ac0e07385ade7fbef6fc41804a68fc87f:dev/programme/rosters/wave-r11-groups.json | python3 -I -c "
import json,sys,re,collections
g=[g for g in json.load(sys.stdin)['groups'] if g['group']=='R11-INTAKE-R10-RESIDUE'][0]
c=g['carry']; t=[re.search(r'\[(moved|dismissed)[^\]]*\]\s*$',x) for x in c]
o=[x for x,m in zip(c,t) if not m]
fs={f for x in o for f in re.findall(r'((?:tools|tests|dev|custom_components|docs)/[\w./-]+\.(?:py|sh|mjs|md|json|js))',x)}
print(g['size'],len(c),'open',len(o),collections.Counter(m.group(1) for m in t if m),'files',len(fs),'no-file',sum(1 for x in o if not re.search(r'(tools|tests|dev|custom_components|docs)/',x)))"
```

It printed: `L 164 open 42 Counter({'dismissed': 70, 'moved': 52}) files 35 no-file 14`. The open
set equals the dispatch payload's (its 42 carries without a `[moved` or `[dismissed` tag).

## What would unblock a design

The architect's triage, per carry: re-home it to the live group owning its seam (that group's
designer or fixer then owns it), refuse it with a reason, or, where a cluster of carries does
share one seam and no live group owns it, cut a new group for that cluster with its own `files`
and size. A designer dispatched on such a cut group has one owner to name. Re-dispatching a
designer on this group as it stands reaches this stop again.

## Notes for the fixer

- No fixer is owed: this note approves no shape. Carry: dismissed: no design produced; the
  group's next step is the round-11 architect's triage per its brief
- The roster's `files` (`tools/audit/seat/merge_train.py`, `tools/audit/seat/orchestrator_tick.py`)
  no longer match any open carry's seam, and `size` L counts unrelated residue; the architect who
  re-homes the carries should correct both or close the group when it holds none. Carry:
  R11-INTAKE-R10-RESIDUE

Seat token count: not reported by this harness.
