#!/usr/bin/env python3
"""Roster rev 4.2: lane WEB (the product page, tvofi 2026-09-30) over the LIVE round-9 roster.

    python3 build_roster_rev42.py LIVE.json OUT.json [SITE_COMMIT]

LIVE is .claude/workflows/wave-r9-groups.json on handoff/audit-r9-fixplan (9e63d2a3 when written: rev 4.1 applied, lane
UX Part of #1795). It adds two groups:
- R9-WEB-1: the page as docs/index.html and its pin, one new arm in tests/doc_claims.py;
- R9-WEB-2: the GitHub Pages deploy workflow.

It also adds after-edges on R9-RO-2 (WEB-1) and R9-RO-3 (WEB-2), carries into R9-RO-3, R9-RO-4, R9-RO-9 and the
lane-UX card groups, waves for the new groups only, and one _comment line. It changes no stage, no issue and no other
brief.

It refuses:
- a file without rev 4.1 (no R9-UX-1);
- a file that already has R9-WEB-1;
- a dangling edge or a cycle;
- any result that lengthens the longest open chain or EG-A4's open chain.
"""
import copy, json, sys

LIVE, OUT = sys.argv[1], sys.argv[2]
SC = sys.argv[3] if len(sys.argv) > 3 else '2b5031bf'
r = json.load(open(LIVE))
G = {g['group']: g for g in r['groups']}
if 'R9-UX-1' not in G:
    sys.exit('refused: R9-UX-1 absent; apply rev 4.1 (build_roster_rev41.py) first')
if 'R9-WEB-1' in G:
    sys.exit('refused: R9-WEB-1 already present; rev 4.2 is applied')
NEED = ('R9-UI-2', 'R9-UI-4', 'R9-F10.4', 'R9-RO-2', 'R9-RO-3', 'R9-RO-4', 'R9-RO-9', 'R9-EG-A4',
        'R9-UX-1', 'R9-UX-2', 'R9-UX-3', 'R9-UX-5', 'R9-UX-6', 'R9-UX-7')
for n in NEED:
    if n not in G:
        sys.exit(f'refused: {n} missing from the live roster; re-plan rev 4.2 against it')
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

SITE = 'handoff/round9/state/alt/design/site'
DOR = (f'Design of record: {SITE}/DESIGN-SITE.md (at {SC} on handoff/audit-r9-alt), with the page {SITE}/index.html, '
       f'the pin prototype {SITE}/check_site.py, its planted-error controls {SITE}/controls.py and their output '
       f'{SITE}/SITE-CHECKS.txt, and {SITE}/CONTRAST.json beside it, all in the lane-UI identity of '
       f'handoff/round9/state/alt/design/DESIGN.md (at 7bca8ab3); where this brief and those files disagree, the newer is '
       f'right and the other is the bug.')
DECIDED = ('tvofi decided on 2026-09-30: "Design a full product web page, based on the user facing documentation in the '
           'repo, in the same design language as the showcase page", implemented and pinned to the master documentation; '
           'W1 pinning is test-pinned and linked: every claim on the page carries a source anchor into the README or the '
           'reader docs, a test refuses drift, and the README links the page; W2 the page is served by GitHub Pages '
           'through a workflow. The design adds S3: no savings percentage (the docs call the only one a one-off '
           'measurement on the author\'s house), unless tvofi asks for it as a labelled note.')
FIRST = ('First rule: before any work, read CLAUDE.md and every rules file it references (.claude/rules, the role contract '
         'tools/audit/briefs/fixer.md), and follow them; pass this rule on in every sub-agent brief. Never call the owner '
         'anything but tvofi, in commits, PR bodies, comments and delivery notes; the PR attribution line is '
         '_Requested by **tvofi**_.')
FEATURE = ('This is a new feature, not a finding: there is no class, no barrier and no RCA. It touches no Python module '
           'under custom_components, so every value-bearing golden stays byte-identical (CLAUDE.md rule 3), and it '
           'states no version on the page (rule 4).')
BUDGET = ('Budgets (U4, CLAUDE.md rule 2): no structure metric measures docs/ or tests/ and the policy caps do not cover '
          'docs/, so nothing here should bite; if a cap does, design to fit first, and a raise is the last resort, '
          'confirmed by tvofi before the push and merged only on tvofi\'s approving review (budget-raise-gate). Run '
          'python3 tests/structure.py and node .claude/workflows/policy_lint.mjs before every hand-off; carry no number.')
STANDING = ('Standing: cloud seat: no PRs, no GitHub comments, no issues, no gh; hand the branch and body off on your handoff '
            'branch and the Mac orchestrator pushes as the hpo-author App via tools/audit/app_push.sh; hpo-approver approves a '
            'non-code-owned PR, tvofi reviews a code-owned one (decision 0011). Mutation: pin the sites this change adds '
            '(mutation_table.py --scope changed --base origin/main); --max 0 is never proof. Resumability (tvofi 19:05Z): '
            'commit and push to your handoff branch at every step boundary and at least every 30 minutes, update the resume '
            'note in this entry\'s resume field with every push, and append one dated line per milestone to the round-9 '
            'resume log. No VERSION, manifest version or notes-heading edits. Part of #201; issues stay empty until the '
            'orchestrator files the lane\'s feature issue.')


def group(gid, after, why, effort, gate, branch, brief):
    g = copy.deepcopy(G['R9-UX-4'])
    g.update(group=gid, lane='WEB', issues=[], fixes=[], findings=[], covers=[], cap_exception=None, sweep_instances=[],
             **{'class': 'feature'}, fixerModel='sonnet', reviewerModel='opus', effort=effort, fixture=False,
             owner_gate=gate, rca=False, barrier=[], barrier_prototype=[], blocked_on=None, after=after, brief=brief)
    g['model'] = dict(fixer='sonnet', fixer_why=why, reviewer='opus', rca=None, runner='haiku', record='sonnet')
    n = gid.replace('R9-', '')
    g['resume'].update(stage='not-started', branch=branch, commit=None, last_step=None,
                       next_step=(f'fixer.md step 1 at a fresh merge base once every after-edge has merged: re-read '
                                  f'{SITE}/DESIGN-SITE.md, then write the failing test'),
                       note_file=f'handoff/round9/fix/resume/{n}.md on {branch}', review_branch=branch + '-review',
                       review_note_file=f'handoff/round9/fix/resume/{n}-review.md on {branch}-review',
                       plan=(f'handoff/audit-r9-alt: handoff/round9/state/ALT-ENDGAME-PLAN.md (rev 4.2) and {SITE}/ at '
                             f'{SC}; this roster'),
                       note=('Added by roster rev 4.2 (tvofi\'s product page, 2026-09-30); issues stay empty until the '
                             'orchestrator files the feature issue. The seat\'s resume note on its branch outranks this '
                             'entry for in-flight state.'))
    for k in ('pickup_cloud', 'pickup_local'):
        g['resume'].pop(k, None)
    return g


def head(n, what, why):
    return (f'Round-9 feature PR {n} (lane WEB, {what}). Models: fixer sonnet ({why}); reviewer opus in another session; '
            f'runner haiku; record sonnet. {DECIDED} {FIRST} {DOR} {FEATURE}')


WHY1 = 'a static page ported from the design of record and one doc_claims arm ported from a working prototype'
WHY2 = 'one workflow of shell staging and the two Pages actions'
new = [
    group('R9-WEB-1', ['R9-UI-2', 'R9-UI-4', 'R9-F10.4'], WHY1, 'high',
          'tests/closure.py and tests/layout.json are code-owned; merges on tvofi\'s approving review at the head',
          'handoff/r9-web-page',
          head('WEB-1', 'the product page and its pin', WHY1) +
          ' Scope: port the design page to the root of docs/ as index.html, so that its relative image paths resolve '
          'the same in the tree and on Pages; its self-hosted fonts and their OFL texts go in a new site folder under '
          'docs/. Image sources become the paths under docs/ that each data-repo attribute names: the hero is the '
          'README hero docs/img/card-plan-chart.png that R9-UI-4 regenerates, and the how-it-works figure is the one '
          'R9-UI-2 lands. The design note and the design-only PENDING map go. Port check_site.py into '
          'tests/doc_claims.py as one new arm with its own anchor, beside check_figures, reading the page and the reader '
          'corpus from the working tree, never from a git ref. Name it in the module docstring as every arm is. '
          'Claim rules, as DESIGN-SITE.md states them:'
          ' (1) an element with data-src is a claim on a README or reader-doc section addressed by its GitHub heading '
          'slug; in verbatim mode every text node, split on the ellipsis, must appear in that section\'s reader text; '
          'in key-phrase mode (data-q) the phrase must appear and every number must be one the section states;'
          ' (2) data-copy marks page copy that states no fact, and the arm reports how many there are;'
          ' (3) refused: a digit outside any claim; a missing image or alt text; a repository link whose path or slug '
          'does not resolve; any third-party script, stylesheet, CSS url() or image; the stamped VERSION or a '
          'version literal;'
          ' (4) two-sided: every README "What it does" bold lead is a data-feature heading and nothing else is, and the '
          'page\'s data-doc set equals the README Documentation table\'s link targets;'
          ' (5) anchor: no page, or zero claims, features or docs rows, is red.'
          ' Failing test first: run the arm before the page exists and show the anchor red, then show each planted '
          'error of controls.py red at the head, in the body\'s table, with the baseline green. Link it: add a Product '
          'page row to the README Documentation table and one line under the badges, pointing at the page file until '
          'R9-WEB-2 serves it. The pin then requires the page\'s docs section to list the new row, so add it. Classify '
          'deliberately: the page and its folder go on INERT_EXCEPT in tests/closure.py, and tests/layout.json gets one '
          'category glob for them. The closure of doc_claims.py will read UNDER-SCOPED: CI\'s closures-autofix records '
          'it, so do not re-derive it by hand. Do not edit tests/README.md, which is code-owned and in the F11.4/F11.5 '
          'lane; if tests/entities.py demands a line there, stop and hand back so the orchestrator orders this PR after '
          'R9-F11.5. Must keep working: the README rules in tests/entities.py (mermaid only inside details, no relative '
          'img tags, the pinned hero line, the counts), tests/md_tables.mjs, and every existing doc_claims.py arm; run '
          'all three at the merge base and at the head. Out of scope: any savings figure (S3), a second language '
          '(the page is English, like the README), and analytics of any kind. ' + BUDGET + ' ' + STANDING),
    group('R9-WEB-2', ['R9-WEB-1'], WHY2, 'medium',
          '.github/workflows is code-owned; merges on tvofi\'s approving review at the head, and tvofi enables Pages '
          '(Settings, Pages, Source: GitHub Actions) once before the first dispatch',
          'handoff/r9-web-pages',
          head('WEB-2', 'the GitHub Pages deploy', WHY2) +
          ' Scope: one new workflow file under .github/workflows that deploys the product page to GitHub Pages. Triggers: '
          'a push of a v* tag, the same trigger .github/workflows/release.yml uses (the stamp pushes the tag over the '
          'deploy key, so the event fires), plus workflow_dispatch, so the served page matches the release HACS '
          'installs. Permissions: contents read, pages write, id-token write, with one concurrency group. One job '
          'checks out the tag and stages the site with shell only: the page, its site folder, and every png and svg '
          'under docs/ at its own path. It never stages a .md, so the development record is not published as web '
          'pages. It then runs the upload and deploy actions, pinned the way the other workflows pin theirs. It runs '
          'no repository script, so the required-check enforcement surface does not grow: re-run '
          'tools/audit/round6/D11/fix/codeowners_gap.py and show the surface count unchanged in the body. The '
          'workflow is not a required check. Once tvofi has enabled Pages, dispatch it once at the branch head and '
          'show the served page, its fonts and one image loading, and that a .md path returns 404. Then replace the '
          'README row\'s file link with the served URL; the pin and the HACS README rules stay green. Failing test '
          'first: a check in the existing workflow lint, or a new arm, fails at the merge base (no Pages workflow, or '
          'one that stages a .md) and passes at the head. Use whichever of those the repository already runs over '
          'workflows. ' + BUDGET + ' ' + STANDING),
]
G.update({g['group']: g for g in new})
r['groups'].extend(new)

G['R9-RO-2']['after'].append('R9-WEB-1')
G['R9-RO-3']['after'].append('R9-WEB-2')

C = (f'Carry from roster rev 4.2 (tvofi\'s product page, 2026-09-30; design of record {SITE}/DESIGN-SITE.md at {SC}): ')
G['R9-RO-3']['brief'] += (' ' + C + 'the product page R9-WEB-1 lands at the root of docs/ references images under docs/img '
                          'and docs/setup by relative path; move its references with the images in the same commit. The '
                          'doc_claims.py page arm refuses a dead one. The Pages workflow stages images by pattern, so it '
                          'needs no edit.')
G['R9-RO-4']['brief'] += (' ' + C + 'archiving docs/backlog.md removes its row from the README Documentation table; the '
                          'doc_claims.py page arm then requires the page\'s docs section to drop it in this PR.')
G['R9-RO-9']['brief'] += (' ' + C + 'the layout enforcement covers the product page and its site folder through the glob '
                          'R9-WEB-1 adds; keep it.')
for gid in ('R9-UX-1', 'R9-UX-2', 'R9-UX-3', 'R9-UX-5', 'R9-UX-6', 'R9-UX-7'):
    G[gid]['brief'] += (' ' + C + 'decision U5 extends to the product page: a card page whose screenshot this PR adds or '
                        'regenerates takes its gallery slot on the page in the same PR (DESIGN-SITE.md, gallery slots), '
                        'with the caption quoted from its section of docs/dashboard-card.md. A README feature paragraph '
                        'this PR adds or removes is forced onto or off the page by the doc_claims.py page arm.')


def need(g):
    return 1 + max((G[a]['wave'] for a in g['after']), default=0)
for g in new:
    g['wave'] = need(g)
for gid in ('R9-RO-2', 'R9-RO-3'):
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
    f'rev 4.2 (2026-09-30, handoff/audit-r9-alt): lane WEB, the product page tvofi asked for (design of record '
    f'{SITE}/ at {SC}): R9-WEB-1 the page at the root of docs/ and its pin, one doc_claims.py arm, after R9-UI-2, R9-UI-4 '
    f'and R9-F10.4; R9-WEB-2 the GitHub Pages workflow, after WEB-1. R9-RO-2 after WEB-1; R9-RO-3 after WEB-2. Carries '
    f'into R9-RO-3, RO-4, RO-9 and UX-1, 2, 3, 5, 6, 7. Open chains unchanged: longest {after_longest}, EG-A4 {after_a4}.')
json.dump(r, open(OUT, 'w'), indent=2, ensure_ascii=False)
open(OUT, 'a').write('\n')
print(f'{len(r["groups"])} groups; open chains longest {before_longest}->{after_longest}, EG-A4 {before_a4}->{after_a4}; '
      f'depths ' + ', '.join(f'{g["group"][3:]} {dep[g["group"]]}' for g in new) +
      f'; RO-2 {dep["R9-RO-2"]}, RO-3 {dep["R9-RO-3"]}; waves ' + ', '.join(f'{g["group"][3:]} {g["wave"]}' for g in new))
