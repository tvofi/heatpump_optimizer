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
"""
import argparse, contextlib, copy, io, itertools, json, re, subprocess, sys, tempfile
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
    a = ap.parse_args()
    tree = set(subprocess.check_output(["git", "-C", a.repo, "ls-tree", "-r", "--name-only", a.ref], text=True).split())
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
        def default_run(sc):
            with tempfile.NamedTemporaryFile("w", suffix=".json") as fh:
                json.dump(sc, fh)
                fh.flush()
                return subprocess.run([sys.executable, str(Path(__file__).resolve()), "--repo", a.repo,
                                       "--ref", a.ref, "--scopes", fh.name], capture_output=True, text=True)
        run_live, run_bp = default_run(scopes), default_run(no_bp)
        cited = " harness citations: "
        cov["the default invocation exits 0 on the live scopes"] = run_live.returncode == 0 and cited in run_live.stdout
        cov["and exits 1 without D4's and D6's blueprints globs"] = (run_bp.returncode == 1 and cited in run_bp.stdout
            and "in no universe and not excluded: blueprints/" in run_bp.stdout)
        print(f"   default invocation: live rc={run_live.returncode}, blueprints dropped rc={run_bp.returncode}")
        good = not any(res) and all(cov.values())
        print("SELF-TEST", "passed (every perturbed scope refused)" if good else
              f"FAILED (accepted: owned twice {res[0]}, unowned {res[1]}; coverage arms {cov})")
        sys.exit(0 if good else 1)
    sys.exit(0 if verdict(scopes, tree, loc, *read_harnesses(a.repo, a.ref, tree)) else 1)

main()
