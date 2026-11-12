#!/usr/bin/env python3
"""Convergence scorecard: ten report-only lines, one per signal, each with its null control.

    python3 -I scorecard.py report --dir D --train-log PATH [--repo DIR] [--sweep-record PATH]
    python3 -I scorecard.py --self-test [--no-mutants]

Report-only (R10-MACH-SCORECARD): no line sets an exit code or holds a merge. It
is the baseline from which thresholds can later be set. Read-only on every
input and no GitHub call; the inputs are refreshed elsewhere and an input it
cannot read prints `<line>  unread (<why>)`, never a guessed value.

INPUTS, all under D (the beat's `<state>/scorecard/`) except the train log:
  runs.json      [{id, t, c}] main `CI` push runs: id, UTC stamp, run conclusion
  jobs/jobs_<id>.json   the run's job listing (`{"jobs": [{name, conclusion}]}`)
  verdicts.json  {"verdicts": [{pr, head, kind, cls, t}]} review verdicts
  merges.tsv     TSV with columns pr, ct, class, tokens (merge order by ct)
  roster.json    {"groups": [...]} the round's roster
  ../study/work/yield.py  holds `FAMILY = [(name, regex), ...]`, read as a
                 literal (never executed), the class-word to family map of M_first

THE LINES (rule, then the null control the self-test holds it to):
  A_gate   share of the last 20 concluded (success or failure) main runs whose
           job named `gate` concluded success; a run with no cached job listing
           is `unread`, reported and not guessed.
           NULL: a run whose only failed job is `governance / instrument-self-tests`
           counts green here and red in A_run.
  A_run    share of the same runs whose run conclusion is success.
           NULL: the same run counts red.
  Y_rev    over the last 50 pull requests by first verdict (the earliest verdict by `t`,
           whatever the order of verdicts.json): share whose first verdict is `merge`.
           NULL: a bus of merge verdicts only prints 100%.
  M_first  same 50: share whose first verdict is `blocked` in a machinery family
           (MACH: carry, body, CI state, merge state, root-cause form, ruling or roster).
           NULL: the same bus prints 0%.
  Y_train  over the last 50 merged pull requests the merge train named: share
           never on a `SKIP #n` or `PARK` line. A pull request the train never
           named is not counted.
           NULL: a log with no SKIP or PARK line prints 100%.
  H        hotfix-token merges among the last 50 code merges (class production
           or instrument), with the production merges among those 50 beside it.
           NO NULL CONTROL: it is a naming measure (a branch token), read with
           that caveat. The study's own text gives it none and none is invented.
  S        size: `machinery_ratchet.py --measure --head origin/main` (its JSON's
           non-production merges per window and churn per 1 000 product lines),
           and machinery lines over product lines from `git grep -c ''` over
           `tools .github .claude dev/governance` against `custom_components blueprints`.
           NULL: a frozen machinery gives a flat or falling ratio (the ratio
           of two unchanged counts is unchanged).
  E        escapes: roster groups whose source is `outside`, and hotfix or bug
           groups (group names HOTFIX, or kind bug|hotfix) whose files include
           the product (`custom_components/`); and how many of both are still
           open (resume.stage not `done`).
           NULL: a round with no escape adds none.
  C        detection delay: the longest run of consecutive cancelled main runs
           in the last 50 runs (cancelled runs included, ordered by stamp).
           NULL: C is 0 when no main run is cancelled.
  K        seat cost: `recycle` lines of the standing dispatch and triage seats
           in the day's sweep record.
           NULL: K is 0 with no recycle line.
C and K are one row of the study's table and print on one line.
"""
from __future__ import annotations

import argparse
import ast
import collections
import csv
import io
import json
import re
import subprocess
import sys
from pathlib import Path

WINDOW_RUNS = 20
WINDOW_PRS = 50
WINDOW_MERGES = 50
WINDOW_CANCEL = 50
MACH = {"carry-bookkeeping", "body-bookkeeping", "ci-state", "merge-state", "root-cause-form", "ruling-or-roster"}
RECYCLE = re.compile(r"\brecycle", re.I)
SEATS = re.compile(r"standing[- ](?:dispatch|triage)|\b(?:dispatch|triage)\b", re.I)


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.0f}%" if d else "n/a"


def family_of(cls: str, fam: list) -> str:
    for name, rx in fam:
        if re.match(rx, cls):
            return name
    return "unmapped"


def load_family(text: str) -> list:
    """FAMILY from yield.py's source, as a literal; nothing is executed."""
    i = text.index("FAMILY = [")
    j = text.index("def fam(", i)
    return ast.literal_eval(text[i:j].split("=", 1)[1].strip())


def line_a(runs: list, gate: dict) -> list[str]:
    ok = [r for r in sorted(runs, key=lambda r: r["t"]) if r["c"] in ("success", "failure")][-WINDOW_RUNS:]
    if not ok:
        return ["A_gate  unread (no concluded main run)", "A_run   unread (no concluded main run)"]
    g = collections.Counter("success" if r["c"] == "success" else gate.get(r["id"], "unread") for r in ok)
    read = g["success"] + g["failure"]
    run_ok = sum(r["c"] == "success" for r in ok)
    gate_part = f"{g['success']}/{read} read = {pct(g['success'], read)}" if read else "0/0 read"
    return [f"A_gate  {gate_part}  (unread {g['unread']} of {len(ok)}; window {ok[0]['t']} .. {ok[-1]['t']})",
            f"A_run   {run_ok}/{len(ok)} = {pct(run_ok, len(ok))}"]


def line_review(verdicts: list, fam: list | None) -> list[str]:
    first: dict = {}
    for v in sorted(verdicts, key=lambda v: v["t"]):  # the first verdict is the earliest by t, whatever the file order
        first.setdefault(v["pr"], v)
    last = list(first.values())[-WINDOW_PRS:]
    if not last:
        return ["Y_rev   unread (no verdict)", "M_first unread (no verdict)"]
    n = len(last)
    first_merge = sum(v["kind"] == "merge" for v in last)
    span = f"first verdicts {last[0]['t'][:16]} .. {last[-1]['t'][:16]}"
    y = f"Y_rev   first verdict merge {first_merge}/{n} = {pct(first_merge, n)}  ({span})"
    if fam is None:
        return [y, "M_first unread (no family map)"]
    mf = sum(v["kind"] == "blocked" and family_of(v["cls"], fam) in MACH for v in last)
    return [y, f"M_first {mf}/{n} = {pct(mf, n)}  ({span})"]


def line_train(merged: list[str], train_text: str) -> str:
    skipped, named = set(), set()
    for ln in train_text.splitlines():
        m = re.match(r"SKIP #(\d+)", ln)
        if m:
            skipped.add(m[1])
        if ln.startswith("PARK"):
            skipped |= set(re.findall(r"#(\d{4})", ln)[:1])
        if re.match(r"(BATCH|SKIP|PARK|MERGED|ADMIT|ALREADY)", ln):
            named |= set(re.findall(r"#(\d{4})", ln))
    tn = [p for p in merged if p in named][-WINDOW_MERGES:]
    clean = sum(p not in skipped for p in tn)
    return f"Y_train never skipped or parked {clean}/{len(tn)} = {pct(clean, len(tn))}  (last {WINDOW_MERGES} train-named merged PRs)"


def line_hotfix(rows: list[dict]) -> str:
    code = [r for r in rows if r["class"] in ("production", "instrument")][-WINDOW_MERGES:]
    hot = sum("hotfix" in r["tokens"] for r in code)
    prod = sum(r["class"] == "production" for r in code)
    return (f"H       hotfix-token merges {hot}/{len(code)} of the last {WINDOW_MERGES} code merges; "
            f"production merges among them {prod}  (naming measure, no null control)")


def line_escapes(groups: list[dict]) -> str:
    out = [x for x in groups if x.get("source") == "outside"]
    ph = [x for x in groups if ("HOTFIX" in x["group"] or x.get("kind") in ("bug", "hotfix"))
          and any(f.startswith("custom_components/") for f in (x.get("files") or []))]
    openn = sum((x.get("resume") or {}).get("stage") != "done" for x in out + ph)
    return (f"E       roster groups from outside reports {len(out)}; hotfix or bug groups touching the product "
            f"{len(ph)}; open among both {openn}")


def cancel_streak(runs: list) -> int:
    best = cur = 0
    for r in sorted(runs, key=lambda r: r["t"])[-WINDOW_CANCEL:]:
        cur = cur + 1 if r["c"] == "cancelled" else 0
        best = max(best, cur)
    return best


def recycle_count(record: str) -> int:
    return sum(bool(RECYCLE.search(ln) and SEATS.search(ln)) for ln in record.splitlines())


def line_ck(runs: list | None, record: str | None) -> str:
    c = f"C {cancel_streak(runs)}" if runs is not None else "C unread"
    k = f"K {recycle_count(record)}" if record is not None else "K unread"
    return f"C, K    {c}; {k}  (longest cancelled main-run streak; recycle lines of the dispatch and triage seats)"


def sh_out(argv: list[str], cwd: Path) -> tuple[int, str]:
    try:
        p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, str(e)
    return p.returncode, p.stdout


def count_lines(repo: Path, paths: list[str], run=sh_out) -> int | None:
    rc, out = run(["git", "grep", "-c", "", "origin/main", "--", *paths], repo)
    if rc not in (0, 1):
        return None
    return sum(int(ln.rsplit(":", 1)[1]) for ln in out.splitlines() if ":" in ln and ln.rsplit(":", 1)[1].isdigit())


def line_size(repo: Path, run=sh_out) -> list[str]:
    rc, out = run([sys.executable, "-I", "tools/audit/machinery_ratchet.py", "--measure", "--head", "origin/main"], repo)
    mach = count_lines(repo, ["tools", ".github", ".claude", "dev/governance"], run)
    prod = count_lines(repo, ["custom_components", "blueprints"], run)
    try:
        m = json.loads(out) if rc == 0 else None
        lines = [f"S       non-production merges {m['nonproduction_merges']} per {m['window']}; "
                 f"churn {m['churn_per_kilo_product_lines']} per 1 000 product lines"]
    except (ValueError, KeyError, TypeError):
        lines = ["S       ratchet unread"]
    if mach is None or not prod:
        lines.append("S       machinery/product unread")
    else:
        lines.append(f"S       machinery {mach} / product {prod} = {mach / prod:.2f}")
    return lines


def rd(path: Path):
    try:
        return path.read_text()
    except OSError:
        return None


def report(d: Path, train_log: Path, repo: Path | None, record: Path | None, run=sh_out) -> list[str]:
    out: list[str] = []

    def load(name):
        t = rd(d / name)
        try:
            return None if t is None else json.loads(t)
        except ValueError:
            return None

    runs = load("runs.json")
    gate: dict = {}
    for f in sorted((d / "jobs").glob("jobs_*.json")) if (d / "jobs").is_dir() else []:
        try:
            for j in json.loads(f.read_text()).get("jobs", []):
                if j["name"] == "gate":
                    gate[int(f.stem.split("_")[1])] = j["conclusion"]
        except (ValueError, KeyError, IndexError):
            continue
    out += line_a(runs, gate) if runs else ["A_gate  unread (runs.json)", "A_run   unread (runs.json)"]
    v = load("verdicts.json")
    ytxt = rd(d.parent / "study" / "work" / "yield.py")
    try:
        fam = load_family(ytxt) if ytxt else None
    except (ValueError, SyntaxError):
        fam = None
    out += line_review(v["verdicts"], fam) if v else ["Y_rev   unread (verdicts.json)", "M_first unread (verdicts.json)"]
    mt, tt = rd(d / "merges.tsv"), rd(train_log)
    rows = sorted(csv.DictReader(io.StringIO(mt), delimiter="\t"), key=lambda r: int(r["ct"])) if mt else None
    out.append(line_train([r["pr"] for r in rows if r["pr"]], tt) if rows is not None and tt is not None
               else "Y_train unread (merges.tsv or train log)")
    out.append(line_hotfix(rows) if rows is not None else "H       unread (merges.tsv)")
    out += line_size(repo, run) if repo else ["S       unread (no checkout)"]
    ro = load("roster.json")
    out.append(line_escapes(ro["groups"]) if ro else "E       unread (roster.json)")
    out.append(line_ck(runs, rd(record) if record else None))
    return out


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        import scorecard_selftest
        return scorecard_selftest.run(Path(__file__), mutants="--no-mutants" not in argv)
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("cmd", choices=["report"])
    ap.add_argument("--dir", required=True, type=Path)
    ap.add_argument("--train-log", required=True, type=Path)
    ap.add_argument("--repo", type=Path)
    ap.add_argument("--sweep-record", type=Path)
    a = ap.parse_args(argv)
    print("\n".join(report(a.dir, a.train_log, a.repo, a.sweep_record)))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main(sys.argv[1:]))
