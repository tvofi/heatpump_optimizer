#!/usr/bin/env python3
"""D13 / round 5 -- first-pass yield, rounds per merge, verdict coverage, block classes.

METRIC, over the window (first-parent commits of the pinned baseline whose
committer date is in [D13_WINDOW_START, BASELINE_UTC], D13.md item 1):

  n_merges            merged pull requests the enumerator returns, where a merge
                      is a first-parent commit of the window resolved to a pull
                      request by `/commits/<sha>/pulls` -- `policy_lint.mjs`'s
                      `enumerateMerges` in API mode.
  first_pass_yield    share of those merges whose FIRST verdict is `merge`; a
                      verdict is an issue comment (`/issues/<n>/comments`) or a
                      pull-request review (`/pulls/<n>/reviews`) whose first
                      line matches `^Fix review:\\s*(merge|blocked)`, ordered by
                      time across both endpoints. THE BRIEF'S PREFIX RULE, which
                      is deliberately LOOSER than the wave script's
                      `VERDICT_RE`: `Fix review: merge <sha> -- Round 1` is a
                      merge under it and not under `VERDICT_RE`. Both are
                      reported (`first_pass_yield` / `first_pass_yield_strict`,
                      `rounds_*` / `strict_rounds_*`) so the difference between
                      the process-level count and the parser-level count is a
                      number rather than an argument.
  rounds_mean/max     verdicts per merge, mean and max. A merge with no verdict
                      has 0 rounds and is counted in the denominator, so yield
                      and rounds describe the same population.
  outside_grammar     items whose first line starts `Fix review:` and does NOT
                      match the production VERDICT_RE -- its own row, never
                      folded in.

THE BLOCK-CLASS TABLE is keyed on THE CLASS WORD THE REVIEWER WROTE, which is
the only thing a router can act on: a blocked verdict whose class word is not in
`VERDICT_CLASSES` is unroutable whether or not it parsed, and a bare `Fix
review: blocked` wrote no word at all. Bucketing is mine (D13.md leaves it to
the finder) and is stated in BUCKET below; a word the grammar does not have is
its own row and is bucketed by the same axis, never folded into `other`.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 /tmp/heatpump-orch/audit-r5-D13/h1_verdicts.py
  ... --perturb reshape   one accepted verdict re-shaped out of the grammar
  ... --perturb grammar   a one-line production edit to VERDICT_RE, applied to a
                          COPY of web-fix-wave.js under the temp root
  ... --perturb classes   the nine words the reviewers used that the grammar
                          does not have appended to VERDICT_CLASSES in a COPY

PERTURBATION AND DIRECTION. `--perturb reshape` rewrites ONE parsable verdict's
first line so the grammar no longer takes it ("Fix review: merge <sha>" becomes
"Fix review — merge <sha>"); parsed_verdicts must fall by exactly 1, and
outside_grammar must rise by exactly 1. `--perturb grammar` narrows VERDICT_RE's
`\\s+` to `\\s\\s+` in a copy of the production file; parsed_verdicts must fall
to 0. `--perturb classes` adds the nine unknown words to VERDICT_CLASSES in a
copy; outside_grammar must fall by exactly 9 (the seven bare `blocked` items,
the abbreviated merge SHA and the trailing-text merge stay outside). Neither
touches a live pull request and neither edits production in place.

MACHINE: any; network-bound counts, no timing claim. `RESULT api_failures=0`
is required before any figure here is evidence.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d13lib as L  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# MY BUCKETING of VERDICT_CLASSES into the three families D13.md asks for,
# stated here because D13.md leaves it to the finder. The axis is WHAT HAS TO
# CHANGE for the next round to pass:
#   engineering          the fix or its proof is wrong -- a defect in the code,
#                        in the harness that measures it, or in the control arm.
#   record-and-body      the PR's own BODY is what is wrong: a figure it cannot
#                        support, a version it must not touch, a carried finding
#                        it did not carry.
#   orchestration        neither the code nor the body: the process around the
#                        pull request -- a head that moved under the review, a
#                        conflict, a root-cause answer the process owes.
# A class the grammar does not have never reaches here: it is counted under
# `(outside grammar)` by the caller.
BUCKET = {
    'mutation-vacuous': 'engineering',
    'harness': 'engineering',
    'null-control': 'engineering',
    'preflight-mismatch': 'engineering',
    'claims': 'record-and-body',
    'version': 'record-and-body',
    'carry-missing': 'record-and-body',
    'head-moved': 'orchestration',
    'conflict': 'orchestration',
    'root-cause-unanswered': 'orchestration',
    'other': 'orchestration',
    # The words the reviewers wrote that VERDICT_CLASSES does not have. They are
    # bucketed on the same axis and are NOT folded into `other`: a router that
    # cannot read the word cannot act on it, and the class the grammar has
    # (`other`) is a decision, while these are the grammar failing to keep up.
    'body-only': 'record-and-body',
    'claim-contradiction': 'record-and-body',
    'carry-unfaithful': 'record-and-body',
    'regression': 'engineering',
    'unseen-write-failure': 'engineering',
    'missing-id-unload': 'engineering',
    'remedy': 'engineering',
    'stale-ownership': 'orchestration',
    'body-figure': 'record-and-body',
}
# A verdict line with no class word at all: the reviewer wrote the two words and
# put the reason on the SECOND line, which `parseVerdict` never reads (`raw =
# comment.split('\n')[0]`). It routes nowhere and it is not a class.
NO_WORD = '(no class word)'
BUCKET[NO_WORD] = 'orchestration'

BOT_LOGINS = ('github-actions[bot]', 'dependabot[bot]', 'claude[bot]',
              'codex[bot]', 'cursor[bot]')


def first_line(text):
    return (text or '').split('\n')[0].strip()


def loads_or_empty(raw):
    try:
        return json.loads(raw)
    except Exception:  # noqa: BLE001
        return []


def grammar_file(perturb):
    """The production grammar file, or a perturbed COPY of it under the temp root."""
    src = os.path.join(L.ROOT, '.claude', 'workflows', 'web-fix-wave.js')
    if perturb in ('none', 'reshape'):
        return src
    text = open(src).read()
    if perturb == 'grammar':
        # THE ONE-LINE PRODUCTION EDIT, applied to a copy: `\s+` -> `\s\s+`
        # after the verdict word. Every verdict the wave currently posts spells
        # one space, so this must take parsed_verdicts to 0.
        before = text
        text = text.replace('`^Fix review:\\\\s+', '`^Fix review:\\\\s\\\\s+', 1)
        if text == before:
            raise SystemExit('grammar perturbation did not apply: the anchor '
                             '`^Fix review:\\s+ was not found in web-fix-wave.js')
    elif perturb == 'classes':
        # THE OTHER ONE-LINE PRODUCTION EDIT: the nine words the window's
        # reviewers wrote and the grammar does not have, appended to
        # VERDICT_CLASSES. This is what a fix to the coverage hole looks like,
        # and it must move outside_grammar DOWN by exactly those nine.
        words = sorted({w for w in BUCKET if w not in
                        {'mutation-vacuous', 'harness', 'null-control',
                         'preflight-mismatch', 'claims', 'version',
                         'carry-missing', 'head-moved', 'conflict',
                         'root-cause-unanswered', 'other', NO_WORD}})
        anchor = "'conflict', 'other',\n]"
        if anchor not in text:
            raise SystemExit('classes perturbation did not apply: the '
                             'VERDICT_CLASSES tail anchor was not found')
        add = "".join(f"  '{w}',\n" for w in words)
        text = text.replace(anchor, "'conflict',\n" + add + "'other',\n]", 1)
        print(f'perturbation: VERDICT_CLASSES in the copy gains {words}')
    else:
        raise SystemExit(f'unknown perturbation {perturb!r}')
    tmp = tempfile.mkdtemp(prefix='d13-grammar-')
    out = os.path.join(tmp, 'web-fix-wave.js')
    open(out, 'w').write(text)
    print(f'perturbation: web-fix-wave.js copied to {out}')
    return out


def parse_all(lines, perturb):
    """Drive the production grammar over first-line strings. Returns (parsed, source)."""
    f = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False)
    json.dump(lines, f)
    f.close()
    env = dict(os.environ, D13_ROOT=str(L.ROOT))
    gfile = grammar_file(perturb)
    env['D13_GRAMMAR_FILE'] = gfile
    p = subprocess.run(['node', os.path.join(HERE, 'h1_grammar.mjs'), f.name],
                       capture_output=True, text=True, env=env, cwd=str(L.ROOT))
    if p.returncode != 0:
        raise SystemExit(f'the grammar driver failed: {p.stderr[:400]}')
    d = json.loads(p.stdout)
    return d['parsed'], d['source'], d['classes']


def main():
    perturb = 'none'
    if '--perturb' in sys.argv:
        perturb = sys.argv[sys.argv.index('--perturb') + 1]

    commits = L.window_commits()
    merges, blind = L.enumerate_merges(commits)
    print(f'window {L.W0} .. {L.W1}  first-parent commits={len(commits)}  '
          f'merges enumerated={len(merges)}  unattributed={len(blind)}')
    for sha, subject in blind:
        print(f'  UNATTRIBUTED {sha[:7]} {subject[:70]}')

    # One fetch per pull request: metadata, the ISSUE COMMENT endpoint and the
    # REVIEWS endpoint, because `policy_lint.mjs:fetchWindow` reads the first
    # alone and a verdict posted as a review is invisible to it.
    meta, comments, reviews = {}, {}, {}
    from concurrent.futures import ThreadPoolExecutor
    nums = [m['number'] for m in merges]

    def grab(n):
        return n, L.pr(n), L.pr_comments(n), L.pr_reviews(n)

    with ThreadPoolExecutor(max_workers=6) as ex:
        for n, p, c, r in ex.map(grab, nums):
            meta[n], comments[n], reviews[n] = p, c, r

    # The texts the grammar is driven over, in the order the merge's verdicts
    # are ordered: one entry per candidate item, carrying its endpoint.
    items = []          # (pr, origin, time, first_line, body)
    for n in nums:
        for c in (comments[n] or []):
            items.append((n, 'issue-comment', L.utc(c.get('created_at', '')),
                          first_line(c.get('body')), c.get('body') or '',
                          (c.get('user') or {}).get('login', '')))
        for r in (reviews[n] or []):
            t = L.utc(r.get('submitted_at') or '')
            if not t:
                continue
            items.append((n, 'review', t, first_line(r.get('body')),
                          r.get('body') or '', (r.get('user') or {}).get('login', '')))

    if perturb == 'reshape':
        # The fixture perturbation: the FIRST parsable verdict in time order is
        # re-shaped out of the grammar. One item, one character class, never on
        # a live pull request -- the text is rewritten in this process only.
        idx = None
        for i, (_n, _o, _t, fl, _b, _u) in enumerate(items):
            if fl.startswith('Fix review:') and ' — ' not in fl:
                idx = i
                break
        if idx is None:
            raise SystemExit('no parsable verdict to re-shape')
        n, o, t, fl, b, u = items[idx]
        # Still inside the brief's prefix rule (`Fix review:`), outside the
        # wave's VERDICT_RE: the shape a reviewer drifts into, and the reason
        # the two counts differ by a number rather than by a story.
        reshaped = fl.replace('Fix review: merge', 'Fix review: merge pending', 1)
        body = b.replace(fl, reshaped, 1)
        items[idx] = (n, o, t, reshaped, body, u)
        print(f'perturbation: re-shaped one verdict (#{n} {o}) to {reshaped[:60]!r}')

    parsed, source, classes = parse_all([i[3] for i in items], perturb)
    print(f'grammar: {source}')
    print(f'grammar classes: {classes}')

    by_pr = defaultdict(list)
    outside = []
    parsed_total = 0
    for (n, origin, t, fl, body, user), got in zip(items, parsed):
        if fl.startswith('Fix review:'):
            if got is None:
                outside.append((n, origin, t, fl, user))
                continue
            parsed_total += 1
            by_pr[n].append((t, got, origin))

    # THE BRIEF'S PREFIX RULE (D13.md item 1): a verdict is any item whose first
    # line matches `^Fix review:\s*(merge|blocked)`, whatever follows. This is
    # the process-level count; VERDICT_RE is the parser-level one. Both are
    # printed because they differ over exactly the items the grammar refuses.
    LAX = re.compile(r'^Fix review:\s*(merge|blocked)\b')
    lax_by_pr = defaultdict(list)
    for (n, origin, t, fl, body, user) in items:
        m = LAX.match(fl)
        if m:
            lax_by_pr[n].append((t, m.group(1), origin, user, fl))

    first_is_merge = 0
    rounds = []
    for m in merges:
        n = m['number']
        vs = sorted(by_pr.get(n, []), key=lambda x: x[0])
        rounds.append(len(vs))
        if vs and vs[0][1]['verdict'] == 'merge':
            first_is_merge += 1

    lax_first_merge, lax_rounds = 0, []
    for m in merges:
        vs = sorted(lax_by_pr.get(m['number'], []), key=lambda x: x[0])
        lax_rounds.append(len(vs))
        if vs and vs[0][1] == 'merge':
            lax_first_merge += 1

    n_merges = len(merges)
    noverdict = [m['number'] for m in merges if not by_pr.get(m['number'])]
    print(f'parsed verdicts={parsed_total}  merges with >=1 verdict='
          f'{n_merges - len(noverdict)}  merges with none={len(noverdict)}')
    print(f'outside-grammar items (first line starts "Fix review:")='
          f'{len(outside)}')
    # THE SHAPES OF WHAT THE GRAMMAR CANNOT READ, and each is its own row
    # rather than a single "unparsed" bucket: a class the grammar does not have
    # is an actionable verdict a script cannot route, a bare `blocked` names
    # nothing at all, and an abbreviated head SHA is refused by the gate even
    # when this grammar takes it (#1106). Counted separately because the three
    # need three different repairs.
    UNKNOWN = re.compile(r'^Fix review:\s+blocked\s+([0-9a-f]{40})\s+([A-Za-z][A-Za-z-]*):')
    ABBREV = re.compile(r'^Fix review:\s+merge\s+([0-9a-f]{1,39})$')
    shapes = Counter()
    for n, origin, t, fl, user in sorted(outside):
        m = UNKNOWN.match(fl)
        if m:
            shapes['unknown-class'] += 1
            shapes[f'unknown-class:{m.group(2)}'] += 1
        elif ABBREV.match(fl):
            shapes['abbreviated-merge-sha'] += 1
        elif re.match(r'^Fix review:\s+blocked\s*$', fl):
            shapes['bare-blocked'] += 1
        else:
            shapes['other-shape'] += 1
        print(f'  OUTSIDE-GRAMMAR #{n} {origin} {user}: {fl[:100]!r}')
    for k, v in sorted(shapes.items()):
        if not k.startswith('unknown-class:'):
            L.result(f'outside_shape_{k}', v)

    L.result('n_merges', n_merges)
    L.result('unattributed_merge_commits', len(blind))
    L.result('parsed_verdicts', parsed_total)
    L.result('outside_grammar', len(outside))
    L.result('merges_with_verdict', n_merges - len(noverdict))
    L.result('merges_without_verdict', len(noverdict))
    L.result('first_pass_yield',
             round(first_is_merge / n_merges, 3) if n_merges else 0.0)
    L.result('rounds_mean', round(sum(rounds) / len(rounds), 2) if rounds else 0.0)
    L.result('rounds_max', max(rounds) if rounds else 0)
    L.result('rounds_median', sorted(rounds)[len(rounds) // 2] if rounds else 0)
    # the same two figures under the brief's prefix rule
    L.result('lax_verdicts', sum(lax_rounds))
    L.result('lax_first_pass_yield',
             round(lax_first_merge / n_merges, 3) if n_merges else 0.0)
    L.result('lax_rounds_mean',
             round(sum(lax_rounds) / len(lax_rounds), 2) if lax_rounds else 0.0)
    L.result('lax_rounds_max', max(lax_rounds) if lax_rounds else 0)
    L.result('lax_rounds_median',
             sorted(lax_rounds)[len(lax_rounds) // 2] if lax_rounds else 0)
    L.result('rounds_total', sum(rounds))
    # ENDPOINT, for every verdict rather than for the blocked ones alone: the
    # wave reads issue comments and `policy_lint --stats` reads the same
    # endpoint, so a verdict posted as a review is invisible to both.
    origins = Counter(o for vs in lax_by_pr.values() for (_t, _w, o, _u, _f) in vs)
    for o, c in sorted(origins.items()):
        L.result(f'verdict_endpoint_{o}', c)
    authors = Counter(u for vs in lax_by_pr.values() for (_t, _w, _o, u, _f) in vs)
    for a, c in sorted(authors.items()):
        L.result(f'verdict_author_{a or "?"}', c)

    # ---- item 3: every blocked verdict by the class word the reviewer wrote
    #
    # KEYED ON THE WRITTEN WORD, across every blocked-shaped item and not only
    # the ones the grammar took. A blocked verdict whose word is outside
    # VERDICT_CLASSES (or missing) is still the class word the process used, and
    # a table that dropped it would report a vocabulary narrower than the one in
    # use -- which is how the coverage hole stays invisible.
    WORD = re.compile(
        r'^Fix review:\s+blocked\s+([0-9a-f]{40})\s+([A-Za-z][A-Za-z-]*):')
    cls, write_class = Counter(), Counter()
    origin_c = Counter()
    blocked_rows = []
    for (n, origin, t, fl, body, user), got in zip(items, parsed):
        if not re.match(r'^Fix review:\s+blocked\b', fl):
            continue
        m = WORD.match(fl)
        word = m.group(2) if m else NO_WORD
        write_class[word] += 1
        origin_c[origin] += 1
        cls[got['class'] if got else '(outside grammar)'] += 1
        blocked_rows.append((n, word, got['class'] if got else None, origin,
                             user, fl, got['why'] if got else ''))
    print(f'\nevery blocked-shaped verdict in the window: {len(blocked_rows)}')
    for n, word, gclass, origin, user, fl, why in sorted(blocked_rows):
        print(f'  #{n:<5} wrote={word:<24} parsed={str(gclass):<22} '
              f'{origin:<14} {(user or "")[:20]:<20} {fl[:96]!r}')
    for w in sorted(write_class):
        L.result(f'blocked_word_{w}', write_class[w])
    for k, c in sorted(cls.items()):
        L.result(f'blocked_grammarclass_{k}', c)
    L.result('blocked_shaped_total', len(blocked_rows))
    L.result('blocked_routable', sum(1 for r in blocked_rows if r[2]))
    L.result('blocked_unroutable', sum(1 for r in blocked_rows if not r[2]))
    L.result('blocked_words_outside_grammar',
             sum(c for w, c in write_class.items()
                 if w != NO_WORD and w not in classes))
    L.result('blocked_no_class_word', write_class.get(NO_WORD, 0))
    for o, c in sorted(origin_c.items()):
        L.result(f'blocked_endpoint_{o}', c)
    buck = Counter()
    for (_n, word, _g, _o, _u, _f, _w) in blocked_rows:
        buck[BUCKET.get(word, 'orchestration')] += 1
    for b in ('engineering', 'record-and-body', 'orchestration'):
        L.result(f'blocked_bucket_{b}', buck.get(b, 0))
    print(f'blocked-shaped verdicts by bucket (written word): {dict(buck)}')
    buck_p = Counter()
    for (_n, _w, g, _o, _u, _f, _y) in blocked_rows:
        if g:
            buck_p[BUCKET.get(g, 'orchestration')] += 1
    print(f'  of those, bucketed by the PARSED class alone: {dict(buck_p)}')
    for b in ('engineering', 'record-and-body', 'orchestration'):
        L.result(f'blocked_parsed_bucket_{b}', buck_p.get(b, 0))
    for k, c in cls.items():
        L.result(f'blocked_class_{k}', c)
    L.result('blocked_total', sum(cls.values()))

    # ---- item 2: coverage by class, by title prefix and author
    rows = Counter()
    by_author = Counter()
    detail = []
    for m in merges:
        n = m['number']
        p = meta.get(n) or {}
        if n not in noverdict:
            continue
        title = (p.get('title') or m['subject'] or '')
        author = ((p.get('user') or {}).get('login') or '?')
        head = ((p.get('head') or {}).get('ref') or '')
        if author in BOT_LOGINS or author.endswith('[bot]'):
            klass = 'bot-cycle'
        elif title.lower().startswith('fix') or head.startswith('fix/'):
            klass = 'fix'
        elif title.lower().startswith('feat') or head.startswith('feat/'):
            klass = 'feature'
        elif title.lower().startswith('record') or head.startswith('record'):
            klass = 'record'
        elif title.lower().startswith('chore') or head.startswith('chore'):
            klass = 'chore'
        else:
            klass = 'other-lane'
        rows[klass] += 1
        by_author[author] += 1
        detail.append((n, klass, author, head, title[:58]))
    print('\nmerges with no parsable verdict, by class:')
    for k, c in sorted(rows.items(), key=lambda x: -x[1]):
        print(f'  {k:<11} {c:>3}')
    for k in ('fix', 'feature', 'record', 'chore', 'bot-cycle', 'other-lane'):
        L.result(f'noverdict_{k}', rows.get(k, 0))
    print('  by author:', dict(by_author))
    for n, k, a, h, t in detail:
        print(f'  #{n:<5} {k:<11} {a:<22} {h[:34]:<34} {t}')

    L.footer()


if __name__ == '__main__':
    main()
