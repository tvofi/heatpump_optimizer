#!/usr/bin/env python3
"""Prove the finder scopes are disjoint and complete within each dimension, and cover the tree.

Usage: python3 tools/audit/check_scopes.py --repo <checkout> [--ref <baseline sha>] [--scopes scopes.json]
Exit 0 only if every dimension passes and coverage passes; each failure prints the cells owned
twice or not at all. Coverage: every tracked path at --ref is in some dimension's universe or
matches one entry of scopes.json's `_coverage_excluded` (glob -> reason), never both, and every
entry matches some path; a path in neither is refused by name, so no path goes unmeasured.
Null control: --self-test duplicates one seat's block and empties another's, drops D10's
universe, strips the tests/ and blueprints/ globs, and excludes a covered path; it exits 0 only
when the checker refuses each perturbed file by the path it names. It also runs the default
invocation as a subprocess, on the live scopes (rc 0) and without D4's and D6's blueprints globs (rc 1).
Harness citations: a harness under dev/audit/harnesses/ whose header names a dimension brief
(`D<k>.md`) implements that brief's rule, so the brief must cite the harness's path; each one
that does not is refused by name.
--seat <D<k>-s<n>> prints the cells one seat owns instead, one line per (block, file):
steps, axis values, file. `rest` is resolved here, so a finder is handed files, not a rule.
.claude/workflows/audit-find.js runs the check, coverage included, in its Prepare step and refuses the
round on rc != 0.
--round <N> adds the start evaluation (dev/governance/decisions/0017-objective-function.md): round
N starts only when round N-1's OBJECTIVE.json and round N's EVALUATION.json are in the tree at
--ref, every term is read or NO-READ with its reason, every object file has a verdict with
evidence from an evaluator who is not its reviewer, and every card carries the owner's decision,
an accepted one merged at --ref. Each gap is refused by the path or id it names; audit-find.js
passes its round. --self-test drives a complete record (passes) and one perturbation per rule.
The record also needs: an approving review at a commit in --ref's history whose EVALUATION.json
graded the same objects, a ruling on every decided card, an accepted card's commit after that review
and changing the card's file, reads that are numbers with a tracked enumerator, NO-READs that name
what would read them and who builds it, no removal on a NO-READ, and a card for every unset
threshold, owner criterion and unowned item.
--population prints the install population objective.json lists, read from the sources at --ref:
one line per axis (levels), then LEVELS, PAIRS (level pairs from two axes) and NO-READ AXES; exit 1
and `UNREADABLE <axis>: <why>` when a source is missing or an axis yields no level.
"""
import argparse, ast, contextlib, copy, io, itertools, json, re, subprocess, sys, tempfile
from pathlib import Path

def expand_braces(p):
    m = re.search(r"\{([^{}]*)\}", p)
    if not m:
        return [p]
    return [q for alt in m.group(1).split(",") for q in expand_braces(p[:m.start()] + alt + p[m.end():])]

def glob_re(p):
    out, i = "", 0
    while i < len(p):
        if p.startswith("**", i):
            out += ".*"; i += 2
        elif p[i] == "*":
            out += "[^/]*"; i += 1
        else:
            out += re.escape(p[i]); i += 1
    return re.compile(out + r"\Z")

def match(files, globs):
    rx = [glob_re(q) for g in globs for q in expand_braces(g)]
    return {f for f in files if any(r.match(f) for r in rx)}

def resolver(d, tree):
    """The dimension's universe, and a block's files with `rest` resolved against it."""
    uni = match(tree, d["universe"]) if d["universe"] else {"<none>"}
    def rest_for(steps):
        # files no explicit block sharing one of these steps names
        named = set()
        for blocks in d["seats"].values():
            for b in blocks:
                if b["files"] != "rest" and (d["mode"] == "files" or set(b["steps"]) & set(steps)):
                    named |= match(uni, b["files"]) if d["universe"] else uni
        return uni - named
    def files_of(b):
        return rest_for(b["steps"]) if b["files"] == "rest" else (match(uni, b["files"]) if d["universe"] else uni)
    return uni, files_of

def check(scopes, tree, loc):
    ok = True
    for dim, d in scopes.items():
        if dim.startswith("_"):
            continue
        uni, files_of = resolver(d, tree)
        axis_vals = next(iter(d.get("axis", {}).values()), [None])
        owners, seat_files = {}, {}
        for seat, blocks in d["seats"].items():
            fs = set()
            for b in blocks:
                bf = files_of(b)
                fs |= bf
                ax = b.get("axis", axis_vals)
                for f in bf:
                    for s in b["steps"]:
                        for a in ax:
                            key = (f, s, a) if d["mode"] == "cells" else (f,)
                            owners.setdefault(key, set()).add(seat)
                if d["mode"] == "files":
                    for s in b["steps"]:
                        owners.setdefault(("step", s), set()).add(seat)
            seat_files[seat] = fs
        if d["mode"] == "cells":
            want = set(itertools.product(uni, d["steps"], axis_vals))
            dup = {k: v for k, v in owners.items() if len(v) > 1}
        else:
            want = {(f,) for f in uni} | {("step", s) for s in d["steps"]}
            dup = {k: v for k, v in owners.items() if len(v) > 1 and k[0] != "step"}
        missing = want - set(owners)
        extra = set(owners) - want
        status = "ok" if not (dup or missing or extra) else "FAIL"
        ok &= status == "ok"
        sizes = ", ".join(f"{s}:{len(fs)}f/{sum(loc.get(f,0) for f in fs)}loc" for s, fs in seat_files.items())
        print(f"{status} {dim} mode={d['mode']} seats={len(d['seats'])} universe={len(uni)} [{sizes}]")
        for k in sorted(missing, key=str)[:10]:
            print(f"   unowned {k}")
        for k, v in sorted(dup.items(), key=str)[:10]:
            print(f"   owned twice {k} by {sorted(v)}")
        for k in sorted(extra, key=str)[:10]:
            print(f"   outside universe/steps {k}")
    return ok

def coverage(scopes, tree, quiet=False):
    """Paths in no universe and on no exclusion, exclusions that also name a
    covered path, and exclusions that name nothing. Returns (ok, unclassified)."""
    covered = set()
    for dim, d in scopes.items():
        if not dim.startswith("_") and d["universe"]:
            covered |= match(tree, d["universe"])
    excl = scopes.get("_coverage_excluded", {})
    excluded = {g: match(tree, [g]) for g in excl if not g.startswith("_")}
    unclassified = sorted(tree - covered - set().union(*excluded.values()))
    both = sorted(f for fs in excluded.values() for f in fs & covered)
    dead = sorted(g for g, fs in excluded.items() if not fs)
    unreasoned = sorted(g for g in excluded if not str(excl[g]).strip())
    ok = not (unclassified or both or dead or unreasoned)
    if not quiet:
        print(f"{'ok' if ok else 'FAIL'} coverage tracked={len(tree)} in_universe={len(covered)} "
              f"excluded={len(tree & set().union(*excluded.values()))} unclassified={len(unclassified)}")
        for f in unclassified:
            print(f"   in no universe and not excluded: {f}")
        for f in both[:10]:
            print(f"   excluded but in a universe: {f}")
        for g in dead:
            print(f"   exclusion matches no tracked path: {g}")
        for g in unreasoned:
            print(f"   exclusion carries no reason: {g}")
    return ok, unclassified


BRIEF_DIR = "dev/governance/dimensions/"
HARNESS_DIR = "dev/audit/harnesses/"
BRIEF_NAMED = re.compile(r"(?<![\w/])(D\d{1,2})\.md\b")


def uncited_harnesses(harnesses, briefs):
    """[(harness, brief)] where a harness's header (first 40 lines) names a
    dimension brief, so it implements that brief's rule, and the brief does not
    cite the harness's path: a finder reading the brief never learns it exists."""
    out = []
    for h, text in sorted(harnesses.items()):
        for dim in sorted(set(BRIEF_NAMED.findall("\n".join(text.splitlines()[:40])))):
            if dim in briefs and h not in briefs[dim]:
                out.append((h, BRIEF_DIR + dim + ".md"))
    return out


def read_harnesses(repo, ref, tree):
    show = lambda f: subprocess.run(["git", "-C", repo, "show", f"{ref}:{f}"], capture_output=True, text=True).stdout
    harnesses = {f: show(f) for f in tree if f.startswith(HARNESS_DIR) and f.endswith((".py", ".mjs", ".js", ".sh"))}
    briefs = {Path(f).stem: show(f) for f in tree if f.startswith(BRIEF_DIR) and f.endswith(".md")}
    return harnesses, briefs


def verdict(scopes, tree, loc, harnesses, briefs, quiet=False):
    """The default run's answer: every dimension disjoint and complete, the
    tree covered, and every brief-named harness cited by its brief."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out if quiet else sys.stdout):
        ok = check(scopes, tree, loc)
        cov_ok, _ = coverage(scopes, tree)
        bad = uncited_harnesses(harnesses, briefs)
        print(f"{'ok' if not bad else 'FAIL'} harness citations: {len(bad)} harness(es) implementing a brief's rule the brief does not cite")
        for h, b in bad:
            print(f"   {h} names {b} in its header; {b} does not cite it")
    return ok and cov_ok and not bad

OBJECTIVE = "dev/audit/config/objective.json"
VERDICTS = ("keep", "change", "remove")
DECISIONS = ("accepted", "rejected", "deferred")


def object_globs(spec):
    return [g for v in spec["objects"].values() for g in ([v] if isinstance(v, str) else v)]


def isnum(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def full(v):
    return isinstance(v, str) and bool(v.strip())


def norm(s):
    return re.sub(r"[\W_]+", "", str(s).casefold())


def enumerates(cmd, tree):
    """The first path-like token of an enumerator command is a tracked file."""
    for tok in cmd.split() if isinstance(cmd, str) else ():
        if tok not in ("python3", "python", "node", "bash", "sh") and not tok.startswith("-") and "=" not in tok:
            return tok in tree
    return False


def evaluation_gaps(rnd, tree, show, merged, anc, changed):
    """Why round `rnd` may not start, one line per gap, [] when it may.
    `show(path, at=None)` is the file's text at the ref (or at commit `at`);
    `merged(sha)` says whether the ref contains that commit, `anc(a, b)` whether
    a is an ancestor of or equal to b, `changed(sha)` the paths it changed
    against its first parent. The terms and the object globs come from
    OBJECTIVE at the ref, so the record is checked against the definition it
    was written under, and neither list is carried here."""
    spec = json.loads(show(OBJECTIVE))
    prev = f"dev/audit/rounds/round{rnd - 1}/OBJECTIVE.json"
    path = f"dev/audit/rounds/round{rnd}/EVALUATION.json"
    gaps, terms, builders = [], {}, []
    if prev not in tree:
        gaps.append(f"{prev} is not in the tree: round {rnd - 1}'s close wrote no record to evaluate")
    else:
        terms = json.loads(show(prev)).get("terms", {})
        for t in spec["terms"]:
            row = terms.get(t)
            v = row.get("value") if isinstance(row, dict) else None
            if not isinstance(row, dict):
                gaps.append(f"{prev} has no term {t}")
            elif "value" in row and not str(row.get("enumerator", "")).strip():
                gaps.append(f"{prev} term {t} carries a value and no enumerator")
            elif "value" in row and not (isnum(v) or (isinstance(v, dict) and v and all(isnum(x) for x in v.values()))):
                gaps.append(f"{prev} term {t} value is not a number or a non-empty dict of numbers")
            elif "value" in row and not enumerates(row["enumerator"], tree):
                gaps.append(f"{prev} term {t} enumerator names no file tracked at the ref")
            elif "value" not in row and not str(row.get("no_read", "")).strip():
                gaps.append(f"{prev} term {t} is neither read nor NO-READ with its reason")
            elif "value" not in row:
                gaps += [f"{prev} term {t} NO-READ carries no {k}" for k in ("would_read", "builder") if not full(row.get(k))]
                if full(row.get("builder")) and row["builder"].startswith("card:"):
                    builders.append((t, row["builder"][5:]))
    if path not in tree:
        return gaps + [f"{path} is not in the tree: the start evaluation has not run"]
    ev = json.loads(show(path))
    if ev.get("round") != rnd or ev.get("reads") != prev:
        gaps.append(f"{path} is not round {rnd}'s evaluation of {prev}")
    seat, rev = (norm(ev.get(k, "")) for k in ("evaluator", "reviewer"))
    if not seat or not rev or seat == rev or "orchestrator" in seat or "orchestrator" in rev:
        gaps.append(f"{path} evaluator {seat!r} and reviewer {rev!r} must be two seats, neither the orchestrator")
    cards, rows = ev.get("cards", {}), ev.get("objects", {})
    rv, revsha = ev.get("review"), None
    if not isinstance(rv, dict) or rv.get("verdict") != "approve":
        gaps.append(f"{path} review is not an approve verdict")
    elif not (full(rv.get("sha")) and merged(rv["sha"])):
        gaps.append(f"{path} review sha {rv.get('sha')!r} is not a commit in the ref's history")
    else:
        revsha = rv["sha"]
        try:
            graded = json.loads(show(path, revsha)).get("objects")
        except Exception:
            graded = None
        if graded != rows:
            gaps.append(f"{path} at review sha {revsha} is missing or graded other objects than this record")
    for t, b in builders:
        if b not in cards:
            gaps.append(f"{prev} term {t} builder card:{b} is no card of {path}")
    objects = match(tree, object_globs(spec))
    gaps += [f"{path} grades {f}, which is no object of {OBJECTIVE}" for f in sorted(rows) if f not in objects]
    for f in sorted(objects):
        row = rows.get(f)
        if not isinstance(row, dict) or row.get("verdict") not in VERDICTS:
            gaps.append(f"{path} has no keep/change/remove verdict for {f}")
        elif not str(row.get("evidence", "")).strip():
            gaps.append(f"{path} verdict for {f} carries no evidence")
        elif row["verdict"] == "remove" and str(row["evidence"]).strip().startswith("NO-READ"):
            gaps.append(f"{path} remove verdict for {f} rests on a NO-READ")
        elif row["verdict"] != "keep" and row.get("card") not in cards:
            gaps.append(f"{path} {row['verdict']} verdict for {f} names no card")
    for cid, card in sorted(cards.items()):
        if card.get("decision") not in DECISIONS:
            gaps.append(f"{path} card {cid} carries no owner decision")
            continue
        if not full(card.get("ruling")):
            gaps.append(f"{path} card {cid} carries no ruling naming where the owner ruled")
        if card["decision"] != "accepted":
            continue
        c = card.get("merged")
        want = {x for x in (card.get("object"), *(card.get("paths") or ())) if x}
        if not (c and merged(c)):
            gaps.append(f"{path} card {cid} is accepted and not merged at this ref")
        elif revsha and anc(c, revsha):
            gaps.append(f"{path} card {cid} merged {c} is not after the review at {revsha}")
        elif not want:
            gaps.append(f"{path} card {cid} is accepted and names no object or paths")
        elif not want & changed(c):
            gaps.append(f"{path} card {cid} merged {c} changes none of its object or paths")
    carded = lambda k: {c.get(k) for c in cards.values()}
    for k, th in spec.get("thresholds", {}).items():
        if th.get("value") is None and k not in carded("threshold"):
            gaps.append(f"{path} threshold {k} is unset and no card carries it")
    for d, p in spec.get("owner_criteria", {}).items():
        if p is None and d not in carded("criterion"):
            gaps.append(f"{path} owner criterion {d} is unset and no card carries it")
        elif p is not None and p not in tree:
            gaps.append(f"{OBJECTIVE} owner criterion {d} names {p}, not tracked at the ref")
    for ax in spec.get("population", []):
        gaps += [f"{OBJECTIVE} population axis {ax.get('axis')} is NO-READ and carries no {k}"
                 for k in ("no_read", "builder") if ax.get("kind") is None and not full(ax.get(k))]
    u = terms.get("unowned")
    n = sum(1 for c in cards.values() if str(c.get("unowned", "")).strip())
    if isinstance(u, dict) and isnum(u.get("value")) and n < u["value"]:
        gaps.append(f"{path} carries {n} card(s) with an unowned item but {prev} counts {u['value']}")
    return gaps


def population(axes, tree, show):
    """(lines, ok): the install population's levels per axis as read from the
    sources at the ref, then the totals. An axis that cannot be read prints
    UNREADABLE in its place, never an empty axis, and fails the run."""
    def module_assign(mod, name):
        for n in mod.body:
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
                return n.value
            if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id == name and n.value:
                return n.value

    def tuple_levels(f, symbol):
        mod = ast.parse(show(f))
        const = f.rpartition("/")[0] + "/const.py" if "/" in f else "const.py"
        def lookup(name):
            node = module_assign(mod, name)
            if node is None and const in tree:
                node = module_assign(ast.parse(show(const)), name)
            if node is None:
                raise ValueError(f"{name} is bound in neither {f} nor {const}")
            return node
        def strs(node):
            if isinstance(node, ast.Dict):
                elts = node.keys
            elif isinstance(node, (ast.Tuple, ast.List, ast.Set)):
                elts = node.elts
            else:
                raise ValueError(f"{symbol} is not a literal collection")
            out = []
            for e in elts:
                if isinstance(e, ast.Starred):
                    out += strs(lookup(e.value.id) if isinstance(e.value, ast.Name) else e.value)
                    continue
                if isinstance(e, ast.Name):
                    e = lookup(e.id)
                if not (isinstance(e, ast.Constant) and isinstance(e.value, str)):
                    raise ValueError(f"element {ast.unparse(e) if e else '**'} is not a string")
                out.append(e.value)
            return out
        node = module_assign(mod, symbol)
        if node is None:
            raise ValueError(f"symbol {symbol} is not assigned at module level in {f}")
        return strs(node)

    def compare_levels(f, function, argument):
        fn = next((n for n in ast.parse(show(f)).body if isinstance(n, ast.FunctionDef) and n.name == function), None)
        if fn is None:
            raise ValueError(f"function {function} is not defined at module level in {f}")
        isarg = lambda n: isinstance(n, ast.Name) and n.id == argument
        out = []
        for c in (n for n in ast.walk(fn) if isinstance(n, ast.Compare)):
            for op, l, r in zip(c.ops, [c.left, *c.comparators], c.comparators):
                if isinstance(op, ast.Eq):
                    out += [x.value for x in ((r,) if isarg(l) else (l,) if isarg(r) else ()) if isinstance(x, ast.Constant)]
                elif isinstance(op, ast.In) and isarg(l) and isinstance(r, (ast.Tuple, ast.List, ast.Set)):
                    out += [x.value for x in r.elts if isinstance(x, ast.Constant)]
        return out

    def levels(ax):
        k, f = ax.get("kind"), ax.get("file")
        if k == "glob":
            return [Path(g).stem for g in match(tree, [ax["glob"]])]
        if f not in tree:
            raise ValueError(f"{f} is not tracked at the ref")
        if k == "tuple":
            return tuple_levels(f, ax["symbol"])
        if k == "regex":
            return [m if isinstance(m, str) else m[0] for m in re.findall(ax["pattern"], show(f))]
        if k == "compare":
            return [x for x in compare_levels(f, ax["function"], ax["argument"]) if isinstance(x, str)]
        raise ValueError(f"unknown kind {k!r}")

    lines, sizes, noread, ok = [], [], 0, True
    for ax in axes:
        name = ax.get("axis")
        if ax.get("kind") is None:
            noread += 1
            lines.append(f"{name}\tNO-READ\t{ax.get('no_read')} (builder: {ax.get('builder')})")
            continue
        try:
            lv = sorted(set(levels(ax)))
            if not lv:
                raise ValueError("no level found")
        except Exception as e:
            ok = False
            lines.append(f"UNREADABLE {name}: {e}")
            continue
        if ax.get("binary"):
            sizes += [2] * len(lv)
            lines.append(f"{name}\t{len(lv)} binary axes\t{','.join(lv)}")
        else:
            sizes.append(len(lv))
            lines.append(f"{name}\t{len(lv)}\t{','.join(lv)}")
    lines += [f"LEVELS: {sum(sizes)}", f"PAIRS: {(sum(sizes) ** 2 - sum(n * n for n in sizes)) // 2}", f"NO-READ AXES: {noread}"]
    return lines, ok


def evaluation_self_test(tree, show):
    """{arm: held}. A complete record over the live object files passes; each
    perturbation of it is refused by the path, term or card it names, checked
    alone so none masks another. The spec is the live one plus the owner-value
    keys, so the arms do not depend on the shape committed at the ref."""
    ME = "tools/audit/check_scopes.py"
    live = json.loads(show(OBJECTIVE))
    spec = {**live, "thresholds": {"floor": {"value": None}, "band": {"value": 0.2}},
            "owner_criteria": {"D4": None, "D7": ME},
            "population": [{"axis": "n", "kind": None, "no_read": "r", "builder": "G1"}]}
    prev, path = "dev/audit/rounds/round7/OBJECTIVE.json", "dev/audit/rounds/round8/EVALUATION.json"
    objs = sorted(match(tree, object_globs(spec)))
    terms = {t: {"value": 1, "enumerator": "python3 " + ME} for t in spec["terms"]}
    terms[spec["terms"][-1]] = {"no_read": "no ledger", "would_read": "a ledger", "builder": "card:C2"}
    good = {"round": 8, "reads": prev, "evaluator": "evaluator-r8", "reviewer": "plan-review-r8",
            "review": {"verdict": "approve", "sha": "rev"},
            "objects": {f: {"verdict": "keep", "evidence": "e"} for f in objs},
            "cards": {"C1": {"decision": "accepted", "ruling": "R1", "merged": "abc", "object": ME},
                      "C2": {"decision": "rejected", "ruling": "R2", "unowned": "u", "threshold": "floor", "criterion": "D4"}}}
    good["objects"][objs[0]] = {"verdict": "change", "evidence": "e", "card": "C1"}
    # commits: old is an ancestor of the review rev, abc is after it
    def run(ev=good, tm=terms, drop=(), sp=spec, revdoc=None, merged=lambda sha: sha in ("abc", "rev", "old")):
        files = {OBJECTIVE: json.dumps(sp), prev: json.dumps({"terms": tm}), path: json.dumps(ev)}
        sh = lambda f, at=None: (revdoc or json.dumps({"objects": ev.get("objects")})) if at else files[f]
        return evaluation_gaps(8, (tree | set(files)) - set(drop), sh, merged,
                               lambda a, b: (a, b) in (("old", "rev"), ("rev", "rev")),
                               lambda c: {"abc": {ME}, "old": {ME}}.get(c, set()))
    def edit(fn, base=good):
        c = copy.deepcopy(base)
        fn(c)
        return c
    only = lambda gaps, needle: len(gaps) == 1 and needle in gaps[0]
    t0, t9 = spec["terms"][0], spec["terms"][-1]
    card = lambda k, **kw: edit(lambda c: c["cards"][k].update(kw))
    return {
        "a complete record passes": bool(objs) and run() == [],
        "every object class has a file": all(match(tree, [g]) and match(tree, [g]) <= set(objs) for v in spec["objects"].values() for g in ([v] if isinstance(v, str) else v)),
        "a missing evaluation is refused": only(run(drop=[path]), path + " is not in the tree"),
        "a missing previous record is refused": only(run(drop=[prev]), prev + " is not in the tree"),
        "a missing term is refused": only(run(tm={k: v for k, v in terms.items() if k != t0}), "no term " + t0),
        "a value with no enumerator is refused": only(run(tm=edit(lambda c: c[t0].pop("enumerator"), terms)), t0 + " carries a value"),
        "a NO-READ with no reason is refused": only(run(tm=edit(lambda c: c[t9].update(no_read=" "), terms)), t9 + " is neither"),
        "another round's record is refused": only(run(edit(lambda c: c.update(round=9))), "is not round 8's"),
        "one seat as evaluator and reviewer is refused": only(run(edit(lambda c: c.update(reviewer="evaluator-r8"))), "two seats"),
        "the orchestrator as evaluator is refused": only(run(edit(lambda c: c.update(evaluator="orchestrator"))), "two seats"),
        "an object with no verdict is refused": only(run(edit(lambda c: c["objects"].pop(objs[-1]))), "verdict for " + objs[-1]),
        "a verdict with no evidence is refused": only(run(edit(lambda c: c["objects"][objs[-1]].update(evidence=""))), objs[-1] + " carries no evidence"),
        "a change with no card is refused": only(run(edit(lambda c: c["objects"][objs[0]].pop("card"))), objs[0] + " names no card"),
        "an undecided card is refused": only(run(edit(lambda c: c["cards"]["C2"].pop("decision"))), "card C2 carries no owner decision"),
        "an accepted card not merged is refused": only(run(merged=lambda sha: sha != "abc"), "card C1 is accepted and not merged"),
        "B1 a disguised orchestrator or the same seat respelled is refused":
            all(only(run(edit(lambda c: c.update(**{k: v}))), "two seats") for k, v in (
                ("evaluator", "orchestrator-r10"), ("evaluator", "the orchestrator"), ("reviewer", "Orchestrator"), ("reviewer", "Evaluator R8"))),
        "B2 a review that is no approve verdict is refused":
            only(run(edit(lambda c: c.pop("review"))), "review is not an approve") and only(run(edit(lambda c: c["review"].update(verdict="revise"))), "review is not an approve"),
        "B2 a review sha outside the ref's history is refused": only(run(edit(lambda c: c["review"].update(sha="zzz"))), "is not a commit in the ref"),
        "B2 a review that graded other objects or none is refused":
            only(run(revdoc=json.dumps({"objects": {}})), "graded other objects") and only(run(revdoc="not json"), "graded other objects"),
        "B3 a decided card with no ruling is refused": only(run(edit(lambda c: c["cards"]["C2"].pop("ruling"))), "card C2 carries no ruling"),
        "B4 an accepted commit that predates the review is refused": only(run(card("C1", merged="old")), "is not after the review"),
        "B4 an accepted commit that changes none of the card's file is refused": only(run(card("C1", object="other")), "changes none of"),
        "B4 an accepted card naming no file is refused": only(run(edit(lambda c: c["cards"]["C1"].pop("object"))), "names no object or paths"),
        "B4 paths stand for object": run(edit(lambda c: c["cards"]["C1"].update(object=None, paths=[ME]))) == [],
        "B5 a null value is refused": only(run(tm=edit(lambda c: c[t0].update(value=None), terms)), t0 + " value is not a number"),
        "B5 an enumerator naming no tracked file is refused": only(run(tm=edit(lambda c: c[t0].update(enumerator="by hand"), terms)), t0 + " enumerator names no file"),
        "B5 an enumerator that is an interpreter and no file is refused": only(run(tm=edit(lambda c: c[t0].update(enumerator="python3 -I"), terms)), t0 + " enumerator names no file"),
        "B5 a dict of numbers is a value": run(tm=edit(lambda c: c[t0].update(value={"a": 1}), terms)) == [],
        "B6 a NO-READ naming nothing that would read it is refused": only(run(tm=edit(lambda c: c[t9].pop("would_read"), terms)), t9 + " NO-READ carries no would_read") and only(run(tm=edit(lambda c: c[t9].pop("builder"), terms)), t9 + " NO-READ carries no builder"),
        "B6 a builder card the evaluation lacks is refused": only(run(tm=edit(lambda c: c[t9].update(builder="card:C9"), terms)), "card:C9 is no card"),
        "B7 a removal on a NO-READ is refused": only(run(edit(lambda c: c["objects"][objs[-1]].update(verdict="remove", evidence=" NO-READ x", card="C2"))), "rests on a NO-READ"),
        "B8 an unset threshold with no card is refused": only(run(card("C2", threshold="band")), "threshold floor is unset"),
        "B8 an unset owner criterion with no card is refused": only(run(card("C2", criterion="D7")), "owner criterion D4 is unset"),
        "B8 an owner criterion naming an untracked path is refused": only(run(sp=edit(lambda s: s["owner_criteria"].update(D7="no/such"), spec)), "owner criterion D7 names"),
        "B8 a NO-READ axis with no builder is refused": only(run(sp=edit(lambda s: s["population"][0].pop("builder"), spec)), "population axis n is NO-READ and carries no builder"),
        "B9 fewer unowned cards than the read counts is refused": only(run(tm=edit(lambda c: c["unowned"].update(value=2), terms)), "1 card(s) with an unowned item but"),
        "B11 a row for a file outside the object globs is refused": only(run(edit(lambda c: c["objects"].update({"README.md": {"verdict": "keep", "evidence": "e"}}))), "grades README.md, which is no object"),
        "B10 a verdict outside keep/change/remove is refused": only(run(edit(lambda c: c["objects"][objs[-1]].update(verdict="retain", card="C1"))), "no keep/change/remove verdict for " + objs[-1]),
    }


def population_self_test():
    """{arm: held} on a synthetic tree: one axis per kind with levels counted by
    hand, a missing symbol and an empty glob refused, a NO-READ axis kept."""
    files = {"p/const.py": 'K = "k"\n', "p/m.py": 'T = (K, "w")\nD = {"d1": 1, "d2": 2}\nL = [*T, "v"]\nX = tuple(T)\n'
             'def f(profile):\n    if profile == "flat" or "ramp" == profile:\n        return 0\n    return profile in ("flat", "dip")\n',
             "p/cfg.py": "CONF_A_ENTITY CONF_B_ENTITY CONF_A_ENTITY", "t/en.json": "", "t/fi.json": ""}
    pop = lambda *axes: population(list(axes), set(files), lambda f: files[f])
    tup = lambda sym: {"axis": "a", "kind": "tuple", "file": "p/m.py", "symbol": sym}
    binary = {"axis": "e", "kind": "regex", "file": "p/cfg.py", "pattern": r"\b(CONF_[A-Z]_ENTITY)\b", "binary": True}
    glob = {"axis": "g", "kind": "glob", "glob": "t/*.json"}
    cmp = {"axis": "c", "kind": "compare", "file": "p/m.py", "function": "f", "argument": "profile"}
    nr = {"axis": "n", "kind": None, "no_read": "why", "builder": "G1"}
    every = pop(tup("T"), tup("D"), tup("L"), binary, glob, cmp, nr)
    return {
        "a tuple axis resolves a Name through const.py": pop(tup("T"))[0][0] == "a\t2\tk,w",
        "a dict axis reads its keys": pop(tup("D"))[0][0] == "a\t2\td1,d2",
        "a starred element expands": pop(tup("L"))[0][0] == "a\t3\tk,v,w",
        "a regex binary axis is one two-level axis per capture":
            pop(binary)[0] == ["e\t2 binary axes\tCONF_A_ENTITY,CONF_B_ENTITY", "LEVELS: 4", "PAIRS: 4", "NO-READ AXES: 0"],
        "a glob axis takes the file stems": pop(glob)[0][0] == "g\t2\ten,fi",
        "a compare axis takes the compared strings": pop(cmp)[0][0] == "c\t3\tdip,flat,ramp",
        "levels and pairs match the hand count": every[1] and every[0][-3:] == ["LEVELS: 16", "PAIRS: 109", "NO-READ AXES: 1"],
        "a NO-READ axis prints its reason and builder": "n\tNO-READ\twhy (builder: G1)" in every[0],
        "a missing symbol is UNREADABLE and fails": pop(tup("nope")) [1] is False and pop(tup("nope"))[0][0].startswith("UNREADABLE a: symbol nope"),
        "a call-built symbol is UNREADABLE": not pop(tup("X"))[1],
        "an empty glob is UNREADABLE": not pop({**glob, "glob": "none/*"})[1],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ref", default="HEAD")
    _repo = Path(__file__).resolve().parent
    for _cand in (_repo, *_repo.parents):
        if (_cand / "custom_components/heatpump_optimizer/manifest.json").is_file():
            _repo = _cand
            break
    sys.path.insert(0, str(_repo / "tests"))
    from layout import locate as _locate_scopes
    ap.add_argument("--scopes", default=str(_repo / _locate_scopes("dev/audit/config/scopes.json", root=_repo)))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--seat", help="print the cells this seat (D<k>-s<n>) owns and exit")
    ap.add_argument("--round", type=int, help="also refuse this round's start without its start evaluation")
    ap.add_argument("--population", action="store_true", help="print the install population's levels read at --ref and exit")
    a = ap.parse_args()
    show = lambda f, at=None: subprocess.check_output(["git", "-C", a.repo, "show", f"{at or a.ref}:{f}"], text=True)
    anc = lambda x, y: subprocess.run(["git", "-C", a.repo, "merge-base", "--is-ancestor", str(x), y],
                                      capture_output=True).returncode == 0
    merged = lambda sha: anc(sha, a.ref)
    changed = lambda c: set(subprocess.run(["git", "-C", a.repo, "diff", "--name-only", f"{c}^1", str(c)],
                                           capture_output=True, text=True).stdout.split())
    tree = set(subprocess.check_output(["git", "-C", a.repo, "ls-tree", "-r", "--name-only", a.ref], text=True).split())
    if a.population:
        lines, ok = population(json.loads(show(OBJECTIVE)).get("population", []), tree, show)
        print("\n".join(lines))
        sys.exit(0 if ok else 1)
    loc = {}
    for f in tree:
        if f.startswith("custom_components/") and f.endswith((".py", ".js")):
            try:
                loc[f] = subprocess.check_output(["git", "-C", a.repo, "show", f"{a.ref}:{f}"], text=True).count("\n")
            except Exception:
                pass
    scopes = json.load(open(a.scopes))
    if a.seat:
        dim, _, seat = a.seat.partition("-")
        d = scopes.get(dim)
        if dim.startswith("_") or not d or seat not in d["seats"]:
            print(f"no seat {a.seat} in {a.scopes}", file=sys.stderr)
            sys.exit(2)
        _, files_of = resolver(d, tree)
        axis_vals = next(iter(d.get("axis", {}).values()), [None])
        for b in d["seats"][seat]:
            ax = ",".join(v for v in b.get("axis", axis_vals) if v) or "-"
            for f in sorted(files_of(b)):
                print(f"{'+'.join(b['steps'])}\t{ax}\t{'(any file: no file axis)' if f == '<none>' else f}")
        sys.exit(0)
    seats = sum(len(d["seats"]) for k, d in scopes.items() if not k.startswith("_"))
    print(f"ref={subprocess.check_output(['git','-C',a.repo,'rev-parse',a.ref],text=True).strip()} seats={seats}")
    if a.self_test:
        # Two perturbations, each checked alone so neither masks the other: a
        # block owned twice (D1's first seat's block copied into its second) and
        # cells owned by nobody (D2's last seat emptied). Seat keys are read off
        # the file, never named, so a re-cut cannot turn either into a no-op.
        twice = copy.deepcopy(scopes)
        s1, s2 = list(twice["D1"]["seats"])[:2]
        twice["D1"]["seats"][s2].append(copy.deepcopy(twice["D1"]["seats"][s1][0]))
        none = copy.deepcopy(scopes)
        none["D2"]["seats"][list(none["D2"]["seats"])[-1]] = [{"files": ["**"], "steps": []}]
        res = [check(bad, tree, loc) for bad in (twice, none)]
        # Coverage arms, each refused by the path it must name, so a broad
        # exclusion cannot satisfy an arm by rc alone. D10 is the one universe
        # that alone holds py.typed; stripping every tests/ and blueprints/ glob
        # is the shape scopes.json had before the suite and the blueprints were
        # measured; excluding a covered path is classifying it twice.
        PKG = "custom_components/heatpump_optimizer/"
        nulls = PKG + "optimizer.py"
        no_d10 = copy.deepcopy(scopes)
        no_d10["D10"]["universe"] = []
        bare = copy.deepcopy(scopes)
        for k, d in bare.items():
            if not k.startswith("_"):
                d["universe"] = [g for g in d["universe"] if not g.startswith(("tests/", "blueprints/"))]
        bare.get("_coverage_excluded", {}).pop("tests/golden/**", None)
        twice_cls = copy.deepcopy(scopes)
        twice_cls.setdefault("_coverage_excluded", {})[nulls] = "perturbation: a covered path excluded"
        arms = {
            "drop D10's universe": (no_d10, [PKG + "py.typed"]),
            "strip tests/ and blueprints/ globs": (bare, ["tests/closure.py", "blueprints/automation/notifications.yaml"]),
        }
        cov = {}
        for name, (bad, must) in arms.items():
            ok, unc = coverage(bad, tree, quiet=True)
            cov[name] = (not ok) and all(m in unc for m in must) and nulls not in unc
            print(f"   coverage arm {name}: refused={not ok} names {must}={all(m in unc for m in must)}")
        ok_tc, _ = coverage(twice_cls, tree, quiet=True)
        cov["exclude a covered path"] = not ok_tc
        dead = copy.deepcopy(scopes)
        dead.setdefault("_coverage_excluded", {})["no/such/dir/**"] = "perturbation: names nothing"
        unreasoned = copy.deepcopy(scopes)
        unreasoned.setdefault("_coverage_excluded", {})[next(g for g in scopes.get("_coverage_excluded", {"x": 0}) if not g.startswith("_"))] = " "
        cov["an exclusion naming nothing"] = not coverage(dead, tree, quiet=True)[0]
        cov["an exclusion with no reason"] = not coverage(unreasoned, tree, quiet=True)[0]
        live_ok, live_unc = coverage(scopes, tree, quiet=True)
        cov["null control: optimizer.py covered"] = nulls in tree and nulls not in live_unc
        print(f"   coverage arms dead/unreasoned exclusion: refused={cov['an exclusion naming nothing']}/{cov['an exclusion with no reason']}")
        print(f"   coverage arm exclude a covered path: refused={not ok_tc}; null control {nulls} covered={cov['null control: optimizer.py covered']}")
        # Harness citations: a harness naming D15.md in its header, against a
        # brief that cites it (null control) and one that does not.
        planted = {HARNESS_DIR + "planted.py": '"""Planted: D15.md step 1 rule."""\n'}
        cov["a harness the brief does not cite is refused"] = uncited_harnesses(planted, {"D15": "no citation"}) == [
            (HARNESS_DIR + "planted.py", BRIEF_DIR + "D15.md")]
        cov["null control: the brief citing it passes"] = uncited_harnesses(planted, {"D15": "run dev/audit/harnesses/planted.py"}) == []
        print(f"   harness-citation arms: {cov['a harness the brief does not cite is refused']}, null {cov['null control: the brief citing it passes']}")
        # The default run's verdict, driven as a function: the live scopes pass
        # it, and dropping D10's universe or leaving a brief-named harness
        # uncited fails it. That pins verdict(), not the exit code main() returns.
        hs, bs = read_harnesses(a.repo, a.ref, tree)
        live = verdict(scopes, tree, loc, hs, bs, quiet=True)
        no_d10_refused = not verdict(no_d10, tree, loc, hs, bs, quiet=True)
        uncited_refused = not verdict(scopes, tree, loc, {**hs, **planted}, {**bs, "D15": "no citation"}, quiet=True)
        cov.update({"the default verdict passes the live scopes": live,
                    "and refuses them without D10's universe": no_d10_refused,
                    "and refuses an uncited brief-named harness": uncited_refused})
        print(f"   default verdict: live {live}, no D10 refused {no_d10_refused}, uncited refused {uncited_refused}")
        # The default invocation, run whole as a subprocess of this file with
        # --repo/--ref: the live scopes exit 0, and the scopes with D4's and D6's
        # blueprints/** globs dropped exit 1 naming a blueprint, both printing
        # verdict()'s citation line. So coverage cannot fall out of main()'s exit
        # code, and that exit is verdict()'s, whose citation arm is pinned above.
        no_bp = copy.deepcopy(scopes)
        for k in ("D4", "D6"):
            no_bp[k]["universe"] = [g for g in no_bp[k]["universe"] if not g.startswith("blueprints/")]
        def default_run(sc, *more):
            with tempfile.NamedTemporaryFile("w", suffix=".json") as fh:
                json.dump(sc, fh)
                fh.flush()
                return subprocess.run([sys.executable, str(Path(__file__).resolve()), "--repo", a.repo,
                                       "--ref", a.ref, "--scopes", fh.name, *more], capture_output=True, text=True)
        run_live, run_bp = default_run(scopes), default_run(no_bp)
        cited = " harness citations: "
        cov["the default invocation exits 0 on the live scopes"] = run_live.returncode == 0 and cited in run_live.stdout
        cov["and exits 1 without D4's and D6's blueprints globs"] = (run_bp.returncode == 1 and cited in run_bp.stdout
            and "in no universe and not excluded: blueprints/" in run_bp.stdout)
        print(f"   default invocation: live rc={run_live.returncode}, blueprints dropped rc={run_bp.returncode}")
        # The start evaluation: the rules as a function, then the default
        # invocation whole. Round 1 has no evaluation and never will, so
        # --round 1 exits 1 naming the file while the run without --round
        # (above) exits 0: the refusal is --round's and reaches the exit code.
        ev = evaluation_self_test(tree, show)
        cov.update({"evaluation: " + k: v for k, v in ev.items()})
        run_r1 = default_run(scopes, "--round", "1")
        cov["--round exits 1 with no evaluation in the tree"] = (run_r1.returncode == 1 and cited in run_r1.stdout
            and "FAIL start evaluation" in run_r1.stdout and "round1/EVALUATION.json is not in the tree" in run_r1.stdout)
        print(f"   evaluation arms: {sum(ev.values())}/{len(ev)} held; --round 1 rc={run_r1.returncode}")
        pop = population_self_test()
        cov.update({"population: " + k: v for k, v in pop.items()})
        print(f"   population arms: {sum(pop.values())}/{len(pop)} held")
        good = not any(res) and all(cov.values())
        print("SELF-TEST", "passed (every perturbed scope refused)" if good else
              f"FAILED (accepted: owned twice {res[0]}, unowned {res[1]}; coverage arms {cov})")
        sys.exit(0 if good else 1)
    ok = verdict(scopes, tree, loc, *read_harnesses(a.repo, a.ref, tree))
    if a.round is not None:
        gaps = evaluation_gaps(a.round, tree, show, merged, anc, changed)
        print(f"{'ok' if not gaps else 'FAIL'} start evaluation round={a.round}: {len(gaps)} gap(s)")
        for g in gaps:
            print(f"   {g}")
        ok = ok and not gaps
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
