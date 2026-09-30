#!/usr/bin/env python3
"""Roster rev 4.1: lane UX (tvofi's UX decisions of 2026-09-30) over the LIVE round-9 roster.

    python3 build_roster_rev41.py LIVE.json OUT.json [UX_COMMIT]

LIVE is .claude/workflows/wave-r9-groups.json on handoff/audit-r9-fixplan (1c3558f0 when written; rev 4 applied). It adds
seven groups R9-UX-1..7, after-edges on R9-RO-2 (UX-1..4) and R9-RO-9 (UX-5..7), carries into R9-UI-3, R9-UI-4, R9-SW-3,
R9-RO-3, R9-RO-4 and R9-EG-A4, waves for the new groups only, one _comment line, and re-truths R9-EG-B3's two sensor.py line
numbers that #1788 moved. It changes no stage, no issue and no other brief. It refuses a file that already has R9-UX-1, a dangling edge, a cycle, and any result that lengthens the
longest open chain or EG-A4's open chain.
"""
import copy, json, sys

LIVE, OUT = sys.argv[1], sys.argv[2]
UC = sys.argv[3] if len(sys.argv) > 3 else '1a90e4cb'
r = json.load(open(LIVE))
G = {g['group']: g for g in r['groups']}
if 'R9-UX-1' in G:
    sys.exit('refused: R9-UX-1 already present; rev 4.1 is applied')
NEED = ('R9-UI-3', 'R9-UI-4', 'R9-EG-B3', 'R9-EG-B6', 'R9-SW-1', 'R9-EG-B5', 'R9-EG-B1', 'R9-EG-A2', 'R9-EG-B7',
        'R9-EG-B11', 'R9-RO-2', 'R9-RO-3', 'R9-RO-4', 'R9-RO-9', 'R9-SW-3', 'R9-EG-A4')
for n in NEED:
    if n not in G:
        sys.exit(f'refused: {n} missing from the live roster; re-plan rev 4.1 against it')
DONE = ('done', 'rca-done')


def chains():
    opn = {k for k, g in G.items() if g['resume']['stage'] not in DONE}
    dep = {}
    def d(k):
        if k not in dep:
            dep[k] = 1 + max((d(a) for a in G[k]['after'] if a in opn), default=0)
        return dep[k]
    for k in opn: d(k)
    return max(dep.values()), dep.get('R9-EG-A4', 0), dep


before_longest, before_a4, _ = chains()

DOR = (f'Design of record: handoff/round9/state/alt/design/ux/DESIGN-UX.md and the pre-study '
       f'handoff/round9/state/alt/design/ux/PRE-STUDY-UX.md (at {UC} on handoff/audit-r9-alt), with the mockups and '
       f'CONTRAST.json beside them, built on the lane-UI design of record handoff/round9/state/alt/design/DESIGN.md (at '
       f'7bca8ab3); where this brief and those files disagree, the newer is right and the other is the bug.')
DECIDED = ('tvofi decided on 2026-09-30: U1 notifications are documented events plus a blueprint, no option fields; U2 the '
           'trust replay is the full day-ahead replay; U3 the shared household power budget is deferred beyond round 9 as a '
           'feature request; U4 "the budgets are in place to make sound architectural decisions, they can be raised as a '
           'last resort if payment does not yield better code, after codeowner approval"; U5 "make sure that the finished '
           'card pages gets described with screenshots in the documentation".')
FIRST = ('First rule: before any work, read CLAUDE.md and every rules file it references (.claude/rules, the role contract '
         'tools/audit/briefs/fixer.md), and follow them; pass this rule on in every sub-agent brief. Never call the owner '
         'anything but tvofi, in commits, PR bodies, comments and delivery notes; the PR attribution line is '
         '_Requested by **tvofi**_.')
FEATURE = ('This is a new production feature, not a finding: there is no class, no barrier and no RCA, except where this '
           'brief names a defect to fix with its failing test first. Value-bearing goldens stay byte-identical unless this '
           'brief says otherwise; moved card states are claimed in tests/golden/card_claimed_drift.txt with claims-for '
           'equal to VERSION, never re-recorded (CLAUDE.md rule 3).')
BUDGET = ('Budgets (U4, CLAUDE.md rule 2): design to fit first, putting new logic where it belongs architecturally rather '
          'than in the coordinator; pay for lines only where the payment is itself the better design, never by deleting '
          'working functionality or shuffling lines to meet a number; a raise is the last resort, and then the body shows '
          'why payment would not give better code and tvofi confirms the raise as code owner before the push, and it '
          'merges only on tvofi\'s approving review (budget-raise-gate). The 2026-09-29 mandate does not pre-confirm raises '
          'for this lane: ask on #201, and while it waits the orchestrator keeps dispatching everything else. Run python3 '
          'tests/structure.py before every hand-off and re-measure at your own merge base; carry no number.')
DOCS = ('Documentation (U5): regenerate, with the browser test\'s page-screenshot mode that R9-UI-3 lands, the screenshots '
        'of every card page this PR changes, light and dark, into docs/img/card, and describe the page in '
        'docs/dashboard-card.md in the same PR; never hand-capture a screenshot, so the docs stay true to the code (D6).')
STANDING = ('Standing: cloud seat: no PRs, no GitHub comments, no issues, no gh; hand the branch and body off on your handoff '
            'branch and the Mac orchestrator pushes as the hpo-author App via tools/audit/app_push.sh; hpo-approver approves a '
            'non-code-owned PR, tvofi reviews a code-owned one (decision 0011). Mutation: pin the sites this change adds '
            '(mutation_table.py --scope changed --base origin/main); --max 0 is never proof. Resumability (tvofi 19:05Z): '
            'commit and push to your handoff branch at every step boundary and at least every 30 minutes, update the resume '
            'note in this entry\'s resume field with every push, and append one dated line per milestone to the round-9 '
            'resume log. No VERSION, manifest version or notes-heading edits. Part of #201; issues stay empty until the '
            'orchestrator files the lane\'s feature issue.')
CARD_GATE = 'tests/card_browser.mjs is code-owned; merges on tvofi\'s approving review at the head'


def group(gid, after, fixer, why, effort, gate, branch, brief):
    g = copy.deepcopy(G['R9-UI-3'])
    g.update(group=gid, lane='UX', issues=[], fixes=[], findings=[], covers=[], cap_exception=None, sweep_instances=[],
             **{'class': 'feature'}, fixerModel=fixer, reviewerModel='opus', effort=effort, fixture=False,
             owner_gate=gate, rca=False, barrier=[], barrier_prototype=[], blocked_on=None, after=after, brief=brief)
    g['model'] = dict(fixer=fixer, fixer_why=why, reviewer='opus', rca=None, runner='haiku', record='sonnet')
    n = gid.replace('R9-', '')
    g['resume'].update(stage='not-started', branch=branch, commit=None, last_step=None,
                       next_step=('fixer.md step 1 at a fresh merge base once every after-edge has merged: re-read '
                                  'handoff/round9/state/alt/design/ux/DESIGN-UX.md, then write the failing test'),
                       note_file=f'handoff/round9/fix/resume/{n}.md on {branch}', review_branch=branch + '-review',
                       review_note_file=f'handoff/round9/fix/resume/{n}-review.md on {branch}-review',
                       plan=(f'handoff/audit-r9-alt: handoff/round9/state/ALT-ENDGAME-PLAN.md (rev 4.1) and '
                             f'handoff/round9/state/alt/design/ux/ at {UC}; this roster'),
                       note=('Added by roster rev 4.1 (tvofi\'s UX decisions, 2026-09-30); issues stay empty until the '
                             'orchestrator files the feature issue. The seat\'s resume note on its branch outranks this '
                             'entry for in-flight state.'))
    for k in ('pickup_cloud', 'pickup_local'):
        g['resume'].pop(k, None)
    return g


def head(n, what, fixer, why):
    return (f'Round-9 feature PR {n} (lane UX, {what}). Models: fixer {fixer} ({why}); reviewer opus in another session; '
            f'runner haiku; record sonnet. {DECIDED} {FIRST} {DOR} {FEATURE}')


CARD = 'custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js'
new = [
    group('R9-UX-1', ['R9-UI-4'], 'sonnet', 'card-only presentation over fields the plan sensors already publish', 'high', CARD_GATE,
          'handoff/r9-ux-explain',
          head('UX-1', 'why now, why not', 'sonnet', 'card-only presentation over fields the plan sensors already publish') +
          f' Borrowed files: {CARD} from F6 (after R9-UI-4, which lands the stacked panels this PR explains). Scope, per '
          'DESIGN-UX.md section UX-1: (1) the headline lists every narrative line the narrative sensor already publishes '
          '(it shows the first today); (2) an idle step\'s tooltip explains, under the words "likely because", from the '
          'published per-step fields only: the step\'s price rank within the horizon, the previous run it coasts on and '
          'the next run, the tank temperature against the published hot-water minimum on a hot-water step, and the solar '
          'surplus ahead; it states nothing the fields cannot show (no room floor, no fuse cap: those are R9-UX-5\'s exact '
          'sub-codes); (3) the tooltip stays inside the chart. Failing tests first in tests/card.mjs: the idle-step '
          'explanation present and correct on the fixture (the pin that says idle steps produce no explanation changes '
          'with the reason in the body), every narrative line shown. Must keep working: hover on active steps with '
          'today\'s reason strings, the lane editor, pan and zoom. ' + DOCS + ' ' + BUDGET + ' ' + STANDING),
    group('R9-UX-2', ['R9-UX-1'], 'sonnet', 'card-only inbox over advisor sensors, using existing services', 'high', CARD_GATE,
          'handoff/r9-ux-inbox',
          head('UX-2', 'advisor inbox', 'sonnet', 'card-only inbox over advisor sensors, using existing services') +
          f' Borrowed files: {CARD} from F6 (after R9-UX-1). Scope, per DESIGN-UX.md section UX-2: the Advisor tab becomes '
          'an inbox ranked by monthly value, reading the advisor sensors that are enabled by default (sensor gap, '
          'hot-water setpoint, valve target) and the price-of-a-degree tiles when their option is on; actions through '
          'existing services only (assign_entity for a sensor gap and for a manual valve target; the hot-water setpoint '
          'opens the schedule editor until R9-UX-5 adds a persistent apply); advisors that are off by default are offered '
          'as "enable to see" rows and never read, because tests/entities.py refuses card reads of disabled-by-default '
          'sensors. The advisor sensors join the card\'s render signature through a list of their own, not '
          'HEADLINE_SUFFIXES. States: empty, waiting (the advisor\'s own reason), error. Failing tests first in '
          'tests/card.mjs (ranking, actions call the named services with the payloads in DESIGN-UX.md, the opt-in rows). '
          'Must keep working: today\'s sensor ranking and its assign flow. ' + DOCS + ' ' + BUDGET + ' ' + STANDING),
    group('R9-UX-3', ['R9-UX-2'], 'sonnet', 'card-only page over published health data', 'high', CARD_GATE,
          'handoff/r9-ux-health',
          head('UX-3', 'health view', 'sonnet', 'card-only page over published health data') +
          f' Borrowed files: {CARD} from F6 (after R9-UX-2). Scope, per DESIGN-UX.md section UX-3: a Health tab beside '
          'Plan, Setup, Savings and Advisor with the inputs (Input Problem\'s published problems in words, with age and '
          'limit, and the fallback in use), plan freshness, the sensors still waiting for evidence and why, a first-plan '
          'checklist (required inputs, a recommended power meter, the count of insight sensors off by default), and a '
          'link to the diagnostics download; the header pill summarises input health. Failing tests first in '
          'tests/card.mjs; claim the new page states. Must keep working: every existing tab. ' + DOCS +
          ' The Health page gets its own section in docs/dashboard-card.md. ' + BUDGET + ' ' + STANDING),
    group('R9-UX-4', ['R9-EG-B3'], 'sonnet', 'a listener module and a blueprint over signals the coordinator already publishes', 'medium',
          'none expected; a new test script would need the code-owned tests/run.sh, so tests go in tests/features.py',
          'handoff/r9-ux-events',
          head('UX-4', 'events and blueprint', 'sonnet', 'a listener module and a blueprint over signals the coordinator already publishes') +
          ' Scope, per DESIGN-UX.md section UX-4 and decision U1: a new notifier module registered in '
          'custom_components/heatpump_optimizer/__init__.py next to where the entry stores its coordinator, listening '
          'to coordinator updates and firing documented events once per occurrence (monthly receipt, comfort at risk, '
          'input stale, plan stale, manual plan released), remembering what it sent across restarts; it reads the typed '
          'payload contract R9-EG-B3 lands (the after edge), never bare keys; no line is added to coordinator.py. Ship '
          'a blueprint under blueprints/automation beside the existing three that routes the chosen events to a notify '
          'target with quiet hours, and document every event and its data in docs/automations.md. Classify the new '
          'module in a measured closure through CI\'s closures autofix, never INERT. Failing tests first in '
          'tests/features.py: each event fires once on its signal and not on a repeat; nothing fires on an unchanged '
          'refresh (the null control). If R9-EG-A4 has landed, show the architecture score delta with the counters '
          '(new public surface counts). ' + BUDGET + ' ' + STANDING),
    group('R9-UX-5', ['R9-EG-B6', 'R9-SW-1', 'R9-EG-B5', 'R9-EG-B1', 'R9-EG-A2', 'R9-UX-3'], 'opus',
          'service schema, solver classifiers and card in one change', 'high',
          'tests/card_browser.mjs is code-owned; a budget raise, if any, is asked first (U4); merges on tvofi\'s approving review at the head',
          'handoff/r9-ux-actions',
          head('UX-5', 'advisor actions and exact idle reasons', 'opus', 'service schema, solver classifiers and card in one change') +
          ' Scope, per DESIGN-UX.md section UX-5: (1) apply_schedule gains a persistent hot-water setpoint (and the '
          'comfort target) written to the entry\'s options like its other fields, so the inbox\'s Apply survives a reload '
          '(set_thermal_parameters does not: show the reload losing it first); services.yaml, strings and translations '
          'follow; (2) idle steps get exact sub-codes in the space and hot-water classifiers of '
          'custom_components/heatpump_optimizer/optimizer.py (dearer than the hours used, above the floor and coasting, '
          'capped by the fuse, waiting for solar, the other channel has the capacity), published per step and added to '
          'the narrative templates in English and Swedish; the hot-water classifier also covers the path where its '
          'reasons are empty today; (3) the card replaces "likely because" with "because" where a sub-code exists and '
          'wires the inbox\'s Apply. After R9-EG-B6 and R9-SW-1 (services.py), R9-EG-B5, R9-EG-B1 and R9-EG-A2 '
          '(optimizer.py), R9-UX-3 (the card). Goldens: sub-codes change published reasons, not values; claim any '
          'value drift, never re-record. ' + DOCS + ' ' + BUDGET + ' ' + STANDING),
    group('R9-UX-6', ['R9-EG-B7', 'R9-EG-B11', 'R9-UX-5'], 'opus',
          'ledger and accuracy stores, a receipt defect with its failing test, and two card views', 'high',
          'tests/card_browser.mjs is code-owned; a budget raise, if any, is asked first (U4); merges on tvofi\'s approving review at the head',
          'handoff/r9-ux-money',
          head('UX-6', 'money and memory', 'opus', 'ledger and accuracy stores, a receipt defect with its failing test, and two card views') +
          ' Scope, per DESIGN-UX.md section UX-6 and PRE-STUDY-UX.md item 3: (1) defect, failing test first: the monthly '
          'receipt\'s total_sek sums every line except the reasons, so it counts spot together with the space and dhw '
          'lines that split it and the two savings lines (_freeze_month_report in '
          'custom_components/heatpump_optimizer/coordinator.py, lines booked at its space line and in ledger.py\'s savings '
          'lines); (2) the receipt freeze moves out of the coordinator into custom_components/heatpump_optimizer/ledger.py '
          'as a pure, tested function, its sound home, which also pays for this PR\'s call sites; (3) the capacity charge '
          'is booked as a ledger line before the peak tracker resets at month change, so a receipt can name it; (4) every '
          'receipt kept (24 months) is published unrecorded on the enabled monthly-savings sensor; (5) a daily snapshot of '
          'the plan\'s promise (the room trajectory and the cost, taken at a fixed hour) is kept beside the accuracy '
          'history in custom_components/heatpump_optimizer/accuracy.py\'s store, bounded, and published unrecorded '
          '(decision U2); (6) the Savings tab shows the receipt with a sentence saying what it covers, the cost by reason, '
          'and "Yesterday: the plan against reality" in the concept-A panel style (promise dashed, measurement solid, '
          'shared time axis, colours of record). Also correct the stale comment in _learning_view that still describes '
          'the fixed heat-loss defect (#110). After R9-EG-B7 (coordinator.py), R9-EG-B11 (sensor.py) and R9-UX-5 (the '
          'card). R9-UX-7 is a sibling with no edge: both edit the card and sensor.py in different functions, and '
          'whichever merges second merges main. Must keep working: the monthly savings table and its estimate badge. ' +
          DOCS + ' ' + BUDGET + ' ' + STANDING),
    group('R9-UX-7', ['R9-EG-B6', 'R9-EG-B11', 'R9-UX-5'], 'opus',
          'new sensors over published data, a richer diagnostics bundle with redaction, and a card section', 'high',
          'tests/card_browser.mjs is code-owned; a budget raise, if any, is asked first (U4); merges on tvofi\'s approving review at the head',
          'handoff/r9-ux-model',
          head('UX-7', 'model status and diagnostics', 'opus', 'new sensors over published data, a richer diagnostics bundle with redaction, and a card section') +
          ' Scope, per DESIGN-UX.md section UX-7: (1) a model-status sensor in custom_components/heatpump_optimizer/sensor.py '
          'reading the learning view the coordinator already publishes (heat loss, lower floor, solar aperture, internal '
          'gains, capacity envelope, COP health, tank cooling, system identification), attributes compact or unrecorded, '
          'no coordinator line; (2) a recorded sensor for the next-interval indoor prediction, so the recorder keeps its '
          'history; (3) custom_components/heatpump_optimizer/diagnostics.py adds the last diagnosis, input states, a plan '
          'summary and the learning view, and redacts the person and calendar entity ids held in the options in addition '
          'to the token, the name and the coarsened location; (4) the card\'s Health page gains "What the model has '
          'learned". New entities move the README entity count and the tests/entities.py rosters in the same PR, and '
          'their names follow the family rule the architecture score checks. After R9-EG-B6 (diagnostics.py), R9-EG-B11 '
          '(sensor.py) and R9-UX-5 (the card). Sibling of R9-UX-6, no edge. ' + DOCS + ' ' + BUDGET + ' ' + STANDING),
]
# Re-truthing a figure (never a citation): #1788 (R9-F1.7, 5dfa6684) moved sensor.py, so R9-EG-B3's line numbers for the
# no-producer horizon_hours reads moved from 1511 and 1544 to 1505 and 1539. The live roster fails brief_lint on it alone.
_b3 = G['R9-EG-B3']['brief']
if 'sensor.py:1511 and :1544' in _b3:
    G['R9-EG-B3']['brief'] = _b3.replace('sensor.py:1511 and :1544', 'sensor.py:1505 and :1539 at 5dfa6684')

r['groups'].extend(new)
G.update({g['group']: g for g in new})

for gid in ('R9-UX-1', 'R9-UX-2', 'R9-UX-3', 'R9-UX-4'):
    G['R9-RO-2']['after'].append(gid)
for gid in ('R9-UX-5', 'R9-UX-6', 'R9-UX-7'):
    G['R9-RO-9']['after'].append(gid)

C = ('Carry from roster rev 4.1 (tvofi\'s UX decisions, 2026-09-30; design of record '
     f'handoff/round9/state/alt/design/ux/DESIGN-UX.md at {UC}): ')
G['R9-UI-3']['brief'] += (' ' + C + 'decision U5, "make sure that the finished card pages gets described with screenshots in '
                          'the documentation": generalise the browser test\'s hero mode into a page-screenshot mode that '
                          'renders each card page (Plan, Setup, Savings, Advisor) from the repository fixture in light and '
                          'dark into docs/img/card, which tests/layout.json already admits as the final folder, and describe '
                          'each page with its screenshots in docs/dashboard-card.md in this PR; every later card group '
                          'regenerates the pages it changes with this mode.')
G['R9-UI-4']['brief'] += (' ' + C + 'decision U5: regenerate the Plan page screenshots with the page-screenshot mode R9-UI-3 '
                          'lands and update the Plan section of docs/dashboard-card.md in this PR.')
G['R9-SW-3']['brief'] += (' ' + C + 'R9-UX-1, R9-UX-2 and R9-UX-3 also edit the card before or beside you: whichever merges '
                          'second merges main. Decision U5: regenerate the screenshots of the pages you change with the '
                          'page-screenshot mode R9-UI-3 lands and describe the silent-window rows in docs/dashboard-card.md.')
G['R9-RO-3']['brief'] += (' ' + C + 'the card page screenshots R9-UI-3 and the UX groups write into docs/img/card are already '
                          'at their final paths: do not move them.')
G['R9-RO-4']['brief'] += (' ' + C + 'three docs/backlog.md entries are already closed on main and still read as open: options '
                          'back navigation (#123, 4daf8c51), the wizard\'s no-tank answer (3110b24d, ed2318e6) and the '
                          'heat-loss re-anchor (#110, cca2b115); mark them closed with those references when you archive the '
                          'file.')
G['R9-EG-A4']['brief'] += (' ' + C + 'R9-UX-5, R9-UX-6 and R9-UX-7 may land after the score becomes a required check: each '
                           'shows its delta with the counters, and a negative delta is explained in its body, never paid by '
                           'a move the pre-study\'s section 7 lists as gaming.')

def need(g):
    return 1 + max((G[a]['wave'] for a in g['after']), default=0)
for g in new:
    g['wave'] = need(g)
for gid in ('R9-RO-2', 'R9-RO-9'):
    G[gid]['wave'] = max(G[gid]['wave'], need(G[gid]))

for g in r['groups']:
    for a in g['after']:
        if a not in G:
            sys.exit(f'dangling edge {g["group"]} -> {a}')
seen, stack = set(), set()
def visit(n):
    if n in stack: sys.exit(f'cycle at {n}')
    if n in seen: return
    stack.add(n)
    for a in G[n]['after']: visit(a)
    stack.discard(n); seen.add(n)
for n in G: visit(n)

after_longest, after_a4, dep = chains()
if after_longest > before_longest or after_a4 > before_a4:
    sys.exit(f'refused: the open chains grow ({before_longest}->{after_longest}, EG-A4 {before_a4}->{after_a4})')

r['_comment'].append(
    f'rev 4.1 (2026-09-30, handoff/audit-r9-alt): lane UX, seven feature groups R9-UX-1..7 for tvofi\'s UX decisions of '
    f'2026-09-30 (design of record and pre-study handoff/round9/state/alt/design/ux/ at {UC}): UX-1 explanations, UX-2 '
    f'advisor inbox and UX-3 health view on the card after R9-UI-4; UX-4 events and blueprint after R9-EG-B3; UX-5 advisor '
    f'actions and idle sub-codes, UX-6 receipts, capacity line and day-ahead replay, UX-7 model status and diagnostics, '
    f'late, after the last owners of their files. R9-RO-2 after UX-1..4; R9-RO-9 after UX-5..7. Carries into R9-UI-3, UI-4, '
    f'SW-3, RO-3, RO-4 and EG-A4. R9-EG-B3 sensor.py line numbers re-truthed after #1788. Item 5 deferred as a feature request. Open chains unchanged: longest {after_longest}, '
    f'EG-A4 {after_a4}.')
json.dump(r, open(OUT, 'w'), indent=2, ensure_ascii=False)
open(OUT, 'a').write('\n')
print(f'{len(r["groups"])} groups; open chains longest {before_longest}->{after_longest}, EG-A4 {before_a4}->{after_a4}; '
      f'depths ' + ', '.join(f'{g["group"][3:]} {dep[g["group"]]}' for g in new))
