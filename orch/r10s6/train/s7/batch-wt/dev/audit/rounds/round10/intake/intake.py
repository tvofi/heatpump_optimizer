"""Audit intake by file, not by agent reply: the mechanical half of
.claude/workflows/audit-find.js's `from: "intake"` pass.

Round 10's agent gatherer failed twice: 45 reports do not fit through one
reply. This reads each box's evidence branch with `git show`, so nothing is
summarised on the way in.

What it does, in the workflow's order:
  1. gather   reports-<box>.json from every box branch; checks each dispatched
              seat (scopes.json, the round's active dimensions) has a report and
              a seat directory on its box branch. Prints the seat count and
              STOPS (exit 2) naming the missing seats when it is short.
  2. reject   the driver's three checks (scope is the seat, id numbered under it,
              class_guess a ledger id or "new"), then each finding validated
              against dev/audit/config/finding.schema.json's finding definition;
              a failure is rejected with the validator's message, never repaired.
  3. leads    every lead any seat raised, grouped by owner seat (--leads-out).
  4. ledger   rotation.json rounds[<round>] exactly as audit-find.js computes it
              (coverage = deepest depth any seat reports per step; returned =
              findings past the driver's checks; leads raised/converted).
Optional inputs fold the later phases in: --leads-result (the leads seat's
JSON), --quiet (quiet.tsv from quiet.sh plus --d3-map finding=mutant[,mutant]),
--extra (seat reports that came in outside the boxes, with --rekey old=new).
Optional outputs: --json, --write-rotation <path>, --write-register <path>.

Run from a checkout whose origin has the box branches:
  python3 dev/audit/rounds/round10/intake/intake.py --repo . --round 10 \
      --baseline 17f1c55fad1b [--config-ref origin/main] [--json out.json]
Needs jsonschema (pip install jsonschema into a venv). Exit 0 on a complete
gather, 2 when seats are missing, 1 on a usage or git error.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import OrderedDict

DIMS = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15"]
# audit-find.js DISPATCH block, copied: which dimensions a round runs.
CADENCE = {"D0": 1, "D1": 1, "D2": 1, "D3": 1, "D4": 1, "D7": 1, "D8": 1, "D9": 1, "D10": 1,
           "D12": 1, "D14": 1, "D15": 1, "D5": 2, "D6": 2, "D11": 3, "D13": 3}
EVERY_DIM_ROUNDS = {9, 10}
BOXES = [f"B{i}" for i in range(1, 12)]  # B11: D15, run as its own box in round 10
RANK = {"none": 0, "spot": 1, "deep": 2}


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(args)}: rc {p.returncode}: {p.stderr.strip()}")
    return p


def show_json(repo, ref, path):
    p = git(repo, "show", f"{ref}:{path}", check=False)
    return json.loads(p.stdout) if p.returncode == 0 else None


def active(rnd, dim):
    return dim in CADENCE and (rnd in EVERY_DIM_ROUNDS or rnd % CADENCE[dim] == 0)


def seats_from_scopes(scopes, dim):
    d = scopes[dim]
    out = []
    for key, blocks in d["seats"].items():
        named = {m for b in blocks for m in b.get("steps", [])}
        out.append({"id": f"{dim}-{key}", "dim": dim, "key": key,
                    "steps": [m for m in d.get("steps", []) if m in named]})
    return out


def finding_validator(schema):
    import jsonschema
    sub = {"$schema": schema.get("$schema"), "definitions": schema["definitions"],
           "$ref": "#/definitions/finding"}
    cls = jsonschema.validators.validator_for(sub)
    return cls(sub), cls(schema)


def schema_errors(validator, obj):
    errs = sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))
    return ["/".join(str(x) for x in e.absolute_path) + ": " + e.message[:200] for e in errs]


def dump_inline_scalars(obj, ind=0):
    """json.dumps(indent=2), but a list of scalars stays on one line -- the
    hand-kept layout of rotation.json, so a round entry adds lines only."""
    pad, sub = "  " * ind, "  " * (ind + 1)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = [f"{sub}{json.dumps(k, ensure_ascii=False)}: {dump_inline_scalars(v, ind + 1)}" for k, v in obj.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(obj, list):
        if all(not isinstance(x, (dict, list)) for x in obj):
            return json.dumps(obj, ensure_ascii=False, separators=(", ", ": "))
        return "[\n" + ",\n".join(sub + dump_inline_scalars(x, ind + 1) for x in obj) + "\n" + pad + "]"
    return json.dumps(obj, ensure_ascii=False)


def driver_reasons(f, seat_id, class_ids):
    why = []
    if f.get("scope") != seat_id:
        why.append(f"scope {json.dumps(f.get('scope'))} is not the seat that returned it ({seat_id})")
    if not (isinstance(f.get("id"), str) and f["id"].startswith(f"{seat_id}-")):
        why.append(f"id {json.dumps(f.get('id'))} is not numbered under {seat_id}")
    if str(f.get("class_guess", "")) not in class_ids:
        why.append(f"class_guess {json.dumps(f.get('class_guess'))} is neither a ledger id nor \"new\"")
    return why


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--config-ref", default="origin/main", help="ref holding scopes/rotation/schema")
    ap.add_argument("--branch", default="origin/handoff/audit-r{round}-find-{box}")
    ap.add_argument("--reports-override", help="{seat id: report} replacing gathered reports (normalise.py output)")
    ap.add_argument("--defer", default="", help="comma-separated seat ids deferred to a catch-up batch")
    ap.add_argument("--leads-out", help="write the grouped leads JSON here")
    ap.add_argument("--leads-result", help="the leads seat's JSON {findings, converted, closed, ...}")
    ap.add_argument("--leads-routed", help="the --leads-out file the leads seat was given; leads absent from it are marked not routed")
    ap.add_argument("--quiet", help="quiet.tsv from quiet.sh")
    ap.add_argument("--d3-map", default="", help="finding=mutant[+mutant],... for the quiet window")
    ap.add_argument("--extra", action="append", default=[],
                    help="LABEL=path.json: a seat report that came in outside the boxes")
    ap.add_argument("--extra-source", action="append", default=[], help="LABEL=text cited for an extra report")
    ap.add_argument("--rekey", default="", help="old=new,... id remaps for extra reports")
    ap.add_argument("--json", help="write the full intake result here")
    ap.add_argument("--write-rotation", help="rotation.json to set rounds[<round>] in")
    ap.add_argument("--write-register", help="register .md to (re)write the '## Round <N>' section of")
    ap.add_argument("--register-date", default="", help="date stamped in the section heading")
    ap.add_argument("--register-preamble", default="", help="file whose text opens the section, after the heading")
    ap.add_argument("--quiet-print", action="store_true", help="print the summary only")
    a = ap.parse_args()

    rnd, repo = a.round, a.repo
    root = f"dev/audit/rounds/round{rnd}"
    scopes = show_json(repo, a.config_ref, "dev/audit/config/scopes.json")
    rotation = show_json(repo, a.config_ref, "dev/audit/config/rotation.json")
    schema = show_json(repo, a.config_ref, "dev/audit/config/finding.schema.json")
    if not (scopes and rotation and schema):
        print(f"cannot read scopes/rotation/schema at {a.config_ref}", file=sys.stderr)
        return 1
    class_ids = set(schema["definitions"]["finding"]["properties"]["class_guess"]["enum"])
    fval, rval = finding_validator(schema)
    defer = [x for x in a.defer.split(",") if x]

    act = [d for d in DIMS if active(rnd, d)]
    seats = [s for d in act for s in seats_from_scopes(scopes, d)]
    seat_by_id = {s["id"]: s for s in seats}

    # 1. gather
    reports, box_of, seat_dir_files, box_info = {}, {}, {}, {}
    for b in BOXES:
        ref = a.branch.format(round=rnd, box=b)
        sha = git(repo, "rev-parse", "--short=12", ref, check=False)
        doc = show_json(repo, ref, f"{root}/reports-{b}.json")
        box_info[b] = {"ref": ref, "sha": sha.stdout.strip() if sha.returncode == 0 else None,
                       "present": doc is not None, "missing": (doc or {}).get("missing", [])}
        if doc is None:
            continue
        for sid, rep in (doc.get("reports") or {}).items():
            if sid in reports:
                print(f"WARNING {sid} reported in both {box_of[sid]} and {b}; keeping {box_of[sid]}")
                continue
            reports[sid], box_of[sid] = rep, b
            dim, key = sid.split("-")
            ls = git(repo, "ls-tree", "-r", "--name-only", ref, f"{root}/{dim}/{key}/", check=False)
            seat_dir_files[sid] = [x for x in ls.stdout.split("\n") if x]
    if a.reports_override:
        ov = json.load(open(a.reports_override))
        for sid, rep in ov.items():
            if sid in reports:
                reports[sid] = rep
        print(f"reports overridden from {a.reports_override}: {len([x for x in ov if x in reports])} seat(s)")
    missing = [s["id"] for s in seats if s["id"] not in reports and s["id"] not in defer]
    nodir = [sid for sid in reports if sid in seat_by_id and not seat_dir_files.get(sid)]
    stray = [sid for sid in reports if sid not in seat_by_id]
    print(f"round {rnd} intake: {len(act)} active dimension(s), {len(seats)} dispatched seat(s)")
    for b in BOXES:
        i = box_info[b]
        print(f"  box {b:<3} {i['ref']} @ {i['sha']}  reports-{b}.json "
              f"{'present' if i['present'] else 'ABSENT'}  collector-missing={i['missing']}")
    print(f"SEATS FOUND: {len([s for s in seats if s['id'] in reports])} of {len(seats)}")
    if stray:
        print(f"  reports for seats scopes.json does not dispatch: {stray}")
    if nodir:
        print(f"  seats with a report but no seat directory on their box branch: {nodir}")
    if missing:
        print(f"MISSING SEATS: {', '.join(missing)} -- intake refused")
        if a.json:
            json.dump({"missing": missing}, open(a.json, "w"), indent=2)
        return 2

    # 2. reject
    accepted, rejected, per_seat = [], [], OrderedDict()
    for s in seats:
        sid = s["id"]
        if sid not in reports:
            continue
        rep = reports[sid]
        rerrs = [e for e in schema_errors(rval, rep) if not e.startswith("findings/")]
        row = {"box": box_of[sid], "baseline_sha": rep.get("baseline_sha"), "report_path": rep.get("report_path"),
               "seat_dir_files": len(seat_dir_files.get(sid, [])),
               "report_md": f"{root}/{s['dim']}/{s['key']}/REPORT.md" in seat_dir_files.get(sid, []),
               "accepted": [], "rejected": [], "report_schema_errors": rerrs,
               "coverage": [(c.get("step"), c.get("depth")) for c in rep.get("coverage", [])],
               "unfinished": [(u.get("step"), u.get("what", "")) for u in rep.get("unfinished", [])],
               "leads": rep.get("leads", []), "non_findings": len(rep.get("non_findings", []))}
        for f in rep.get("findings", []) or []:
            why = driver_reasons(f, sid, class_ids)
            serr = schema_errors(fval, f)
            if why:
                rejected.append({"id": f.get("id", f"{sid}-?"), "seat": sid, "stage": "driver", "title": f.get("title"),
                                 "reason": "; ".join(why + serr)})
                row["rejected"].append(rejected[-1])
            elif serr:
                rejected.append({"id": f["id"], "seat": sid, "stage": "schema", "title": f.get("title"), "reason": "; ".join(serr)})
                row["rejected"].append(rejected[-1])
            else:
                accepted.append(dict(f, seat=sid))
                row["accepted"].append(f["id"])
        # driver-only count, for the ledger's `returned` (audit-find.js counts before step 1)
        row["driver_ok"] = sum(1 for f in rep.get("findings", []) or [] if not driver_reasons(f, sid, class_ids))
        per_seat[sid] = row

    # 3. leads
    leads = [dict(l, raised_by=sid) for sid in per_seat for l in per_seat[sid]["leads"]]
    by_owner = OrderedDict()
    for l in leads:
        by_owner.setdefault(l.get("owner_seat", "unknown"), []).append(l)
    if a.leads_out:
        json.dump({"by_owner": by_owner,
                   "report_paths": {sid: (f"{box_info[box_of[sid]]['ref']}:" + (per_seat[sid]['report_path'] or ""))
                                    for sid in per_seat}},
                  open(a.leads_out, "w"), indent=2)

    converted, closed, lead_findings = [], [], []
    if a.leads_result:
        lr = json.load(open(a.leads_result))
        converted, closed = lr.get("converted", []), lr.get("closed", [])
        for f in lr.get("findings", []):
            owner = f.get("scope")
            why = []
            if owner not in seat_by_id or not str(f.get("id", "")).startswith(f"{owner}-") \
                    or str(f.get("class_guess", "")) not in class_ids:
                why.append("a converted lead must carry an owner seat as scope, an id under it, and a class_guess;"
                           f" got scope {json.dumps(owner)} id {json.dumps(f.get('id'))}")
            why += schema_errors(fval, f)
            if why:
                rejected.append({"id": f.get("id", "leads-?"), "seat": "leads", "stage": "leads", "title": f.get("title"), "reason": "; ".join(why)})
            else:
                accepted.append(dict(f, seat=owner, from_lead=True))
                lead_findings.append(f["id"])

    # D3 quiet window: a D3 finding stays only if every mutant it rests on survived the full gate
    quiet_rows, d3_rejected = [], []
    if a.quiet:
        lines = [l.rstrip("\n").split("\t") for l in open(a.quiet) if l.strip()]
        hdr, rows = lines[0], lines[1:]
        qd = {r[0]: dict(zip(hdr, r)) for r in rows}
        null_failed = set(filter(None, qd.get("NULL", {}).get("failed", "").split(";")))
        fmap = {}
        for kv in filter(None, a.d3_map.split(",")):
            k, v = kv.split("=")
            fmap[k] = v.split("+")
        for fid, muts in fmap.items():
            for m in muts:
                r = qd.get(m)
                if r is None:
                    quiet_rows.append({"mutant": m, "finding_id": fid, "survived": None, "killed_by": "not run",
                                       "load1": None})
                    continue
                failed = set(filter(None, r.get("failed", "").split(";")))
                kills = sorted(failed - null_failed)
                quiet_rows.append({"mutant": m, "finding_id": fid, "survived": not kills, "killed_by": kills,
                                   "rc": r.get("rc"), "load1": f"{r.get('load1_start')}/{r.get('load1_end')}",
                                   "seconds": r.get("seconds"), "null_red": sorted(failed & null_failed)})
        for fid in fmap:
            rs = [q for q in quiet_rows if q["finding_id"] == fid]
            if any(q["survived"] is False for q in rs):
                kills = sorted({k for q in rs for k in (q["killed_by"] or []) if isinstance(q["killed_by"], list)})
                d3_rejected.append(fid)
                note = f"mutant killed by the full gate: {', '.join(kills)}"
                prior = next((x for x in rejected if x["id"] == fid), None)
                if prior:
                    prior["reason"] += f"; quiet window: {note}"
                else:
                    t = next((f.get("title") for sid in per_seat for f in reports[sid].get("findings", []) if f.get("id") == fid), "")
                    rejected.append({"id": fid, "seat": fid.rsplit("-", 1)[0], "stage": "quiet window", "title": t,
                                     "reason": note})
        accepted = [f for f in accepted if f["id"] not in d3_rejected]

    # extras: reports outside the boxes, re-keyed, validated, kept apart from the ledger
    extras = []
    remap = dict(kv.split("=") for kv in filter(None, a.rekey.split(",")))
    sources = dict(kv.split("=", 1) for kv in a.extra_source)
    for spec in a.extra:
        label, path = spec.split("=", 1)
        rep = json.load(open(path))
        for f in rep.get("findings", []):
            orig = f.get("id")
            g = dict(f)
            g["id"] = remap.get(orig, orig)
            m = re.match(r"^(D\d+-s\d+)-\d\d$", g["id"])
            if m:
                g["scope"] = m.group(1)
            if not re.match(r"^D(1[0-4]|[0-9])\.M[0-9]+$", str(g.get("step", ""))):
                g["step"] = g["id"].split("-")[0] + ".M1"
            why = driver_reasons(g, g.get("scope"), class_ids) + schema_errors(fval, g)
            extras.append({"label": label, "source": sources.get(label, path), "orig_id": orig, "id": g["id"],
                           "scope": g.get("scope"), "step": g.get("step"), "severity": g.get("severity"),
                           "class_guess": g.get("class_guess"), "title": g.get("title"),
                           "schema_ok": not why, "schema_errors": why})

    # 4. ledger -- audit-find.js's ledgerRound, field for field
    ledger = OrderedDict()
    for d in act:
        mine = [s for s in seats if s["dim"] == d]
        cov = {}
        for m in rotation[d]["steps"]:
            seen = [c[1] for s in mine for c in per_seat.get(s["id"], {}).get("coverage", [])
                    if c[0] in (f"{d}.{m}", m)]
            best = "none"
            for x in seen:
                if RANK.get(x, -1) > RANK[best]:
                    best = x
            cov[m] = best
        unf = [{"step": str(u[0]).replace(f"{d}.", ""), "what": u[1]}
               for s in mine for u in per_seat.get(s["id"], {}).get("unfinished", [])]
        returned = {s["key"]: per_seat.get(s["id"], {}).get("driver_ok", 0) for s in mine}
        raised = [l for l in leads if l["raised_by"].startswith(f"{d}-")]
        conv = [c for c in converted if str(c.get("raised_by", "")).startswith(f"{d}-")]
        ledger[d] = {"seats": [s["steps"] for s in mine], "coverage": cov, "unfinished": unf,
                     "returned": returned, "leads": {"raised": len(raised), "converted": len(conv)}}

    # print
    print()
    for sid, r in per_seat.items():
        print(f"== {sid} ({r['box']}, baseline {r['baseline_sha']}) accepted {len(r['accepted'])} rejected {len(r['rejected'])} "
              f"non-findings {r['non_findings']} seat-dir files {r['seat_dir_files']} "
              f"REPORT.md {'yes' if r['report_md'] else 'NO'}")
        for x in r["rejected"]:
            print(f"   REJECTED {x['id']} [{x['stage']}]: {x['reason']}")
        if r["report_schema_errors"] and not a.quiet_print:
            print(f"   report-level schema: {'; '.join(r['report_schema_errors'])[:400]}")
        print(f"   coverage: {', '.join(f'{st}={dp}' for st, dp in r['coverage']) or '(none)'}")
        for st, w in r["unfinished"]:
            print(f"   unfinished {st}: {w[:160]}")
        for l in r["leads"]:
            print(f"   lead -> {l.get('owner_seat')}: {l.get('file')} :: {l.get('symbol')}")
    print()
    print("per dimension: accepted / rejected / leads raised / converted")
    for d in act:
        acc = [f for f in accepted if f["seat"].startswith(f"{d}-")]
        rej = [x for x in rejected if str(x["seat"]).startswith(f"{d}-")]
        print(f"  {d:<4} {len(acc):>2} / {len(rej):>2} / {ledger[d]['leads']['raised']:>2} / {ledger[d]['leads']['converted']}")
    print(f"TOTAL accepted {len(accepted)} (from leads {len(lead_findings)}), rejected {len(rejected)}, "
          f"leads raised {len(leads)}, converted {len(converted)}, closed {len(closed)}")
    if quiet_rows:
        print("D3 quiet window:")
        for q in quiet_rows:
            print(f"  {q['mutant']} {q['finding_id']} survived={q['survived']} killed_by={q['killed_by']} load1={q['load1']}")
    for e in extras:
        print(f"  extra {e['label']}: {e['orig_id']} -> {e['id']} schema {'ok' if e['schema_ok'] else 'FAILS: ' + '; '.join(e['schema_errors'])[:300]}")

    provisional = [f["id"] for f in accepted
                   if f.get("provisional") or (f.get("evidence") or {}).get("cpu_or_wall") in ("cpu", "wall")]
    result = {"round": rnd, "baseline": a.baseline, "boxes": box_info, "seats": len(seats),
              "missing": missing, "per_seat": per_seat, "accepted": accepted, "rejected": rejected,
              "leads": leads, "leads_by_owner": by_owner, "converted": converted, "closed": closed,
              "quiet": quiet_rows, "extras": extras, "provisional": provisional, "ledger_round": ledger}
    if a.leads_routed:
        routed = json.load(open(a.leads_routed))["by_owner"]
        keys = {(l["raised_by"], l.get("file"), l.get("symbol")) for ls in routed.values() for l in ls}
        for l in leads:
            l["routed"] = (l["raised_by"], l.get("file"), l.get("symbol")) in keys
    if a.json:
        json.dump(result, open(a.json, "w"), indent=2)
    if a.write_rotation:
        rot = json.load(open(a.write_rotation), object_pairs_hook=OrderedDict)
        for d in act:
            rot[d].setdefault("rounds", OrderedDict())[str(rnd)] = json.loads(json.dumps(ledger[d], sort_keys=True))
        with open(a.write_rotation, "w") as fh:
            fh.write(dump_inline_scalars(rot) + "\n")
        print(f"wrote rounds[{rnd}] for {len(act)} dimension(s) into {a.write_rotation}")
    if a.write_register:
        text = open(a.write_register).read()
        pre = open(a.register_preamble).read().strip() if a.register_preamble else ""
        sec = register_section(result, act, a.register_date, pre)
        head = f"## Round {rnd} "
        i = text.find("\n" + head)
        if i >= 0:
            j = text.find("\n## ", i + 1)
            text = text[:i + 1] + sec + (text[j + 1:] if j >= 0 else "")
        else:
            text = text.rstrip("\n") + "\n\n" + sec
        open(a.write_register, "w").write(text)
        print(f"wrote the Round {rnd} section into {a.write_register}")
    return 0


def _cell(x):
    return str(x if x is not None else "").replace("|", "\\|").replace("\n", " ")


def register_section(r, act, date, preamble):
    rnd, out = r["round"], []
    acc, rej = r["accepted"], r["rejected"]
    out.append(f"## Round {rnd} — baseline `{r['baseline'][:8]}`{', ' + date if date else ''}\n")
    if preamble:
        out.append(preamble + "\n")
    out.append(f"### Findings register — round {rnd}\n")
    out.append("Intake registers; it does not merge, cluster or deduplicate. Status `reported` "
               "until verification. Every row's evidence is its seat's report under "
               f"`dev/audit/rounds/round{rnd}/D<k>/s<n>/` and `reports-<box>.json`.\n")
    out.append("#### Dimension status\n")
    out.append("| dim | seats reported | baseline | findings returned by its seats | accepted (incl. converted leads it owns) | rejected at intake | leads its seats raised | of those, converted |")
    out.append("|---|---|---|---|---|---|---|---|")
    for d in act:
        seats = [sid for sid in r["per_seat"] if sid.startswith(f"{d}-")]
        ret = sum(len(r["per_seat"][sid]["accepted"]) + len(r["per_seat"][sid]["rejected"]) for sid in seats)
        a_ = len([f for f in acc if f["seat"].startswith(f"{d}-")])
        j_ = len([x for x in rej if str(x["seat"]).startswith(f"{d}-")])
        lr = r["ledger_round"][d]["leads"]
        bl = ", ".join(sorted({str(r["per_seat"][sid].get("baseline_sha"))[:12] for sid in seats}))
        out.append(f"| {d} | {len(seats)} of {len(r['ledger_round'][d]['seats'])} | `{bl}` | {ret} | {a_} | {j_} | {lr['raised']} | {lr['converted']} |")
    out.append("")
    prov = set(r["provisional"])
    for d in act:
        rows = [f for f in acc if f["seat"].startswith(f"{d}-")]
        if not rows:
            continue
        out.append(f"#### {d}\n")
        out.append("| id | scope | step | severity | class_guess | title | status | provisional |")
        out.append("|---|---|---|---|---|---|---|---|")
        for f in rows:
            out.append(f"| {f['id']}{' (lead)' if f.get('from_lead') else ''} | {f.get('scope')} | {f.get('step')} | "
                       f"{f.get('severity')} | {f.get('class_guess')} | {_cell(f.get('title'))} | reported | "
                       f"{'yes' if f['id'] in prov else 'no'} |")
        out.append("")
    if rej:
        out.append("### Rejected at intake\n")
        out.append("A rejected finding is not repaired beyond the form rules of `NORMALISE.md`; its seat's report keeps the full text. "
                   "`schema` = fails `dev/audit/config/finding.schema.json`'s finding definition (the validator's "
                   "messages, cut at 200 characters each); `driver` = audit-find.js's three checks; "
                   "`quiet window` = its mutant was killed by the full gate.\n")
        out.append("| id | seat | stage | title | reason |")
        out.append("|---|---|---|---|---|")
        for x in rej:
            out.append(f"| {x['id']} | {x['seat']} | {x['stage']} | {_cell(x.get('title', ''))} | {_cell(x['reason'])} |")
        out.append("")
    out.append("### Leads\n")
    conv = {(c.get("raised_by"), c.get("file"), c.get("symbol")): c.get("finding_id") for c in r["converted"]}
    clos = {(c.get("raised_by"), c.get("file"), c.get("symbol")): c for c in r["closed"]}
    out.append("| raised by | owner seat | file | symbol | converted to / closed because |")
    out.append("|---|---|---|---|---|")
    for l in r["leads"]:
        k = (l["raised_by"], l.get("file"), l.get("symbol"))
        if k in conv:
            disp = f"converted to {conv[k]}"
        elif k in clos:
            c = clos[k]
            disp = f"closed{(' (owner ' + c['owner_seat'] + ')') if c.get('owner_seat') else ''}: {c.get('why', '')}"
        elif l.get("routed") is False:
            disp = "not routed: raised after the leads seat ran; open for the judge"
        else:
            disp = "unconverted (the leads seat returned no disposition)"
        out.append(f"| {l['raised_by']} | {l.get('owner_seat')} | `{_cell(l.get('file'))}` | {_cell(l.get('symbol'))} | {_cell(disp)} |")
    out.append("")
    if r["quiet"]:
        out.append("### D3 quiet window\n")
        out.append("| mutant | finding id | survived | killed_by | load1 (start/end) | gate seconds |")
        out.append("|---|---|---|---|---|---|")
        for q in r["quiet"]:
            kb = ", ".join(q["killed_by"]) if isinstance(q["killed_by"], list) else q["killed_by"]
            out.append(f"| {q['mutant']} | {q['finding_id']} | {q['survived']} | {_cell(kb) or '—'} | {q.get('load1')} | {q.get('seconds')} |")
        out.append("")
    if r["extras"]:
        out.append("### Extra seats outside the boxes\n")
        out.append("Reports that reached the round outside the ten boxes, re-keyed to the schema's id pattern "
                   "(mapping in the first two columns). They are not in the dimension counts above or in "
                   "rotation.json's round entry.\n")
        out.append("| source | original id | register id | step | severity | class_guess | title | schema | status |")
        out.append("|---|---|---|---|---|---|---|---|---|")
        for e in r["extras"]:
            sch = "ok" if e["schema_ok"] else "fails: " + "; ".join(e["schema_errors"])[:240]
            out.append(f"| {_cell(e['source'])} | {e['orig_id']} | {e['id']} | {e.get('step')} | {e.get('severity')} | "
                       f"{e.get('class_guess')} | {_cell(e.get('title'))} | {_cell(sch)} | reported |")
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


if __name__ == "__main__":
    sys.exit(main())
