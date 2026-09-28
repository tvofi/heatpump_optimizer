#!/usr/bin/env python3
"""Generate round-9 Phase E per-class issue drafts + INDEX.json.

Reads:
  /mnt/project-files/audit-r9/judge/CLASSES-DRAFT.json  (46 classes, final)
  /mnt/project-files/audit-r9/sweep/S1..S7.json          (final N, rca, instances, barrier)
Writes:
  <OUT>/<slug>.md  one per class
  <OUT>/INDEX.json
"""
import json, re, sys, os

JU = '/mnt/project-files/audit-r9/judge/'
SW = '/mnt/project-files/audit-r9/sweep/'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/audit-r9/issues'
BASELINE = '1936d5ca'
BASELINE_FULL = '1936d5ca72a06556eeed4e8e5bf3dea520e517e1'
JUDGE_JUDGE_JSON_COMMIT = '2f97b0a'
JUDGE_CLASSES_DRAFT_COMMIT = 'bad458a'

SEV_ORDER = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}

MANUAL_MAP = {
    'live input with no physical-plausibility bound': 'live-input-no-plausibility-bound',
    'production member reached by no production code': 'production-member-no-caller',
    'a sign floor on a price margin breaks the stated piecewise identity': 'sign-floor-price-margin',
    'an entity family whose names do not lead with a shared token splits under the name sort': 'entity-family-name-sort-split',
    'error-translating try opened after the call it should cover': 'error-translating-try-after-call',
    'fit integrator differs from the simulated plant': 'fit-integrator-differs-from-plant',
    'markdown the renderer misplaces': 'markdown-renderer-misplaces',
    'persistent failure swallowed at DEBUG': 'persistent-failure-debug-swallow',
    'series resolution inferred from the minimum gap': 'series-resolution-min-gap',
    'shutdown reap waits on the lock a solve holds': 'shutdown-reap-lock-held',
    "staleness limit shorter than a report-on-change sensor's quiet interval": 'staleness-limit-shorter-than-quiet-interval',
    'structure metric blind to a code shape': 'structure-metric-blind-to-shape',
    'avoidable interpreter-bound recomputation in the solve': 'avoidable-interpreter-bound-recomputation',
    'CPU gate blind to a regression outside its sampled work': 'cpu-gate-blind',
    'user state not surviving restart': 'user-state-not-surviving-restart',
}

# sweep keys for the 14 brand-new (round-9) "new: ..." classes -> already-clean slugs
NEW_PREFIX = 'new: '


def slugify(s):
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip('-')
    return s


def load_sweep_classes():
    by_key = {}
    for i in range(1, 8):
        d = json.load(open(f'{SW}S{i}.json'))
        if isinstance(d, dict) and 'classes' in d:
            classes = d['classes']
        elif isinstance(d, dict) and 'class' in d:
            classes = [d]
        elif isinstance(d, list):
            classes = d
        else:
            raise Exception('unknown shape S%d' % i)
        for c in classes:
            c['_source_file'] = f'S{i}.json'
            by_key[c['class']] = c
    return by_key


def main():
    os.makedirs(OUT, exist_ok=True)
    judge = json.load(open(JU + 'CLASSES-DRAFT.json'))
    sweep_by_key = load_sweep_classes()
    sweep_norm = {slugify(k[len(NEW_PREFIX):] if k.startswith(NEW_PREFIX) else k): k for k in sweep_by_key}

    index = []
    conflicts = []

    for jc in judge['classes']:
        jid = jc.get('id')
        jname = jc['name']
        # resolve sweep key
        skey = None
        if jid and jid in sweep_by_key:
            skey = jid
        elif jname in MANUAL_MAP and MANUAL_MAP[jname] in sweep_norm.values():
            skey = MANUAL_MAP[jname]
        elif slugify(jname) in sweep_norm:
            skey = sweep_norm[slugify(jname)]
        else:
            sys.exit(f'UNRESOLVED sweep match for judge class {jid} / {jname!r}')

        sc = sweep_by_key[skey]

        # ---- slug ----
        if jid:
            slug = jid.lower()
        elif jname in MANUAL_MAP:
            slug = MANUAL_MAP[jname]
        else:
            slug = slugify(jname.replace(NEW_PREFIX, ''))

        # ---- N / rca: sweep is the later, authoritative phase ----
        judge_n, judge_rca = jc['n'], jc['rca']
        sweep_n, sweep_rca = sc.get('N'), sc.get('rca')
        if (judge_n, judge_rca) != (sweep_n, sweep_rca):
            conflicts.append((jid or slug, jname, (judge_n, judge_rca), (sweep_n, sweep_rca), sc['_source_file']))
        n = sweep_n if sweep_n is not None else judge_n
        rca = sweep_rca if sweep_rca is not None else judge_rca

        # ---- findings (judge-verified/weakened instances) ----
        findings = jc.get('findings', [])
        finding_ids = [f['id'] for f in findings]
        highest_sev = 'low'
        for f in findings:
            if SEV_ORDER.get(f['severity'], 0) > SEV_ORDER.get(highest_sev, 0):
                highest_sev = f['severity']

        # ---- sweep seams: split into (a) extra instances beyond the judge's findings
        # and (b) sites the sweep checked and excluded (guarded / not applicable, or
        # already the widened evidence for one of the findings above, under either the
        # 'finding_id' key some sweep files use or a bare finding id in 'probe') ----
        FID_RE = re.compile(r'D\d+-s\d+-\d+')
        extra, excluded, widened_notes = [], [], []
        for s in sc.get('seams', []):
            fid = s.get('finding_id')
            probe = s.get('probe') or ''
            note = s.get('note') or ''
            note_prefix = note.split(';', 1)[0].strip()
            candidate_fids = set(FID_RE.findall(probe)) | set(FID_RE.findall(note_prefix))
            linked_fid = fid if (fid and fid in finding_ids) else next(
                (c for c in candidate_fids if c in finding_ids), None)
            disp = s.get('disposition', 'instance')
            if linked_fid:
                widened_notes.append((linked_fid, s))
                continue  # already a judge finding row; this is one of its widened sites
            if disp == 'instance':
                extra.append(s)
            else:
                excluded.append(s)
        for s in extra:
            sv = s.get('severity')
            if sv and SEV_ORDER.get(sv, 0) > SEV_ORDER.get(highest_sev, 0):
                highest_sev = sv

        # ---- build instance table rows ----
        widened_paths_by_fid = {}
        for fid, s in widened_notes:
            p = s.get('path')
            if p:
                widened_paths_by_fid.setdefault(fid, []).append(p)

        rows = []
        for f in findings:
            fl = f['files'][0] if f.get('files') else '(no file recorded)'
            base_extra = set(f['files'][1:]) if f.get('files') else set()
            extra_files = []
            for p in widened_paths_by_fid.get(f['id'], []):
                # a widened path like 'drift.py:148' supersedes the bare 'drift.py' from `files`
                base_extra.discard(p.split(':', 1)[0])
                if p != fl and p not in extra_files:
                    extra_files.append(p)
            for p in base_extra:
                if p != fl and p not in extra_files:
                    extra_files.append(p)
            rows.append({
                'ref': f['id'],
                'file': fl,
                'extra_files': extra_files,
                'severity': f['severity'],
                'verdict': f['verdict'],
                'title': f['title'],
                'seam_rule': f.get('seam_rule', ''),
                'merged': f.get('merged', []),
            })
        for s in extra:
            rows.append({
                'ref': 'sweep',
                'file': s.get('path', '(no path recorded)'),
                'extra_files': [],
                'severity': s.get('severity', '(unrated)'),
                'verdict': 'sweep-confirmed',
                'title': s.get('note', ''),
                'seam_rule': s.get('probe', ''),
                'merged': [],
            })

        barrier = sc.get('barrier_proposal')

        # ---- write markdown ----
        title_line = f"[R9-{slug.upper()}] {jname}"
        lines = []
        lines.append(f"# {title_line}")
        lines.append("")
        lines.append(f"**Class `{jid or slug}`.** {jname}. The mechanism the sweep confirms across "
                      f"{n} instance{'s' if n != 1 else ''}: the shared fact above is decided, guarded, "
                      f"or read differently at each site below rather than by one canonical rule, so a fix "
                      f"at one site leaves its siblings unfixed.")
        lines.append("")
        lines.append(f"Highest severity: **{highest_sev}**.")
        lines.append("")
        judge_n_str = len(findings)
        sweep_extra_str = len(extra)
        lines.append(f"N = {n} ({judge_n_str} judge-verified finding{'s' if judge_n_str != 1 else ''} "
                      f"+ {sweep_extra_str} sweep-confirmed instance{'s' if sweep_extra_str != 1 else ''}).")
        lines.append("")
        lines.append(f"RCA: {'owed' if rca else f'not triggered (N={n})'}.")
        lines.append("")
        if (judge_n, judge_rca) != (sweep_n, sweep_rca):
            lines.append(f"> Note: the judge's class table (`CLASSES-DRAFT.json`) recorded n={judge_n}, "
                          f"rca={judge_rca} for this class; the class sweep (`{sc['_source_file']}`), run "
                          f"after the judge and enumerating every sibling seam, found N={sweep_n}, "
                          f"rca={sweep_rca}. The sweep count is the one this issue uses, being the later, "
                          f"complete enumeration.")
            lines.append("")
        lines.append("## Instances")
        lines.append("")
        lines.append(f"File:line is at baseline `{BASELINE}` (`{BASELINE_FULL}`).")
        lines.append("")
        lines.append("| ref | file:line | severity | what |")
        lines.append("|---|---|---|---|")
        for r in rows:
            what = r['title'].replace('|', '\\|').replace('\n', ' ')
            fileref = r['file'].replace('|', '\\|')
            lines.append(f"| {r['ref']} | `{fileref}` | {r['severity']} | {what} |")
        lines.append("")
        if any(r['extra_files'] for r in rows):
            lines.append("Findings touching more than one file (first file is the table's file:line; "
                          "the rest share the same fact):")
            lines.append("")
            for r in rows:
                if r['extra_files']:
                    lines.append(f"- {r['ref']}: also `" + "`, `".join(r['extra_files']) + "`")
            lines.append("")
        if excluded:
            lines.append("The sweep also checked, and excluded as not this class's fact "
                          "(recorded so the count is not re-derived from scratch next round):")
            lines.append("")
            for s in excluded:
                lines.append(f"- `{s.get('path', '?')}` — {s.get('disposition')}: {s.get('note', '')}")
            lines.append("")

        lines.append("## Reproduction")
        lines.append("")
        lines.append("Per-finding seam rule / enumerator (each re-anchors at the baseline above; run "
                      "`PYTHONPATH=tests/hastub` from the repository root per `tools/audit/README.md`'s "
                      "harness contract):")
        lines.append("")
        for f in findings:
            if f.get('seam_rule'):
                lines.append(f"- **{f['id']}**: `{f['seam_rule']}`")
        if sc.get('enumerator'):
            lines.append(f"- class enumerator: `{sc['enumerator']}`")
        if sc.get('probes'):
            lines.append(f"- class probes: `{sc['probes']}`")
        if sc.get('null_and_perturbation'):
            lines.append(f"- null/perturbation: `{sc['null_and_perturbation']}`")
        lines.append("")

        lines.append("## Evidence")
        lines.append("")
        lines.append(f"- Judge outputs, branch `handoff/audit-r9-judge`: `JUDGE.json@{JUDGE_JUDGE_JSON_COMMIT}`, "
                      f"`CLASSES-DRAFT.json@{JUDGE_CLASSES_DRAFT_COMMIT}`.")
        lines.append(f"- Harnesses: `handoff/audit-r9-evidence`, under `tools/audit/round9/`.")
        sweep_branch = sc.get('branch') or (sc.get('_meta') or {}).get('branch')
        evidence_line = f"- Class sweep output: `{sc['_source_file']}`"
        if sweep_branch:
            evidence_line += f", branch `{sweep_branch}`"
        evidence_line += "."
        lines.append(evidence_line)
        if sc.get('checked_on_main'):
            lines.append(f"- Also re-checked on `origin/main@{sc['checked_on_main']}` (post `handoff/audit-r9-judge`'s baseline): still present.")
        lines.append(f"- Baseline: `{BASELINE_FULL}` (v6.7.1).")
        lines.append("")

        lines.append("## Barrier proposal")
        lines.append("")
        if barrier:
            lines.append(barrier if isinstance(barrier, str) else json.dumps(barrier))
        elif rca:
            lines.append("None recorded by the sweep; owed by the RCA seat alongside the fix "
                          "(`tools/audit/briefs/root-cause.md`).")
        else:
            lines.append(f"None: N={n} does not trigger RCA (`CLAUDE.md`'s N >= 3 rule).")
        lines.append("")

        lines.append("## Fix")
        lines.append("")
        lines.append("Fix: see round-9 fix plan.")
        lines.append("")

        path = os.path.join(OUT, f"{slug}.md")
        with open(path, 'w') as fh:
            fh.write("\n".join(lines) + "\n")

        index.append({
            'class': jid or jname,
            'slug': slug,
            'title': title_line,
            'severity': highest_sev,
            'N': n,
            'rca': rca,
            'finding_ids': finding_ids,
            'file': f"{slug}.md",
        })

    with open(os.path.join(OUT, 'INDEX.json'), 'w') as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")

    print(f"wrote {len(index)} class files + INDEX.json to {OUT}")
    print()
    print("CONFLICTS (judge n/rca vs sweep N/rca):")
    for cid, name, jv, sv, src in conflicts:
        print(f"  {cid} ({name[:60]}): judge={jv} sweep={sv} [{src}]")


if __name__ == '__main__':
    main()
