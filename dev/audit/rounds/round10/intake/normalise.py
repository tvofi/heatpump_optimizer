"""Form-only normaliser for round-10 finder reports (orchestrator decision of
2026-10-15, under mandate: a finding is not lost to a form error the finder
prompt never stated -- audit-find.js's reportSchema carries none of these
enums or types).

It changes FORM, never a claim: every change keeps the original text in a
sibling `<field>_original` key (the schema does not forbid extra keys), and
anything a rule cannot settle is left as it was, so intake still rejects it.

Rules (each changed field records its rule id in NORMALISE.md):
  R1 expected_direction prose that OPENS with an enum word: that word;
     "down to 0" / "down to zero" -> to_zero.
  R2 otherwise the FIRST numeric transition in the prose ("A -> B", "A->B",
     "A → B", "from A to B"): B == 0 != A -> to_zero; A and B of opposite
     sign -> sign_flip; B < A -> down; B > A -> up.
  R2b otherwise an arrow to zero with no number before it ("delta_S -> 0",
     the finding's own non-zero value being the start): to_zero.
  R3 otherwise exactly one direction verb (rises/up/increases | falls/drops/
     down/decreases) in the prose: up | down. Two or none: unresolved.
  R4 a numeric string in evidence.load1/thread_factor -> that number.
  R5 a leading number followed only by a parenthetical remark -> the number;
     the remark is kept in `<field>_original`. A range ("19.98-25.98") is
     unresolved.
  R6 evidence.cpu_or_wall outside the enum: an enum value named in its
     parenthetical ("n/a (count)" -> count), else its leading token when that
     is an enum value ("cpu (process_time)" -> cpu).
  R7 evidence.tolerance given as a number -> its decimal string.
  R8 step "M<n>" -> "<dimension>.M<n>", the dimension taken from the id.
  R9 title over 120 / metric_definition over 200 characters -> cut at the
     last word boundary that fits, with a trailing ellipsis; the full text is
     kept in `<field>_original`.

Usage (repository root, origin holding the box branches):
  python3 dev/audit/rounds/round10/intake/normalise.py --repo . --round 10 \
      --out <dir> [--extra LABEL=path.json ...]
writes <dir>/normalised-reports.json ({seat id: report}), <dir>/extra-<LABEL>.json
and <dir>/NORMALISE.md. Exit 0.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import intake  # noqa: E402

ENUM_DIR = ["up", "down", "to_zero", "sign_flip"]
NUM = r"[-+]?\d+(?:\.\d+)?"
PAIR = re.compile(rf"(?:from\s+)?({NUM})\s*%?\s*(?:[a-zA-Z]{{0,3}}\s*)?(?:->|→|\bto\b)\s*({NUM})")
UPV = re.compile(r"\b(rises|rise|up|increases|increase|grows)\b", re.I)
DOWNV = re.compile(r"\b(falls|fall|drops|drop|down|decreases|decrease)\b", re.I)


def direction(prose):
    p = prose.strip()
    m = re.match(r"^(up|down|to_zero|sign_flip)\b", p, re.I)
    if m:
        w = m.group(1).lower()
        if w == "down" and re.match(r"^down\s+to\s+(0|zero)\b", p, re.I):
            return "to_zero", "R1"
        return w, "R1"
    m = PAIR.search(p)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        if b == 0 and a != 0:
            return "to_zero", "R2"
        if a * b < 0:
            return "sign_flip", "R2"
        if b < a:
            return "down", "R2"
        if b > a:
            return "up", "R2"
    if re.search(r"(?:->|→)\s*0(?:\.0+)?\b", p):
        return "to_zero", "R2b"
    u, d = bool(UPV.search(p)), bool(DOWNV.search(p))
    if u != d:
        return ("up" if u else "down"), "R3"
    return None, "unresolved: no leading enum word, no numeric transition, and not exactly one direction verb"


def number(v):
    if isinstance(v, (int, float)):
        return v, None
    s = str(v).strip()
    if re.fullmatch(NUM, s):
        return float(s), "R4"
    m = re.fullmatch(rf"({NUM})\s*\(.*\)", s)
    if m:
        return float(m.group(1)), "R5"
    return None, "unresolved: not a single number" + (" (a range)" if re.fullmatch(rf"{NUM}\s*-\s*{NUM}", s) else "")


def cut(text, n):
    if len(text) <= n:
        return text
    head = text[: n - 1]
    sp = head.rfind(" ")
    return (head[:sp] if sp > n // 2 else head).rstrip(" ,;:") + "…"


def normalise_finding(f, enum_cw, log, fid=None):
    fid = fid or f.get("id")
    dim = str(fid).split("-")[0]

    def rec(field, before, after, rule):
        log.append({"id": fid, "field": field, "before": before, "after": after, "rule": rule})

    p = f.get("perturbation")
    if isinstance(p, dict):
        ed = p.get("expected_direction", p.get("expect"))
        if ed is not None and ed not in ENUM_DIR:
            d, rule = direction(str(ed))
            if d:
                p["expected_direction_original"] = ed
                p["expected_direction"] = d
                rec("perturbation.expected_direction", ed, d, rule)
            else:
                rec("perturbation.expected_direction", ed, "(unchanged)", rule)
    ev = f.get("evidence")
    if isinstance(ev, dict):
        for k in ("load1", "thread_factor"):
            if k in ev and not isinstance(ev[k], (int, float)):
                v, rule = number(ev[k])
                if v is not None:
                    rec(f"evidence.{k}", ev[k], v, rule)
                    ev[f"{k}_original"], ev[k] = ev[k], v
                else:
                    rec(f"evidence.{k}", ev[k], "(unchanged)", rule)
        cw = ev.get("cpu_or_wall")
        if cw is not None and cw not in enum_cw:
            paren = re.findall(r"\(([^)]*)\)", str(cw))
            lead = str(cw).split()[0] if str(cw).split() else ""
            new = next((t.strip() for t in paren if t.strip() in enum_cw), None)
            new = new or (lead if lead in enum_cw else None)
            if new:
                rec("evidence.cpu_or_wall", cw, new, "R6")
                ev["cpu_or_wall_original"], ev["cpu_or_wall"] = cw, new
            else:
                rec("evidence.cpu_or_wall", cw, "(unchanged)", "unresolved: names no enum value")
        if isinstance(ev.get("tolerance"), (int, float)):
            rec("evidence.tolerance", ev["tolerance"], str(ev["tolerance"]), "R7")
            ev["tolerance"] = str(ev["tolerance"])
    st = f.get("step")
    if isinstance(st, str) and re.fullmatch(r"M\d+", st) and re.fullmatch(r"D\d+", dim):
        rec("step", st, f"{dim}.{st}", "R8")
        f["step_original"], f["step"] = st, f"{dim}.{st}"
    for k, n in (("title", 120), ("metric_definition", 200)):
        if isinstance(f.get(k), str) and len(f[k]) > n:
            new = cut(f[k], n)
            rec(k, f"({len(f[k])} chars)", f"({len(new)} chars) {new}", "R9")
            f[f"{k}_original"], f[k] = f[k], new
    return f


def normalise_report(rep, enum_cw, log):
    for c in rep.get("coverage", []) + rep.get("unfinished", []):
        st = c.get("step")
        if isinstance(st, str) and re.fullmatch(r"M\d+", st):
            c["step"] = f"{rep.get('dimension', '')}.{st}"
    for f in rep.get("findings", []):
        normalise_finding(f, enum_cw, log)
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--config-ref", default="origin/main")
    ap.add_argument("--branch", default="origin/handoff/audit-r{round}-find-{box}")
    ap.add_argument("--out", required=True)
    ap.add_argument("--extra", action="append", default=[])
    a = ap.parse_args()
    schema = intake.show_json(a.repo, a.config_ref, "dev/audit/config/finding.schema.json")
    enum_cw = schema["definitions"]["evidence"]["properties"]["cpu_or_wall"]["enum"]
    root = f"dev/audit/rounds/round{a.round}"
    log, out = [], {}
    for b in intake.BOXES:
        doc = intake.show_json(a.repo, a.branch.format(round=a.round, box=b), f"{root}/reports-{b}.json")
        for sid, rep in ((doc or {}).get("reports") or {}).items():
            out[sid] = normalise_report(rep, enum_cw, log)
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "normalised-reports.json"), "w"), indent=2)
    for spec in a.extra:
        label, path = spec.split("=", 1)
        rep = json.load(open(path))
        for f in rep.get("findings", []):
            normalise_finding(f, enum_cw, log, fid=f"{label}:{f.get('id')}")
        json.dump(rep, open(os.path.join(a.out, f"extra-{label}.json"), "w"), indent=2)
    rows = ["# Round 10 form normalisation", "",
            "Written by `dev/audit/rounds/round10/intake/normalise.py` (its docstring states rules R1-R9). "
            "Form only: no claim, number or command is changed; every changed field keeps its original in "
            "`<field>_original`. A row whose `after` is `(unchanged)` names why no rule applied; intake still "
            "rejects that finding.", "",
            "| id | field | before | after | rule |", "|---|---|---|---|---|"]
    esc = lambda s: str(s).replace("|", "\\|").replace("\n", " ")  # noqa: E731
    for r in log:
        rows.append(f"| {r['id']} | {r['field']} | {esc(r['before'])} | {esc(r['after'])} | {esc(r['rule'])} |")
    changed = sum(1 for r in log if r["after"] != "(unchanged)")
    rows += ["", f"{changed} field(s) changed, {len(log) - changed} left unresolved."]
    open(os.path.join(a.out, "NORMALISE.md"), "w").write("\n".join(rows) + "\n")
    print(f"normalised {len(out)} seat report(s); {changed} field(s) changed, {len(log) - changed} unresolved")
    for r in log:
        if r["after"] == "(unchanged)":
            print(f"  UNRESOLVED {r['id']} {r['field']}: {r['before']!r} -- {r['rule']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
