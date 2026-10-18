#!/usr/bin/env python3
"""The round drivers against round 10's own replies (R10-TICK e, g, h; #2265).

Written by the R10-TICK-DRIVERS fixer. It drives `--tree`'s
`.claude/workflows/audit-find.js` and `audit-verify.js` in node with every
agent() stubbed, the way tools/policy/check-wave-script.mjs does, and feeds the
stubs round 10's real box reports: `dev/audit/rounds/round10/reports-B<n>.json`
of `--evidence` (a checkout carrying them; main since the round-10 register).

  form_gap        box findings finding.schema.json rejects (jsonschema,
                  draft-07) that the finder's return schema, the one the
                  driver hands the runtime, accepts: what reaches intake to be
                  rejected on form rather than being refused at return (g);
  form_file_rej   the first term alone: box findings the file rejects;
  gather_max_kb   the largest single gather reply a `from: "intake"` run asks
                  for, in KiB of JSON: one reply for every box, or one per box (e);
  gather_missing  seats intake reads as not reported once the replies are read;
  text_read       findings reaching the judge when the register read returns
                  them as one JSON string (h); -1 when the driver throws;
  text_gather     gather_missing when every box reply is JSON text (e, h).

Perturbation (`--perturb`): drop the expected_direction enum from the
finder's return schema before measuring, as a hand-kept copy would; form_gap
rises at a head that derives the schema. Null control: the findings both
schemas accept are counted the same way (`form_both_ok`), and the file's own
verdict (`form_file_rej`) does not depend on the tree.

    python3 dev/audit/harnesses/r10_tick_drivers.py --tree <worktree> [--evidence <repo>] [--perturb]
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import tempfile

import jsonschema

JS = r"""
const fs = require('fs'), path = require('path')
const [tree, evid, perturb] = process.argv.slice(2)
const rd = (p) => fs.readFileSync(path.join(tree, p), 'utf8')
const body = (src) => { const i = src.indexOf('export const meta'); return src.slice(0, i) + src.slice(src.indexOf('\n}\n', i) + 3) }
const scopes = JSON.parse(rd('dev/audit/config/scopes.json')), rotation = JSON.parse(rd('dev/audit/config/rotation.json'))
const boxFiles = Object.fromEntries(fs.readdirSync(path.join(evid, 'dev/audit/rounds/round10')).filter((f) => /^reports-B\d+\.json$/.test(f))
  .map((f) => [f.slice(8, -5), JSON.parse(fs.readFileSync(path.join(evid, 'dev/audit/rounds/round10', f), 'utf8'))]))
const pipeline = (items, f) => Promise.all(items.map((x) => f(x)))
const run = async (src, args, agent) => {
  const fn = new Function('agent', 'log', 'phase', 'pipeline', 'parallel', 'args', `return (async () => { ${body(src)} })()`)
  return fn(agent, () => {}, () => {}, pipeline, (th) => Promise.all(th.map((t) => t())), args)
}
const PREP = { exportDir: '/x', worktrees: new Proxy({}, { get: (_, k) => `/w/${String(k)}` }), python: 'py', rotation_ok: true, scopes_ok: true, scopes_rc: 0, scopes_out: '' }
const find = rd('.claude/workflows/audit-find.js')
const out = {}
;(async () => {
  // The finder's return schema: the first finder call's, then stop.
  let schema = null
  try { await run(find, { round: 10, baseline: 'b', repo: '/r', rotation, scopes, box: 'B1' }, async (p, o) => { if (o.label === 'prepare') return PREP; schema = o.schema; throw new Error('stop') }) } catch {}
  if (perturb === '1') delete schema.properties.findings.items.properties.perturbation.properties
  out.schema = schema
  // The gather: what each reply carries, answered from the box files.
  const ask = (prompt, text) => {
    // The boxes the prompt names, as the gatherer would read them.
    const boxes = [...new Set(prompt.match(/\bB\d+\b/g) ?? [])]
    const reports = Object.assign({}, ...boxes.map((b) => boxFiles[b]?.reports ?? {}))
    const absent = boxes.filter((b) => !boxFiles[b])
    return text ? { reports: JSON.stringify(reports), absent_boxes: JSON.stringify(absent) } : { reports, absent_boxes: absent }
  }
  for (const text of [false, true]) {
    const sizes = []
    let res = null
    try {
      res = await run(find, { round: 10, baseline: 'b', repo: '/r', rotation, scopes, from: 'intake' }, async (p, o) => {
        if (o.label === 'prepare') return PREP
        if (o.label === 'gather') { const r = ask(p, text); sizes.push(JSON.stringify(r).length); return r }
        if (o.label === 'leads') return { report_path: '/l', findings: [], non_findings: [], harnesses: [], converted: [], closed: [] }
        if (o.label === 'quiet') return { quiet_path: '/q', d3_confirmed: [] }
        return { branch: 'b', registered: [], rejected: [] }
      })
    } catch (e) { res = { error: e.message } }
    out[text ? 'text_gather' : 'gather'] = { max_bytes: Math.max(0, ...sizes), replies: sizes.length, missing: res?.error ? -1 : (res?.missing ?? []).length }
  }
  // The register read, returned as one JSON string.
  const ver = rd('.claude/workflows/audit-verify.js')
  const findings = Object.values(boxFiles).flatMap((f) => Object.values(f.reports ?? {})).flatMap((r) => r.findings ?? [])
    .map((f) => ({ id: f.id, dimension: f.id.split('-')[0], scope: f.scope, step: f.step, severity: f.severity, title: f.title, claim: f.claim, class_guess: f.class_guess, report_path: 'r', harness_paths: [], attached_refutation: null }))
  let judged = -1
  try {
    await run(ver, { round: 10, repo: '/r', from: 'judge' }, async (p, o) => {
      if (o.label === 'read') return { findings: JSON.stringify(findings) }
      if (o.label === 'judge/dedup') { judged = findings.filter((f) => p.includes(`"id":"${f.id}"`)).length; return { canonical: [], merged: [], input_path: 'i' } }
      if (String(o.label).startsWith('judge/runner')) return { table: 't', rows: 0 }
      if (o.label === 'judge') return { verdicts: [] }
      if (o.label === 'fold') return { rc: 0, check_rc: 0, output: '' }
      if (o.label === 'record') return { branch: 'b' }
      return { issues: [] }
    })
  } catch (e) { if (judged < 0) judged = -1 }
  out.text_read = judged
  out.findings = findings.length
  process.stdout.write(JSON.stringify(out))
})()
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tree", required=True)
    ap.add_argument("--evidence", default=".")
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    tree, evid = os.path.abspath(a.tree), os.path.abspath(a.evidence)
    with tempfile.TemporaryDirectory() as td:
        js = os.path.join(td, "drive.js")
        open(js, "w").write(JS)
        r = subprocess.run(["node", js, tree, evid, "1" if a.perturb else "0"], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout:
        sys.exit(f"the node driver failed: rc={r.returncode} {r.stderr[-400:]}")
    got = json.loads(r.stdout)
    file_schema = json.load(open(os.path.join(tree, "dev/audit/config/finding.schema.json")))
    finding_file = {**file_schema["definitions"]["finding"], "definitions": file_schema["definitions"]}
    finding_drv = got["schema"]["properties"]["findings"]["items"]
    v_file = jsonschema.Draft7Validator(finding_file)
    v_drv = jsonschema.Draft7Validator(finding_drv)
    file_rej = drv_rej = gap = both = 0
    for f in sorted(glob.glob(os.path.join(evid, "dev/audit/rounds/round10/reports-B*.json"))):
        for rep in json.load(open(f)).get("reports", {}).values():
            for x in rep.get("findings", []):
                fr, dr = not v_file.is_valid(x), not v_drv.is_valid(x)
                file_rej += fr
                drv_rej += dr
                gap += fr and not dr
                both += not fr and not dr
    print(f"tree {tree}{' (perturbed: expected_direction enum dropped)' if a.perturb else ''}")
    print(f"RESULT findings={got['findings']}")
    print(f"RESULT form_file_rej={file_rej}")
    print(f"RESULT form_driver_rej={drv_rej}")
    print(f"RESULT form_gap={gap}")
    print(f"RESULT form_both_ok={both}")
    print(f"RESULT gather_replies={got['gather']['replies']}")
    print(f"RESULT gather_max_kb={got['gather']['max_bytes'] / 1024:.1f}")
    print(f"RESULT gather_missing={got['gather']['missing']}")
    print(f"RESULT text_gather={got['text_gather']['missing']}")
    print(f"RESULT text_read={got['text_read']}")


if __name__ == "__main__":
    main()
