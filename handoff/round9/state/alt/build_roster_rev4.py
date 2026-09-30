#!/usr/bin/env python3
"""Roster rev 4: lane UI (tvofi's design decisions of 2026-09-30) over the LIVE round-9 roster.

    python3 build_roster_rev4.py LIVE.json OUT.json [DESIGN_COMMIT]

LIVE is .claude/workflows/wave-r9-groups.json on handoff/audit-r9-fixplan (rev 3.3 was 35800d45). The script only adds:
four groups R9-UI-1..4, two after-edges (R9-SW-3 after R9-UI-4; R9-RO-2 after R9-UI-2 and R9-UI-4), four carries
(R9-RO-3, R9-RO-4, R9-SW-3, R9-F6.3), the resulting wave bumps, and one _comment line. It truths four groups merged on
main (F2.4 #1782, F9.3 #1785, EG-B8 #1786, RO-1 #1790), and changes no issue and no other brief. It refuses a file that already has R9-UI-1, and refuses a dangling edge or a cycle.
DESIGN_COMMIT defaults to the commit that carries handoff/round9/state/alt/design/ on handoff/audit-r9-alt.
"""
import copy, json, sys

LIVE, OUT = sys.argv[1], sys.argv[2]
DC = sys.argv[3] if len(sys.argv) > 3 else '7bca8ab3'
r = json.load(open(LIVE))
G = {g['group']: g for g in r['groups']}
if 'R9-UI-1' in G:
    sys.exit('refused: R9-UI-1 already present; rev 4 is applied')
for need in ('R9-SW-3', 'R9-F6.4', 'R9-RO-2', 'R9-RO-3', 'R9-RO-4', 'R9-F6.3'):
    if need not in G:
        sys.exit(f'refused: {need} missing from the live roster; re-plan rev 4 against it')

DOR = (f'Design of record: handoff/round9/state/alt/design/DESIGN.md (at {DC} on handoff/audit-r9-alt), with the scripts, '
       f'the palette checks handoff/round9/state/alt/design/PALETTE-CHECKS.txt and the rendered assets beside it (the proposal '
       f'tvofi decided on 2026-09-30); where this brief and that file disagree, the newer is right and the other is the bug.')
DECIDED = ('tvofi decided the design proposal on 2026-09-30: D1 the "dusk" mark; D2 plan chart concept A, stacked panels, '
           '"make sure the plan editor and what-if-simulator still works"; D2b a fourth stat tile, indoor temperature; '
           'D3 adopt the series palette; D4 extend the card colour-vision test from deuteranopia to protanopia and tritanopia; '
           'D5 no plan-lock change (a manual plan already holds its slots for its 20-hour window, MANUAL_PLAN_WINDOW_HOURS).')
FIRST = ('First rule: before any work, read CLAUDE.md and every rules file it references (.claude/rules, the role contract '
         'tools/audit/briefs/fixer.md), and follow them; pass this rule on in every sub-agent brief. Never call the owner '
         'anything but tvofi, in commits, PR bodies, comments and delivery notes; the PR attribution line is '
         '_Requested by **tvofi**_.')
FEATURE = ('This is a new production feature, not a finding: there is no class, no barrier and no RCA. It touches no Python '
           'module, so every value-bearing golden stays byte-identical and tests/golden/claimed_drift.txt stays untouched '
           '(CLAUDE.md rule 3); moved card states are claimed in tests/golden/card_claimed_drift.txt with claims-for equal to '
           'VERSION, never re-recorded.')
STANDING = ('Standing: cloud seat: no PRs, no GitHub comments, no issues, no gh; hand the branch and body off on your handoff '
            'branch and the Mac orchestrator pushes as the hpo-author App via tools/audit/app_push.sh; hpo-approver approves a '
            'non-code-owned PR, tvofi reviews a code-owned one (decision 0011). Every figure is re-derived at your own merge '
            'base; carry no number. Run python3 tests/structure.py before every hand-off: no structure metric measures the '
            'card, so no raise is expected; if an honest re-record still needs one, the mandate (rev 3.1) confirms it, post '
            'the measured value and reason on #201 before the push, and it merges only on tvofi\'s approving review '
            '(budget-raise-gate). Mutation: pin the sites this change adds (mutation_table.py --scope changed --base '
            'origin/main); --max 0 is never proof. Resumability (tvofi 19:05Z): commit and push to your handoff branch at '
            'every step boundary and at least every 30 minutes, update the resume note in this entry\'s resume field with '
            'every push, and append one dated line per milestone to the round-9 resume log. No VERSION, manifest version or '
            'notes-heading edits. Part of #201; issues stay empty until the orchestrator files the lane\'s feature issue.')
LAYOUT = ('Layout barrier (R9-RO-1, merged as #1790): tests/layout.json admits only docs/img/card, docs/img/model and '
          'docs/img/setup under docs/img, and its dead-category arm refuses a glob that matches no file, so this PR admits '
          'the folder it creates: add the folder\'s glob to the docs category in the same commit as its files, and put '
          'python3 tests/layout.py before and after in the body (tests/layout.json is code-owned: the merge waits on '
          'tvofi\'s approving review).')


def group(gid, after, fixer, why, effort, gate, branch, brief):
    g = copy.deepcopy(G['R9-SW-3'])
    g.update(group=gid, lane='UI', issues=[], fixes=[], findings=[], covers=[], cap_exception=None, sweep_instances=[],
             **{'class': 'feature'}, fixerModel=fixer, reviewerModel='opus', effort=effort, fixture=False,
             owner_gate=gate, rca=False, barrier=[], barrier_prototype=[], blocked_on=None, after=after, brief=brief)
    g['model'] = dict(fixer=fixer, fixer_why=why, reviewer='opus', rca=None, runner='haiku', record='sonnet')
    n = gid.replace('R9-', '')
    g['resume'].update(stage='not-started', branch=branch, commit=None, last_step=None,
                       next_step=('fixer.md step 1 at a fresh merge base once every after-edge has merged: re-read '
                                  'handoff/round9/state/alt/design/DESIGN.md, then write the failing test'),
                       note_file=f'handoff/round9/fix/resume/{n}.md on {branch}', review_branch=branch + '-review',
                       review_note_file=f'handoff/round9/fix/resume/{n}-review.md on {branch}-review',
                       plan=(f'handoff/audit-r9-alt: handoff/round9/state/ALT-ENDGAME-PLAN.md (rev 4) and '
                             f'handoff/round9/state/alt/design/ at {DC}; this roster'),
                       note=('Added by roster rev 4 (tvofi\'s design decisions, 2026-09-30); issues stay empty until the '
                             'orchestrator files the feature issue. The seat\'s resume note on its branch outranks this '
                             'entry for in-flight state.'))
    for k in ('pickup_cloud', 'pickup_local'):
        g['resume'].pop(k, None)
    return g


def head(n, what, fixer, why):
    return (f'Round-9 feature PR {n} (lane UI, {what}). Models: fixer {fixer} ({why}); reviewer opus in another session; '
            f'runner haiku; record sonnet. {DECIDED} {FIRST} {DOR} {FEATURE}')


# 0. Truthing: four groups merged on main before this revision while the live roster (35800d45) still shows them open.
# Only a group whose live stage is not already done is touched; the merge commit is the record.
MERGED = {
    'R9-F2.4': ('3dfebc169096e53a5d3713a019de2b525174bc27', 1782),
    'R9-F9.3': ('3d1826b2a8986a758f2b9d76eedb8528b0194816', 1785),
    'R9-EG-B8': ('830f84ad7a25453248a7709f4dfd13769b2d9684', 1786),
    'R9-RO-1': ('48786f657cd785d1963073b9f710af7565aac517', 1790),
}
for gid, (sha, pr) in MERGED.items():
    rs = G[gid]['resume']
    if rs['stage'] != 'done':
        rs.update(stage='done', commit=sha, next_step='none',
                  last_step=f'MERGED as #{pr} at {sha[:8]} (truthed by roster rev 4 from origin/main; the delivery row and the '
                            f'seat notes hold the review record)')

new = []
new.append(group(
    'R9-UI-1', [], 'sonnet', 'asset replacement from rendered masters, no code', 'low',
    'tests/layout.json is code-owned (the new folder\'s glob); merges on tvofi\'s approving review at the head',
    'handoff/r9-ui-brand',
    head('UI-1', 'brand identity', 'sonnet', 'asset replacement from rendered masters, no code') +
    ' Scope: the integration\'s Home Assistant brand images and icons, from the design of record\'s assets/brand/ and '
    'assets/svg/. (1) Replace custom_components/heatpump_optimizer/brand/icon.png and brand/logo.png with the dusk icon '
    '(256 px) and logo (shortest side 130 px), and add the @2x and dark_ variants beside them, the eight files of Home '
    'Assistant\'s brand spec: transparent, trimmed, sizes as DESIGN.md section 2 lists; verify each with PIL (size, alpha '
    'channel, trimmed bounding box) and put the table in the body. (2) custom_components/heatpump_optimizer/icon.png '
    'becomes the 512 px dusk icon, and the root icon.png is replaced by the same bytes: R9-RO-4 deletes the root copy '
    'on the premise that the two are byte-identical, so prove it with the two blob ids in the body. (3) The SVG masters '
    '(mark, app tile, inline and stacked lockups, light and dark) go into a new docs/img/brand folder. Classify every new '
    'file deliberately (tests/entities.py refuses an unclassified one): the brand PNGs sit under the product tree the '
    'closure already classifies, and docs/img is INERT unless a script pins the file (INERT_EXCEPT); state which in the '
    'body. ' + LAYOUT + ' Tests: none change behaviour; run tests/entities.py and the scoped gate, and quality_scale.yaml '
    'keeps its brands rule true. ' + STANDING))
new.append(group(
    'R9-UI-2', ['R9-UI-1'], 'sonnet', 'README edits and a figure generator ported from the design of record', 'medium',
    'tests/layout.json is code-owned (the new folder\'s glob); merges on tvofi\'s approving review at the head',
    'handoff/r9-ui-readme',
    head('UI-2', 'README graphics', 'sonnet', 'README edits and a figure generator ported from the design of record') +
    ' Scope: README.md and a new docs/img/readme folder. Apply the design of record\'s assets/readme/README.proposal.diff '
    'as re-derived at your merge base: (1) the banner as one inline image line above the title, in the HACS link '
    'rewriter\'s form (tests/entities.py pins it: an inline ![alt](src) image alone on its line, no relative <img>, no '
    'second :// on the line); (2) the four badges recoloured to fjord with License in ember, and the License link made '
    'absolute, because its relative target breaks the badge image under HACS today (show the failing rewriter case '
    'first); (3) the "At a glance" 3x2 table, every cell a claim the README already makes, run through tests/doc_claims.py '
    'and the D6 claim register; (4) the "how it works" figure under that heading, the mermaid diagrams staying in their '
    'details blocks. The pinned hero line docs/img/card-plan-chart.png is not touched (R9-UI-4 regenerates the image, '
    'R9-RO-3 moves it). Port readme_assets.py from the design of record into a generator in the new folder beside its '
    'outputs, the repository\'s generator convention (docs/img/make_card_figures.mjs), with fonts outlined or embedded so '
    'the output is byte-stable; classify it and its outputs deliberately. The design of record\'s CHECKS.txt shows '
    'tests/entities.py, doc_claims.py and md_tables.mjs green with the proposal applied at f88e6af8: re-run all three at '
    'your head. The social preview is not a tracked file: tvofi uploads it under the repository settings; name the file '
    'in the body. ' + LAYOUT + ' ' + STANDING))
new.append(group(
    'R9-UI-3', ['R9-F6.4'], 'opus', 'a token layer across the card plus new headline components, under the P9 grid and the theme-contrast pins', 'high',
    'tests/card_browser.mjs is code-owned; merges on tvofi\'s approving review at the head',
    'handoff/r9-ui-card',
    head('UI-3', 'card visual system', 'opus', 'a token layer across the card plus new headline components, under the P9 grid and the theme-contrast pins') +
    ' Borrowed files: custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js from F6 (the after edge on '
    'R9-F6.4, the lane\'s last PR, orders this PR after R9-F1.8\'s money-unit resolver, whose units the tiles show, and '
    'after R9-F6.3\'s P9 grid, which measures what this PR paints); translations/en.json and translations/sv.json only '
    'if a new label needs a key. Scope, per DESIGN.md section 3: (1) a token layer, custom properties with an hpo prefix '
    'defined inside cardStyleBlock(darkMode), one var() level deep with a literal fallback (tests/card.mjs resolves one '
    'level and refuses deeper), absorbing the card\'s hex literals; (2) the dusk mark before the title and a status pill '
    'after it (heating, idle, stale plan, fallback, and "manual plan until HH:MM" while the manual override is active); '
    '(3) four stat tiles in one style: price now, planned heat, plan cost and indoor temperature (D2b), the last read from '
    'the indoor-temperature sensor the card already resolves for the chart\'s now-temperature label; that sensor is not '
    'in the card\'s render signature today, so add it to headlineSignature or the tile never refreshes, and pin the '
    'refresh; a 2x2 grid on a phone; the existing savings and score tiles stay (CLAUDE.md: never delete working '
    'functionality merely to fit); (4) compact legend chips with the 24 px hit target kept (44 px on touch), one '
    'scrolling row on a phone; (5) the dashed-line sentence becomes a footnote under the legend; (6) price and solar area '
    'fills at 16% and 10% opacity. Every new colour must pass tests/card.mjs (the READABLE 4.5:1 set, the one-level var() '
    'rule, the .dearer literal) and R9-F6.3\'s P9 grid in both themes: the component contrast table in DESIGN.md is the '
    'expectation, the grid is the proof. Failing tests first: the indoor tile present and refreshing on a sensor change, '
    'the pill states, the token resolution in both themes. Claim every moved state in tests/golden/card_claimed_drift.txt; '
    're-take the README hero only if the tile row changes it (tests/card_browser.mjs hero mode) and leave the chart itself '
    'to R9-UI-4. Put before and after screenshots, light and dark, 900 and 375 px, in the body. ' + STANDING))
new.append(group(
    'R9-UI-4', ['R9-UI-3'], 'opus', 'chart geometry rework inside the one SVG, under the plan-editor, what-if and CVD pins', 'high',
    'tests/card_browser.mjs is code-owned; merges on tvofi\'s approving review at the head',
    'handoff/r9-ui-chart',
    head('UI-4', 'plan chart concept A, palette, colour-vision gate', 'opus', 'chart geometry rework inside the one SVG, under the plan-editor, what-if and CVD pins') +
    ' Borrowed files: custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js from F6 (after R9-UI-3), '
    'docs/img/make_card_figures.mjs, docs/dashboard-card.md. Failing test first (D4): extend the colour-vision block of '
    'tests/card.mjs from the deuteranope simulation to protanopia and tritanopia, every pair of series drawn in one panel; '
    'run it on the current series definitions and show it red (DESIGN.md section 4 and PALETTE-CHECKS.txt record today\'s '
    'failures: protan dE 0.4 between house and hot-water heating, and the grey and teal below the chroma floor), then land '
    'the palette of record (D3, the per-panel table in DESIGN.md) and show it green; keep the existing 3:1 and '
    'dash-where-close arms. Then concept A (D2), per DESIGN.md section 4: three panels, price, heating power and '
    'temperatures, drawn inside the one chart SVG each copy already has, with the one shared x-scale and the lane strip '
    'under the bottom panel; keep the geometry object\'s x fields, so the lane editor\'s hit-test, pan, wheel and the '
    'inline and dialog copies stay valid, and change only the y-scales, axes, gridlines, the series-to-panel assignment, '
    'the crosshair\'s vertical extent and the lane placement. Actioned power moves into the power panel with its '
    'colour of record. Must keep working, a review blocker, each pinned by a test that runs at the head: plan-editor drag, '
    'resize, add and remove, the keyboard menu, edge auto-pan, 24 and 44 px slot targets; apply_manual_plan and '
    'clear_manual_plan called with unchanged payloads; the what-if panel\'s simulate_plan and apply_schedule calls '
    'unchanged, and its draft wood slots in the wood lane; hover with the crosshair across all panels and a tooltip row '
    'per series; pan, wheel zoom and the expanded dialog; the 8 px chart font floor on a phone. tests/card_drift.mjs: '
    'claim every moved chart state in tests/golden/card_claimed_drift.txt. Rewrite docs/img/make_card_figures.mjs for the '
    'panel layout (it hard-codes the single plot and its "four units on four axes" subtitle) and regenerate its figures; '
    'regenerate the README hero at its current path with the browser test\'s hero mode; update the chart text in '
    'docs/dashboard-card.md; run tests/doc_claims.py and tests/entities.py at the head. Before and after screenshots, light '
    'and dark, 900 and 375 px, and an editor drag recording, in the body. ' + STANDING))

r['groups'].extend(new)
G.update({g['group']: g for g in new})

# edges
G['R9-SW-3']['after'].append('R9-UI-4')
for e in ('R9-UI-2', 'R9-UI-4'):
    G['R9-RO-2']['after'].append(e)

# carries
C = 'Carry from roster rev 4 (tvofi\'s design decisions, 2026-09-30; design of record handoff/round9/state/alt/design/DESIGN.md at ' + DC + '): '
G['R9-RO-3']['brief'] += (' ' + C + 'the two docs/img folders R9-UI-1 and R9-UI-2 created are already at their final paths: '
                          'do not move them; R9-UI-4 regenerated the README hero and the card figures at their old paths, '
                          'so move them as planned, and re-derive the move map at your merge base.')
G['R9-RO-4']['brief'] += (' ' + C + 'R9-UI-1 replaced custom_components/heatpump_optimizer/icon.png and the root icon.png '
                          'with the same bytes; re-check that the two blob ids are equal at your merge base before deleting '
                          'the root copy, and stop if they differ.')
G['R9-SW-3']['brief'] += (' ' + C + 'R9-UI-3 lands the card token layer and R9-UI-4 the stacked-panel chart before you: '
                          'style the silent-window rows with the tokens, and draw the silent and off band in the heating '
                          'power panel, beside the lanes, using the shared x-scale; the band\'s colours pass the extended '
                          'colour-vision test R9-UI-4 adds.')
G['R9-F6.3']['brief'] += (' ' + C + 'R9-UI-3 will replace the card\'s colour literals with custom properties resolved one '
                          'var() level deep; write the P9 contrast and reach arms against computed colours, not against '
                          'literal hex strings in the source, so they keep measuring after that change.')

# waves: the live waves are not strict depths (several groups sit below 1 + max(after)), so rev 4 sets only the new
# groups' waves and lifts the two groups that gained an edge; it renumbers nothing else
def need(g):
    return 1 + max((G[a]['wave'] for a in g['after']), default=0)
for g in new:
    g['wave'] = need(g)
for gid in ('R9-SW-3', 'R9-RO-2'):
    G[gid]['wave'] = max(G[gid]['wave'], need(G[gid]))

# checks
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

r['_comment'].append(
    f'rev 4 (2026-09-30, handoff/audit-r9-alt): truthed F2.4 (#1782), F9.3 (#1785), EG-B8 (#1786) and RO-1 (#1790) to done; lane UI, four feature groups R9-UI-1..4 for tvofi\'s design decisions of '
    f'2026-09-30 (design of record handoff/round9/state/alt/design/ at {DC}): UI-1 brand and UI-2 README start now; UI-3 '
    f'card visual system after R9-F6.4; UI-4 chart concept A, palette and colour-vision gate after UI-3. Edges: R9-SW-3 '
    f'after R9-UI-4; R9-RO-2 after R9-UI-2 and R9-UI-4. Carries into R9-RO-3, RO-4, SW-3 and F6.3. D5 (full-horizon '
    f'plan lock) withdrawn by tvofi: no group. No critical-path group gains an edge.')
json.dump(r, open(OUT, 'w'), indent=2, ensure_ascii=False)
open(OUT, 'a').write('\n')
print(f'{len(r["groups"])} groups; waves UI-1..4 = {[G["R9-UI-" + str(i)]["wave"] for i in range(1, 5)]}; '
      f'SW-3 wave {G["R9-SW-3"]["wave"]}, RO-2 wave {G["R9-RO-2"]["wave"]}')
