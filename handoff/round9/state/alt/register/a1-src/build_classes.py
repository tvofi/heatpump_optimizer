#!/usr/bin/env python3
"""Writes the authored half of classes_v2.json (mechanisms, aliases, notes,
detector/barrier/status copied from main's register). derive.py --write fills
instances/total/max_per_round from register_rows.tsv."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
v1 = json.load(open(f'{HERE}/bugclasses_main.json'))

NOTES = {
    'P1': "Stretched. R1-7 already held live-input and output-boundary rows (R5 D1-06 'nan' sensor state, R5 D1-07 weather feed, R2 D8-02 numpy scalars to attributes) that cross no persisted store; R8 D1-s3-01 (Open-Meteo shape) and the R9 re-maps N-plausibility (finite-but-absurd live input), N-min-gap (one off-grid stamp voids a feed) and N-service-clamp (unbounded service input) add more, and R9 D1-s5-02/D1-s3-06 are finite-but-out-of-domain. Proposed wording: 'A non-finite, malformed or out-of-domain value crosses an input boundary (persisted store, live entity, external feed, service call) with no guard'. The detector idea (fuzz the store roster) reaches none of the non-store members.",
    'P2': "Stretched. Used as the catch-all for sibling-seam guard gaps; R8/R9 add entity default-enabled/availability (N-dup-entity, N-availability, R8 D8-s2-02), a try opened after the call it should fence (N-late-try) and a state-blind flow menu (N-menu), all 'guard present at a sibling, missing here'. R1-7 misfits flagged in reclassifications.md (coordinator size, name sort).",
    'P3': "Stretched. In practice 'a clamp, floor, limit or step constant in a physics or tariff formula breaks the identity its siblings keep' (R2 D2-05, R4 D2-02/03, R5 D2-01, R6 D2-02); R9 re-maps N-sign-floor (price-margin sign floor), N-euler-coupled (sub-step bound judged per store) and N-clamp-range (bias clamp sized to an assumed range), and R8 D2-s2-01 (tariff top-k by window, not by day) is a low-confidence placement.",
    'P5': "Stretched to model-structure mismatch in the fit (already R1 D7-02, R4 D7-01); R9 N-fit-integrator (coarser integrator than the plant) re-mapped here, which puts it under the barriered class's obligation (F4.2 carried both).",
    'P6': "Stretched. R1-7 already held swallowed failures (R1 D10-07, R2 D10-04) that read no missing key; R9 N-debug-swallow (persistent failure logged at DEBUG) re-mapped here; R8 D7-s1-03 is a refusal path that writes no reason, read back as the default 'ok'.",
    'P9': "Stretched to keyboard access: R8 D4-01 (Tab order) and R9 N-keyboard (pointer-only editing) are card accessibility rules that do not reach a control, the class's shape, but the mechanism text names only clipping/colour/hit target.",
    'P10': "Stretched. R9 N-loop-cpu is CPU work run inline on the event loop (no thread, no GIL contention); same harm (loop starvation). Conversely R1 D9-01, R2 D9-03, R4 D9-05, R7 D9-02 are avoidable solve CPU, not starvation, and are flagged to N-solve-recompute.",
    'I1': "Stretched to performance gates: R2 D9-02, R4 D9-06, R5 D9-07, R6 D9-02 already here; R8 D9-s2-01 and the R9 re-map N-cpu-gate-blind (a 2x regression outside the sampled work leaves the gate green) join them.",
    'I2': "R8 D3-s1-02 is a cache key whose input set diverges from what the capture reads: scope-vs-real-dependency, same shape.",
    'I5': "Stretched. Holds production translation/icon coverage (R1 D10-13, R4 D8-02, R8 D4-s2-01; R9 re-maps N-escape, N-service-icons, N-language) and rendering defects (R9 N-markdown), which are not drift against code; and R1 D10-01/D10-02/D10-12 are HA quality-scale code conformance (flagged, no class fits).",
}

NEW = {
    'N-solve-recompute': dict(kind='production',
        mechanism='The solve recomputes interpreter-bound work per iterate or per row that is invariant or vectorisable (per-row Python loops, uncached parameter derivations, scalar re-evaluation, polishes whose result is discarded)',
        nearest_existing='P10', mechanism_difference='P10 is where the solve runs (a GIL-holding thread starving the loop); this is avoidable CPU inside the solve wherever it runs, fixed by vectorising or caching, not by moving work off the loop',
        detector_idea='S5 enumerate.py: profiled call counts per (module, qualname) against a once-per-solve boundary; recompute_instances may only fall'),
    'N-structure-blind': dict(kind='instrument',
        mechanism='A structural ratchet or dead-code metric measures a name or regex proxy instead of the property it gates, so dead production members or cross-seam coupling pass it unmeasured',
        nearest_existing='I4', mechanism_difference='I4 is two maintained readers of one concept disagreeing; here there is one in-tree metric, blind to a code shape (rename, module-level helper(self), property, attribute-only load), and the second reader exists only as an audit harness',
        detector_idea='Run structure.py against a reachability/attribute-load oracle over the package (the S6 production-member-no-caller and structure-metric-blind enumerators)'),
    'N-name-sort': dict(kind='production',
        mechanism="An entity family's display names do not lead with a shared token, so the name sort Home Assistant and the card use splits the family, per language",
        nearest_existing='P2', mechanism_difference='P2 needs a predicate decided twice; here no predicate exists: names are written per entity and per language and nothing keys them to the family',
        detector_idea='S6 entity-family-name-sort-split enumerate.sh: per family, sort by name (en, sv) and entity_id and count unexplained splits'),
    'N-shared-config': dict(kind='production',
        mechanism='Solve-scoped state is mutated on, or read from, live shared objects while the solve runs off the loop, so a concurrent reader publishes it or a concurrent writer is reverted',
        nearest_existing='P2', mechanism_difference='P2 is a guard present at a sibling and missing here; this is shared mutable state across the solve boundary (no snapshot), which P2\'s call-site detector cannot see',
        detector_idea='Drive a service write and an entity read at every await point of async_run_optimization and diff against a snapshot-isolated run'),
    'N-approval-rebuy': dict(kind='instrument',
        mechanism='An approval or verdict is bound to the exact head SHA rather than to the diff it reviewed, so a diff-identical head move (a merge from main, a ci: commit) re-buys the review',
        nearest_existing='I3', mechanism_difference='I3 is enforcement too weak (skipped, stale, bypassable); this is enforcement keyed on the wrong identity, costing rounds without catching defects',
        detector_idea='Per merged PR, patch-id of the reviewed diff vs the merged diff; count re-verifications whose patch-id did not change'),
    'N-finally-return': dict(kind='instrument',
        mechanism='A return inside finally swallows an in-flight exception, cancellation included',
        nearest_existing='I1', mechanism_difference='I1 is a gate blind to a behaviour change; this is a code shape that discards the failure signal itself',
        detector_idea='S6 return-inside-finally enumerate.py (AST: return/break/continue whose scope escapes a finally)'),
    'N-step-grid': dict(kind='production',
        mechanism="A number selector's minimum or default is not on its own step grid, so native validity flags legal values and a spinner click lands off-grid",
        nearest_existing='P2', mechanism_difference='no guard is missing at a sibling; one declaration (min, step, default) is internally inconsistent',
        detector_idea='S7 selector_min_off_step_grid enumerate.py: every box-mode NumberSelector (min - base) % step == 0'),
    'N-reap-lock': dict(kind='production',
        mechanism='Shutdown reaps the solve worker only after acquiring the lock a long solve holds, so stop latency is the solve\'s remaining time',
        nearest_existing='P2', mechanism_difference='P2 lifecycle rows (R2 D1-02, R9 D1-s3-02) are a missing guard; this is lock ordering between shutdown and an in-flight solve',
        detector_idea='Stop latency ratio vs an unlocked reap (the finder harness perturbation)'),
    'N-staleness': dict(kind='production',
        mechanism="A staleness limit is shorter than a report-on-change source's legitimate quiet interval, so a valid unchanged reading is declared stale or unavailable",
        nearest_existing='P6', mechanism_difference='P6 misses staleness behind a silent fallback; this declares false staleness',
        detector_idea='S6 staleness-limit-shorter-than-quiet-interval enumerate.sh: silence cells beyond each INPUT_MAX_AGE limit'),
}

ALIASES = {}
import csv
for r in csv.DictReader(open(f'{OUT}/register_rows.tsv'), delimiter='\t'):
    if r['r9_alias'] and r['r9_alias'] != r['class_id'] and r['kind'] == 'judged':
        ALIASES.setdefault(r['class_id'], set()).add(r['r9_alias'])
    import re as _re
    m = _re.search(r'judge class "(.*?)"', r['note'])
    if m:
        ALIASES.setdefault(r['class_id'], set()).add('new: ' + m.group(1))
ALIASES.setdefault('N-structure-blind', set()).add('N-dead-member')

out = {'_source': 'Phase A1 v2 (one-time enumeration, rounds 1-9). Counting rule: judged survivors plus counted instances beyond them (defect-root-cause.md:88-89, audit-verify.js:211-214). Instances derived from register_rows.tsv by derive.py; mechanisms of existing ids kept verbatim from origin/main 3490cb16 tools/audit/bugclasses.json; mechanism_note flags where R8/R9 members stretch them. Classification reasons: reclassifications.md.'}
for cid, c in v1.items():
    if cid.startswith('_'):
        continue
    e = {'kind': c['kind'], 'mechanism': c['mechanism'], 'mechanism_note': NOTES.get(cid),
         'aliases': sorted(ALIASES.get(cid, [])), 'instances': {}, 'total': 0, 'max_per_round': 0,
         'detector': c['detector'], 'detector_idea': c['detector_idea'], 'barrier': c['barrier'], 'status': c['status']}
    nr = [i for i in c['instances'] if i.startswith('v') or i.startswith('#')]
    if nr:
        e['non_round_instances'] = nr
        e['non_round_note'] = 'Incident-derived instances carried in v1; not audit findings, not in register_rows.tsv, not counted in total.'
    out[cid] = e
for cid, c in NEW.items():
    out[cid] = {'kind': c['kind'], 'mechanism': c['mechanism'], 'mechanism_note': None,
                'nearest_existing': c['nearest_existing'], 'mechanism_difference': c['mechanism_difference'],
                'aliases': sorted(ALIASES.get(cid, [])), 'instances': {}, 'total': 0, 'max_per_round': 0,
                'detector': None, 'detector_idea': c['detector_idea'], 'barrier': None, 'status': 'open', 'new_in_v2': True}
json.dump(out, open(f'{OUT}/classes_v2.json', 'w'), indent=2, ensure_ascii=False)
open(f'{OUT}/classes_v2.json', 'a').write('\n')
print(len(out) - 1, 'classes')
