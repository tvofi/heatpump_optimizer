#!/usr/bin/env python3
"""Roster rev 3: the live roster (handoff/audit-r9-fixplan .claude/workflows/wave-r9-groups.json at c5af8f3a)
plus the architecture-score pre-study (handoff/round9/state/alt/archscore/PRE-STUDY.md, 2026-09-29).

  python3 build_roster_rev3.py LIVE.json OUT.json

Deltas:
  1. resume truthing: R9-F1.6 merged as #1767 at f88e6af8; the live file (c5af8f3a) says not-started with an
     empty commit (LIVE-STATUS.md disagreement 1). The other 33 merged groups already read done at their merge SHAs.
  2. carries: R9-F10.4 (the metric review: retirements, merges, modifications, eleven verified metric defects,
     and the new metrics as a re-record with a reason); the expected delta-S and per-metric targets into
     R9-EG-B1, B2, B3, B5, B6, B7 (PRE-STUDY.md section 8), with the honesty obligations.
  3. new groups: R9-EG-A1 (score, report-only), R9-EG-A2 (clone consolidation), R9-EG-A3 (parameter objects),
     R9-F7.5 (the three recorded family splits, owner-gated).
  No edge is added to a planned group: the planned groups measure with the prototype until R9-EG-A1 lands.
"""
import copy, json, sys

live, out = sys.argv[1:3]
L = json.load(open(live))
G = {g['group']: g for g in L['groups']}
AS = 'handoff/audit-r9-alt'
PS = 'handoff/round9/state/alt/archscore'   # the pre-study directory on handoff/audit-r9-alt
PSC = 'PRESTUDY_COMMIT'                        # replaced with the pushed commit by the caller

# ---- 1. resume truthing (re-based to origin/main f88e6af8: #1767 merged 2026-09-29T22:46Z)
G['R9-F1.6']['resume'].update({
    'stage': 'done', 'commit': 'f88e6af8b609c674ae7fa87838b9f13cf50aaecb',
    'last_step': 'MERGED as #1767 at f88e6af8 (round-2 head 929e5aa0 plus main); the live file still read not-started with an empty commit through review round 2 (LIVE-STATUS.md disagreement 1)',
    'next_step': 'none; its merge opens R9-F2.4, R9-F9.3 and R9-EG-B10; stamp v6.7.11 (EG-B9 #1765 and F1.6 unstamped)'})

# ---- 2. carries
def carry(gid, text):
    G[gid]['brief'] = G[gid]['brief'].rstrip() + ' ' + text
    return gid

HONEST = ('Measure delta-S before and after with the prototype at ' + PSC + ' (python3 ' + PS + '/b/arch_score.py --delta on two vectors from ' + PS + '/b/measure_vec.py and ' + PS + '/b/metrics_v1.py, '
          'with the red-team counters of ' + PS + '/redteam/counters/counters.py swapped in as ' + PS + '/redteam/counters/score_proto.py does, or the in-tree copy once R9-EG-A1 lands) and put the per-metric deltas in the PR body; a gain that appears only without the counters is not a gain. The score is report-only: '
          'a shortfall is not a failure, a rise in any score metric is explained in the body, and none of the red-team moves in ' + PS + '/PRE-STUDY.md section 7 '
          '(an Any-typed payload key, a passthrough property over a private, a renamed or re-spelled defect) counts as progress.')

carried = [
    carry('R9-F10.4', f'Carry (architecture-score pre-study, {AS} {PS}/PRE-STUDY.md sections 2 and 4 at {PSC}; evidence {PS}/a1/metric_review.md, 30 perturbations with nulls): '
          'retire attrbag_classes_over_30, classes_over_300 (#1738 arm c), internal_call_edges and coordinator_methods; move const_modules_over_50, the cc rows, max_cc, max_method_loc and methods_over_150/200 out of the architecture view (they stay quality rows or go, owner\'s call); '
          'merge coordinator_loc into max_class_loc and cross_seam_edges with the five cut rows into one seam_cut_total computed against the base\'s seam map and charging f(coord) functions to their seam; '
          'count coordinator attribute writers inside and outside the class; replace duplication_blocks with AST statement windows package-wide (#1738 arm a; the prototype is dup_pairs_v1, counted as redundant copies, not pairs); replace local_imports with import_cycle_modules (function-scope imports in, TYPE_CHECKING out); '
          'resolve dead_methods by receiver with properties included and dead_top_level_symbols through import * (or adopt dead_by_reachability, the N-structure-blind barrier this brief already carries). '
          'The eleven metric defects are verified there, each with its perturbation and null; #1738 gains a comment listing them, and no further issue is filed. '
          'A retired row is a loosening; tvofi approved this retirement list as decision R3-2 (2026-09-29), which also settles #1738 arm (c) by retiring classes_over_300, and each new metric enters at its measured baseline as a re-record with the reason in the commit message.'),
    carry('R9-EG-B1', f'Carry (architecture score, {PS}/PRE-STUDY.md section 8 at {PSC}): expected delta-S +29.5 of the 2x plan: hub_solve_writes 40 -> 0 (the 40 sites include away.apply_setback/restore_setback/lower_floor), and HeatPumpOptimizer.optimize taking the record keyword-only moves params_over_10 28 -> about 22. ' + HONEST),
    carry('R9-EG-B3', f'Carry (architecture score, {PS}/PRE-STUDY.md section 8 at {PSC}): expected delta-S +50.9, the largest single step of the 2x plan: untyped_payload_keys 164 -> 0, each key with its real value type (a key typed Any is not typed; the metric is tightened to say so in R9-EG-A1), and the one read with no producer (horizon_hours, sensor.py:1511 and :1544) becomes a typing error, not a silent fallback. ' + HONEST),
    carry('R9-EG-B6', f'Carry (architecture score, {PS}/PRE-STUDY.md section 8 at {PSC}): expected delta-S +4.2: private_reach 92 -> 13 (pump_arbiter.py 37, boost.py 9, diagnostics.py 8, __init__.py 7, away.py 7, wood_fuel.py 7, services.py 2, setpoint_check.py 2, weighted counts at 7952d8f9) and the four collaborator in-place writes. ' + HONEST),
    carry('R9-EG-B2', f'Carry (architecture score, {PS}/PRE-STUDY.md section 8 at {PSC}): expected delta-S +3.8: the surface half of private_reach (sensor.py 8, entity.py 2, binary_sensor.py, datetime.py, switch.py 1 each) -> 0. ' + HONEST),
    carry('R9-EG-B7', f'Carry (architecture score, {PS}/PRE-STUDY.md section 8 at {PSC}): expected delta-S about +5.2 for two seams (coord_footprint_v1 2512 -> about 1900, coordinator attributes with more than one writer 130 -> about 90, shared in-place writes 18 -> about 10). A seam extracted as free functions of the coordinator is the B7 perturbation the pre-study shows the current metrics reward; the footprint charges it back. ' + HONEST),
    carry('R9-EG-B5', f'Carry (architecture score, {PS}/PRE-STUDY.md section 6 at {PSC}): the prototype prices only the coordinator\'s size, so this extraction reads delta-S about 0; that is a known limit of the instrument (v2 queue, section 10), not a verdict on the PR. Report the per-class logical-statement counts of HeatPumpOptimizer before and after in the body.'),
]

# ---- 3. new groups
TEMPLATE = copy.deepcopy(G['R9-EG-B8'])


def group(gid, lane, issues, fixes, after, wave, why, branch, brief, owner_gate=None, cls='architecture', effort='high',
          fixer='opus'):
    g = copy.deepcopy(TEMPLATE)
    short = gid.replace('R9-', '')
    g.update({'group': gid, 'lane': lane, 'issues': issues, 'fixes': fixes, 'after': after, 'wave': wave,
              'class': cls, 'effort': effort, 'owner_gate': owner_gate, 'brief': brief, 'fixerModel': fixer,
              'findings': [], 'covers': [], 'sweep_instances': [], 'rca': None, 'barrier': None,
              'barrier_prototype': None, 'blocked_on': None})
    g['model'] = dict(g['model'], fixer=fixer, fixer_why=why)
    g['resume'] = dict(g['resume'], stage='not-started', commit=None, last_step=None,
                       next_step='fixer.md step 1 at a fresh merge base: re-measure with the prototype, then write the failing check',
                       branch=branch, note_file=f'handoff/round9/fix/resume/{short}.md on {branch}',
                       review_branch=f'{branch}-review',
                       review_note_file=f'handoff/round9/fix/resume/{short}-review.md on {branch}-review',
                       plan=f'{AS}: handoff/round9/state/ALT-ENDGAME-PLAN.md (rev 3), handoff/round9/state/ALT-ROSTER.json, {PS}/PRE-STUDY.md',
                       note='Added by roster rev 3 (the architecture-score pre-study, 2026-09-29). The seat\'s resume note on its branch outranks this entry for in-flight state.')
    for k in ('pr',):
        g['resume'].pop(k, None)
    G[gid] = g
    return gid


new = [
    group('R9-EG-A1', 'EG', [1774, 1738], [], ['R9-F10.4'], 16,
          'a report-only instrument with a calibration self-check; tooling, no production change',
          'handoff/r9-eg-archscore',
          f'Round-9 endgame PR EG-A1 (lane EG, the architecture score, report-only). Issue #1738 (Part of). Land the pre-study\'s prototype ({AS} at {PSC}: {PS}/b/arch_score.py, {PS}/b/measure_vec.py, {PS}/b/metrics_v1.py, the a3 metric modules under {PS}/a3/metrics, the a1 probes {PS}/a1/probes.py, and {PS}/b/weights.json with its recorded hash) as a new directory under tools/audit, '
          'reading the metrics R9-F10.4 landed in tests/structure.py where they overlap so there is one definition of each. '
          f'Before landing, apply the section-7 counters the red team proved ({PS}/redteam/counters/counters.py and flatten_coord.py: an Any-typed key is untyped, effect-free statements do not split a clone, the coordinator is measured as its whole package class hierarchy, a passthrough property is a reach, orphan family overrides and unread private globals, keyword-bag parameters, and reflective-write tripwires until the role engine reads reflective writes as writes), each with its attempt script under {PS}/redteam/attempts as a planted case and a rename null. '
          'It prints delta-S, the gate rises and the per-metric deltas for a diff (its --delta mode on the base and head vectors), and the PR template gains an optional "Architecture score" line (the template is policy: tvofi approves). '
          f'Its own check (a new script under tests, classified in a measured closure or on the INERT list as tests/entities.py requires) re-runs the calibration: every planted and corpus case must classify exactly as {PS}/PRE-STUDY.md section 6 records (amended by the counters\' one recorded correction), and every red-team attempt must stay NULL or not admissible, so a metric change that silently moves a verdict or re-opens a game fails. The score is a report and a review trigger, never a target a seat is rewarded for moving. '
          'The weights stay frozen at their recorded hash; a weight change is a policy change. No budget raise, no gate on other PRs: whether delta-S becomes a required check is a round-10 decision (section 9).',
          owner_gate='decided: R3-1 adopted and R3-3 weights accepted (2026-09-29); the PR template and tests are code-owned, so the merge takes tvofi\'s approving review at the head (a GitHub requirement, not a pending decision)', cls='architecture', effort='medium'),
    group('R9-EG-A2', 'EG', [1775], [1775], ['R9-EG-A1', 'R9-EG-B3', 'R9-EG-B5'], 17,
          'behaviour-preserving consolidation of duplicated formulas and helpers, where a solver float can move',
          'handoff/r9-eg-one-copy',
          f'Round-9 endgame PR EG-A2 (lane EG, one copy per formula and helper; classes P2 and P3). Issue #1775 (Fixes). '
          f'The pre-study ({PS}/PRE-STUDY.md section 8 at {PSC}) samples the clone windows dup_pairs_v1 finds (121 pairs at 7952d8f9): the scalar and batch physics steps in thermal_model.py (_simulate_step_two_zone, _stability_substeps, simulate_trajectory_batch share the slab and inter-zone transfer lines, a P3 divergence risk), _finite in freq_control.py and inputs.py, the store-load prelude in boost.restore and pump_arbiter._load, the r-squared confidence in sysid._slab_confidence and sysid.identify, the requirement arrays in optimizer._plan_dhw_cheapest_first and _plan_dhw_min_cost, and the option-flow step functions config_flow.async_step_* that the settings registry (#597) made identical. '
          'Consolidate each into one definition its callers use. Target dup_pairs_v1 121 -> 40 or lower, expected delta-S +14.1. A window that is framework idiom rather than logic is argued in the body and left, not hidden. '
          'The physics consolidation may move solver floats: value-bearing goldens are claimed in tests/golden/claimed_drift.txt with direction (CLAUDE.md rule 3), never re-recorded; the fixer proves the scalar and batch paths agree to the golden tolerance before and after. ' + HONEST,
          cls='P3', effort='high'),
    group('R9-EG-A3', 'EG', [1776], [1776], ['R9-EG-B1', 'R9-EG-B5'], 13,
          'parameter objects for the solver and planner signatures, mechanical once EG-B1 and EG-B5 have landed',
          'handoff/r9-eg-param-objects',
          f'Round-9 endgame PR EG-A3 (lane EG, parameter objects). Issue #1776 (Fixes). After R9-EG-B1\'s per-solve record and R9-EG-B5\'s DHW planner move, the functions with more than ten parameters (28 at 7952d8f9, about 22 after EG-B1) take the record or a frozen dataclass of their related arrays instead of positional lists; the pre-study\'s fragment-chain perturbation B3c shows why the count is a guard: a split that decomposes nothing raises it. Target params_over_10 about 22 -> 14, expected delta-S +0.6; goldens byte-identical. ' + HONEST,
          cls='architecture', effort='medium', fixer='sonnet'),
    group('R9-F7.5', 'F7', [1777], [1777], ['R9-F7.4'], 3,
          'user-visible entity renames that close the three recorded family splits',
          'handoff/r9-f7-entities-5',
          f'Round-9 fix PR F7.5 (entities, class N-name-sort). Issue #1777 (Fixes). R9-F7.4 (#1766) declared the entity families and recorded three splits the contiguity check allows: en away, sv away and sv compressor ({PS}/a3/new_metrics.md, family_splits = 3 at 7952d8f9). '
          'tvofi chose rename for all three (decision R3-4, 2026-09-29). Change only the translated display names in translations/en.json, translations/sv.json and strings.json so each family leads with its token (for example Expected Return -> Away Expected Return, Förväntad hemkomst -> Borta förväntad hemkomst, Rådgivare för kompressorfrekvens -> Kompressorfrekvensrådgivare; confirm each under the check\'s collation), and remove the three allowances from the contiguity check so it passes with none. No translation_key, unique_id or entity id changes (the #285 refusal was about entity-id renames); state in the body what a new install\'s derived entity id becomes, and check no card, doc or test reads the old display strings. Expected delta-S +10.9. ' + HONEST,
          owner_gate=None, cls='N-name-sort', effort='low', fixer='sonnet'),
]


# ---- 5. rev 3.1 (2026-09-29): tvofi's decisions, the mandate to programme completion, and every open issue covered
LEGACY = [1167, 1168, 1170, 1171, 1173, 1174, 1175, 1176, 1177, 1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185, 1187,
          1188, 1189, 1190, 1191, 1193, 1196, 1197, 1198, 1199, 1200, 1201, 1204]
assert len(LEGACY) == 30
MANDATE = ('Mandate (rev 3.1): tvofi extended the programme mandate to programme completion on 2026-09-29, so no step waits for a human decision. '
           'A budget raise that an honest re-record requires is confirmed by that mandate: post the measured value and the reason on #201 before the push (CLAUDE.md rule 2), '
           'and the raise still merges only on tvofi\'s approving review at the head (budget-raise-gate), which the orchestrator requests; a code-owned file likewise merges on that review.')
for gid, g in G.items():
    if g['resume'].get('stage') in ('done', 'rca-done'):
        continue
    if 'asked before the push' in g['brief'] or g.get('owner_gate'):
        g['brief'] = g['brief'].rstrip() + ' ' + MANDATE
    if g.get('owner_gate') and 'mandate' not in g['owner_gate']:
        g['owner_gate'] = g['owner_gate'] + ' (decisions given under the 2026-09-29 mandate; the approving review at the head remains a GitHub requirement)'
DECIDED = {
    'R9-F1.8': 'Decided under the mandate (plan rev 3.1 section 7, D6): the displayed currency follows the price feed\'s currency where the feed declares one and the configured currency otherwise; state the rule and its measured effect in the body instead of asking.',
    'R9-F2.4': 'Decided under the mandate (D7): record the P4 refusal on #1664 and in the body, priced in money and CPU as the brief says.',
    'R9-F11.4': 'Decided under the mandate (D8): build the N-silent-zero class barrier, since its refusal was overturned on the re-run cost test.',
    'R9-F10.1c': 'Decided under the mandate (D9): fix, do not exempt: the manual override lasts its stated length in absolute time across a DST change.',
    'R9-F10.7': 'Decided under the mandate (D11): the host Profiler run is tvofi\'s optional action and the group does not wait for it; the heartbeat instrument lands on its own evidence.',
    'R9-EG-R1': 'Decided under the mandate (D5): adopt the four policy clauses as specified in handoff/round9/state/alt/rca/RCA-BULK-2.md section 3.4 at c5c32f2b; the policy PR still merges on tvofi\'s approving review at the head.',
    'R9-EG-B1': 'Decided under the mandate (D12, H2): judge quiet comfort periods against the configured band, not the per-solve effective band this PR removes from shared state; measure and report the effect.',
}
for gid, t in DECIDED.items():
    carry(gid, t)

new += [
    group('R9-EG-L0', 'EG', LEGACY + [1655], LEGACY, [], 1,
          're-measure-and-close of 30 legacy round-5 issues and one round-9 remainder; judgement on harnesses, no production change',
          'handoff/r9-eg-legacy-close',
          'Round-9 record PR EG-L0 (lane EG, legacy issues). Issues ' + ', '.join(f'#{n}' for n in LEGACY) + ' (each closed here) and #1655 (dispositioned). '
          'The 30 were filed 2026-09-19 by the retired tvofi-seat-author identity from the round-5 audit (baseline eaa2a06a) and became visible again when that account\'s flag was lifted; their siblings #1192, #1194 and #1195 were fixed and closed at the time, and tvofi directs (2026-09-29) that they be re-measured and closed. '
          'Run the web-triage procedure (.claude/skills/web-triage) at a fresh merge base: re-measure each claim with its own harness (the tools/audit/round5 harness its body names) plus a null for any quantitative claim, then close it with one comment (gh_comment.py, read back) giving the number and exactly one verdict: '
          'FIXED (the fixing PR and the check that pins it), SUPERSEDED (the owning round-9 issue and group; if that group\'s brief does not already name this instance, carry it into the brief first by finding-propagation.md, then close as a duplicate of the owning issue), REFUTED or NOT-REPRODUCIBLE (with the measurement), or LIVE-CARRIED (still reproduces: carried into the not-started group that owns the files, or a new issue filed when none does; a live defect is never closed without its carry). '
          'The governance three (#1191 D11-01 sev:critical, the deploy-key bypass mode; #1193 D11-03 sev:high, reviewer and author; #1196 D11-06, stale-review dismissal) are ruleset state: compare the current ruleset with decisions 0009 and 0011, and where a repository-settings change is needed record the exact setting on #201 and as owed work in docs/HANDOVER.md, since only tvofi can apply it, and close only after the setting is verified or with that record. '
          '#1655: re-read the record R9-F4.2 left when it kept the issue open, then schedule what remains into its owning group or close it with that record. '
          'Dispatch in W0 so every carry lands before its destination group starts. The delivery row lists all 31 verdicts.',
          cls='record', effort='high'),
    group('R9-EG-B11', 'EG', [1745], [1745], ['R9-EG-B1', 'R9-EG-A3'], 14,
          'typed entry configuration read once per entry; follows the per-solve record so the two shapes do not collide',
          'handoff/r9-eg-entry-config',
          'Round-9 endgame PR EG-B11 (lane EG, typed entry configuration). Issue #1745 (Fixes). Brought into round 9 by tvofi\'s 2026-09-29 direction that the plan cover every open issue. '
          'Measure first at the merge base: the issue\'s enumerator counted 281 .get(CONF_...) reads of 149 keys in 20 modules, each with its own default and coercion. '
          'Build one frozen per-entry configuration object, with its defaults and coercion in one place, built at setup and on each options update; readers take it instead of the raw dict. '
          'Where R9-EG-B1\'s per-solve record already carries a value, that record reads from this object and does not re-read the dict. Goldens byte-identical; the options-flow round trip and migrations unchanged. ' + HONEST,
          cls='architecture', effort='high'),
    group('R9-EG-A4', 'EG', [1774], [1774], ['R9-EG-A1', 'R9-EG-B7', 'R9-EG-A2', 'R9-EG-A3', 'R9-EG-B11'], 18,
          'turn the report-only score into a required check after one wave of data; policy already approved',
          'handoff/r9-eg-archscore-required',
          f'Round-9 endgame PR EG-A4 (lane EG, the architecture score becomes a required check). Issue #1774 (Fixes). tvofi approved it as decision R3-6 on 2026-09-29. '
          'After one wave of report-only data (R9-EG-B1, B2, B3, B6, B7, R9-EG-A2, A3 and B11 each reported a delta-S with the counters), compare every reported delta with its PR\'s review verdict and write the comparison into the body; any case where the score and the verdict disagree becomes a new planted case in R9-EG-A1\'s self-check before this PR goes further. '
          'Then make "delta-S >= 0 with the counters, or a gate rise explained in the body like a budget raise" a required check: a CI job beside the existing ones (tests.yml is code-owned) and the required-context list in the main-protect ruleset, a repository-settings change only tvofi can apply, which the orchestrator requests and records on #201. The weights stay at their recorded hash.',
          cls='architecture', effort='medium'),
]

# ---- 6. rev 3.1: every open issue has one closing group
for gid, n, why in (('R9-F10.7', 1758, 'the loop-stall heartbeat is what #1758 asks for; the freeze\'s cause, once the instrument finds it, is filed as its own issue'),
                    ('R9-F10.3', 1748, 'it owns the per-site mutation ratchet #1748 is about'),
                    ('R9-F1.10', 1741, 'it carries A2, both halves of #1741'),
                    ('R9-F10.4', 1738, 'it lands the metric fixes for arms (a) to (c) and the eleven defects of the #1738 addendum; R9-EG-A1 stays Part of')):
    g = G[gid]
    if n not in g['issues']:
        g['issues'] = g['issues'] + [n]
    if n not in g['fixes']:
        g['fixes'] = g['fixes'] + [n]
    carry(gid, f'Rev 3.1: this PR closes #{n} (Fixes), because {why}.')

order = [g['group'] for g in L['groups']] + [n for n in new if n not in [g['group'] for g in L['groups']]]
L['groups'] = [G[k] for k in order]
L['_comment'] = list(L.get('_comment') or []) + [f'rev 3 (2026-09-29, {AS}): F1.6 truthed to done (#1767, f88e6af8); architecture-score carries into F10.4, EG-B1, B2, B3, B5, B6, B7; groups EG-A1, EG-A2, EG-A3, F7.5.']
txt = json.dumps(L, indent=2, ensure_ascii=False) + '\n'
open(out, 'w').write(txt)

ids = {g['group'] for g in L['groups']}
bad = [(g['group'], a) for g in L['groups'] for a in g['after'] if a not in ids]
seen = {}


def visit(n):
    if seen.get(n) == 1:
        raise SystemExit(f'cycle at {n}')
    if seen.get(n) == 2:
        return
    seen[n] = 1
    for a in G[n]['after']:
        visit(a)
    seen[n] = 2


for n in ids:
    visit(n)
print(f'carries: {carried}\nnew: {new}\ndangling edges: {bad}\nacyclic: yes, {len(ids)} groups')
