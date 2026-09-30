#!/usr/bin/env python3
"""Roster rev 4.3: documentation sub-pages (tvofi 2026-09-30) over a roster with rev 4.2 applied.

    python3 build_roster_rev43.py ROSTER.json OUT.json [DOCS_COMMIT]

ROSTER is the live .claude/workflows/wave-r9-groups.json once rev 4.2 is applied. If rev 4.2 is not yet applied, run
build_roster_rev42.py first.

It adds R9-WEB-3: the generator that renders the reader docs into sub-pages at deploy, plus its build check, one new
tests/doc_claims.py arm. It also adds these after-edges:
- R9-WEB-2 after WEB-3;
- R9-RO-2 after WEB-3.

It appends carries to R9-WEB-2 (the workflow now runs the generator), R9-RO-3, R9-RO-4, R9-RO-6 and R9-RO-9. It sets
waves for WEB-3 and lifts only the groups that gained an edge. It adds one _comment line, and changes no stage and no
issue.

It refuses:
- a roster without R9-WEB-1;
- a roster that already has R9-WEB-3;
- a dangling edge or a cycle;
- any result that lengthens the longest open chain or EG-A4's open chain.
"""
import copy, json, sys

IN, OUT = sys.argv[1], sys.argv[2]
DC = sys.argv[3] if len(sys.argv) > 3 else '6c539ee3'
r = json.load(open(IN))
G = {g['group']: g for g in r['groups']}
if 'R9-WEB-1' not in G:
    sys.exit('refused: R9-WEB-1 absent; apply rev 4.2 (build_roster_rev42.py) first')
if 'R9-WEB-3' in G:
    sys.exit('refused: R9-WEB-3 already present; rev 4.3 is applied')
for n in ('R9-WEB-2', 'R9-RO-2', 'R9-RO-3', 'R9-RO-4', 'R9-RO-6', 'R9-RO-9', 'R9-EG-A4'):
    if n not in G:
        sys.exit(f'refused: {n} missing; re-plan rev 4.3 against this roster')
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
w1 = G['R9-WEB-1']
DOR = (f'Design of record: {SITE}/DESIGN-SITE.md, section "Documentation sub-pages" (at {DC} on handoff/audit-r9-alt), '
       f'with the generator prototype {SITE}/docs_build.mjs, its stylesheet {SITE}/docs.css, its planted-error '
       f'controls {SITE}/docs_controls.py and their output {SITE}/DOCS-CHECKS.txt, and the renders in '
       f'{SITE}/docs_shots; where this brief and those files disagree, the newer is right and the other is the bug.')
DECIDED = ('tvofi decided on 2026-09-30: "The docs should also be adopted to sub pages, if that is not unfeasible", on '
           'top of the product page (W1 test-pinned and linked, W2 GitHub Pages through a workflow). The design adds S7 '
           'built at deploy and never committed, S8 GitHub heading slugs, S9 the page set derived from the README '
           'Documentation table, S10 mermaid self-hosted from a lockfile, S11 no third-party request.')
# the rev 4.2 WEB briefs carry the shared first rule, feature note, budget and standing paragraphs; reuse them verbatim
b1 = w1['brief']
FIRST = b1[b1.index('First rule:'):b1.index('Design of record:')].strip()
BUDGET = b1[b1.index('Budgets (U4'):b1.index('Standing:')].strip()
STANDING = b1[b1.index('Standing:'):].strip()
FEATURE = ('This is a new feature, not a finding: there is no class, no barrier and no RCA. It touches no Python module '
           'under custom_components, so every value-bearing golden stays byte-identical (CLAUDE.md rule 3); no VERSION '
           'or version literal is written (rule 4).')
WHY = 'a markdown renderer ported from a working prototype over the vendored parser, and one doc_claims arm'

g = copy.deepcopy(w1)
g.update(group='R9-WEB-3', issues=[], fixes=[], after=['R9-WEB-1'], effort='high',
         owner_gate=('tests/layout.json, tests/closure.py and .github/CODEOWNERS are code-owned; merges on tvofi\'s '
                     'approving review at the head'))
g['model'] = dict(g['model'], fixer_why=WHY)
g['resume'].update(stage='not-started', branch='handoff/r9-web-docs', commit=None, last_step=None,
                   next_step=(f'fixer.md step 1 at a fresh merge base once every after-edge has merged: re-read the '
                              f'sub-pages section of {SITE}/DESIGN-SITE.md, then write the failing test'),
                   note_file='handoff/round9/fix/resume/WEB-3.md on handoff/r9-web-docs',
                   review_branch='handoff/r9-web-docs-review',
                   review_note_file='handoff/round9/fix/resume/WEB-3-review.md on handoff/r9-web-docs-review',
                   plan=(f'handoff/audit-r9-alt: handoff/round9/state/ALT-ENDGAME-PLAN.md (rev 4.3) and {SITE}/ at '
                         f'{DC}; this roster'),
                   note=('Added by roster rev 4.3 (tvofi\'s documentation sub-pages, 2026-09-30); issues stay empty '
                         'until the orchestrator adds the lane WEB feature issue. The seat\'s resume note on its branch '
                         'outranks this entry for in-flight state.'))
g['brief'] = (
    f'Round-9 feature PR WEB-3 (lane WEB, documentation sub-pages). Models: fixer sonnet ({WHY}); reviewer opus in '
    f'another session; runner haiku; record sonnet. {DECIDED} {FIRST} {DOR} {FEATURE}'
    ' Scope: port the generator prototype into a new site folder under tools/, together with a package.json and '
    'lockfile that pin mermaid for the deploy only; tests never install it. It renders the README, and every row of '
    'the README Documentation table except its EXCLUDE list (today only the archive docs/backlog.md), into one page '
    'each beside the product page. It uses the markdown-it 14.1.0 the repository vendors at .claude/workflows/vendor, '
    'required by the path .claude/workflows/render_md.mjs uses; add no parser. The build keeps GitHub\'s heading '
    'slugs, turns links to published docs into their pages and links to other tracked files into GitHub links, and '
    'renders badges and other third-party images as their words. It writes nothing into the tree: output goes to the '
    'directory it is given. The stylesheet goes in the site folder under docs/ that R9-WEB-1 made, beside the fonts. '
    'The build is its own check. Add one new arm to tests/doc_claims.py, beside the R9-WEB-1 page arm: it runs the '
    'build over the working tree into a temporary directory with the tracked-file list, and fails on every FAIL line '
    'the build prints. Those are: a dead anchor (same page or across pages), a missing image, a link to an untracked '
    'file, a README row whose file does not exist, and an EXCLUDE entry that is no longer a row. Its anchor: zero '
    'pages built is red. Name the arm in the module docstring. Failing test first: run the arm before the generator '
    'exists and show the anchor red, then show each docs_controls.py case red at the head in the body\'s table, with '
    'the baseline green and the page, link, anchor and image counts the build prints. Switch the product page\'s '
    'documentation cards, its card and setup links and its footer to the sub-pages. Extend the page arm with the '
    'prototype\'s sub-page rule: a link to a page the build does not produce is refused. The docs index still mirrors '
    'the README table, and the archive row keeps its GitHub link. Classify deliberately: one tests/layout.json glob '
    'for the new tools folder. The doc_claims.py closure will read UNDER-SCOPED, and CI\'s closures-autofix records '
    'it; do not re-derive it by hand. Add /tools/site/ with owner @tvofi to .github/CODEOWNERS in this PR: R9-WEB-2\'s '
    'workflow will execute the generator, which puts it on the required-check enforcement surface, and owning it here '
    'means WEB-2 need not edit CODEOWNERS. Do not edit tests/README.md, the reader docs themselves or the README '
    'beyond what the page links need. If the build finds a real defect in a doc (a dead anchor at the merge base), '
    'fix the doc in this PR with the finding named in the body; a docs defect is never excluded to pass. Must keep '
    'working: every existing doc_claims.py arm, tests/md_tables.mjs, the README rules in tests/entities.py, and the '
    'R9-WEB-1 page arm; run all at the merge base and at the head. Out of scope: a second language, search, versioned '
    'docs, and committing any generated HTML (S7). ' + BUDGET + ' ' + STANDING)
r['groups'].append(g)
G['R9-WEB-3'] = g

G['R9-WEB-2']['after'].append('R9-WEB-3')
G['R9-RO-2']['after'].append('R9-WEB-3')

C = f'Carry from roster rev 4.3 (tvofi\'s documentation sub-pages, 2026-09-30; design of record {SITE}/DESIGN-SITE.md at {DC}): '
G['R9-WEB-2']['brief'] += (
    ' ' + C + 'this supersedes "runs no repository script". The workflow now runs npm ci in the site folder under '
    'tools/ that R9-WEB-3 lands, runs its generator into the staging directory beside the product page, and copies the '
    'single mermaid file into the site folder. The rest stages as before, and no .md is ever published. Re-run '
    'tools/audit/round6/D11/fix/codeowners_gap.py and show that the surface grew by exactly the generator and what the '
    'harness says it imports, all of it owned. WEB-3 owns the generator folder. If the harness reports anything '
    'unowned, stop and hand back: the orchestrator then orders this PR before R9-RO-2, which also edits '
    '.github/CODEOWNERS. After the dispatch, show one sub-page with a drawn diagram and one cross-page anchor landing.')
G['R9-RO-3']['brief'] += (' ' + C + 'the rendered documentation pages resolve images and links from the markdown at '
                          'deploy, so your moves need no generator edit; the doc_claims.py docs-build arm fails on any '
                          'link or image your rewrite leaves dead.')
G['R9-RO-4']['brief'] += (' ' + C + 'when you archive docs/backlog.md and drop its README row, remove it from the docs '
                          'generator\'s EXCLUDE list in the same PR; the docs-build arm refuses a stale exclusion.')
G['R9-RO-6']['brief'] += (' ' + C + 'the docs generator in the site folder under tools/ requires the vendored markdown-it '
                          'by the path .claude/workflows/render_md.mjs uses; re-point it when you move the vendor '
                          'directory. The doc_claims.py docs-build arm refuses a missing parser.')
G['R9-RO-9']['brief'] += (' ' + C + 'the layout enforcement covers the site folder under tools/ through the glob R9-WEB-3 '
                          'adds; keep it.')


def need(x):
    return 1 + max((G[a]['wave'] for a in x['after']), default=0)
g['wave'] = need(g)
for gid in ('R9-WEB-2', 'R9-RO-2', 'R9-RO-3'):
    G[gid]['wave'] = max(G[gid]['wave'], need(G[gid]))

for x in r['groups']:
    for a in x['after']:
        if a not in G:
            sys.exit(f'dangling edge {x["group"]} -> {a}')
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
    f'rev 4.3 (2026-09-30, handoff/audit-r9-alt): R9-WEB-3, the reader docs rendered as sub-pages of the product page at '
    f'deploy with the vendored markdown-it, its build a doc_claims.py arm (design of record {SITE}/ at {DC}); after '
    f'WEB-1. R9-WEB-2 after WEB-3 (its workflow now runs the generator); R9-RO-2 after WEB-3 (layout, closure, '
    f'CODEOWNERS). Carries into R9-WEB-2, RO-3, RO-4, RO-6 and RO-9. Open chains unchanged: longest {after_longest}, '
    f'EG-A4 {after_a4}.')
json.dump(r, open(OUT, 'w'), indent=2, ensure_ascii=False)
open(OUT, 'a').write('\n')
print(f'{len(r["groups"])} groups; open chains longest {before_longest}->{after_longest}, EG-A4 {before_a4}->{after_a4}; '
      f'depths WEB-1 {dep["R9-WEB-1"]}, WEB-3 {dep["R9-WEB-3"]}, WEB-2 {dep["R9-WEB-2"]}, RO-2 {dep["R9-RO-2"]}, '
      f'RO-3 {dep["R9-RO-3"]}; waves WEB-3 {g["wave"]}, WEB-2 {G["R9-WEB-2"]["wave"]}')
