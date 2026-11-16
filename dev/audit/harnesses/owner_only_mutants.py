#!/usr/bin/env python3
"""owner_only_mutants.py -- the single-line mutants of the owner-only channel's edits to existing instruments.

    python3 -I dev/audit/harnesses/owner_only_mutants.py [--only GROUP[,GROUP]]

The new instruments (tools/audit/seat/owner_only.py, corpus_mirror.py,
finder_overlap.py's arms, tools/audit/leak_detectors.py) carry their mutants
in their own `--self-test`. This file holds the rest (R11-PRE-SECURITY-PRIVACY):
the owner-only branch and the literal return of both workflow drivers, the
finding-id class of ref_privacy.py, fold_ledger.py's refusal, gh_read.py's
conditional read and budget floor, gh_calls.py's bucket rule, and the gh
shim's owner-only mode. Each mutant is applied in a detached worktree of HEAD
(so it needs a checkout and committed files, and never touches this tree),
the group's check is run there, and the mutant is KILLED when the check exits
non-zero. Prints one line per mutant, then `RESULT mutants=<n> survived=<n>`;
exit 1 when a needle is not found exactly once or a mutant survives.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)

#: group -> (the check, run from the worktree root; [(file, needle, replacement)])
GROUPS = {'drivers': (['node', 'tools/policy/check-wave-script.mjs'],
             [('.claude/workflows/audit-find.js', 'table[d].owner_only === true).sort()', 'false).sort()'),
              ('.claude/workflows/audit-find.js',
               'for (const d of DIMS) if (!OWNER_ONLY.includes(d)) PUBLIC.push(d)',
               'for (const d of DIMS) PUBLIC.push(d)'),
              ('.claude/workflows/audit-find.js', 'if (privateRoot !== undefined) {', 'if (false) {'),
              ('.claude/workflows/audit-find.js', '  if (refusal) throw new Error(refusal)\n  const ownSeats', '  const ownSeats'),
              ('.claude/workflows/audit-find.js', 'if (ready.probe_rc !== 0) throw', 'if (false) throw'),
              ('.claude/workflows/audit-find.js',
               '  return ownerOnlyStatus(round, baseline, privateRoot)\n}',
               '  return { ...ownerOnlyStatus(round, baseline, privateRoot), finished }\n}'),
              ('.claude/workflows/audit-find.js',
               '      return r?.done === true\n    } catch { return false }',
               '      return r?.done === true\n    } catch (e) { log(e.message); return false }'),
              ('.claude/workflows/audit-find.js', '{ label: seat.id, schema: OWNER_ONLY_REPLY },', '{ label: seat.id, schema: reportSchema },'),
              ('.claude/workflows/audit-find.js',
               "additionalProperties: false, properties: { path: { type: 'string' }, done: { type: 'boolean' } } }\n"
               '// What an owner-only run returns',
               "properties: { path: { type: 'string' }, done: { type: 'boolean' } } }\n// What an owner-only run returns"),
              ('.claude/workflows/audit-verify.js', 'if (reg.findings.some((f) => ownerOnlyRecord(f, OWNER_ONLY))) throw', 'if (false) throw'),
              ('.claude/workflows/audit-verify.js', '[f?.dimension, f?.scope, f?.id].some(', '[f?.dimension].some('),
              ('.claude/workflows/audit-verify.js', 'if (a.file === true) return', 'if (false) return'),
              ('.claude/workflows/audit-verify.js', 'if (ready.probe_rc !== 0) throw', 'if (false) throw'),
              ('.claude/workflows/audit-verify.js', 'if (ready.reports_ok !== true) throw', 'if (false) throw'),
              ('.claude/workflows/audit-verify.js',
               '  return ownerOnlyStatus(round, privateRoot)\n}',
               '  return { ...ownerOnlyStatus(round, privateRoot), judged }\n}'),
              ('.claude/workflows/audit-verify.js',
               '?.done === true } catch { return false }',
               '?.done === true } catch (e) { log(e.message); return false }'),
              ('.claude/workflows/audit-verify.js',
               "if (!judged) throw new Error('owner-only verification: the judge did not finish",
               "if (false) throw new Error('owner-only verification: the judge did not finish")]),
 'ref_privacy': (['python3', '-I', 'tools/audit/seat/ref_privacy.py', '--self-test'],
                 [('tools/audit/seat/ref_privacy.py', '    if owner_only_id(text, ident.owner_only):\n', '    if False:\n'),
                  ('tools/audit/seat/ref_privacy.py', 'r")(?:-s[0-9]+)?-[0-9]{2}(?![0-9])"', 'r")-s[0-9]+-[0-9]{2}(?![0-9])"'),
                  ('tools/audit/seat/ref_privacy.py', 'r")(?:-s[0-9]+)?-[0-9]{2}(?![0-9])"', 'r")(?:-s[0-9]+)?(?:-[0-9]{2})?(?![0-9])"'),
                  ('tools/audit/seat/ref_privacy.py', '                     text, re.I) is not None', '                     text) is not None'),
                  ('tools/audit/seat/ref_privacy.py', 'e.get("owner_only") is True))', 'e.get("owner_only")))'),
                  ('tools/audit/seat/ref_privacy.py',
                   '"scratch-root", "owner-only-id")\n\n\ndef body_refusal',
                   '"scratch-root")\n\n\ndef body_refusal'),
                  ('tools/audit/seat/ref_privacy.py', '{socket.gethostname()}, owner_only_dims())', '{socket.gethostname()})'),
                  ('tools/audit/seat/ref_privacy.py',
                   'r"(?<![A-Za-z0-9])(?:" + "|".join(re.escape(d) for d in dims)',
                   'r"(?:" + "|".join(re.escape(d) for d in dims)')]),
 'fold_ledger': (['python3', '-I', 'tools/audit/fold_ledger.py', '--self-test'],
                 [('tools/audit/fold_ledger.py', '    bad += owner_only_records(root, led, judge_files)\n', ''),
                  ('tools/audit/fold_ledger.py', '    if private:\n        raise SystemExit', '    if False:\n        raise SystemExit'),
                  ('tools/audit/fold_ledger.py', 'e.get("owner_only") is True} if', 'e.get("owner_only") is not None} if'),
                  ('tools/audit/fold_ledger.py', '            continue  # refused above', '            pass  # refused above'),
                  ('tools/audit/fold_ledger.py', '            d = owner_only_dim(p[1], dims) if p else None', '            d = None'),
                  ('tools/audit/fold_ledger.py', '        d = owner_only_dim(u.get("finding_id"), dims)', '        d = None'),
                  ('tools/audit/fold_ledger.py', 'return m.group(1) if m and m.group(1) in dims else None', 'return m.group(1) if m else None')]),
 'gh_read': (['python3', '-I', '-c', "import sys; sys.path.insert(0, 'tools/audit/seat'); import gh_read; sys.exit(gh_read.self_test())"],
             [('tools/audit/seat/gh_read.py', '        if status == 304:\n            return ("unchanged", "", etag), None\n', ''),
              ('tools/audit/seat/gh_read.py', 'if code == 0 and status is not None and 200 <= status < 300:', 'if status is not None:'),
              ('tools/audit/seat/gh_read.py', '+ (["-H", f"If-None-Match: {etag}"] if etag else [])', ''),
              ('tools/audit/seat/gh_read.py',
               '    if spent:\n'
               '        return wait\n'
               '    if not http_transient(status, body):\n'
               '        return None\n'
               '    return wait or 0.0\n'
               '\n'
               '\n'
               'def rate_wait',
               '    if not http_transient(status, body):\n        return None\n    return wait or 0.0\n\n\ndef rate_wait'),
              ('tools/audit/seat/gh_read.py',
               'if status is None or not (rate_limited(status, body) or (status == 403 and SECONDARY in body.lower())):',
               'if status is None:'),
              ('tools/audit/seat/gh_read.py',
               'n not in buckets or buckets[n][1] < floor * buckets[n][0]]',
               'n in buckets and buckets[n][1] < floor * buckets[n][0]]'),
              ('tools/audit/seat/gh_read.py', 'buckets[n][1] < floor * buckets[n][0]]', 'buckets[n][1] <= floor * buckets[n][0]]'),
              ('tools/audit/seat/gh_read.py', '    if not buckets:\n        return ["unread"]\n', ''),
              ('tools/audit/seat/gh_read.py',
               '    if code:\n        return None\n    try:\n        res = json.loads(out).get("resources")',
               '    try:\n        res = json.loads(out).get("resources")'),
              ('tools/audit/seat/gh_read.py',
               'not any(w in docs[0].lower() for w in ("mutation", "subscription"))',
               'not any(w in docs[0].lower() for w in ("mutation",))'),
              ('tools/audit/seat/gh_read.py', '        if value.startswith("@"):\n            return False\n', ''),
              ('tools/audit/seat/gh_read.py', 'if rest[k] != "-f" or k + 1 >= len(rest)', 'if rest[k] not in ("-f", "-F") or k + 1 >= len(rest)'),
              ('tools/audit/seat/gh_read.py', 'return len(docs) == 1 and not any(', 'return len(docs) >= 1 and not any(')]),
 'gh_calls': (['python3', '-I', 'tools/audit/seat/gh_calls.py', '--self-test'],
              [('tools/audit/seat/gh_calls.py',
                'path) else "unattributed"',
                 'path) or True else "unattributed"'),
               ('tools/audit/seat/gh_calls.py', 'return "core" if sub in CORE_CMDS else "unattributed"', 'return "core"'),
               ('tools/audit/seat/gh_calls.py', '        if path == "rate_limit":\n            return "free"\n', ''),
               ('tools/audit/seat/gh_calls.py', 'if path == "search" or path.startswith("search/"):', 'if path.startswith("search"):'),
               ('tools/audit/seat/gh_calls.py', 'if m and (since is None or m.group(1) >= since):', 'if m:')]),
 'shim': (['python3', '-I', 'dev/audit/harnesses/owner_only_channel.py', '--only', 'P5'],
          [('tools/audit/seat/shims/seat-gh', '  [ -n "$ro" ] || { echo "gh shim: owner-only mode', '  : || { echo "gh shim: owner-only mode'),
           ('tools/audit/seat/shims/seat-gh', '    api) api_gate "$@" && [ -n "$API_READ" ] && ro=1 ;;', '    api) ro=1 ;;'),
           ('tools/audit/seat/shims/seat-gh', '    pr) [ "${2-}" = view ] && ro=1 ;;', '    pr) ro=1 ;;'),
           ('tools/audit/seat/shims/seat-gh',
            '    case ${meth:-GET} in GET|get) API_READ=1; return 0 ;; esac',
            '    API_READ=1; case ${meth:-GET} in GET|get) return 0 ;; esac')])}


def main(argv: list[str]) -> int:
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else set(GROUPS)
    total = bad = 0
    with tempfile.TemporaryDirectory() as td:
        wt = Path(td) / "wt"
        subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "-q", "--detach", str(wt), "HEAD"], check=True)
        try:
            for group, (check, mutants) in GROUPS.items():
                if group not in only:
                    continue
                for rel, old, new in mutants:
                    total += 1
                    p = wt / rel
                    src = p.read_text()
                    if src.count(old) != 1:
                        bad += 1
                        print(f"NEEDLE   {group}: found {src.count(old)} times in {rel}: {old[:50]!r}")
                        continue
                    p.write_text(src.replace(old, new))
                    try:
                        r = subprocess.run(check, cwd=wt, capture_output=True, text=True, timeout=900)
                    finally:
                        p.write_text(src)
                    fails = [ln.strip()[:110] for ln in (r.stdout + r.stderr).splitlines() if "FAIL" in ln and "(probe, expected)" not in ln]
                    bad += r.returncode == 0
                    print(("KILLED   " if r.returncode else "SURVIVED ") + f"{group}: {old[:50]!r}" + (" -> " + fails[0] if fails else ""))
        finally:
            subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(wt)], check=False)
    print(f"RESULT mutants={total} survived={bad}")
    return 1 if bad or not total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
