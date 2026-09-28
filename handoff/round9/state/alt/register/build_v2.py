#!/usr/bin/env python3
"""Build bug-class register v2 (tools/audit/bugclasses.json) from the one-time enumeration.

Inputs, all beside this file:
  register_rows.tsv   one row per surviving finding, rounds 1-9 (phase A1); a note may carry FLAG-><class>
  classes_v2.json     A1's class entries (mechanism, detector, barrier, status, aliases, non-round instances)
  rca_inventory.json  every RCA conducted to 2026-09-28 (phase A2)
  rca_scheduled.json  every RCA scheduled or owed (phase A2)

Outputs:
  rows_v2.tsv          the rows with final_class and move (the classification that counts)
  bugclasses.v2.json   the register: v1-compatible class fields plus per_round, total, max_per_round,
                       aliases, rca, rca_planned, trigger; top-level _unclassified and _rca
  trigger.out          which classes owe an RCA under each trigger arm, and which still lack one

  python3 build_v2.py           build and print trigger.out
  python3 build_v2.py --check   rebuild in memory; exit 1 if bugclasses.v2.json or rows_v2.tsv differ

Every count is derived from rows_v2.tsv; nothing is carried by hand.
"""
import csv, io, json, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROUNDS = [f'R{i}' for i in range(1, 10)]
ALT = 'handoff/audit-r9-alt:handoff/round9/state/alt'

# ---- moves beyond A1's FLAGs, each decided by an RCA seat that read the seams
RCA_MOVES = {
    ('R3', 'D3-FLAKE'): ('_unclassified', 'RCA-BULK-2 I2: a wall-clock test flake (#810), not a closure divergence'),
    ('R5', 'R5-INST-01'): ('I4', 'RCA-BULK-2 I2: a hand-typed dimension list, guarded by check-wave-script.mjs/check_scopes.py'),
    ('R7', 'R7-INSTR-01'): ('I4', 'RCA-BULK-2 I2: a hand-typed dimension list, as R5-INST-01'),
}

# ---- class-level updates the bulk RCAs established (text fields only; counts stay derived)
UPDATES = {
    'P4': {
        'status': 'detector',
        'detector': 'PYTHONPATH=tests/hastub python3 tests/optimality.py (the solve certificate, #1409)',
        'barrier_refusal': 'Class-eliminating barrier refused on numbers (RCA-BULK-1): tighter ftol cost 6.4 % money on one '
                           'backtest cell at 2.4x CPU (#1293, #1294, owner-refused); the certificate stays the detector',
    },
    'P7': {
        'barrier_gap': 'RCA-BULK-1 measured two blind spots of the F1.1 tracer: the R3 tariff seam (#777; the replay '
                       'fixture configures no capacity tariff) and the R5 plan-age seam (#1299; its operands never straddle '
                       'the transition in the replayed day). Both re-introduced shapes pass main\'s dst_checks.py. '
                       '13 raw zoned-datetime sites remain (services.py:873 / manual_plan.py:288: a 20 h override lasts 21 h '
                       'across the autumn fold). Owed: a config arm and a straddle arm (R9-F10.1c)',
    },
    'P8': {
        'detector_idea': 'The published money unit is the price feed\'s currency: replay with a EUR/kWh feed on a SEK instance '
                         'and count published money units in the instance currency (11/11 at 3490cb16; 0 when fixed). '
                         'currency.py already is the one shared resolver, and it canonicalises the instance label, not the '
                         'feed: forcing every surface through it (#1657\'s proposal) would lock the defect in (RCA-BULK-1)',
    },
    'P10': {
        'mechanism': 'CPU work (a model kernel, a fit, a batch simulation) runs outside the process worker, on the event loop '
                     'or on a GIL-holding executor thread, and starves the loop',
        'mechanism_note': 'Widened from "a solve on a GIL-holding thread starves the loop" (RCA-BULK-1): R9 re-minted it as '
                          'N-loop-cpu because the v1 text excluded loop-inline work',
        'detector_idea': 'Count model-kernel calls outside the process worker over a replayed day: 2304 on the loop at '
                         '3490cb16 (topology.py _advisor_replay), 0 with the advisor removed, 3926 on an executor thread when '
                         'the worker is forced to fail (RCA-BULK-1 p10_loop_kernels.py); extend the kernel list to sysid',
    },
    'I2': {
        'detector_idea': 'Nightly strace -f of the gate against the committed closures, reporting files the recorder missed '
                         '(child-process reads, .pyc-only loads); over-scope needs no barrier (RCA-BULK-2)',
    },
    'N-structure-blind': {
        'detector_idea': 'Liveness by reachability from production roots (tests are not roots), with a self-check planting one '
                         'example per past shape and a printed count of shapes the metric cannot measure (RCA-BULK-2)',
    },
    'N-shared-config': {
        'detector_idea': 'alt/evidence/m1_hub_writes.py: solve-path hub write sites must be 0 once the per-solve record lands '
                         '(26 sites / 23 fields at c54b20d2); extend to _current_action and the what-if cache (#1752, #1753)',
    },
}

NEW_CLASSES = {
    'N-silent-zero': {
        'kind': 'instrument',
        'mechanism': 'A derivation\'s failure path returns the same empty value as its success path, so a count over a set '
                     'never enumerated reads as a clean zero',
        'nearest_existing': 'I1',
        'mechanism_difference': 'I1 is a mutation kill miscounted or a vacuous guard; this is any derivation (a census, a '
                                'sample, a --stats line) whose failure is indistinguishable from an empty success',
        'members_elsewhere': ['R8 D7-s2-01', 'R9 D7-s3-02', 'R9 D13-s1-01', 'R9 D14-s4-02', 'R9 D9-s2-71'],
        'members_note': 'One mechanism class per finding: these members count under their own classes (I1, I4, P11, '
                        'N-structure-blind); listed here so the cross-cutting count is visible. #1041 recorded 5 earlier '
                        'sightings outside audit rounds and RCA-BULK-3 counts 8 new ones since 2026-09-16 (1 per 3.1 releases)',
        'detector': None,
        'detector_idea': 'Register count-printing instruments (structure.py dead_*, stress sampling, policy_lint --stats) in '
                         'field_coverage.mjs\'s perturb-to-red registry; merge_shape_guard for the merge-subject derivation',
        'barrier': None,
        'status': 'open',
    },
}

NON_ROUND_ADD = {
    'N-shared-config': [
        'mold-guard cap reads the configured target (v4.0.0, 32e2d8e4; reader taught)',
        '#1752 boost overlay mutates _current_action in place (screen S1)',
        '#1753 tile/advisor borrow the what-if cache and restore unconditionally (screen S2)',
        '#1754 manual override swapped mid-solve inherits the old releases (screen C2)',
        'H1 concurrent cycle publishes the away setback (screen, carried to R9-EG-B1)',
        'H3 dhw_hourly_draw_pattern has two writers (screen, carried to R9-EG-B1)',
        'H4 external_heat_active read from the per-solve copy (screen, carried to R9-EG-B1)',
    ],
    'P10': ['v6.6.0 options-flow freeze (provisional; cause not established, RCA-BULK-3)',
            '#70 v5.1.1 options save froze the instance (provisional)'],
}

# ---- RCA -> class. Process RCAs (no audit bug class) map to None and are indexed only
RCA_CLASS = {
    'RCA-1336-d9-memory-arm': 'I1', 'RCA-vacuous-acceptance-arm': 'I1', 'RCA-1485-ledger-line-shift': 'I1',
    'RCA-1595-nan-ratchets': 'I1', 'RCA-R8-I1a-kill-rule': 'I1', 'R9-I1': 'I1', 'R9-N-cpu-gate-blind': 'I1',
    'RCA-1514': 'I3', 'RCA-1515': 'I3', 'RCA-R8-I3-1516': 'I3', 'RCA-1567-unpinned-installs': 'I3',
    'R9-RC1-pinned-local': 'I3', 'R9-I3': 'I3', 'RCA-1589-policy-docs-red': 'I3',
    'R9-I4': 'I4', 'RCA-R8-I5b': 'I5', 'RCA-1546': 'I5', 'R9-I5': 'I5',
    'RCA-1499': 'P2', 'RCA-R8-P2': 'P2', 'R9-P2': 'P2', 'RCA-R8-P1': 'P1', 'R9-P1': 'P1',
    'RCA-R8-P3': 'P3', 'RCA-coil-drain': 'P3', 'R9-P3': 'P3',
    'RCA-1525': 'P5', 'RCA-R8-P5-1523': 'P5', 'R9-P5': 'P5', 'RCA-R8-P6-1526': 'P6', 'R9-P6': 'P6',
    'RCA-R8-P8-1513': 'P8', 'RCA-R8-P9-1522': 'P9', 'R9-P9': 'P9',
    'V6612-bug5-switch': 'P11', 'V6612-listener-callback': 'P11', 'V6612-bug3-4-echo': 'P11',
    'V6612-bug1-6-ownership': 'P11', 'V6612-bug2-lease': 'P11', 'V6612-bug7-card-history': 'P11', 'R9-P11': 'P11',
    'R9-RC2-bug5-reboot': 'N-restart', 'R9-1638-clobbered-store': 'N-restart', 'PRE-1249-picker-revert': 'N-restart',
    'R9-N-future-instant': 'N-future-instant', 'R9-N-solve-recompute': 'N-solve-recompute',
    'RCA-R8-P12-1517-1529': 'N-shared-config', 'R9-RCA-1736': 'N-shared-config',
    'RCA-1041-silent-zero': 'N-silent-zero', 'PRE-70-v511-freeze': 'P10',
}
# class-level RCAs (the ones that answer the class trigger, as opposed to one instance's trigger 1/2)
CLASS_LEVEL = {'R9-I1', 'R9-N-cpu-gate-blind', 'R9-I3', 'R9-I4', 'R9-I5', 'R9-P1', 'R9-P2', 'R9-P3', 'R9-P5', 'R9-P6',
               'R9-P9', 'R9-P11', 'R9-RC2-bug5-reboot', 'R9-N-future-instant', 'R9-N-solve-recompute', 'R9-RCA-1736',
               'RCA-1041-silent-zero', 'BULK-1-P4', 'BULK-1-P7', 'BULK-1-P8', 'BULK-1-P10', 'BULK-2-I2',
               'BULK-2-N-structure-blind'}

NEW_RCAS = [
    ('BULK-1-P4', 'P4', 'refuse barrier; certificate is the detector (owner refusals #1293/#1294 on record)', None, 'RCA-BULK-1.md'),
    ('BULK-1-P7', 'P7', 'build: tracer config arm + straddle arm (F1.1 barrier catches 1 of 3 historical members)', None, 'RCA-BULK-1.md'),
    ('BULK-1-P8', 'P8', 'build: carry the feed currency from ingest + EUR-feed check; refuse #1657\'s resolver metric', None, 'RCA-BULK-1.md'),
    ('BULK-1-P10', 'P10', 'build: model-kernel calls outside the process worker = 0 (2304 on the loop at main)', None, 'RCA-BULK-1.md'),
    ('BULK-2-I2', 'I2', 'build: nightly strace comparison; refuse an over-scope barrier', None, 'RCA-BULK-2.md'),
    ('BULK-2-N-structure-blind', 'N-structure-blind', 'build: reachability liveness + self-check + unmeasured-shape count', None, 'RCA-BULK-2.md'),
    ('BULK-2-R-register', None, 'build: fold_ledger.py + round-record PR, register --check, in-tree RCA docs; policy parts to the owner; refuse rebuilding 9 lost records', None, 'RCA-BULK-2.md'),
    ('BULK-3-1721', 'P11', 'build: governance step in graders-head-copy running the PR\'s own policy_lint/field_coverage under GITHUB_TOKEN', None, 'RCA-BULK-3.md'),
    ('BULK-3-1545', 'I5', 'confirmed: #1590\'s typing check fails at ba938dc3 and passes at main; gap: qs_py_typed_files has no check', None, 'RCA-BULK-3.md'),
    ('BULK-3-1070', None, 'band confirmed (#1124, 97d9bdb3); per-file band refused until 3 per-file frictions in one window', '97d9bdb3 (#1124)', 'RCA-BULK-3.md'),
    ('BULK-3-v660-freeze', 'P10', 'instrument first: nightly-ha loop heartbeat across options round-trips; cause not established', None, 'RCA-BULK-3.md'),
    ('BULK-3-1041-rerun', 'N-silent-zero', 'refusal overturned: land merge_shape_guard (in agreement.mjs); lint/helper refusals confirmed', None, 'RCA-BULK-3.md'),
]

PLANNED = {  # class -> roster groups owed to land its barrier or RCA countermeasure
    'P1': ['R9-F1.6'], 'P3': ['R9-F1.10'], 'P2': ['R9-F1.11'], 'P6': ['R9-F1.11'], 'P9': ['R9-F6.3'],
    'N-solve-recompute': ['R9-F10.2'], 'I1': ['R9-F10.2', 'R9-F10.3'], 'I5': ['R9-F10.4'], 'I4': ['R9-F11.4'],
    'N-shared-config': ['R9-EG-B9', 'R9-EG-B10', 'R9-EG-B1'], 'P7': ['R9-F10.1c'], 'P10': ['R9-F1.7', 'R9-F10.7'],
    'P8': ['R9-F1.8'], 'P4': ['R9-F2.4'], 'I2': ['R9-F10.3'], 'N-structure-blind': ['R9-F10.4'],
    'N-silent-zero': ['R9-F11.4'], 'P11': ['R9-F11.7'],
}


def load_rows():
    rows = list(csv.DictReader(open(os.path.join(HERE, 'register_rows.tsv')), delimiter='\t'))
    out = []
    for r in rows:
        final, move = r['class_id'], ''
        m = re.match(r'FLAG->(\S+)(?: \((.*?)\);)?', r['note'])
        if m:
            tgt = m.group(1)
            final = '_unclassified' if tgt == 'none' else tgt
            move = f'A1 flag: {r["class_id"]} -> {tgt}' + (f' ({m.group(2)})' if m.group(2) else '')
        k = (r['round'], r['finding_id'])
        if k in RCA_MOVES:
            final, why = RCA_MOVES[k]
            move = f'{r["class_id"]} -> {final}: {why}'
        out.append({**r, 'final_class': final, 'move': move})
    return out


def triggers(per):
    counts = [len(per.get(r, [])) for r in ROUNDS]
    per_round = max(counts) >= 3
    three_consec = any(sum(counts[i:i + 3]) >= 3 for i in range(len(counts) - 2))
    return per_round, three_consec, sum(counts)


def build():
    rows = load_rows()
    a1 = json.load(open(os.path.join(HERE, 'classes_v2.json')))
    inv = json.load(open(os.path.join(HERE, 'rca_inventory.json')))
    sched = json.load(open(os.path.join(HERE, 'rca_scheduled.json')))

    per = defaultdict(lambda: defaultdict(list))
    unclassified = []
    for r in rows:
        if r['final_class'] == '_unclassified':
            unclassified.append({'round': r['round'], 'finding_id': r['finding_id'], 'issue': r['issue'] or None,
                                 'was': r['class_id'], 'reason': r['move']})
        else:
            per[r['final_class']][r['round']].append(r['finding_id'])

    # ---- RCA index
    rcas = {}
    for x in inv:
        rcas[x['id']] = {
            'class': RCA_CLASS.get(x['id']), 'level': 'class' if x['id'] in CLASS_LEVEL else 'instance-or-process',
            'subject': x['subject'], 'trigger': x['trigger'], 'date': x['date'], 'status': x['status'],
            'parts_missing': [k for k, v in x['parts_present'].items() if not v],
            'process_state': x['process_state'], 'countermeasure': x['countermeasure'],
            'landed': x['landed_sha_on_main'], 'doc': x['doc_locations'],
            'in_tree_home': f'tools/audit/rca/{x["id"]}.md' if x['status'] != 'partial' or x['doc_locations'] else None,
        }
    for rid, cls, verdict, landed, doc in NEW_RCAS:
        rcas[rid] = {'class': cls, 'level': 'class' if rid in CLASS_LEVEL else 'instance-or-process',
                     'subject': rid, 'trigger': 'owed (register v2)', 'date': '2026-09-28',
                     'status': 'done' if landed else 'prototype-only', 'parts_missing': [], 'process_state': 'see doc',
                     'countermeasure': verdict, 'landed': landed, 'doc': [f'{ALT}/rca/{doc}'],
                     'in_tree_home': f'tools/audit/rca/{rid}.md'}

    # ---- classes
    reg = {
        '_source': 'v2, 2026-09-28: one-time enumeration and classification of every surviving finding of rounds 1-9 '
                   '(alt/register/rows_v2.tsv, 486 rows; A1 flags and three RCA-seat moves applied, each recorded in its '
                   'row), folded with the inventory of every RCA conducted (alt/register/rca_inventory.json) and the bulk '
                   'RCAs owed by the rebuild (alt/rca/RCA-BULK-{1,2,3}.md). v1 was seeded from the round-8 classification '
                   'of rounds 1-7 and never received a round-8 member. Counts derive from rows_v2.tsv by build_v2.py.',
        '_status': a1.get('_status') or 'open: no detector; detector: a command enumerates every seam; barriered: that command is a CI check.',
        '_counting': 'An instance is a judged survivor or an instance counted beyond it (a sweep, RCA or fixer seat found '
                     'the seam and it is not the judged site); non_round_instances are incidents and screens, listed, '
                     'not counted. trigger.per_round is the rule in force (defect-root-cause.md:87-91); '
                     'trigger.cross_round is the proposed clause (>=3 over any 3 consecutive rounds, or >=5 total while open), '
                     'owner-gated in R9-EG-R1.',
    }
    ids = [k for k in a1 if not k.startswith('_')] + [k for k in NEW_CLASSES if k not in a1]
    for cid in ids:
        base = dict(a1.get(cid) or NEW_CLASSES[cid])
        for drop in ('instances', 'rounds', 'total', 'max_per_round', 'per_round_judged_sweep', 'new_in_v2'):
            base.pop(drop, None)
        base.update(UPDATES.get(cid, {}))
        p = {r: sorted(per[cid][r]) for r in ROUNDS if per[cid].get(r)}
        pr, tc, total = triggers(p)
        class_rcas = sorted(k for k, v in rcas.items() if v['class'] == cid)
        has_class_rca = any(rcas[k]['level'] == 'class' for k in class_rcas)
        non_round = list(base.pop('non_round_instances', None) or []) + NON_ROUND_ADD.get(cid, [])
        entry = {
            'kind': base.pop('kind'), 'mechanism': base.pop('mechanism'),
            'rounds': [int(r[1:]) for r in p],
            'instances': [f'{r} {i}' for r in p for i in p[r]],
            'per_round': {r: len(v) for r, v in p.items()}, 'total': total,
            'max_per_round': max((len(v) for v in p.values()), default=0),
            'detector': base.pop('detector', None), 'detector_idea': base.pop('detector_idea', None),
            'barrier': base.pop('barrier', None), 'status': base.pop('status', 'open'),
        }
        entry.update({k: v for k, v in base.items() if v not in (None, [], '')})
        if non_round:
            entry['non_round_instances'] = non_round
        entry['rca'] = class_rcas
        entry['rca_planned'] = PLANNED.get(cid, [])
        entry['trigger'] = {
            'per_round': pr, 'cross_round': tc or (total >= 5 and entry['status'] != 'barriered'),
            'barriered_any': entry['status'] == 'barriered' and total >= 1,
            'class_rca_on_record': has_class_rca,
        }
        reg[cid] = entry
    reg['_unclassified'] = unclassified
    reg['_rca'] = rcas
    return rows, reg


def render(rows, reg):
    buf = io.StringIO()
    cols = list(rows[0].keys())
    w = csv.DictWriter(buf, fieldnames=cols, delimiter='\t', lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue(), json.dumps(reg, indent=2, ensure_ascii=False) + '\n'


def trigger_report(reg):
    lines = ['class                total maxR  per-round cross-round barriered  class-RCA  owed-and-missing']
    owed = []
    for cid, e in reg.items():
        if cid.startswith('_'):
            continue
        t = e['trigger']
        fires = t['per_round'] or t['cross_round'] or t['barriered_any']
        missing = fires and not t['class_rca_on_record']
        if missing:
            owed.append(cid)
        lines.append(f'{cid:20s} {e["total"]:5d} {e["max_per_round"]:4d}  {str(t["per_round"]):9s} {str(t["cross_round"]):11s} '
                     f'{str(t["barriered_any"]):10s} {str(t["class_rca_on_record"]):10s} {"OWED" if missing else ""}')
    lines.append(f'owed and missing a class RCA: {owed or "none"}')
    lines.append(f'unclassified rows: {len(reg["_unclassified"])}; RCAs indexed: {len(reg["_rca"])}')
    return '\n'.join(lines) + '\n', owed


if __name__ == '__main__':
    rows, reg = build()
    tsv, js = render(rows, reg)
    rep, owed = trigger_report(reg)
    paths = {'rows_v2.tsv': tsv, 'bugclasses.v2.json': js, 'trigger.out': rep}
    if '--check' in sys.argv:
        bad = [p for p, t in paths.items() if not os.path.exists(os.path.join(HERE, p)) or open(os.path.join(HERE, p)).read() != t]
        print('stale: ' + ', '.join(bad) if bad else 'ok: outputs match a rebuild')
        sys.exit(1 if bad else 0)
    for p, t in paths.items():
        open(os.path.join(HERE, p), 'w').write(t)
    print(rep, end='')
