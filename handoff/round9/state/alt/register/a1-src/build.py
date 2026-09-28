#!/usr/bin/env python3
"""Builds register_rows.tsv and the metadata half of classes_v2.json.

Helper for phase A1; derive.py (in OUT) owns the counts. Classification
decisions are the tables below; reasons are in reclassifications.md.
"""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
SRC = HERE

REF17 = '12743bf7'
REF8 = '3490cb16'
REFJ = 'bad458a38d'
REFPLAN = '27049219a8'
SWEEP_REF = {'S1': 'c44e7bcd60', 'S2': '38f1230e92', 'S3': '053c4869ad', 'S4': 'b2e3560671',
             'S5': '51a2e98a86', 'S6': '6b65c9c4a8', 'S7': '1152a74346'}

# ---------------------------------------------------------------- R1-7 flags
# (round, id) -> (suggested class, confidence, reason). Flag only: class_id stays v1's.
FLAGS17 = {
    ('R1', 'D9-01'): ('N-solve-recompute', 'med', 'batched gradient bypassed: avoidable solve CPU, not event-loop starvation'),
    ('R2', 'D9-03'): ('N-solve-recompute', 'med', 'batched jac re-evaluates f(x): avoidable recomputation in the solve'),
    ('R4', 'D9-05'): ('N-solve-recompute', 'high', 'cost recomputed in a per-row Python loop: exactly R9 D9-s1-01 shape'),
    ('R7', 'D9-02'): ('N-solve-recompute', 'high', 'polish-per-candidate _lbfgsb_restart share: same seam as R8 D9-s1-01'),
    ('R5', 'D9-05'): ('N-solve-recompute', 'high', '#1208 polish-every-candidate cost share: same seam as R7 D9-02 / R8 D9-s1-01; not a gate-blind (I1) finding'),
    ('R1', 'D7-03'): ('P2', 'low', 'scalar vs batch physics duplicated (one fact computed twice); not loop starvation'),
    ('R2', 'D8-04'): ('N-name-sort', 'med', 'alphabetical order splits entity families: name-sort mechanism, no predicate involved'),
    ('R4', 'D8-01'): ('N-name-sort', 'med', 'alphabetical order interleaves foreign entities in family spans'),
    ('R5', 'D8-01'): ('N-name-sort', 'med', 'card-addressed sensors sort into 3 entity-id blocks'),
    ('R3', 'D8-03'): ('N-name-sort', 'med', 'names mix leading/trailing nouns so sort splits families'),
    ('R5', 'D8-02'): ('N-name-sort', 'med', 'Swedish names drop family lead tokens: R9 D8-s3-01 split in sv'),
    ('R2', 'D1-05'): ('N-shared-config', 'med', 'async_simulate shares live DefrostDerate/gains/dhw_windows with the loop mid-solve'),
    ('R6', 'D7-02'): ('N-structure-blind', 'med', "structure.py's dead-symbol check reads 0 over a 379-line dead method: metric blind, not docs drift"),
    ('R2', 'D7-06'): ('N-structure-blind', 'low', 'dead defs no gate script starts: dead production members'),
    ('R7', 'D2-02'): ('N-structure-blind', 'low', 'unreachable duplicate return line: dead code, not a mutation-kill miscount'),
    ('R2', 'D2-02'): ('P3', 'low', 'COP law non-monotone with a mixing valve: physics formula, not currency/unit precedence'),
    ('R4', 'D2-04'): ('P3', 'med', 'COP floor applied before Carnot/DHW factors: a floor applied inconsistently, not currency/unit'),
    ('R5', 'D12-01'): ('P2', 'med', 'ECL110 commands published where no ecl110 key: an "is configured" gate missing at a sibling seam, not unit precedence'),
    ('R2', 'D10-01'): ('P2', 'med', 'no duplicate-entry guard: same defect as R1 D10-03 (P2) and R9 D10-s1-01 (P2), filed here as I5'),
    ('R6', 'D2-01'): ('P3', 'low', 'hard-edged buckets make COP step across 1e-9 C: discontinuity like R2 D2-05/R4 D2-03 (P3)'),
    ('R4', 'D7-02'): ('P5', 'low', 'sysid sizing model ignores the house slab constants: model-structure mismatch like R4 D7-01'),
    ('R3', 'D9-02'): ('N-restart', 'med', 'fuse advisor rate limit memory-only, lost at restart: state not surviving restart'),
    ('R3', 'D1-03'): ('N-future-instant', 'med', 'backward clock step makes a recorded instant lie ahead of now; the watchdog trusts it (in-process, not persisted)'),
    ('R1', 'D7-01'): ('none', 'low', 'coordinator size/coupling: architecture finding, no mechanism class fits (candidate: coordinator concentration)'),
    ('R2', 'D7-05'): ('none', 'low', 'coordinator size/coupling: architecture finding, no mechanism class fits'),
    ('R1', 'D10-01'): ('none', 'low', 'HA quality-scale code conformance (service registration), not docs drift'),
    ('R1', 'D10-02'): ('none', 'low', 'HA quality-scale code conformance (runtime_data), not docs drift'),
    ('R1', 'D10-12'): ('none', 'low', 'missing diagnostics platform: code conformance, not docs drift'),
    ('R2', 'D10-15'): ('P2', 'low', 'two energy sensors lack the ENERGY device class their siblings carry'),
    ('R7', 'D9-01'): ('none', 'low', 'recorder payload redundancy: an efficiency finding with no producer/consumer key mismatch'),
}

# ------------------------------------------------------------------ R8
# id -> (class, confidence, note)
R8 = {
    'D0-s1-01': ('P4', 'high', 'ftol=1e-6 stop short; survived, not filed: duplicate of owner refusal #1293'),
    'D1-s1-01': ('N-shared-config', 'high', 'away-setback unwind in the solve finally reverts a concurrent set_thermal_parameters write; same mechanism as R9 D1-s3-04'),
    'D1-s1-02': ('N-shared-config', 'med', 'diagnose service reads live state on the executor; alt P2 (the button path deepcopies, the service path does not)'),
    'D1-s2-01': ('P1', 'high', 'non-numeric ledger leaf passes from_dict'),
    'D1-s3-01': ('P1', 'med', 'wrong-shaped Open-Meteo member raises out and fails the cycle: malformed live-feed value, precedent R5 D1-07 (P1)'),
    'D2-s1-01': ('P2', 'med', 'DHW planner prices COP at current humidity while physics uses the forecast: one fact decided twice'),
    'D2-s1-02': ('P2', 'med', 'DHW COP keeps its own lift law beside flow_lift_factor: two laws for one fact'),
    'D2-s2-01': ('P3', 'low', 'PeakTracker bills top-k windows not top-k days; alt P2 (catalog rule vs tracker rule) or P11 (external tariff modelled from the code)'),
    'D2-s2-02': ('P8', 'high', 'entity price unit never read: öre/kWh and SEK/MWh reach the plan at 83x/829x'),
    'D3-s1-01': ('I1', 'high', 'refusal rc scored as a kill: R7 D3-02 shape'),
    'D3-s1-02': ('I2', 'med', "cache key's input set diverges from what the capture reads"),
    'D3-s2-01': ('I1', 'high', 'clamp deletion survives the closure'),
    'D3-s2-02': ('I1', 'high', 'boundary mutant survives both service call sites'),
    'D4-01': ('P9', 'med', 'keyboard Tab order: card a11y, stretches P9 (see mechanism_note)'),
    'D4-s2-01': ('I5', 'high', 'untranslated sv label: translation coverage, I5 by R1-7 precedent'),
    'D5-s1-01': ('I5', 'high', 'README diagram vs prose numbering'),
    'D5-s2-01': ('I5', 'high', 'comments name symbols that do not exist'),
    'D6-s1-01': ('I5', 'high', 'README requirements omit threadpoolctl'),
    'D7-s1-01': ('P2', 'high', 'sysid experiment ignores _learning_frozen the learners honour: R1 D7-05 shape'),
    'D7-s1-02': ('P5', 'high', 'one-room sysid cannot identify two-zone plant; #1524, which main\'s P5 barrier cites'),
    'D7-s1-03': ('P6', 'med', 'refusal path writes no reason; published view falls back to completed/ok (#1525); alt P2'),
    'D7-s2-01': ('N-structure-blind', 'med', "structure.py's name-based dead-code screen reads 0 over 12 dead symbols"),
    'D7-s2-02': ('N-structure-blind', 'med', 'a pure rename moves the cross_seam_edges ratchet: same metric blindness as R9 D7-s1-01'),
    'D7-s2-03': ('I1', 'high', 'branch disabled, no driver notices'),
    'D8-s1-01': ('P2', 'med', 'non-finite scrub on the sensor base only, not the shared entity base; alt P1 (R2 D8-02 precedent)'),
    'D8-s2-02': ('P2', 'high', 'static enabled-default where the gating input is configured: entity default-enabled family'),
    'D9-s1-01': ('N-solve-recompute', 'high', 'per-candidate polish spends gradients on discarded results: same seam as R7 D9-02'),
    'D9-s2-01': ('I1', 'med', 'no budgeted gate covers the coordinator cycle: perf-gate blindness, I1 by R2 D9-02/R4 D9-06 precedent'),
    'D10-s1-01': ('I5', 'high', 'quality_scale.yaml claim contradicted by code'),
    'D10-s1-02': ('I5', 'high', 'quality_scale.yaml claim contradicted by 4 raise sites'),
    'D11-s1-01': ('I3', 'high', 'body edit re-creates skipped required check runs'),
    'D11-s1-03': ('I3', 'high', 'Stop hook misses the staged policy change'),
    'D11-s2-01': ('I3', 'high', 'required checks run unowned PR-editable code (merged: D11-s1-02)'),
    'D11-s2-02': ('I3', 'high', 'release publishes a ref not on main'),
    'D11-s2-03': ('I3', 'high', 'install commands not hash-pinned: R4 D11-07 shape'),
    'D12-s1-01': ('P2', 'high', 'domain accepted at assign_entity, actuation assumes switch: R9 D12-s2-02 shape'),
    'D12-s1-02': ('P2', 'high', 'boost switch created without the has-DHW gate its siblings honour'),
    'D13-s1-01': ('I4', 'high', 'two yield definitions disagree: R6 D13-01/02 shape'),
    'D13-s1-02': ('I3', 'high', 'owner-approved merges bypass the fix-review verdict'),
}

# ------------------------------------------------------------------ R9 aliases
# judge class name -> (roster alias, v2 class, confidence)
R9MAP = {
    'avoidable interpreter-bound recomputation in the solve': ('N-solve-recompute', 'N-solve-recompute', 'high'),
    'CPU gate blind to a regression outside its sampled work': ('N-cpu-gate-blind', 'I1', 'med'),
    'CPU work inline on the event loop': ('N-loop-cpu', 'P10', 'high'),
    'live input with no physical-plausibility bound': ('N-plausibility', 'P1', 'med'),
    'persisted future instant trusted without bound': ('N-future-instant', 'N-future-instant', 'high'),
    'production member reached by no production code': ('N-dead-member', 'N-structure-blind', 'med'),
    'structure metric blind to a code shape': ('N-structure-blind', 'N-structure-blind', 'high'),
    'user state not surviving restart': ('N-restart', 'N-restart', 'high'),
    'a sign floor on a price margin breaks the stated piecewise identity': ('N-sign-floor', 'P3', 'med'),
    'an approval bound to an exact head is re-bought on a diff-identical move': ('N-approval-rebuy', 'N-approval-rebuy', 'med'),
    'an entity family whose names do not lead with a shared token splits under the name sort': ('N-name-sort', 'N-name-sort', 'high'),
    'compatibility duplicate entity enabled by default': ('N-dup-entity', 'P2', 'med'),
    'whole-entity availability gated on an optional input': ('N-availability', 'P2', 'med'),
    'error-translating try opened after the call it should cover': ('N-late-try', 'P2', 'med'),
    'explicit-Euler stability judged per store instead of on the coupled step matrix': ('N-euler-coupled', 'P3', 'low'),
    'fit integrator differs from the simulated plant': ('N-fit-integrator', 'P5', 'med'),
    "learned-correction clamp sized against an assumed range, not the model's curve": ('N-clamp-range', 'P3', 'low'),
    'markdown the renderer misplaces': ('N-markdown', 'I5', 'med'),
    'missing icons.json services block': ('N-service-icons', 'I5', 'high'),
    'persistent failure swallowed at DEBUG': ('N-debug-swallow', 'P6', 'med'),
    'pointer-only editing with no keyboard route': ('N-keyboard', 'P9', 'med'),
    'return inside finally': ('N-finally-return', 'N-finally-return', 'med'),
    'selector minimum off its own step grid': ('N-step-grid', 'N-step-grid', 'low'),
    'series resolution inferred from the minimum gap': ('N-min-gap', 'P1', 'low'),
    'service input without an upper-bound clamp': ('N-service-clamp', 'P1', 'low'),
    'shutdown reap waits on the lock a solve holds': ('N-reap-lock', 'N-reap-lock', 'low'),
    'solve-scoped mutation of shared live config seen by a concurrent reader': ('N-shared-config', 'N-shared-config', 'high'),
    "staleness limit shorter than a report-on-change sensor's quiet interval": ('N-staleness', 'N-staleness', 'low'),
    'state-blind menu re-offers a completed path': ('N-menu', 'P2', 'med'),
    'text producer takes no language parameter': ('N-language', 'I5', 'med'),
    'translation leaf double-escaped': ('N-escape', 'I5', 'med'),
}
# roster alias -> class issue (FIX-PLAN.md "Class to PR")
ISSUE9 = {'P2': 1644, 'I5': 1645, 'I1': 1646, 'P1': 1647, 'I3': 1648, 'P11': 1649, 'I4': 1650, 'P6': 1651,
          'P9': 1652, 'N-solve-recompute': 1653, 'P3': 1654, 'P5': 1655, 'N-cpu-gate-blind': 1656, 'P8': 1657,
          'N-loop-cpu': 1658, 'N-plausibility': 1659, 'N-future-instant': 1660, 'N-dead-member': 1661,
          'N-restart': 1662, 'I2': 1663, 'P4': 1664, 'P7': 1665, 'N-sign-floor': 1666, 'N-approval-rebuy': 1667,
          'N-name-sort': 1668, 'N-dup-entity': 1669, 'N-late-try': 1670, 'N-euler-coupled': 1671,
          'N-fit-integrator': 1672, 'N-clamp-range': 1673, 'N-markdown': 1674, 'N-service-icons': 1675,
          'N-debug-swallow': 1676, 'N-keyboard': 1677, 'N-finally-return': 1678, 'N-step-grid': 1679,
          'N-min-gap': 1680, 'N-service-clamp': 1681, 'N-reap-lock': 1682, 'N-shared-config': 1683,
          'N-staleness': 1684, 'N-menu': 1685, 'N-structure-blind': 1686, 'N-language': 1687, 'N-escape': 1688,
          'N-availability': 1689}
# R9 judged rows kept in the judge's existing class but flagged (flag only)
FLAGS9 = {
    'D1-s5-52': ('P1', 'med', 'sentinel -127/85 delivered as ok: the N-plausibility mechanism (now P1), judged P2 after G1-V3'),
    'D1-s5-03': ('P1', 'low', 'one huge JSON integer voids a whole fetch: malformed-input-voids-feed like R5 D1-07 (P1)'),
    'D1-s3-01': ('P1', 'low', 'naive stored/return datetime wedges the cycle: D1-s1-01 (P1) shape at the away seam'),
    'D2-s4-02': ('P5', 'low', 'sysid step sized to the abort bound: a sysid design defect, not a divergent predicate'),
    'D4-s2-01': ('I5', 'low', 'unlabelled/untranslated pre-fill fields: translation coverage, I5 by R1-7 precedent'),
    'D10-s2-01': ('I5', 'low', 'preset states with no translation or icon: translation/icon coverage, I5 by R1-7 precedent'),
    'D7-s3-02': ('N-structure-blind', 'med', "structure.py dead_methods census blind to properties/bare loads: same metric as R8 D7-s2-01"),
}
REFUSED9 = {'D8-s2-01': "refused by tvofi (card C15, 'Keep'); class issue #1689 closed not planned",
            'D11-s1-01': "refused by tvofi (card C16, 'Leave'); recorded in #1648"}

# ------------------------------------------------------------------ R9 counted instances beyond judged
# (id, v2 class, alias, found_by, confidence, source, note)
R9EXTRA = [
    ('RC-sw1', 'N-solve-recompute', 'avoidable interpreter-bound recomputation in the solve', 'S5', 'high',
     f"{SWEEP_REF['S5']}:tools/audit/round9/D14/sweep/S5.json:@seam4", 'cycling_penalty_batch per-row loop; the other ThermalParameters seams S5 listed are folded into D9-s1-71 (SWEEP.md) and not counted'),
    ('RC-rca1', 'N-solve-recompute', 'avoidable interpreter-bound recomputation in the solve', 'RCA', 'med',
     f'{REFPLAN}:handoff/round9/FIX-PLAN.md:814', 'tariff.peak_cost_batch per-row loop; RCA-found (FIX-PLAN §10 RCA fold), not sweep-found'),
    ('RC-rca2', 'N-solve-recompute', 'avoidable interpreter-bound recomputation in the solve', 'RCA', 'med',
     f'{REFPLAN}:handoff/round9/FIX-PLAN.md:815', '_terminal_cost_batch closure per-row loop; RCA-found, S5 disposed it not applicable'),
    ('FI-sw1', 'N-future-instant', 'persisted future instant trusted without bound', 'S7', 'high',
     f"{SWEEP_REF['S7']}:tools/audit/round9/D14/sweep/S7.json:@seam5", 'fuse-advisor cooldown; RCA: month-bounded'),
    ('FI-sw2', 'N-future-instant', 'persisted future instant trusted without bound', 'S7', 'high',
     f"{SWEEP_REF['S7']}:tools/audit/round9/D14/sweep/S7.json:@seam6", 'heavy-snow damping window'),
    ('FI-sw3', 'N-future-instant', 'persisted future instant trusted without bound', 'S7', 'high',
     f"{SWEEP_REF['S7']}:tools/audit/round9/D14/sweep/S7.json:@seam7", '_detect_outage last_tick; not reached by the barrier (main register)'),
    ('FI-sw4', 'N-future-instant', 'persisted future instant trusted without bound', 'S7', 'med',
     f"{SWEEP_REF['S7']}:tools/audit/round9/D14/sweep/S7.json:@seam9", 'immersion-event recency; S7 did not probe it separately, the RCA reproduced it'),
    ('FI-sw5', 'N-future-instant', 'persisted future instant trusted without bound', 'S7', 'high',
     f"{SWEEP_REF['S7']}:tools/audit/round9/D14/sweep/S7.json:@seam8", 'pump_arbiter write-echo grace'),
    ('FI-rca1', 'N-future-instant', 'persisted future instant trusted without bound', 'RCA', 'med',
     f'{REFPLAN}:handoff/round9/FIX-PLAN.md:821', 'legionella parse_datetime restore; RCA-found (S7 grep cannot see parse_datetime)'),
    ('P5-rca1', 'P5', '', 'RCA', 'med',
     f'{REFPLAN}:handoff/round9/FIX-PLAN.md:805', 'half-declared slab mass admitted; RCA-found (P5 axis sweep)'),
    ('P9-rca1', 'P9', '', 'RCA', 'med', f'{REFPLAN}:handoff/round9/FIX-PLAN.md:806', 'armed clear button 4.29:1 contrast; RCA-found'),
    ('P9-rca2', 'P9', '', 'RCA', 'med', f'{REFPLAN}:handoff/round9/FIX-PLAN.md:807', "'estimated prices' label 3.94:1; RCA-found"),
    ('P9-rca3', 'P9', '', 'RCA', 'med', f'{REFPLAN}:handoff/round9/FIX-PLAN.md:808', 'now label vs estimated-prices label shared ink; RCA-found; D4-s1-05 mechanism at a second seam'),
    ('P9-rca4', 'P9', '', 'RCA', 'low', f'{REFPLAN}:handoff/round9/FIX-PLAN.md:809', 'slot-hit target spacing; RCA-found, a counted candidate needing a fix design'),
    ('P9-f61a', 'P9', '', 'fixer-F6.1', 'low', f'{REFPLAN}:handoff/round9/FIX-PLAN.md:810', 'found by the F6.1 fixer re-measuring the RCA grid; table labels it S5; seam not named'),
    ('P9-f61b', 'P9', '', 'fixer-F6.1', 'low', f'{REFPLAN}:handoff/round9/FIX-PLAN.md:811', 'found by the F6.1 fixer; pointer-only hit targets; seam not named'),
    ('P9-f61c', 'P9', '', 'fixer-F6.1', 'low', f'{REFPLAN}:handoff/round9/FIX-PLAN.md:812', 'found by the F6.1 fixer; deferred tap-target candidate'),
]


def jline(path, fid, nextkey):
    lines = open(path).read().split('\n')
    for i, l in enumerate(lines):
        if f'"id": "{fid}"' in l and any(f'"{nextkey}"' in x for x in lines[i + 1:i + 3]):
            return i + 1
    return 0


def seam_line(sweep, cls_sub, idx):
    """line of the idx-th seam 'path' key inside the class whose name contains cls_sub."""
    p = f'{SRC}/r9/tools/audit/round9/D14/sweep/{sweep}.json'
    lines = open(p).read().split('\n')
    start = next(i for i, l in enumerate(lines) if '"class"' in l and cls_sub in l)
    n = -1
    for i in range(start, len(lines)):
        if '"path"' in lines[i]:
            n += 1
            if n == idx:
                return i + 1
    return 0


rows = []
# R1-7
r3issue = {}
for l in open(f'{SRC}/r3_filed.tsv'):
    p = l.rstrip('\n').split('\t')
    if len(p) >= 3:
        r3issue[p[0]] = '#' + p[2].rsplit('/', 1)[-1]
with open(f'{SRC}/r17_findings.tsv') as f:
    for ln, l in enumerate(f, 1):
        if ln == 1:
            continue
        p = l.rstrip('\n').split('\t')
        rnd, fid, sev, cls, summ = p[0], p[1], p[2], p[3], p[4]
        conf, note = 'high', f'{sev}; {summ}'
        fl = FLAGS17.get((rnd, fid))
        if fl:
            conf = fl[1]
            note = f'FLAG->{fl[0]} ({fl[2]}); {note}'
        rows.append([rnd, fid, r3issue.get(fid, '') if rnd == 'R3' else '', cls, '', 'judged', conf,
                     f'{REF17}:handoff/round8/findings.tsv:{ln}', note])

# R8
j8 = json.load(open(f'{SRC}/r8_JUDGE.json'))
issue8 = {}
for l in open('/tmp/claude-0/-home-user-heatpump-optimizer/1b5fa08f-9bd8-59e8-b197-ffb291fc579e/scratchpad/main/docs/audit-2026-09.md').read().split('\n')[1997:2048]:
    m = re.match(r'\| (D[\w-]+) \| (#\d+) \|', l)
    if m:
        issue8[m.group(1)] = m.group(2)
for v in j8['verdicts']:
    if v['verdict'] not in ('verified', 'weakened'):
        continue
    cls, conf, note = R8[v['id']]
    note = f"{v['verdict']} {v['severity']}; {note}"
    rows.append(['R8', v['id'], issue8.get(v['id'], ''), cls, '', 'judged', conf,
                 f"{REF8}:tools/audit/round8/JUDGE.json:{jline(f'{SRC}/r8_JUDGE.json', v['id'], 'dim')}", note])
assert set(R8) == {r[1] for r in rows if r[0] == 'R8'}, 'R8 table mismatch'

# R9 judged
j9p = f'{SRC}/r9/tools/audit/round9/judge/JUDGE.json'
j9 = json.load(open(j9p))
for f in sorted(j9['findings'], key=lambda x: x['id']):
    if not (f['verdict'] == 'verified' or f['verdict'].startswith('weakened')):
        continue
    jc = f['class']
    if jc.startswith('new: '):
        alias, cls, conf = R9MAP[jc[5:]]
    else:
        alias, cls, conf = '', jc, 'high'
    issue = f"#{ISSUE9[alias or jc]}"
    note = f"{f['verdict']} {f['severity']}; {f['title']}"
    if f['merged']:
        note += f" (merged: {','.join(f['merged'])})"
    if f['id'] in REFUSED9:
        note += f"; {REFUSED9[f['id']]}"
    if alias:
        note = f'judge class "{jc[5:]}"' + (f' re-mapped {alias}->{cls}' if alias != cls else ' kept') + f'; {note}'
    fl = FLAGS9.get(f['id'])
    if fl:
        conf = fl[1]
        note = f'FLAG->{fl[0]} ({fl[2]}); {note}'
    rows.append(['R9', f['id'], issue, cls, alias, 'judged', conf,
                 f"{REFJ}:tools/audit/round9/judge/JUDGE.json:{jline(j9p, f['id'], 'dim')}", note])

# R9 beyond-judged
for iid, cls, jcls, by, conf, src, note in R9EXTRA:
    if '@seam' in src:
        sw = src.split('/')[-1].split('.')[0]
        idx = int(src.rsplit('@seam', 1)[1])
        sub = 'avoidable' if sw == 'S5' else 'future instant'
        src = src.split(':@')[0] + ':' + str(seam_line(sw, sub, idx))
    alias = {'N-solve-recompute': 'N-solve-recompute', 'N-future-instant': 'N-future-instant'}.get(cls, '')
    rows.append(['R9', iid, f"#{ISSUE9[cls]}", cls, alias, 'sweep', conf, src, f'found_by={by}; {note}'])

with open(f'{OUT}/register_rows.tsv', 'w', newline='') as fh:
    w = csv.writer(fh, delimiter='\t', lineterminator='\n')
    w.writerow(['round', 'finding_id', 'issue', 'class_id', 'r9_alias', 'kind', 'confidence', 'source', 'note'])
    for r in rows:
        w.writerow([c.replace('\t', ' ').replace('\n', ' ') for c in r])
print(len(rows), 'rows')
