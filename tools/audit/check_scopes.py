#!/usr/bin/env python3
"""Prove the finder scopes are disjoint and complete within each dimension, and cover the tree.

Usage: python3 tools/audit/check_scopes.py --repo <checkout> [--ref <baseline sha>] [--scopes scopes.json]
Exit 0 only if every dimension passes and coverage passes; each failure prints the cells owned
twice or not at all. Coverage: every tracked path at --ref is in some dimension's universe or
matches one entry of scopes.json's `_coverage_excluded` (glob -> reason), never both, and every
entry matches some path; a path in neither is refused by name, so no path goes unmeasured.
An axis tools/audit/enumerate.py also prints (D17's `kind`, its d17-features prefixes) must name
exactly those prefixes: a value in one copy alone is refused.
Null control: --self-test duplicates one seat's block and empties another's (D1 and D2, then D16
and D17, with a kind planted in either copy of D17's axis), drops D10's
universe, strips the tests/ and blueprints/ globs, and excludes a covered path; it exits 0 only
when the checker refuses each perturbed file by the path it names. It also runs the default
invocation as a subprocess, on the live scopes (rc 0) and with every universe's blueprints glob dropped (rc 1).
Ledger dimensions (D5, D6): a dimension's `ledger` {step, max_units} caps each seat's text units
(tools/audit/text_ledger.py, the dimension's own rule) over the files its blocks hold for that step,
so a seat's cell is finishable; a seat over the cap is refused by name. Its `classify` globs and
`static` map {glob: reason} draw the line between documentation the dimension measures and static
records it leaves: every tracked path a `classify` glob matches is in the universe or one `static`
glob, never both, and every `static` entry matches some such path and carries a reason.
A ledger dimension must draw that line: D6's classifies documents, D5's every file whose suffix
text_ledger.D5_SUFFIXES reads comments from, so a comment-bearing file outside D5's universe and
static map is refused by name, as an unmeasured document is for D6.
Harness citations: a harness under dev/audit/harnesses/ whose header names a dimension brief
(`D<k>.md`) implements that brief's rule, so the brief must cite the harness's path; each one
that does not is refused by name.
--seat <D<k>-s<n>> prints the cells one seat owns instead, one line per (block, file):
steps, axis values, file. `rest` is resolved here, so a finder is handed files, not a rule.
.claude/workflows/audit-find.js runs the check, coverage included, in its Prepare step and refuses the
round on rc != 0.
--round <N> adds the start evaluation (dev/governance/decisions/0018-objective-function.md): round
N starts only when round N-1's OBJECTIVE.json and round N's EVALUATION.json are in the tree at
--ref, every term is read or NO-READ with its reason, every object file has a verdict with
evidence from an evaluator who is not its reviewer, and every card carries the owner's decision,
an accepted one merged at --ref unless the owner's ruling sets its `gates_finders` false: such a
card unmerged is no gap, printed `PARALLEL <card>` since it builds beside the finders. Each gap is
refused by the path or id it names; audit-find.js passes its round. --open-cards (with --round)
prints P3's input as JSON {round, ref, roster_ref, open_cards, unmarked_cards, open_groups,
unmarked_groups} and exits: the accepted cards that gate no finder and are unmerged at --ref, and
the open groups of the roster (roster_lib's reader, or --roster-ref) whose `gates_finders` is not
true; rc 1, with an `UNMARKED <card|group>` line, while an accepted card or open group carries no
boolean. Run when the finders finish, it is the architect's input. --self-test drives a complete record (passes) and one perturbation per rule.
The record also needs: an approving review at a commit in --ref's history whose EVALUATION.json
graded the same objects, a ruling on every decided card, an accepted card's commit after that review
and changing the card's file, reads that are numbers with a tracked enumerator, NO-READs that name
what would read them and who builds it (a group the newest roster at --ref can still hand a
carry, or a card), no removal on a NO-READ in any spelling, and a card for every unset threshold, owner
criterion and unowned item, an accepted one only once its value is set. The two records live under
dev/audit/yardstick/, which scopes.json excludes from every universe: --self-test adds one of each
to the tree and has coverage pass, and refuse both by name once the exclusion loses the directory.
--population prints the install population objective.json lists, read from the sources at --ref:
one line per axis (levels), then LEVELS, PAIRS (level pairs from two axes) and NO-READ AXES; exit 1
and `UNREADABLE <axis>: <why>` when a source is missing or an axis yields no level. A `name` axis is
the identifiers a module uses outside its imports, less each one its calls mark required and never
optional: a key no install can leave out, or one no step presents, is no two-level axis.
"""
import argparse, ast, contextlib, copy, importlib.util, io, itertools, json, math, re, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "seat"))
import roster_lib

_spec = importlib.util.spec_from_file_location("text_ledger", Path(__file__).with_name("text_ledger.py"))
text_ledger = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(text_ledger)
_spec = importlib.util.spec_from_file_location("audit_enumerate", Path(__file__).with_name("enumerate.py"))
audit_enumerate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit_enumerate)
# An axis whose values are a second copy of an enumerator's line prefixes: (dimension, axis) -> the prefixes.
AXIS_SOURCES = {("D17", "kind"): lambda: audit_enumerate.KINDS}

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

def ledger_units(dim, d, files_of, units):
    """{seat: units} over the files each seat's blocks hold for the ledger step."""
    step = d["ledger"]["step"]
    return {seat: sum(units(dim, f) for f in set().union(*[files_of(b) for b in blocks if step in b["steps"]] or [set()]))
            for seat, blocks in d["seats"].items()}


def classify_errors(d, tree, uni, dim=None):
    """The measured line: classified paths in neither or both, static entries naming nothing or unreasoned.
    A ledger dimension must draw one, and D5's must classify every suffix text_ledger reads comments from."""
    if "classify" not in d:
        return ["a ledger dimension draws no classify line"] if "ledger" in d else []
    errs = [f"classify misses a D5 comment carrier: *{s}" for s in text_ledger.D5_SUFFIXES
            if dim == "D5" and not match({f"probe/carrier{s}"}, d["classify"])]
    cls = match(tree, d["classify"])
    static = {g: match(cls, [g]) for g in d.get("static", {})}
    stat = set().union(*static.values()) if static else set()
    errs += [f"classified in neither universe nor static: {f}" for f in sorted(cls - uni - stat)]
    errs += [f"static and in the universe: {f}" for f in sorted(stat & uni)]
    errs += [f"static entry matches no classified path: {g}" for g, fs in sorted(static.items()) if not fs]
    errs += [f"static entry carries no reason: {g}" for g in sorted(static) if not str(d["static"][g]).strip()]
    return errs


def axis_errors(dim, d):
    """An axis the enumerator also prints must name exactly the enumerator's prefixes: a kind in one
    copy alone is a cell no seat can print, or a line no seat owns."""
    errs = []
    for name, vals in d.get("axis", {}).items():
        src = AXIS_SOURCES.get((dim, name))
        if src and set(vals) != set(src()):
            errs.append(f"axis {name} {sorted(set(vals) ^ set(src()))} in scopes.json or tools/audit/enumerate.py, not both")
    return errs


def check(scopes, tree, loc, units=lambda dim, f: 0):
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
        over, cls_errs, per_seat = [], classify_errors(d, tree, uni, dim) + axis_errors(dim, d), {}
        if "ledger" in d:
            per_seat = ledger_units(dim, d, files_of, units)
            over = [s for s, n in per_seat.items() if n > d["ledger"]["max_units"]]
        status = "ok" if not (dup or missing or extra or over or cls_errs) else "FAIL"
        ok &= status == "ok"
        sizes = ", ".join(f"{s}:{len(fs)}f/{sum(loc.get(f,0) for f in fs)}loc" + (f"/{per_seat[s]}u" if s in per_seat else "")
                          for s, fs in seat_files.items())
        print(f"{status} {dim} mode={d['mode']} seats={len(d['seats'])} universe={len(uni)} [{sizes}]")
        for s in over:
            print(f"   over ledger.max_units {d['ledger']['max_units']}: {s} holds {per_seat[s]} units")
        for e in cls_errs[:10]:
            print(f"   {e}")
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
BRIEF_NAMED = re.compile(r"(?<![\w/])(D(?:\d{1,2}|X0))\.md\b")


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


def verdict(scopes, tree, loc, harnesses, briefs, quiet=False, units=lambda dim, f: 0):
    """The default run's answer: every dimension disjoint and complete, the
    tree covered, and every brief-named harness cited by its brief."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out if quiet else sys.stdout):
        ok = check(scopes, tree, loc, units)
        cov_ok, _ = coverage(scopes, tree)
        bad = uncited_harnesses(harnesses, briefs)
        print(f"{'ok' if not bad else 'FAIL'} harness citations: {len(bad)} harness(es) implementing a brief's rule the brief does not cite")
        for h, b in bad:
            print(f"   {h} names {b} in its header; {b} does not cite it")
    return ok and cov_ok and not bad

OBJECTIVE = "dev/audit/config/objective.json"
YARDSTICK = "dev/audit/yardstick/"
SCRIPT_SUFFIXES = (".py", ".mjs", ".js", ".sh")
VERDICTS = ("keep", "change", "remove")
DECISIONS = ("accepted", "rejected", "deferred")


def object_globs(spec):
    return [g for v in spec["objects"].values() for g in ([v] if isinstance(v, str) else v)]


def records(rnd):
    """(the closing round's objective record, round `rnd`'s start evaluation)."""
    return f"{YARDSTICK}round{rnd - 1}/OBJECTIVE.json", f"{YARDSTICK}round{rnd}/EVALUATION.json"


def isnum(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def is_read(v):
    """A read is a finite number, or a non-empty dict of them."""
    return isnum(v) or (isinstance(v, dict) and bool(v) and all(isnum(x) for x in v.values()))


def is_no_read(text):
    """The text says NO-READ as words of its own, in any case, separator or
    position: `no` then `read`, with only non-letters between them and no
    letter or digit touching either end, so `no reader` and `piano read` are not one."""
    return bool(re.search(r"(?<![^\W_])no[\W_]*read(?![^\W_])", str(text).casefold()))


def full(v):
    return isinstance(v, str) and bool(v.strip())


def norm(s):
    return re.sub(r"[\W_]+", "", str(s).casefold())


def enumerates(cmd, tree):
    """The first path-like token of an enumerator command is a tracked script.
    A design choice: a tracked document is no enumerator, whatever follows it."""
    for tok in cmd.split() if isinstance(cmd, str) else ():
        if tok not in ("python3", "python", "node", "bash", "sh") and not tok.startswith("-") and "=" not in tok:
            return tok in tree and tok.endswith(SCRIPT_SUFFIXES)
    return False


def open_builders(tree, show):
    """The groups that can still build a read: those of the newest roster
    tracked at the ref that a carry may be routed to (roster_lib.carry_receivable,
    the rule a carry's destination is checked by), since a build nobody was
    handed is carried to its builder. No roster at the ref is no group."""
    newest = roster_lib.newest_roster(f for f in tree if f.startswith(roster_lib.ROSTERS_DIR + "/"))
    groups = roster_lib.groups_of(json.loads(show(newest))) if newest in tree else {}
    return {k for k, g in groups.items() if roster_lib.carry_receivable(g)}


def evaluation_gaps(rnd, tree, show, merged, anc, changed, parallel=None):
    """Why round `rnd` may not start, one line per gap, [] when it may.
    `show(path, at=None)` is the file's text at the ref (or at commit `at`);
    `merged(sha)` says whether the ref contains that commit, `anc(a, b)` whether
    a is an ancestor of or equal to b, `changed(sha)` the paths it changed
    against its first parent. The terms and the object globs come from
    OBJECTIVE at the ref, so the record is checked against the definition it
    was written under, and neither list is carried here. An accepted card
    whose `gates_finders` (the owner's ruling) is false and that is not merged
    at the ref is no gap: its id is appended to `parallel`, when given."""
    spec = json.loads(show(OBJECTIVE))
    prev, path = records(rnd)
    gaps, terms, builders, groups = [], {}, [], open_builders(tree, show)
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
            elif "value" in row and not is_read(v):
                gaps.append(f"{prev} term {t} value is not a finite number or a non-empty dict of them")
            elif "value" in row and not enumerates(row["enumerator"], tree):
                gaps.append(f"{prev} term {t} enumerator names no script tracked at the ref")
            elif "value" not in row and not str(row.get("no_read", "")).strip():
                gaps.append(f"{prev} term {t} is neither read nor NO-READ with its reason")
            elif "value" not in row:
                gaps += [f"{prev} term {t} NO-READ carries no {k}" for k in ("would_read", "builder") if not full(row.get(k))]
                if full(row.get("builder")) and row["builder"].startswith("card:"):
                    builders.append((t, row["builder"][5:]))
                elif full(row.get("builder")) and row["builder"] not in groups:
                    gaps.append(f"{prev} term {t} builder {row['builder']} is no group the roster at the ref can still hand a build, and no card")
    if path not in tree:
        return gaps + [f"{path} is not in the tree: the start evaluation has not run"]
    ev = json.loads(show(path))
    if ev.get("round") != rnd or ev.get("reads") != prev:
        gaps.append(f"{path} is not round {rnd}'s evaluation of {prev}")
    seat, rev = (norm(ev[k]) if full(ev.get(k)) else "" for k in ("evaluator", "reviewer"))
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
        elif row["verdict"] == "remove" and is_no_read(row["evidence"]):
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
        gating = card.get("gates_finders")
        if not isinstance(gating, bool):
            gaps.append(f"{path} card {cid} is accepted and carries no boolean gates_finders (the owner's ruling on whether it gates the finders)")
        elif not gating and not (c and merged(c)):
            if parallel is not None:
                parallel.append(cid)
            continue
        if not (c and merged(c)):
            gaps.append(f"{path} card {cid} is accepted and not merged at this ref")
        elif revsha and anc(c, revsha):
            gaps.append(f"{path} card {cid} merged {c} is not after the review at {revsha}")
        elif not want:
            gaps.append(f"{path} card {cid} is accepted and names no object or paths")
        elif not want & changed(c):
            gaps.append(f"{path} card {cid} merged {c} changes none of its object or paths")
        unset = [f"{k} {card[k]}" for k, vals in (("threshold", {t: th.get("value") for t, th in spec.get("thresholds", {}).items()}),
                                                 ("criterion", spec.get("owner_criteria", {}))) if card.get(k) in vals and vals[card[k]] is None]
        gaps += [f"{path} card {cid} is accepted for {u}, which {OBJECTIVE} still leaves unset" for u in unset]
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
        if ax.get("kind") is not None:
            continue
        gaps += [f"{OBJECTIVE} population axis {ax.get('axis')} is NO-READ and carries no {k}"
                 for k in ("no_read", "builder") if not full(ax.get(k))]
        b = ax.get("builder")
        if full(b) and b not in groups and not (b.startswith("card:") and b[5:] in cards):
            gaps.append(f"{OBJECTIVE} population axis {ax.get('axis')} builder {b} is no group the roster at the ref can still hand a build, and no card")
    u = terms.get("unowned")
    n = sum(1 for c in cards.values() if str(c.get("unowned", "")).strip())
    if isinstance(u, dict) and isnum(u.get("value")) and n < u["value"]:
        gaps.append(f"{path} carries {n} card(s) with an unowned item but {prev} counts {u['value']}")
    return gaps


def open_cards_report(rnd, tree, show, merged, anc, changed):
    """--open-cards: (JSON object, rc, UNMARKED lines). The accepted cards that
    gate no finder and are unmerged at the ref are P3's input; an accepted card
    with no boolean `gates_finders` could be either, so it is named and the
    listing fails (rc 1) rather than printing a list that omits it."""
    out = []
    evaluation_gaps(rnd, tree, show, merged, anc, changed, out)
    cards = json.loads(show(records(rnd)[1])).get("cards", {})
    unmarked = sorted(cid for cid, c in cards.items()
                      if c.get("decision") == "accepted" and not isinstance(c.get("gates_finders"), bool))
    lines = [f"UNMARKED {cid}: accepted, no boolean gates_finders (the owner's ruling on finder gating)" for cid in unmarked]
    return {"round": rnd, "open_cards": sorted(out), "unmarked_cards": unmarked}, 1 if unmarked else 0, lines


def architect_groups_report(roster):
    """--open-cards' group half: (JSON fields, rc, UNMARKED lines). The roster's
    open groups that gate no finder (roster_lib.architect_groups) are P3's input
    with the open cards; an unmarked one is listed and named, rc 1."""
    groups, unmarked = roster_lib.architect_groups(roster)
    lines = [f"UNMARKED {g}: open, no boolean gates_finders (roster_edit.py set-field {g} gates_finders true|false)" for g in unmarked]
    return {"open_groups": groups, "unmarked_groups": unmarked}, 1 if unmarked else 0, lines


def p3_input(rnd, tree, show, merged, anc, changed, roster):
    """--open-cards whole: the card half and the group half, (JSON fields, rc,
    UNMARKED lines); rc 1 when either half names an unmarked card or group."""
    cards, crc, clines = open_cards_report(rnd, tree, show, merged, anc, changed)
    groups, grc, glines = architect_groups_report(roster)
    return {**cards, **groups}, max(crc, grc), clines + glines


def open_cards_cli():
    """(marked, unmarked): `--open-cards --round 8` run whole, as a subprocess
    of this file, on two commits of a scratch repository whose round-8 record
    differs only in C2 and C3's `gates_finders`: booleans in the first, absent
    and the string "true" in the second. C1 is accepted, non-gating, unmerged.
    Both commits carry one roster whose open group G1 is marked non-gating, so
    the group half lists G1 and names nothing UNMARKED: the exit code and the
    UNMARKED lines measured here are the card half's alone."""
    prev, path = records(8)
    cards = {"C1": {"decision": "accepted", "ruling": "R1", "gates_finders": False, "merged": "0" * 40},
             "C2": {"decision": "accepted", "ruling": "R2", "gates_finders": True},
             "C3": {"decision": "accepted", "ruling": "R3", "gates_finders": True},
             "C4": {"decision": "rejected", "ruling": "R4"}}
    unmarked = copy.deepcopy(cards)
    del unmarked["C2"]["gates_finders"]
    unmarked["C3"]["gates_finders"] = "true"
    from throwaway_git import throwaway_git_init  # the one way to build a scratch repo; main() put tests/ on the path
    with tempfile.TemporaryDirectory() as d:
        env = throwaway_git_init(d, "-q")
        git = lambda *a: subprocess.run(["git", "-C", d, *a], env=env, capture_output=True, text=True, check=True).stdout.strip()
        runs = []
        for cs in (cards, unmarked):
            for f, body in ((OBJECTIVE, {"terms": [], "objects": {}}), (prev, {"terms": {}}),
                            (path, {"round": 8, "reads": prev, "cards": cs}),
                            (f"{roster_lib.ROSTERS_DIR}/wave-r8-groups.json",
                             {"groups": [{"group": "G1", "gates_finders": False, "resume": {"stage": "not-started"}}]})):
                (Path(d) / f).parent.mkdir(parents=True, exist_ok=True)
                (Path(d) / f).write_text(json.dumps(body))
            git("add", "-A")
            git("commit", "-q", "-m", "record")
            runs.append(subprocess.run([sys.executable, str(Path(__file__).resolve()), "--repo", d, "--ref", git("rev-parse", "HEAD"),
                                        "--roster-ref", git("rev-parse", "HEAD"), "--round", "8", "--open-cards"], env=env, capture_output=True, text=True))
    return tuple(runs)


def json_or_none(text):
    try:
        return json.loads(text)
    except ValueError:
        return None


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

    def name_levels(f, pattern):
        """The module's identifiers matching `pattern`, imports apart (an
        import binds an alias, never a Name), less each a call marks required
        and none marks optional. Required: the first argument of X.Required(),
        or an argument beside required=True. Optional: the first argument of
        X.Optional(), or an argument of a call to the same function without
        required=True. A name in neither stays: its absence is not shown
        unreachable."""
        calls = [n for n in ast.walk(ast.parse(show(f))) if isinstance(n, ast.Call)]
        named = lambda args: {a.id for a in args if isinstance(a, ast.Name)}
        marked = lambda c: any(k.arg == "required" and isinstance(k.value, ast.Constant) and k.value.value is True for k in c.keywords)
        attr = lambda c, a: isinstance(c.func, ast.Attribute) and c.func.attr == a
        rows = {c.func.id for c in calls if marked(c) and isinstance(c.func, ast.Name)}
        req = set().union(*(named(c.args[:1]) if attr(c, "Required") else named(c.args) for c in calls if attr(c, "Required") or marked(c)))
        opt = set().union(*(named(c.args[:1]) if attr(c, "Optional") else named(c.args) for c in calls
                            if attr(c, "Optional") or (not marked(c) and isinstance(c.func, ast.Name) and c.func.id in rows)))
        used = {n.id for n in ast.walk(ast.parse(show(f))) if isinstance(n, ast.Name) and re.fullmatch(pattern, n.id)}
        return used - (req - opt)

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
        if k == "name":
            return name_levels(f, ax["pattern"])
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
    (prev, path), roster = records(8), roster_lib.ROSTERS_DIR + "/wave-r99-groups.json"
    groups = {"groups": [{"group": "G1", "resume": {"stage": "in-progress"}}, {"group": "G0", "resume": {"stage": "done"}},
                         {"group": "G2", "resume": {"stage": "carries-open"}}, {"group": "G3", "files": [], "resume": {"stage": "not-started"}}]}
    objs = sorted(match(tree, object_globs(spec)))
    terms = {t: {"value": 1, "enumerator": "python3 " + ME} for t in spec["terms"]}
    terms[spec["terms"][-1]] = {"no_read": "no ledger", "would_read": "a ledger", "builder": "card:C2"}
    terms[spec["terms"][-2]] = {"no_read": "no history", "would_read": "a history", "builder": "G1"}
    good = {"round": 8, "reads": prev, "evaluator": "evaluator-r8", "reviewer": "plan-review-r8",
            "review": {"verdict": "approve", "sha": "rev"},
            "objects": {f: {"verdict": "keep", "evidence": "e"} for f in objs},
            "cards": {"C1": {"decision": "accepted", "ruling": "R1", "gates_finders": True, "merged": "abc", "object": ME},
                      "C2": {"decision": "rejected", "ruling": "R2", "unowned": "u", "threshold": "floor", "criterion": "D4"}}}
    good["objects"][objs[0]] = {"verdict": "change", "evidence": "e", "card": "C1"}
    # commits: old is an ancestor of the review rev, abc is after it
    def run(ev=good, tm=terms, drop=(), sp=spec, revdoc=None, merged=lambda sha: sha in ("abc", "rev", "old"), parallel=None, check=None):
        files = {OBJECTIVE: json.dumps(sp), prev: json.dumps({"terms": tm}), path: json.dumps(ev), roster: json.dumps(groups)}
        sh = lambda f, at=None: (revdoc or json.dumps({"objects": ev.get("objects")})) if at else files[f]
        args = (8, (tree | set(files)) - set(drop), sh, merged, lambda a, b: (a, b) in (("old", "rev"), ("rev", "rev")),
                lambda c: {"abc": {ME}, "old": {ME}}.get(c, set()))
        return check(*args) if check else evaluation_gaps(*args, parallel)
    # --open-cards' report, the function main() prints: (JSON object, rc, UNMARKED lines).
    report = lambda ev=good, **kw: run(ev, check=open_cards_report, **kw)
    def beside(ev=good, **kw):
        """(gaps, ids of the cards building beside the finders) of one run."""
        out = []
        return run(ev, parallel=out, **kw), out
    def edit(fn, base=good):
        c = copy.deepcopy(base)
        fn(c)
        return c
    only = lambda gaps, needle: len(gaps) == 1 and needle in gaps[0]
    t0, t8, t9 = spec["terms"][0], spec["terms"][-2], spec["terms"][-1]
    card = lambda k, **kw: edit(lambda c: c["cards"][k].update(kw))
    term = lambda t, **kw: run(tm=edit(lambda c: c[t].update(kw), terms))
    last = lambda **kw: run(edit(lambda c: c["objects"][objs[-1]].update(kw)))
    # NO-READ spelled every way a record might: case, separator, wrapping, position.
    spellings = [pre + a + sep + b + post for a, b in (("NO", "READ"), ("no", "read"), ("No", "Read"), ("nO", "rEAD"))
                 for sep in ("-", "_", " ", "", "\u2011", " - ", "\n") for pre, post in (("", ""), ("", ": no ledger"), ("unscored (", ": none)"), ("'", "'"), ("  ", ""))]
    return {
        "a complete record passes": bool(objs) and run() == [],
        "round N reads round N-1's objective record and its own evaluation": records(8) == (YARDSTICK + "round7/OBJECTIVE.json", YARDSTICK + "round8/EVALUATION.json"),
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
        # Finder gating (tvofi 2026-11-15): only a card the owner's ruling makes
        # gate the finders (`gates_finders` true) holds the round's start; one
        # that does not, unmerged, builds beside the finders, never a gap.
        "a complete record lists nothing beside the finders": beside() == ([], []),
        "a gating accepted card not merged is refused and not listed beside":
            (lambda r: only(r[0], "card C1 is accepted and not merged") and r[1] == [])(beside(merged=lambda sha: sha != "abc")),
        "a non-gating accepted card not merged passes and is listed beside":
            beside(card("C1", gates_finders=False), merged=lambda sha: sha != "abc") == ([], ["C1"]),
        "a non-gating unmerged card's unset value is no gap, it builds with the card":
            beside(card("C1", gates_finders=False, threshold="floor"), merged=lambda sha: sha != "abc") == ([], ["C1"]),
        "a non-gating merged card is checked as any accepted card":
            only(run(card("C1", gates_finders=False, merged="old")), "is not after the review") and beside(card("C1", gates_finders=False)) == ([], []),
        "an accepted card with no boolean gates_finders is refused, in every shape":
            all(only(run(ev), "card C1 is accepted and carries no boolean gates_finders")
                for ev in [edit(lambda c: c["cards"]["C1"].pop("gates_finders"))] + [card("C1", gates_finders=v) for v in (None, "yes", "no", 0, 1, "false")]),
        "an accepted card with no gates_finders is refused even unmerged, and never listed beside":
            (lambda r: len(r[0]) == 2 and r[1] == [])(beside(edit(lambda c: c["cards"]["C1"].pop("gates_finders")), merged=lambda sha: sha != "abc")),
        # --open-cards, P3's input (fix review 3620): it lists what is open and
        # never prints an empty list over cards that carry no gates_finders.
        "--open-cards lists a non-gating unmerged card, rc 0":
            report(card("C1", gates_finders=False), merged=lambda sha: sha != "abc") == ({"round": 8, "open_cards": ["C1"], "unmarked_cards": []}, 0, []),
        "--open-cards lists nothing on a complete record whose gating card is merged (null control)":
            report() == ({"round": 8, "open_cards": [], "unmarked_cards": []}, 0, []),
        "--open-cards refuses an accepted card with no boolean gates_finders by name, rc 1":
            all(report(ev, merged=m)[1:] == (1, ["UNMARKED C1: accepted, no boolean gates_finders (the owner's ruling on finder gating)"])
                and report(ev, merged=m)[0]["unmarked_cards"] == ["C1"]
                for ev in (edit(lambda c: c["cards"]["C1"].pop("gates_finders")), card("C1", gates_finders="no"))
                for m in (lambda sha: sha != "abc", lambda sha: True)),
        "a rejected or deferred card needs no gates_finders": "gates_finders" not in good["cards"]["C2"] and run(card("C2", decision="deferred")) == [],
        # P3's input when the finders finish (tvofi 2026-11-15): the open cards
        # and every open roster group the finders do not wait for. An unmarked
        # group is listed and flagged, and the listing fails until it is marked.
        "P3's group half lists the open non-gating groups, rc 0 when all are marked":
            architect_groups_report({"groups": [{"group": "G", "gates_finders": True, "resume": {"stage": "in-progress"}},
                                                {"group": "N", "gates_finders": False, "resume": {"stage": "not-started"}},
                                                {"group": "D", "gates_finders": False, "resume": {"stage": "done"}}]})
            == ({"open_groups": ["N"], "unmarked_groups": []}, 0, []),
        "an unmarked open group is listed, named and fails the listing":
            architect_groups_report({"groups": [{"group": "U", "resume": {"stage": "not-started"}}]})
            == ({"open_groups": ["U"], "unmarked_groups": ["U"]}, 1,
                ["UNMARKED U: open, no boolean gates_finders (roster_edit.py set-field U gates_finders true|false)"]),
        "--open-cards whole: a marked record and roster pass with both halves listed, rc 0":
            run(card("C1", gates_finders=False), merged=lambda sha: sha != "abc", check=lambda *a: p3_input(*a, {"groups": [
                {"group": "N", "gates_finders": False, "resume": {"stage": "not-started"}}]}))
            == ({"round": 8, "open_cards": ["C1"], "unmarked_cards": [], "open_groups": ["N"], "unmarked_groups": []}, 0, []),
        "--open-cards whole fails on an unmarked group alone, or an unmarked card alone":
            run(check=lambda *a: p3_input(*a, {"groups": [{"group": "U", "resume": {"stage": "not-started"}}]}))[1:]
            == (1, ["UNMARKED U: open, no boolean gates_finders (roster_edit.py set-field U gates_finders true|false)"])
            and run(edit(lambda c: c["cards"]["C1"].pop("gates_finders")), check=lambda *a: p3_input(*a, {"groups": []}))[1] == 1,
        "a null, absent, blank or non-string reviewer or evaluator is refused":
            all(only(run(ev), "two seats") for ev in [edit(lambda c: c.update(**{k: v})) for k in ("reviewer", "evaluator") for v in (None, "", "  ", 0, [], 1, ["x"])]
                + [edit(lambda c: c.pop(k)) for k in ("reviewer", "evaluator")]),
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
        "B5 a null value is refused": only(term(t0, value=None), t0 + " value is not a finite number"),
        "B5 a value that is no finite number is refused": all(only(term(t0, value=v), t0 + " value is not a finite number")
                                                               for v in (float("nan"), float("inf"), True, "1", {}, {"a": "x"}, {"a": 1, "b": None})),
        "B5 an enumerator naming no tracked file is refused": only(term(t0, enumerator="by hand"), t0 + " enumerator names no script"),
        "B5 a tracked document is no enumerator": "CLAUDE.md" in tree and only(term(t0, enumerator="CLAUDE.md by hand"), t0 + " enumerator names no script"),
        "B5 an untracked script is no enumerator": "no/such_script.py" not in tree and only(term(t0, enumerator="python3 no/such_script.py"), t0 + " enumerator names no script"),
        "B5 an enumerator that is an interpreter and no file is refused": only(term(t0, enumerator="python3 -I"), t0 + " enumerator names no script"),
        "B5 a dict of numbers is a value": run(tm=edit(lambda c: c[t0].update(value={"a": 1}), terms)) == [],
        "B6 a NO-READ naming nothing that would read it is refused": only(run(tm=edit(lambda c: c[t9].pop("would_read"), terms)), t9 + " NO-READ carries no would_read") and only(run(tm=edit(lambda c: c[t9].pop("builder"), terms)), t9 + " NO-READ carries no builder"),
        "B6 a builder card the evaluation lacks is refused": only(run(tm=edit(lambda c: c[t9].update(builder="card:C9"), terms)), "card:C9 is no card"),
        "B6 a builder the roster cannot hand a build is refused: unknown, done, carries-open, a sink":
            all(only(term(t8, builder=b), t8 + " builder " + b + " is no group the roster") for b in ("R99-NOBODY", "G0", "G2", "G3", "g1", "card")),
        "B6 with no roster at the ref every group builder is refused":
            [g.partition(" builder G1 is no group the roster")[0].rsplit(" ", 1)[-1] for g in run(drop=[f for f in tree | {roster} if f.startswith(roster_lib.ROSTERS_DIR + "/")])] == [t8, "n"],
        "B7 a removal on a NO-READ is refused in every spelling":
            len(spellings) == 140 and all(only(last(verdict="remove", evidence=e, card="C2"), "rests on a NO-READ") for e in spellings),
        "B7 a removal whose evidence has the letters inside other words passes":
            all(last(verdict="remove", evidence=e, card="C2") == [] for e in ("no reader of this file exists in the tree", "casino readings", "the piano read 0", "piano reads 0")),
        "B7 a removal on a measured zero passes": last(verdict="remove", evidence="yield 0 in rounds 6 and 7", card="C2") == [],
        "B8 an unset threshold with no card is refused": only(run(card("C2", threshold="band")), "threshold floor is unset"),
        "B8 an unset owner criterion with no card is refused": only(run(card("C2", criterion="D7")), "owner criterion D4 is unset"),
        "B8 an owner criterion naming an untracked path is refused": only(run(sp=edit(lambda s: s["owner_criteria"].update(D7="no/such"), spec)), "owner criterion D7 names"),
        "B8 a NO-READ axis with no builder is refused": only(run(sp=edit(lambda s: s["population"][0].pop("builder"), spec)), "population axis n is NO-READ and carries no builder"),
        "B8 a NO-READ axis with no reason is refused": only(run(sp=edit(lambda s: s["population"][0].pop("no_read"), spec)), "population axis n is NO-READ and carries no no_read"),
        "B8 a NO-READ axis whose builder the roster cannot hand a build is refused":
            all(only(run(sp=edit(lambda s: s["population"][0].update(builder=b), spec)), "population axis n builder " + b + " is no group the roster") for b in ("G0", "card:C9"))
            and run(sp=edit(lambda s: s["population"][0].update(builder="card:C2"), spec)) == [],
        "B8 an accepted card for a value still unset is refused":
            only(run(card("C1", threshold="floor")), "card C1 is accepted for threshold floor") and only(run(card("C1", criterion="D4")), "card C1 is accepted for criterion D4"),
        "B8 an accepted card for a value that is set passes": run(card("C1", threshold="band", criterion="D7")) == [],
        "B9 fewer unowned cards than the read counts is refused": only(run(tm=edit(lambda c: c["unowned"].update(value=2), terms)), "1 card(s) with an unowned item but"),
        "B11 a row for a file outside the object globs is refused": only(run(edit(lambda c: c["objects"].update({"README.md": {"verdict": "keep", "evidence": "e"}}))), "grades README.md, which is no object"),
        "B10 a verdict outside keep/change/remove is refused": only(run(edit(lambda c: c["objects"][objs[-1]].update(verdict="retain", card="C1"))), "no keep/change/remove verdict for " + objs[-1]),
    }


def population_self_test():
    """{arm: held} on a synthetic tree: one axis per kind with levels counted by
    hand, a missing symbol and an empty glob refused, a NO-READ axis kept."""
    flow = ("from .const import (\n    CONF_I_ENTITY,\n)\nS = {v.Required(CONF_A_ENTITY): 1, v.Required(CONF_B_ENTITY): 1, v.Optional(CONF_B_ENTITY): 1, v.Optional(CONF_C_ENTITY): 1}\n"
            "R = (_F('p', CONF_D_ENTITY, required=True), _F('p', CONF_E_ENTITY, required=True), _F('q', CONF_E_ENTITY), _F('q', CONF_F_ENTITY, required=False),\n"
            "     *(_F('q', k) for k in (CONF_G_ENTITY,)), get(CONF_A_ENTITY), get(CONF_D_ENTITY), get(CONF_H_ENTITY), get(CONF_K_ENTITY_ID))\n# CONF_Z_ENTITY\n")
    files = {"p/flow.py": flow, "p/const.py": 'K = "k"\n', "p/m.py": 'T = (K, "w")\nD = {"d1": 1, "d2": 2}\nL = [*T, "v"]\nX = tuple(T)\n'
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
        "an untracked source file is UNREADABLE by name": pop({**tup("T"), "file": "p/none.py"}) == (
            ["UNREADABLE a: p/none.py is not tracked at the ref", "LEVELS: 0", "PAIRS: 0", "NO-READ AXES: 0"], False),
        # A required everywhere, D a required row: no absent level. I import only, Z a comment: never presented.
        # B and E are required in one step and optional in another, G is generated, H only read: each stays.
        # CONF_K_ENTITY_ID only starts like one: the pattern is the whole identifier.
        "a name axis drops a key required everywhere or never presented":
            pop({"axis": "o", "kind": "name", "file": "p/flow.py", "pattern": "CONF_[A-Z]_ENTITY", "binary": True})[0][0]
            == "o\t6 binary axes\tCONF_B_ENTITY,CONF_C_ENTITY,CONF_E_ENTITY,CONF_F_ENTITY,CONF_G_ENTITY,CONF_H_ENTITY",
    }


def blob_units(repo, ref):
    """units(dim, path): text_ledger's unit count of the file at ref, read once per file at ref."""
    texts, cache = {}, {}
    def text(f):
        if f not in texts:
            r = subprocess.run(["git", "-C", repo, "show", f"{ref}:{f}"], capture_output=True)
            try:
                texts[f] = r.stdout.decode("utf-8")
            except UnicodeDecodeError:
                texts[f] = ""
        return texts[f]
    def units(dim, f):
        if (dim, f) not in cache:
            cache[dim, f] = len(text_ledger.units_of(f, text(f), dim))
        return cache[dim, f]
    return units


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
    ap.add_argument("--open-cards", action="store_true",
                    help="with --round: print, as JSON, P3's input (open non-gating cards at --ref, open non-gating roster groups) and exit; rc 1 naming any unmarked card or group")
    ap.add_argument("--roster-ref", help="the roster's ref for --open-cards (default: roster_lib.reader_ref)")
    a = ap.parse_args()
    show = lambda f, at=None: subprocess.check_output(["git", "-C", a.repo, "show", f"{at or a.ref}:{f}"], text=True)
    anc = lambda x, y: subprocess.run(["git", "-C", a.repo, "merge-base", "--is-ancestor", str(x), y],
                                      capture_output=True).returncode == 0
    merged = lambda sha: anc(sha, a.ref)
    changed = lambda c: set(subprocess.run(["git", "-C", a.repo, "diff", "--name-only", f"{c}^1", str(c)],
                                           capture_output=True, text=True).stdout.split())
    tree = set(subprocess.check_output(["git", "-C", a.repo, "ls-tree", "-r", "--name-only", a.ref], text=True).split())
    if a.open_cards:
        if a.round is None or records(a.round)[1] not in tree:
            print(f"--open-cards needs --round <N> and {records(a.round or 0)[1]} tracked at {a.ref}", file=sys.stderr)
            sys.exit(2)
        rref = roster_lib.reader_ref(a.repo, a.roster_ref)
        listing, rc, lines = p3_input(a.round, tree, show, merged, anc, changed, roster_lib.show_roster(a.repo, rref))
        for line in lines:
            print(line, file=sys.stderr)
        rev = lambda r: subprocess.check_output(["git", "-C", a.repo, "rev-parse", r], text=True).strip()
        print(json.dumps({**listing, "ref": rev(a.ref), "roster_ref": rev(rref)}))
        sys.exit(rc)
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
    units = blob_units(a.repo, a.ref)
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
        # The same two on the plan-oracle dimensions, each refused by what it names, and the axis
        # D17 shares with the enumerator: a kind planted in either copy alone is refused.
        def _dim(bad, dim):
            o = io.StringIO()
            with contextlib.redirect_stdout(o):
                r = check({dim: bad[dim]}, tree, loc)
            return r, o.getvalue()
        twice16 = copy.deepcopy(scopes)
        a16, b16 = list(twice16["D16"]["seats"])[:2]
        twice16["D16"]["seats"][b16].append(copy.deepcopy(twice16["D16"]["seats"][a16][0]))
        none17 = copy.deepcopy(scopes)
        none17["D17"]["seats"][list(none17["D17"]["seats"])[-1]] = [{"files": ["**"], "steps": []}]
        kind17 = copy.deepcopy(scopes)
        kind17["D17"]["axis"]["kind"].append("planted-kind")
        kind17["D17"]["seats"][list(kind17["D17"]["seats"])[0]][0]["axis"].append("planted-kind")
        r_t16, o_t16 = _dim(twice16, "D16")
        r_n17, o_n17 = _dim(none17, "D17")
        r_k17, o_k17 = _dim(kind17, "D17")
        real_kinds = audit_enumerate.KINDS
        try:
            audit_enumerate.KINDS = real_kinds + ("planted-prefix",)
            r_e17, o_e17 = _dim(scopes, "D17")
        finally:
            audit_enumerate.KINDS = real_kinds
        new_dims = {
            "null control: the live D16 and D17 pass": _dim(scopes, "D16")[0] is True and _dim(scopes, "D17")[0] is True,
            "a D16 block owned by two seats is refused": not r_t16 and f"by ['{a16}', '{b16}']" in o_t16,
            "a D17 seat emptied leaves its cells unowned": not r_n17 and "   unowned (" in o_n17,
            "a D17 kind the enumerator does not print is refused": not r_k17 and "axis kind ['planted-kind']" in o_k17,
            "a prefix the enumerator prints and no D17 seat owns is refused": not r_e17 and "axis kind ['planted-prefix']" in o_e17,
        }
        print(f"   D16 and D17 arms: {sum(new_dims.values())}/{len(new_dims)} held")
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
        cov = dict(new_dims)
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
        # Every brief of the tree is a name a harness header can cite, DX0 included.
        stems = sorted(Path(f).stem for f in tree if f.startswith(BRIEF_DIR) and f.endswith(".md") and f.count("/") == BRIEF_DIR.count("/"))
        every = "every brief's name in a harness header is read"
        cov[every] = len(stems) > 1 and all(
            uncited_harnesses({HARNESS_DIR + "p.py": f'"""Planted: {s}.md rule."""\n'}, {s: ""}) == [(HARNESS_DIR + "p.py", BRIEF_DIR + s + ".md")]
            for s in stems)
        print(f"   harness-citation arm over {len(stems)} briefs: {cov[every]}")
        # Ledger dimensions: the per-seat unit cap and the documentation line,
        # each refused by what it must name, against text_ledger's real units.
        def _q(bad, tr=None, un=None):
            o = io.StringIO()
            with contextlib.redirect_stdout(o):
                r = check({k: v for k, v in bad.items() if k in ("D5", "D6")}, tree if tr is None else tr, loc, un or units)
            return r, o.getvalue()
        live_l, _ = _q(scopes)
        capped = copy.deepcopy(scopes); capped["D6"]["ledger"]["max_units"] = 1
        r_cap, o_cap = _q(capped)
        unstatic = copy.deepcopy(scopes); unstatic["D6"]["static"].pop("dev/archive/**")
        r_un, o_un = _q(unstatic)
        both = copy.deepcopy(scopes); both["D6"]["static"]["README.md"] = "perturbation: static and measured"
        r_both, o_both = _q(both)
        deadst = copy.deepcopy(scopes); deadst["D6"]["static"]["no/such/**.md"] = "perturbation: names nothing"
        r_dead, _ = _q(deadst)
        bare_st = copy.deepcopy(scopes); bare_st["D6"]["static"]["dev/archive/**"] = " "
        r_bare, _ = _q(bare_st)
        cov.update({
            "null control: the live D5 and D6 pass the cap and the line": live_l,
            "a seat over ledger.max_units is refused by name": not r_cap and "over ledger.max_units 1: s1 holds" in o_cap,
            "a classified path in neither universe nor static is refused": not r_un and "classified in neither universe nor static: dev/archive/README.md" in o_un,
            "a static path in the universe is refused": not r_both and "static and in the universe: README.md" in o_both,
            "a static entry naming nothing is refused": not r_dead,
            "a static entry with no reason is refused": not r_bare,
        })
        print(f"   ledger arms: live {live_l}, cap refused {not r_cap}, line refused {not r_un}/{not r_both}/{not r_dead}/{not r_bare}")
        # D5's comment line (fix review 3571, class-open): the verdict's plant, a committed
        # .claude/workflows/zz-planted.js holding one comment, is now a unit of a D5 seat; the same
        # plant in .claude/ (another dimension covers it, D5 does not) is refused by name; and the D6 null control,
        # dev/zz-planted.md, is still refused by D6's own line.
        PIN, POUT, PMD = ".claude/workflows/zz-planted.js", ".claude/zz-planted.js", "dev/zz-planted.md"
        planted_units = lambda dim, f: 1 if f in (PIN, POUT) and dim == "D5" else units(dim, f)
        def d5_total(tr):
            _, fo = resolver(scopes["D5"], tr)
            return sum(ledger_units("D5", scopes["D5"], fo, planted_units).values())
        r_in, _ = _q(scopes, tree | {PIN}, planted_units)
        r_out, o_out = _q(scopes, tree | {POUT}, planted_units)
        r_md, o_md = _q(scopes, tree | {PMD})
        nocls = copy.deepcopy(scopes); nocls["D5"].pop("classify", None)
        r_nocls, o_nocls = _q(nocls)
        narrow = copy.deepcopy(scopes); narrow["D5"]["classify"] = ["**.py"]
        r_narrow, o_narrow = _q(narrow)
        unrounds = copy.deepcopy(scopes); unrounds["D5"].get("static", {}).pop("dev/audit/{rounds,rca,waves}/**", None)
        r_unr, o_unr = _q(unrounds)
        cov.update({
            "the verdict's plant in .claude/workflows/ is a D5 unit": r_in and d5_total(tree | {PIN}) == d5_total(tree) + 1,
            "a comment carrier in neither D5 universe nor static is refused": not r_out and f"classified in neither universe nor static: {POUT}" in o_out,
            "null control: a document in neither D6 universe nor static is still refused": not r_md and f"classified in neither universe nor static: {PMD}" in o_md,
            "a ledger dimension with no classify line is refused": not r_nocls and "draws no classify line" in o_nocls,
            "a D5 classify missing a comment carrier is refused": not r_narrow and "classify misses a D5 comment carrier: *.sh" in o_narrow,
            "D5 without the round-evidence static is refused": not r_unr and "classified in neither universe nor static: dev/audit/r" in o_unr,
        })
        print(f"   D5 comment-line arms: plant measured {r_in}, outside refused {not r_out}, D6 null refused {not r_md}, "
              f"no line refused {not r_nocls}, narrow refused {not r_narrow}, unstatic refused {not r_unr}")
        # The default run's verdict, driven as a function: the live scopes pass
        # it, and dropping D10's universe or leaving a brief-named harness
        # uncited fails it. That pins verdict(), not the exit code main() returns.
        hs, bs = read_harnesses(a.repo, a.ref, tree)
        live = verdict(scopes, tree, loc, hs, bs, quiet=True, units=units)
        no_d10_refused = not verdict(no_d10, tree, loc, hs, bs, quiet=True)
        uncited_refused = not verdict(scopes, tree, loc, {**hs, **planted}, {**bs, "D15": "no citation"}, quiet=True)
        cov.update({"the default verdict passes the live scopes": live,
                    "and refuses them without D10's universe": no_d10_refused,
                    "and refuses an uncited brief-named harness": uncited_refused})
        print(f"   default verdict: live {live}, no D10 refused {no_d10_refused}, uncited refused {uncited_refused}")
        # The default invocation, run whole as a subprocess of this file with
        # --repo/--ref: the live scopes exit 0, and the scopes with the blueprints/**
        # glob dropped from every universe that names one exit 1 naming a blueprint, both printing
        # verdict()'s citation line. So coverage cannot fall out of main()'s exit
        # code, and that exit is verdict()'s, whose citation arm is pinned above.
        no_bp = copy.deepcopy(scopes)
        bp_dims = [k for k, d in scopes.items() if not k.startswith("_") and any(g.startswith("blueprints/") for g in d["universe"])]
        for k in bp_dims:
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
        cov["and exits 1 with the blueprints globs dropped from every universe that names one"] = (run_bp.returncode == 1 and cited in run_bp.stdout
            and "in no universe and not excluded: blueprints/" in run_bp.stdout)
        print(f"   default invocation: live rc={run_live.returncode}, blueprints dropped rc={run_bp.returncode}")
        # The start evaluation: the rules as a function, then the default
        # invocation whole. Round 1 has no evaluation and never will, so
        # --round 1 exits 1 naming the file while the run without --round
        # (above) exits 0: the refusal is --round's and reaches the exit code.
        # The two records --round reads are tracked files of the round that
        # writes them: with one of each in the tree the live scopes still cover
        # it, and an exclusion table without their directory names both. So a
        # round that follows 0018 section 6 is not refused by coverage.
        recs = set(records(11))
        bare_y = copy.deepcopy(scopes)
        bare_y["_coverage_excluded"] = {next(q for q in expand_braces(g) if not q.startswith(YARDSTICK)) if any(q.startswith(YARDSTICK) for q in expand_braces(g)) else g: r
                                        for g, r in scopes.get("_coverage_excluded", {}).items()}
        cov["the round's records are covered once written"] = coverage(scopes, tree | recs, quiet=True) == (True, [])
        cov["and refused by name without the exclusion"] = coverage(bare_y, tree | recs, quiet=True) == (False, sorted(recs))
        print(f"   yardstick records: covered={cov['the round\'s records are covered once written']}, refused without the exclusion={cov['and refused by name without the exclusion']}")
        ev = evaluation_self_test(tree, show)
        cov.update({"evaluation: " + k: v for k, v in ev.items()})
        run_r1 = default_run(scopes, "--round", "1")
        cov["--round exits 1 with no evaluation in the tree"] = (run_r1.returncode == 1 and cited in run_r1.stdout
            and "FAIL start evaluation" in run_r1.stdout and "round1/EVALUATION.json is not in the tree" in run_r1.stdout)
        run_oc = default_run(scopes, "--round", "1", "--open-cards")
        cov["--open-cards refuses a round with no evaluation, never an empty list"] = (run_oc.returncode == 2
            and "round1/EVALUATION.json tracked" in run_oc.stderr and "open_cards" not in run_oc.stdout)
        # --open-cards run whole on a record with and without a boolean
        # gates_finders on C2 and C3 (fix review 3620): main()'s exit code and
        # its UNMARKED stderr lines, which the function arms above cannot reach.
        oc_marked, oc_unmarked = open_cards_cli()
        unmarked_lines = [l.split(":")[0] for l in oc_unmarked.stderr.splitlines() if l.startswith("UNMARKED")]
        cov["--open-cards exits 0 with no UNMARKED line when every accepted card carries a boolean (null control)"] = (
            oc_marked.returncode == 0 and "UNMARKED" not in oc_marked.stderr
            and (json_or_none(oc_marked.stdout) or {}).get("open_cards") == ["C1"]
            and (json_or_none(oc_marked.stdout) or {}).get("open_groups") == ["G1"])
        cov["--open-cards exits 1 naming on stderr each accepted card with no boolean gates_finders"] = (
            oc_unmarked.returncode == 1 and unmarked_lines == ["UNMARKED C2", "UNMARKED C3"]
            and (json_or_none(oc_unmarked.stdout) or {}).get("unmarked_cards") == ["C2", "C3"])
        print(f"   evaluation arms: {sum(ev.values())}/{len(ev)} held; --round 1 rc={run_r1.returncode}; --open-cards rc={run_oc.returncode}, "
              f"marked rc={oc_marked.returncode}, unmarked rc={oc_unmarked.returncode} {unmarked_lines}")
        pop = population_self_test()
        cov.update({"population: " + k: v for k, v in pop.items()})
        print(f"   population arms: {sum(pop.values())}/{len(pop)} held")
        good = not any(res) and all(cov.values())
        print("SELF-TEST", "passed (every perturbed scope refused)" if good else
              f"FAILED (accepted: owned twice {res[0]}, unowned {res[1]}; coverage arms {cov})")
        sys.exit(0 if good else 1)
    ok = verdict(scopes, tree, loc, *read_harnesses(a.repo, a.ref, tree), units=units)
    if a.round is not None:
        beside = []
        gaps = evaluation_gaps(a.round, tree, show, merged, anc, changed, beside)
        print(f"{'ok' if not gaps else 'FAIL'} start evaluation round={a.round}: {len(gaps)} gap(s), {len(beside)} card(s) beside the finders")
        for g in gaps:
            print(f"   {g}")
        for cid in sorted(beside):
            print(f"   PARALLEL {cid} accepted, not merged, gates no finder: builds beside them; open at P3, it is the architect's input (--open-cards)")
        ok = ok and not gaps
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
