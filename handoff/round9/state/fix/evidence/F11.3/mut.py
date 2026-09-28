import subprocess, sys, pathlib
S = sys.argv[1]
M = [
 ("P1 token compare", ".claude/workflows/policy_lint.mjs", "} else if (!refused(r.file, `files_tokens[\"${r.file}\"]`, tcap) && Math.round(r.bytes / 4) > tcap) {", "} else if (false) {", ["node", ".claude/workflows/policy_lint.mjs"]),
 ("P2 token table absent", ".claude/workflows/policy_lint.mjs", "  if (tokenCaps == null) out.push(", "  if (false) out.push(", ["node", ".claude/workflows/policy_lint.mjs"]),
 ("P3 token cap absent for a file", ".claude/workflows/policy_lint.mjs", "    if (tcap === undefined) {\n      out.push(", "    if (tcap === undefined) {\n      if (0) out.push(", ["node", ".claude/workflows/policy_lint.mjs"]),
 ("P4 ruleset leaf compare", ".claude/workflows/counts.mjs", "      if (want[k] === got[k]) continue", "      continue", ["node", ".claude/workflows/policy_lint.mjs"]),
 ("P5 ruleset record absent", ".claude/workflows/counts.mjs", "  if (Object.keys(liveObjs).length && !recObjs) {", "  if (false) {", ["node", ".claude/workflows/policy_lint.mjs"]),
 ("P6 ruleset objects not carried", ".claude/workflows/counts.mjs", "      objects[id] = rs\n", "", ["node", ".claude/workflows/field_coverage.mjs", "--only", "ruleset", "--ruleset-json", S + "/ruleset-live.json"]),
 ("P7 quoted-line pass", ".claude/workflows/policy_lint.mjs", "    if (printedPattern(inner).test(printerSource())) continue\n    out.push({", "    continue\n    out.push({", ["node", ".claude/workflows/policy_lint.mjs"]),
 ("P8 CLAUDE.md misquote restored", "CLAUDE.md", "`MODE: SCOPED -- 0 script(s) run`", "`MODE: SCOPED — 0 script(s) run`", ["node", ".claude/workflows/policy_lint.mjs"]),
 ("P9 registry refusal", ".claude/workflows/field_coverage.mjs", "    if (!d) report.refused.push(", "    if (!d) (() => {})(", ["node", ".claude/workflows/field_coverage.mjs", "--self-test"]),
 ("P10 BLIND verdict", ".claude/workflows/field_coverage.mjs", "    else if (v === 'green') report.blind.push(", "    else if (v === 'green') report.read.push(", ["node", ".claude/workflows/field_coverage.mjs", "--self-test"]),
 ("P11 DEAD IGNORE", ".claude/workflows/field_coverage.mjs", "report.dead.push(`${reg.name}: IGNORE", "report.ignored.push(`${reg.name}: IGNORE", ["node", ".claude/workflows/field_coverage.mjs", "--self-test"]),
 ("P12 unperturbed red", ".claude/workflows/field_coverage.mjs", "  if (v0 !== 'green') {", "  if (false) {", ["node", ".claude/workflows/field_coverage.mjs", "--self-test"]),
]
for name, f, old, new, cmd in M:
    p = pathlib.Path(f); src = p.read_text()
    assert src.count(old) == 1, (name, src.count(old))
    p.write_text(src.replace(old, new, 1))
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
    finally:
        p.write_text(src)
    lines = [l.strip() for l in (r.stdout + r.stderr).splitlines() if any(k in l for k in ("VACUOUS", "OVER-FIRES", "BLIND", "REFUSED ", "citations", "TOTAL:", "FAIL "))]
    print(f"{name}: rc={r.returncode} :: " + " | ".join(lines[:3])[:400])
