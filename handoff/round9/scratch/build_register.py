import json, collections

SCRATCH = "/tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad"
INTAKE = f"{SCRATCH}/intake"

def load(p):
    with open(p) as f:
        return json.load(f)

validated = load(f"{SCRATCH}/validated.json")
rejected = load(f"{SCRATCH}/rejected_at_intake.json")
reports = load(f"{INTAKE}/reports.json")
judge_flags = open(f"{INTAKE}/judge_flags.txt").read().rstrip("\n")

leads_files = {
    "L1": "leads_result.json",
    "L2": "leads_result_L2.json",
    "L3": "leads_result_L3.json",
    "L4": "leads_result_L4.json",
}
leads_data = {k: load(f"{INTAKE}/{v}") for k, v in leads_files.items()}

DIM_NAMES = {
    "D0": "Price optimality",
    "D1": "Robustness and stability",
    "D2": "Mathematical and physical sanity",
    "D3": "Test-suite gaps",
    "D4": "UI/UX",
    "D5": "Docs structure, flow and content; code comments",
    "D6": "README and documentation claim verification",
    "D7": "Architecture and maintainability",
    "D8": "Sensor verification and ordering",
    "D9": "CPU and memory efficiency, Raspberry-Pi-class target",
    "D10": "Home Assistant integration quality scale",
    "D11": "Governance mechanisms and policy",
    "D12": "Generalization",
    "D13": "Process yield and cost",
    "D14": "Recurring bug classes",
}

seats_by_dim = collections.defaultdict(set)
for seat in reports["reports"].keys():
    dim = seat.split("-s")[0]
    seats_by_dim[dim].add(seat)
seats_by_dim["D3"].add("D3-s2")  # catch-up, reported via handoff branch

valid_by_dim = collections.defaultdict(list)
for f in validated:
    dim = f["scope"].split("-s")[0]
    valid_by_dim[dim].append(f)

rejected_by_dim = collections.defaultdict(list)
for r in rejected:
    seat = r.get("seat", "?")
    dim = seat.split("-s")[0] if "-s" in seat else "?"
    rejected_by_dim[dim].append(r)

PROVISIONAL_IDS = {"D9-s1-71", "D9-s2-71"}

dims = [f"D{n}" for n in range(15)]

lines = []
lines.append("## Round 9 — intake, baseline `1936d5ca`, 2026-09-26")
lines.append("")
lines.append(
    "Intake for round 9, batch 1, done by hand from `.claude/workflows/audit-find.js`'s "
    "intake step. Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`. This section is the "
    "**intake register**: findings as reported by their finder and lead seats, validated "
    "against `tools/audit/finding.schema.json` and registered one row per finding. It does "
    "**not** merge, cluster, dedupe or verify — that is the judge's first step, which "
    "follows. `status` is `reported` for every row here; nothing has been judged yet."
)
lines.append("")
lines.append(
    "Inputs: 122 finder findings from 40 seats (`accepted.json`), 25 findings the leads "
    "seats converted (`lead_findings.json`, `from_lead: true`), and D3-s2's catch-up batch "
    "of 2 findings from `origin/handoff/audit-r9-find-B2:tools/audit/round9/reports-B2.json` "
    "(box B2). `rejected.json` and `lead_rejected.json` were both empty at hand-off; the "
    "rejections below are this intake's own schema check."
)
lines.append("")

# --- Dimension status table ---
lines.append("### Dimension status — round 9 intake")
lines.append("")
lines.append("| # | Dimension | Seats reported | Findings accepted | Rejected at intake |")
lines.append("|---|-----------|-----------------|--------------------|----------------------|")
total_seats = 0
total_accepted = 0
total_rejected = 0
for dim in dims:
    n = int(dim[1:])
    name = DIM_NAMES[dim]
    seats_n = len(seats_by_dim.get(dim, []))
    acc_n = len(valid_by_dim.get(dim, []))
    rej_n = len(rejected_by_dim.get(dim, []))
    total_seats += seats_n
    total_accepted += acc_n
    total_rejected += rej_n
    if dim == "D3":
        seats_cell = f"{seats_n} (D3-s2 catch-up); D3-s3 deferred (catch-up)"
    else:
        seats_cell = str(seats_n)
    lines.append(f"| {n} | {name} | {seats_cell} | {acc_n} | {rej_n} |")
lines.append(f"| | **Total** | **{total_seats}** | **{total_accepted}** | **{total_rejected}** |")
lines.append("")
lines.append(
    "Seats reported counts distinct finder seats in `reports.json` plus D3-s2 (reported on "
    "`origin/handoff/audit-r9-find-B2`, not in `reports.json`). D3-s3 has not reported and is "
    "listed separately; it is not counted in D3's seats-reported figure. Findings accepted and "
    "rejected at intake include both finder findings and the leads seats' converted findings, "
    "keyed by each finding's `scope`."
)
lines.append("")

# --- Rejected at intake ---
lines.append("### Rejected at intake")
lines.append("")
lines.append(
    f"{len(rejected)} findings failed validation against `tools/audit/finding.schema.json` "
    "(`#/definitions/finding`) and are rejected at intake, with the validator's message:"
)
lines.append("")
lines.append("| id | seat | source | validator message |")
lines.append("|---|---|---|---|")
for r in rejected:
    msgs = "; ".join(r["errors"])
    msgs = msgs.replace("|", "\\|")
    lines.append(f"| {r['id']} | {r['seat']} | {r['source']} | {msgs} |")
lines.append("")

# --- Per-dimension findings tables ---
lines.append("### Findings register — round 9 (intake, unjudged)")
lines.append("")
lines.append(
    "One table per dimension. Columns: id, scope, step, severity, class_guess, title, "
    "status, provisional. `status` is `reported` for every row: this is the intake register, "
    "before clustering, dedup or judge verification. No finding is provisional under the "
    "driver's rule, except D9-s1-71 and D9-s2-71 (both lead findings), marked provisional "
    "because their CPU ratios were taken on a shared box."
)
lines.append("")

def sort_key(f):
    return f["id"]

for dim in dims:
    items = valid_by_dim.get(dim, [])
    if not items:
        continue
    items = sorted(items, key=sort_key)
    lines.append(f"#### {dim} — {DIM_NAMES[dim]}")
    lines.append("")
    lines.append("| id | scope | step | severity | class_guess | title | status | provisional |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for f in items:
        title = f["title"].replace("|", "\\|")
        notes = []
        if f.get("from_lead"):
            notes.append(f"from lead ({f.get('leads_seat', '?')})")
        if f.get("catch_up_batch"):
            notes.append("catch-up batch")
        note_str = "; ".join(notes)
        if note_str:
            title = f"{title} *[{note_str}]*"
        provisional = "yes" if f["id"] in PROVISIONAL_IDS else ""
        lines.append(
            f"| {f['id']} | {f['scope']} | {f['step']} | {f['severity']} | "
            f"{f['class_guess']} | {title} | reported | {provisional} |"
        )
    lines.append("")

# --- D3 quiet-window note ---
lines.append(
    "**D3 findings rest on the seats' pre-screen evidence.** D3's method "
    "(`tools/audit/briefs/D3.md`) turns a pre-screened survivor into a finding only after "
    "the quiet-window `GATE_SCOPE=full GOLDEN_MODE=drift` gate confirms it; that quiet window "
    "was **not run** this round, by tvofi's rule of 2026-09-26 (no heavy D3 re-runs). D3-s1's "
    "and D3-s2's findings above are registered as reported on the strength of the pre-screen "
    "closures alone, and the judge inherits that gap rather than a re-measured one."
)
lines.append("")

# --- Leads table ---
lines.append("### Leads — round 9")
lines.append("")
lines.append(
    "What the finder seats noticed outside their own cells, routed to the four leads seats "
    "(L1-L4). A lead is **converted** into a finding only with an executed number (rows above, "
    "marked *from lead*), or **closed** with a reason. Taken from `leads_result.json`, "
    "`leads_result_L2.json`, `leads_result_L3.json` and `leads_result_L4.json`."
)
lines.append("")
lines.append("| raised by | owner seat | file | symbol | converted to / closed because |")
lines.append("|---|---|---|---|---|")
for lseat, data in leads_data.items():
    for c in data["converted"]:
        owner = c["finding_id"].rsplit("-", 1)[0]
        outside = " (outside L1's own dimension)" if c.get("outside_L1") else ""
        lines.append(
            f"| {c['raised_by']} | {owner} ({lseat}) | {c['file']} | {c['symbol']} | "
            f"converted to {c['finding_id']}{outside} |"
        )
    for cl in data["closed"]:
        why = cl["why"].replace("|", "\\|")
        lines.append(
            f"| {cl['raised_by']} | ({lseat}, closed) | {cl['file']} | {cl['symbol']} | "
            f"closed: {why} |"
        )
lines.append("")

# --- Judge flags ---
lines.append("### Judge flags")
lines.append("")
lines.append("Verbatim, `judge_flags.txt`:")
lines.append("")
lines.append("```")
lines.append(judge_flags)
lines.append("```")
lines.append("")

out = "\n".join(lines)
with open(f"{SCRATCH}/round9_section.md", "w") as f:
    f.write(out)

print("wrote", len(out), "bytes")
print("total_seats", total_seats, "total_accepted", total_accepted, "total_rejected", total_rejected)
