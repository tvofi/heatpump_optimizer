#!/usr/bin/env python3
"""machinery_ratchet.py -- one-sided caps on what main's merges are spent on.

The owner's ruling (tvofi, 2026-11-01): production work was 59 of 581 merges
in fourteen days, and the machinery feeds itself. This program grades a
window of main's merges against `dev/governance/config/machinery_budgets.json`
and refuses a window past either cap. The design is the approved note on
design/r10-machinery-ratchets; the policy is ratchet-budgets.md's machinery
section.

THE COUNTING RULE, deterministic from one merge commit M (a two-parent commit
on main's first-parent chain) and its first parent P. `git diff -M -w
--numstat -z P M`: a pure move costs 0 lines on both sides (-M), a reformat
costs 0 (-w), and a rename's lines are charged to its destination (-z names
both ends). Product lines are the added plus deleted lines under
PRODUCT_PREFIXES; every other line is a nonproduct line.

  production  its product lines are above 0
  record      every path it touches, both ends of a rename, is a record path
  machinery   every other merge

THE WINDOW is the newest W first-parent merges, W the budgets file's frozen
`window_merges`: a count of merges, never hours, so one commit always reads
one value. Push mode ends it at --head. PR mode is the newest W-1 merges of
--base plus the pull request itself as one candidate, graded by its three-dot
diff (merge-base..head): the candidate takes the newest slot and the oldest
merge drops out. Each merged M is graded by its own P and M in both modes,
never by the head's files.

THE METRICS, each compared against its cap plus its band:
  nonproduction_merges          record plus machinery merges in the window
  churn_per_kilo_product_lines  nonproduct lines per 1000 product lines,
                                rounded half up to an integer

THE EXEMPTION (the owner's: a change proving more than a 10% improvement in
CI time, programme completion time, right-first-time or token usage). An entry
in the budgets file's `exemptions` list exempts merge M only when all hold:
  - its `pr` is M's own number (the merge subject's; the event's for the
    candidate);
  - no entry for that number is in the budgets file at P (the merge base for
    the candidate), and one is at M (the head): it was added by the merge it
    exempts, so an entry appended later for an already-merged PR exempts
    nothing;
  - its improvement is strictly above 1/10, exactly: (before-after)/before
    for a cost, (after-before)/before for right_first_time;
  - its evidence path resolves at M, and before, after and the two commands
    are read from M's tree too.
An exempted merge leaves the window and the next older merge fills its slot.

Exit 0: inside both caps. 1: a cap exceeded. 2: usage, an unreadable budgets
file, or a history shorter than the window.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

BUDGETS = "dev/governance/config/machinery_budgets.json"
PRODUCT_PREFIXES = ("custom_components/", "blueprints/")
RECORD_PREFIXES = ("dev/programme/",)
RECORD_FILES = ("RELEASE_NOTES.md", "VERSION")
WINDOW_KEY = "window_merges"
CAPS = ("nonproduction_merges", "churn_per_kilo_product_lines")
BAND_SUFFIX = "_band"
EXEMPTIONS_KEY = "exemptions"
# A cost improves when it falls, right-first-time when it rises.
MEASURES = {"ci_time": "cost", "programme_completion_time": "cost",
            "token_usage": "cost", "right_first_time": "gain"}
ENTRY_KEYS = ("pr", "measure", "before", "after", "before_command",
              "after_command", "evidence")
THRESHOLD = Fraction(1, 10)
SUBJECT = re.compile(r"^Merge pull request #(\d+)\b")


class Refusal(Exception):
    """A state the ratchet cannot grade: exit 2."""


def _git(repo: str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True,
                          text=True, check=check)


# --- one merge ---------------------------------------------------------------

def is_product(path: str) -> bool:
    return path.startswith(PRODUCT_PREFIXES)


def is_record(path: str) -> bool:
    return path.startswith(RECORD_PREFIXES) or path in RECORD_FILES


def parse_numstat_z(out: str) -> list[tuple[int, int, list[str], str]]:
    """(added, deleted, every path touched, the path the lines are charged
    to) per file of `git diff --numstat -z`. A binary file's '-' is 0."""
    toks = out.split("\0")
    rows = []
    i = 0
    while i < len(toks):
        t = toks[i]
        i += 1
        if not t:
            continue
        added, deleted, path = t.split("\t", 2)
        n = lambda s: 0 if s == "-" else int(s)
        if path == "":  # a rename: source and destination follow
            src, dst = toks[i], toks[i + 1]
            i += 2
            rows.append((n(added), n(deleted), [src, dst], dst))
        else:
            rows.append((n(added), n(deleted), [path], path))
    return rows


def diff_stats(repo: str, p: str, m: str) -> dict:
    """The counting rule over P..M: product and nonproduct lines, the paths
    touched, and the kind."""
    rows = parse_numstat_z(_git(repo, "diff", "-M", "-w", "--numstat", "-z", p, m).stdout)
    product = nonproduct = 0
    paths: list[str] = []
    for added, deleted, touched, charged in rows:
        if is_product(charged):
            product += added + deleted
        else:
            nonproduct += added + deleted
        paths.extend(touched)
    return {"product": product, "nonproduct": nonproduct, "paths": paths,
            "kind": kind_of(product, paths)}


def kind_of(product: int, paths: list[str]) -> str:
    if product > 0:
        return "production"
    if all(is_record(p) for p in paths):
        return "record"
    return "machinery"


# --- the exemption -----------------------------------------------------------

def _doc_at(repo: str, rev: str, path: str) -> dict:
    r = _git(repo, "show", f"{rev}:{path}", check=False)
    if r.returncode != 0:
        return {}
    try:
        doc = json.loads(r.stdout)
    except ValueError:
        return {}
    return doc if isinstance(doc, dict) else {}


def _entries(doc: dict, pr: int) -> list[dict]:
    ex = doc.get(EXEMPTIONS_KEY)
    if not isinstance(ex, list):
        return []
    return [e for e in ex if isinstance(e, dict) and e.get("pr") == pr]


def _exact(v) -> Fraction | None:
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        return None
    return Fraction(repr(v)) if isinstance(v, float) else Fraction(v)


def improvement(entry: dict) -> Fraction | None:
    """The entry's improvement as an exact fraction, or None when it states
    no measurable one."""
    kind = MEASURES.get(entry.get("measure"))
    before, after = _exact(entry.get("before")), _exact(entry.get("after"))
    if kind is None or before is None or after is None or before <= 0:
        return None
    return (before - after) / before if kind == "cost" else (after - before) / before


def entry_grants(repo: str, rev: str, entry: dict) -> tuple[bool, str]:
    """Whether one entry, read from the tree at `rev`, proves its >10%."""
    missing = [k for k in ENTRY_KEYS if k not in entry]
    if missing:
        return False, f"entry for #{entry.get('pr')} lacks {missing}"
    for k in ("before_command", "after_command", "evidence"):
        if not isinstance(entry[k], str) or not entry[k].strip():
            return False, f"entry for #{entry['pr']}: {k} is not a non-empty string"
    gain = improvement(entry)
    if gain is None:
        return False, f"entry for #{entry['pr']}: no measurable improvement"
    if not gain > THRESHOLD:
        return False, f"entry for #{entry['pr']}: improvement {float(gain):.4f} is not above {float(THRESHOLD)}"
    if _git(repo, "cat-file", "-e", f"{rev}:{entry['evidence']}", check=False).returncode != 0:
        return False, f"entry for #{entry['pr']}: evidence {entry['evidence']} does not resolve at {rev[:12]}"
    return True, f"#{entry['pr']} exempt: {entry['measure']} improved {float(gain):.4f}"


def exemption(repo: str, p: str, m: str, pr: int | None, touched: list[str],
              budgets: str = BUDGETS) -> tuple[bool, str]:
    """Whether the change P..M is exempted by an entry it added itself."""
    if pr is None or budgets not in touched:
        return False, ""
    at_m = _entries(_doc_at(repo, m, budgets), pr)
    if not at_m:
        return False, ""
    if _entries(_doc_at(repo, p, budgets), pr):
        return False, f"#{pr}: its entry was already present before its own merge"
    why = ""
    for e in at_m:
        ok, why = entry_grants(repo, m, e)
        if ok:
            return True, why
    return False, why


# --- the window --------------------------------------------------------------

def first_parent_merges(repo: str, tip: str) -> list[tuple[str, str, int | None]]:
    """(M, P, PR number) for each two-parent commit on tip's first-parent
    chain, newest first."""
    out = _git(repo, "log", "--first-parent", "--format=%H%x00%P%x00%s", tip).stdout
    merges = []
    for line in out.splitlines():
        h, parents, subject = line.split("\0", 2)
        ps = parents.split()
        if len(ps) == 2:
            mt = SUBJECT.match(subject)
            merges.append((h, ps[0], int(mt.group(1)) if mt else None))
    return merges


class Grader:
    """Caches the per-merge grading, so a band's 150 overlapping windows cost
    one diff per merge."""

    def __init__(self, repo: str, budgets: str = BUDGETS, honour: bool = True):
        self.repo, self.budgets, self.honour = repo, budgets, honour
        self._cache: dict[tuple[str, str, int | None], dict] = {}

    def grade(self, p: str, m: str, pr: int | None) -> dict:
        key = (p, m, pr)
        if key not in self._cache:
            s = diff_stats(self.repo, p, m)
            ex, why = (exemption(self.repo, p, m, pr, s["paths"], self.budgets)
                       if self.honour else (False, ""))
            self._cache[key] = {**s, "sha": m, "pr": pr, "exempt": ex, "why": why}
        return self._cache[key]

    def window(self, merges: list, w: int, candidate: dict | None = None) -> tuple[list, list]:
        """The graded rows filling W slots, newest first, and the exempted
        rows skipped on the way. A candidate takes the newest slot."""
        rows, skipped = [], []
        if candidate is not None:
            (skipped if candidate["exempt"] else rows).append(candidate)
        for m, p, pr in merges:
            if len(rows) >= w:
                break
            g = self.grade(p, m, pr)
            (skipped if g["exempt"] else rows).append(g)
        if len(rows) < w:
            raise Refusal(f"the history holds {len(rows)} countable merge(s), fewer than "
                          f"the window's {w}: a shallow clone, or the wrong tip")
        return rows, skipped


def metrics(rows: list[dict]) -> dict:
    product = sum(r["product"] for r in rows)
    nonproduct = sum(r["nonproduct"] for r in rows)
    if product == 0:
        raise Refusal("the window holds no product line, so churn per product line is unbounded")
    return {
        "nonproduction_merges": sum(r["kind"] != "production" for r in rows),
        # 1000*N/P rounded half up, in integers.
        "churn_per_kilo_product_lines": (2000 * nonproduct + product) // (2 * product),
        "window": len(rows),
        "production": sum(r["kind"] == "production" for r in rows),
        "machinery": sum(r["kind"] == "machinery" for r in rows),
        "record": sum(r["kind"] == "record" for r in rows),
        "product_lines": product,
        "nonproduct_lines": nonproduct,
    }


def load_budgets(text: str) -> dict:
    """The budgets file, refused unless every key is one this program reads:
    a key it does not read is a cap that measures nothing."""
    try:
        doc = json.loads(text)
    except ValueError as e:
        raise Refusal(f"{BUDGETS} does not parse ({e})")
    if not isinstance(doc, dict):
        raise Refusal(f"{BUDGETS} is not an object")
    known = {WINDOW_KEY, EXEMPTIONS_KEY, *CAPS, *(c + BAND_SUFFIX for c in CAPS)}
    extra = sorted(k for k in doc if not k.startswith("_") and k not in known)
    if extra:
        raise Refusal(f"{BUDGETS}: {extra} is not a key this ratchet reads")
    for k in (WINDOW_KEY, *CAPS, *(c + BAND_SUFFIX for c in CAPS)):
        v = doc.get(k)
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise Refusal(f"{BUDGETS}: {k} is {v!r}, not a non-negative integer")
    if doc[WINDOW_KEY] < 1:
        raise Refusal(f"{BUDGETS}: {WINDOW_KEY} must be at least 1")
    if not isinstance(doc.get(EXEMPTIONS_KEY), list):
        raise Refusal(f"{BUDGETS}: {EXEMPTIONS_KEY} is not a list")
    return doc


def measure(repo: str, head: str, budgets_doc: dict, base: str | None = None,
            pr: int | None = None, grader: Grader | None = None) -> tuple[dict, list, list]:
    """The window's metrics: push mode without `base`, PR mode with it."""
    g = grader or Grader(repo)
    w = budgets_doc[WINDOW_KEY]
    if base is None:
        rows, skipped = g.window(first_parent_merges(repo, head), w)
    else:
        mb = _git(repo, "merge-base", base, head).stdout.strip()
        s = diff_stats(repo, mb, head)
        ex, why = exemption(repo, mb, head, pr, s["paths"], g.budgets) if g.honour else (False, "")
        cand = {**s, "sha": head, "pr": pr, "exempt": ex, "why": why}
        rows, skipped = g.window(first_parent_merges(repo, base), w, cand)
    return metrics(rows), rows, skipped


def over(measured: dict, doc: dict) -> list[str]:
    """Each metric past its cap plus its band."""
    return [c for c in CAPS if measured[c] > doc[c] + doc[c + BAND_SUFFIX]]


def bands(repo: str, head: str, w: int, positions: int) -> dict:
    """Each metric's largest rise above its running minimum, oldest to newest,
    over the windows ending at the newest `positions` merges."""
    g = Grader(repo)
    merges = first_parent_merges(repo, head)
    series = []
    for i in reversed(range(positions)):
        rows, _ = g.window(merges[i:], w)
        series.append(metrics(rows))
    out = {}
    for c in CAPS:
        low, rise = math.inf, 0
        for s in series:
            low = min(low, s[c])
            rise = max(rise, s[c] - low)
        out[c] = {"band": rise, "min": min(s[c] for s in series), "max": max(s[c] for s in series)}
    return out


def _budgets_text(repo: str, rev: str, path: str) -> str:
    r = _git(repo, "show", f"{rev}:{path}", check=False)
    if r.returncode != 0:
        raise Refusal(f"{path} is absent at {rev}")
    return r.stdout


def check(repo: str, head: str, base: str | None, pr: int | None, out=print) -> int:
    doc = load_budgets(_budgets_text(repo, head, BUDGETS))
    m, rows, skipped = measure(repo, head, doc, base, pr)
    who = f"#{pr}" if pr is not None else f"head {head[:12]}"
    mode = f"PR mode, {who} as the candidate on {base}" if base else f"push mode at {head}"
    out(f"machinery_ratchet: {mode}; window {m['window']} merge(s): "
        f"{m['production']} production, {m['machinery']} machinery, {m['record']} record; "
        f"{m['product_lines']} product line(s), {m['nonproduct_lines']} nonproduct")
    for s in skipped:
        out(f"  exempt {s['sha'][:12]}: {s['why']}")
    bad = over(m, doc)
    for c in CAPS:
        cap, band = doc[c], doc[c + BAND_SUFFIX]
        out(f"  {'FAIL' if c in bad else 'ok  '} {c} {m[c]} <= {cap} + band {band}")
    if bad:
        out("machinery_ratchet: refused; pay by landing production work, record an exemption "
            "the change earns (ratchet-budgets.md), or ask the owner for a raise")
        return 1
    return 0


EVENT_ENV = ("MACHINERY_BASE", "MACHINERY_HEAD", "MACHINERY_PR")


def event_args(env) -> tuple[str, str | None, int | None]:
    """(head, base, pr) for `--check-event` from the workflow step's
    environment: PR mode when both a base and a pull-request number are set,
    else push mode at the head (HEAD when none is set)."""
    base, head, pr = (str(env.get(k) or "").strip() for k in EVENT_ENV)
    if base and pr:
        return head or "HEAD", base, int(pr)
    return head or "HEAD", None, None


# --- self-test ---------------------------------------------------------------

def self_test() -> int:
    """The counting rule, the window, the caps and the exemption, offline over
    throwaway repositories. Every exact count is a function of the fixture."""
    import tempfile
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
    from throwaway_git import throwaway_git_environ, throwaway_git_init

    fails = n = 0

    def ok(name: str, got, want) -> None:
        nonlocal fails, n
        n += 1
        good = got == want
        fails += not good
        print(f"  {'ok  ' if good else 'FAIL'} {name}" + ("" if good else f": got {got!r}, want {want!r}"))

    TOOLS, PROD, REC, MV = ("tools/a.py", "custom_components/x/c.py",
                            "dev/programme/r.md", "tools/mv.py")

    def caps(m1=100, m1b=0, m2=10**9, m2b=0, w=4, ex=()):
        return {"_comment": "fixture", WINDOW_KEY: w, "nonproduction_merges": m1,
                "nonproduction_merges_band": m1b, "churn_per_kilo_product_lines": m2,
                "churn_per_kilo_product_lines_band": m2b, EXEMPTIONS_KEY: list(ex)}

    def entry(pr, before=100, after=89, measure_="ci_time", evidence="ev/proof.txt"):
        return {"pr": pr, "measure": measure_, "before": before, "after": after,
                "before_command": "time x", "after_command": "time x", "evidence": evidence}

    class Repo:
        """A main line of no-ff merges, each a side commit off the tip."""

        def __init__(self, root: Path):
            self.d = str(root)
            throwaway_git_init(root, "-q", "-b", "main")
            self.files = {TOOLS: "", PROD: "", REC: "", MV: "move me\n",
                          BUDGETS: json.dumps(caps())}
            self.seq = 0
            self.tip = self._commit([], "root")

        def g(self, *a: str) -> str:
            return _git(self.d, *a).stdout.strip()

        def _commit(self, parents: list[str], msg: str) -> str:
            ix = Path(self.d) / ".git" / "fixture-index"
            ix.unlink(missing_ok=True)
            entries = []
            for path, text in sorted(self.files.items()):
                blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=self.d,
                                      input=text, capture_output=True, text=True,
                                      check=True).stdout.strip()
                entries.append(f"100644 {blob}\t{path}")
            subprocess.run(["git", "update-index", "--add", "--index-info"], cwd=self.d,
                           input="\n".join(entries) + "\n", text=True, check=True,
                           env={**os.environ, "GIT_INDEX_FILE": str(ix)})
            tree = subprocess.run(["git", "write-tree"], cwd=self.d, capture_output=True, text=True,
                                  check=True, env={**os.environ, "GIT_INDEX_FILE": str(ix)}).stdout.strip()
            return self.g("commit-tree", tree, *[x for p in parents for x in ("-p", p)], "-m", msg)

        def change(self, ops: list) -> None:
            for op in ops:
                if op[0] == "add":  # append n distinct lines
                    _, path, k = op
                    self.seq += 1
                    self.files[path] = self.files.get(path, "") + "".join(
                        f"line {self.seq}.{j}\n" for j in range(k))
                elif op[0] == "mv":
                    _, src, dst = op
                    self.files[dst] = self.files.pop(src)
                elif op[0] == "set":
                    self.files[op[1]] = op[2]

        def side(self, ops: list) -> str:
            """A branch commit off the tip carrying `ops`; main is unmoved."""
            self.change(ops)
            return self._commit([self.tip], "work")

        def merge(self, pr: int, ops: list) -> str:
            b = self.side(ops)
            self.tip = self._commit([self.tip, b], f"Merge pull request #{pr} from o/b{pr}")
            return self.tip

    def budgets_ops(doc) -> list:
        return [("set", BUDGETS, json.dumps(doc))]

    def run_cli(repo: "Repo", *argv: str) -> tuple[int, str]:
        r = subprocess.run([sys.executable, "-I", str(Path(__file__).resolve()), "--repo", repo.d, *argv],
                           capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def m12(repo: "Repo", head: str, doc: dict, base=None, pr=None, honour=True) -> tuple:
        m, _, _ = measure(repo.d, head, doc, base, pr, Grader(repo.d, honour=honour))
        return m["nonproduction_merges"], m["churn_per_kilo_product_lines"]

    PRODM = [("add", PROD, 10), ("add", TOOLS, 4)]   # production: 10 product, 4 other
    MACH = [("add", TOOLS, 6)]                        # machinery: 6 nonproduct
    RECM = [("add", REC, 2)]                          # record: 2 nonproduct

    with throwaway_git_environ(), tempfile.TemporaryDirectory() as tmp:
        def fresh(name: str) -> Repo:
            return Repo(Path(tmp) / name)

        # 1. k production merges in N give N-k, and the churn ratio exactly.
        r = fresh("kinds")
        r.merge(1, PRODM); r.merge(2, MACH); r.merge(3, RECM); r.merge(4, PRODM)
        r.merge(5, MACH); r.merge(6, RECM)
        doc6 = caps(w=6)
        m, _, _ = measure(r.d, r.tip, doc6)
        ok("2 production merges in 6 give 4 nonproduction",
           (m["nonproduction_merges"], m["production"], m["machinery"], m["record"]), (4, 2, 2, 2))
        # nonproduct 4+6+2+4+6+2 = 24 over product 20: 1200 per kilo.
        ok("churn per kilo product lines is 1000*24/20", m["churn_per_kilo_product_lines"], 1200)
        ok("a path under blueprints/ is product", is_product("blueprints/a.yaml"), True)
        ok("a lookalike prefix is not product", is_product("custom_components_old/a.py"), False)
        ok("VERSION and RELEASE_NOTES.md are record paths", (is_record("VERSION"),
           is_record("RELEASE_NOTES.md"), is_record("dev/programme/x.md")), (True, True, True))
        ok("a merge touching a record path and a tools path is machinery",
           kind_of(0, [REC, TOOLS]), "machinery")
        ok("a merge with one product line is production", kind_of(1, [PROD]), "production")
        ok("the window is the newest W: W=3 counts merges 4..6 only",
           measure(r.d, r.tip, caps(w=3))[0]["nonproduction_merges"], 2)
        try:
            measure(r.d, r.tip, caps(w=7))
            got = "measured"
        except Refusal:
            got = "refused"
        ok("a history shorter than the window is refused, never measured short", got, "refused")

        # 2. The cap and its band, through the entry point: a candidate
        # machinery merge that drops the oldest production merge.
        r = fresh("cap")
        r.merge(1, PRODM); r.merge(2, PRODM); r.merge(3, MACH); r.merge(4, MACH)
        r.change(budgets_ops(caps(m1=2, m1b=1, w=5)))
        r.merge(5, [])  # commits the caps; a machinery merge, so the base reads 3 of 4
        base = r.tip
        ok("the base window reads 3 nonproduction of 5", m12(r, base, caps(m1=2, m1b=1, w=5))[0], 3)
        cand = r.side(MACH)
        rc, out = run_cli(r, "--check", "--base", base, "--head", cand, "--pr", "6")
        ok("a candidate machinery merge past cap+band exits 1 (4 > 2 + 1)", rc, 1)
        ok("...and prints the metric, its cap and its band",
           "FAIL nonproduction_merges 4 <= 2 + band 1" in out, True)
        got = measure(r.d, cand, caps(m1=2, m1b=1, w=5), base, 6)[0]
        ok("the candidate takes the newest slot and the oldest merge drops out",
           (got["nonproduction_merges"], got["window"]), (4, 5))
        r.files[BUDGETS] = json.dumps(caps(m1=3, m1b=1, w=5))
        cand2 = r._commit([cand], "caps at 3")
        rc, _ = run_cli(r, "--check", "--base", base, "--head", cand2, "--pr", "6")
        ok("the same candidate at exactly cap+band exits 0 (4 <= 3 + 1)", rc, 0)
        rc, _ = run_cli(r, "--check", "--head", base)
        ok("push mode at the base inside cap+band exits 0 (3 <= 2 + 1)", rc, 0)
        ok("over() refuses only past cap+band",
           (over({"nonproduction_merges": 5, "churn_per_kilo_product_lines": 0}, caps(m1=4, m1b=1)),
            over({"nonproduction_merges": 6, "churn_per_kilo_product_lines": 0}, caps(m1=4, m1b=1))),
           ([], ["nonproduction_merges"]))
        ok("over() refuses the churn ratio past its cap+band",
           over({"nonproduction_merges": 0, "churn_per_kilo_product_lines": 12},
                caps(m2=10, m2b=1)), ["churn_per_kilo_product_lines"])

        # 3. Null control: a rename-only move of a tools file into
        # custom_components/ leaves both metrics byte-identical, and the same
        # move with one line edited is product work (the control's control).
        outs = []
        for name, extra in (("plain", []), ("moved", [("mv", MV, "custom_components/x/mv.py")])):
            r = fresh(name)
            r.merge(1, PRODM); r.merge(2, MACH + extra); r.merge(3, RECM)
            outs.append(m12(r, r.tip, caps(w=3)))
        ok("null control: a pure move across the boundary leaves M1 and M2 identical",
           outs[0], outs[1])
        r = fresh("moved-edited")
        r.merge(1, PRODM)
        r.merge(2, MACH + [("mv", MV, "custom_components/x/mv.py"),
                           ("add", "custom_components/x/mv.py", 1)])
        r.merge(3, RECM)
        ok("...and the move with one line added counts that merge production",
           m12(r, r.tip, caps(w=3))[0], outs[0][0] - 1)
        ok("a rename's lines are charged to its destination",
           parse_numstat_z("1\t0\t\0tools/a\0custom_components/a\0"),
           [(1, 0, ["tools/a", "custom_components/a"], "custom_components/a")])

        r = fresh("reformat")
        r.merge(1, PRODM)
        before = r.tip
        r.change([("set", PROD, r.files[PROD].replace("\n", "  \n"))])
        r.merge(2, [("add", TOOLS, 1)])
        got = diff_stats(r.d, before, r.tip)
        ok("a whitespace-only reformat of product code costs 0 product lines",
           (got["product"], got["nonproduct"], got["kind"]), (0, 1, "machinery"))

        # 4. Splitting: a machinery merge in two raises M1 by exactly 1; a
        # production merge in two leaves M2 flat.
        r = fresh("whole")
        r.merge(1, PRODM); r.merge(2, [("add", TOOLS, 6)])
        whole = m12(r, r.tip, caps(w=2))
        r = fresh("split")
        r.merge(1, PRODM); r.merge(2, [("add", TOOLS, 3)]); r.merge(3, [("add", TOOLS, 3)])
        split = m12(r, r.tip, caps(w=3))
        ok("splitting a machinery merge raises M1 by exactly 1 and leaves M2 flat",
           (split[0] - whole[0], split[1]), (1, whole[1]))
        r = fresh("psplit")
        r.merge(1, [("add", PROD, 5), ("add", TOOLS, 2)])
        r.merge(2, [("add", PROD, 5), ("add", TOOLS, 2)]); r.merge(3, [("add", TOOLS, 6)])
        ok("splitting a production merge leaves M2 flat",
           m12(r, r.tip, caps(w=3))[1], whole[1])

        # 5. The exemption, on the candidate through the entry point. The base
        # window is at its cap, so an unexempted machinery candidate refuses.
        def pr_case(name: str, ent: dict | None, evidence: bool = True, pr: str = "9") -> int:
            r = fresh(name)
            r.merge(1, PRODM); r.merge(2, MACH); r.merge(3, PRODM)
            r.change(budgets_ops(caps(m1=2)))
            r.merge(4, [])
            base = r.tip
            ops = list(MACH)
            if ent is not None:
                ops += budgets_ops(caps(m1=2, ex=[ent]))
            if evidence:
                ops += [("set", "ev/proof.txt", "measured\n")]
            rc, _ = run_cli(r, "--check", "--base", base, "--head", r.side(ops), "--pr", pr)
            return rc

        ok("exemption: no entry refuses", pr_case("ex-none", None), 1)
        ok("exemption: exactly 10% refuses", pr_case("ex-10", entry(9, 100, 90)), 1)
        ok("exemption: exactly 10% as floats refuses", pr_case("ex-10f", entry(9, 1.0, 0.9)), 1)
        ok("exemption: 11% with evidence passes", pr_case("ex-11", entry(9)), 0)
        ok("exemption: 11% right-first-time (a gain) passes",
           pr_case("ex-rft", entry(9, 100, 111, "right_first_time")), 0)
        ok("exemption: 11% with a missing evidence path refuses",
           pr_case("ex-noev", entry(9), evidence=False), 1)
        ok("exemption: an entry naming another pull request refuses",
           pr_case("ex-other", entry(8)), 1)
        ok("exemption: an unknown measure refuses",
           pr_case("ex-measure", entry(9, measure_="vibes")), 1)
        ok("improvement() is exact: 100 -> 90 is 1/10", improvement(entry(9, 100, 90)), Fraction(1, 10))

        # Merged merges, in push mode: an entry its own merge added exempts it
        # (the positive control), one appended later exempts nothing.
        def exempted_history(name: str, late: list, own: bool = False, pre: bool = False) -> tuple:
            r = fresh(name)
            r.change([("set", "ev/proof.txt", "measured\n")])
            r.merge(10, PRODM); r.merge(11, PRODM); r.merge(1, PRODM); r.merge(2, PRODM)
            doc = caps(w=5, ex=[entry(3)] if own else [])
            r.merge(3, MACH + (budgets_ops(doc) if own else []))
            r.merge(4, MACH)
            if pre:  # #5 adds an entry for a future #6; #6 then touches the file
                doc = caps(w=5, ex=doc[EXEMPTIONS_KEY] + [entry(6)])
                r.merge(5, MACH + budgets_ops(doc))
                doc = {**doc, "_comment": "touched by #6"}
                r.merge(6, PRODM + budgets_ops(doc))
            late_ops = budgets_ops(caps(w=5, ex=doc[EXEMPTIONS_KEY] + [entry(p) for p in late]))
            r.merge(7, MACH + (late_ops if late else []))
            return m12(r, r.tip, caps(w=5)), m12(r, r.tip, caps(w=5), honour=False)

        honoured, ignored = exempted_history("ex-own", [], own=True)
        ok("positive control: an entry its own merge added takes that merge out of the window",
           honoured != ignored, True)
        honoured, ignored = exempted_history("ex-late", [3])
        ok("an entry appended later for an already-merged PR leaves M1 and M2 unchanged",
           honoured, ignored)
        honoured, ignored = exempted_history("ex-batch", [3, 4])
        ok("one merge appending entries for two merged PRs leaves M1 and M2 unchanged",
           honoured, ignored)
        honoured, ignored = exempted_history("ex-pre", [], pre=True)
        ok("an entry added before its PR merged exempts nothing when that PR merges",
           honoured, ignored)

        # The budgets file: a key the ratchet does not read is refused.
        good = caps()
        ok("load_budgets reads the fixture's caps", load_budgets(json.dumps(good))[WINDOW_KEY], 4)
        for label, bad in (("an unread key", {**good, "open_groups": 3}),
                           ("a float cap", {**good, "nonproduction_merges": 1.5}),
                           ("a missing band", {k: v for k, v in good.items()
                                               if k != "nonproduction_merges_band"}),
                           ("a zero window", {**good, WINDOW_KEY: 0}),
                           ("exemptions not a list", {**good, EXEMPTIONS_KEY: {}})):
            try:
                load_budgets(json.dumps(bad))
                got = "read"
            except Refusal:
                got = "refused"
            ok(f"load_budgets refuses {label}", got, "refused")

    ok("--check-event: a base and a PR number select PR mode",
       event_args({"MACHINERY_BASE": "b", "MACHINERY_HEAD": "h", "MACHINERY_PR": "7"}), ("h", "b", 7))
    ok("--check-event: a base with no PR number is push mode at the head",
       event_args({"MACHINERY_BASE": "b", "MACHINERY_HEAD": "h", "MACHINERY_PR": ""}), ("h", None, None))
    ok("--check-event: nothing set is push mode at HEAD", event_args({}), ("HEAD", None, None))

    print(f"machinery_ratchet self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--check", action="store_true", help="grade the window; exit 1 past a cap")
    ap.add_argument("--check-event", action="store_true",
                    help="--check with base, head and PR number from MACHINERY_BASE/_HEAD/_PR (governance.yml)")
    ap.add_argument("--measure", action="store_true", help="print the metrics and, with --bands, each band")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--base", help="PR mode: the base the candidate merges into")
    ap.add_argument("--pr", default="", help="PR mode: the candidate's pull-request number")
    ap.add_argument("--window", type=int, default=0, metavar="W",
                    help="with --measure: W in place of the budgets file's, for a tree that has none")
    ap.add_argument("--bands", type=int, default=0, metavar="N",
                    help="with --measure: the band over the newest N window positions")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    pr = int(a.pr) if a.pr.strip() else None
    try:
        if a.check_event:
            return check(a.repo, *event_args(os.environ))
        if a.check:
            return check(a.repo, a.head, a.base, pr)
        if a.measure:
            doc = ({WINDOW_KEY: a.window} if a.window
                   else load_budgets(_budgets_text(a.repo, a.head, BUDGETS)))
            m, _, skipped = measure(a.repo, a.head, doc, a.base, pr)
            print(json.dumps({"head": _git(a.repo, "rev-parse", a.head).stdout.strip(), **m,
                              "exempted": [s["sha"] for s in skipped]}, sort_keys=True))
            if a.bands:
                print(json.dumps({"positions": a.bands,
                                  **bands(a.repo, a.head, doc[WINDOW_KEY], a.bands)}, sort_keys=True))
            return 0
    except Refusal as e:
        print(f"machinery_ratchet: {e}", file=sys.stderr)
        return 2
    ap.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
