#!/usr/bin/env python3
# Reviewer's own mutant driver (round 2): applies each mutant to a copy worktree, runs --self-test.
import subprocess, sys, pathlib
W = pathlib.Path(sys.argv[1]); src = (W/"wt/tools/ci/selftest_scope.py").read_text(); F = W/"mwt/tools/ci/selftest_scope.py"
M = [
 # round-1 survivors
 ("prune-cli-no-write", '        write_table(root / TABLE, entries, root)\n        return 0\n    if argv[:1] == ["check"]', '        return 0\n    if argv[:1] == ["check"]'),
 ("prune-cli-ignores-unknown", '        if unknown:\n            print(f"selftest_scope: not in the table', '        if False:\n            print(f"selftest_scope: not in the table'),
 ("probe-dir-ancestor-removed", 'covers(probes, x) or covers(files, x)\n                or any(a in dirs for a in _ancestors(x)),', 'covers(probes, x) or covers(files, x),'),
 ("table-untouched-skip-removed(equivalent-r1)", '    if TABLE not in {p for _, p in rows}:\n        return []\n', ''),
 # round-1 killed, reconstructed
 ("flags-not-unioned", 'bool(old.get(k)) or bool(new[k])', 'bool(new[k])'),
 ("probes-not-filtered", 'got["probes"] = [p for p in got["probes"] if p not in set(got["files"])]', 'pass'),
 ("flag-drop-unchecked", 'for k in FLAG_KINDS if b.get(k) and not h.get(k)]', 'for k in FLAG_KINDS if False]'),
 ("dir-survivor-ignored", 'and not any(r.startswith(p + "/") for r in remaining))', 'and True)'),
 ("deleted-set-empty", '{p for st, p in rows if st == "D"}', 'set()'),
 ("first-parent-none", 'return (r.stdout.strip() if r.returncode == 0 else None), ""', 'return None, ""'),
 ("dirs-kept-always", '"dirs": lambda x: x in dirs,', '"dirs": lambda x: True,'),
 ("gitlist-kept-always", '"git": lambda x: x in set(h.get("git", ()))}', '"git": lambda x: True}'),
 ("record-replaces", 'entries[sid] = union_entry(entries.get(sid), m)', 'entries[sid] = m'),
 # delta mutants (round 2)
 ("unresolved-is-no-problem", 'return None, (f"UNRESOLVED base {c}', 'return None, "" and (f"UNRESOLVED base {c}'),
 ("unresolved-falls-through-to-first-parent", '        return None, (f"UNRESOLVED base {c}', '        continue; (f"UNRESOLVED base {c}'),
 ("static-ignores-unresolved", 'problems += [unresolved] if unresolved else shrink_gaps(root, base)', 'problems += shrink_gaps(root, base)'),
 ("static-runs-guard-never", 'problems += [unresolved] if unresolved else shrink_gaps(root, base)', 'problems += [unresolved] if unresolved else []'),
 ("prune-unknown-rc0", 'nothing written: {unknown}", file=sys.stderr)\n            return 1', 'nothing written: {unknown}", file=sys.stderr)\n            return 0'),
 ("prune-writes-before-refusing", '        if unknown:\n            print(f"selftest_scope: not in the table', '        write_table(root / TABLE, entries, root)\n        if unknown:\n            print(f"selftest_scope: not in the table'),
 ("prune-unknown-step-accepted", 'return entries, [f"no step {step}"]', 'return entries, []'),
 ("prune-list-drop-noop", 'entries[step][kind] = [x for x in entries[step][kind] if x != item]', 'entries[step][kind] = list(entries[step][kind])'),
 ("prune-flag-noop", 'entries[step][kind] = False', 'entries[step][kind] = True'),
 ("prune-unknown-kind-accepted", '        else:\n            unknown.append(d)', '        else:\n            pass'),
 ("merge-base-only-first-cand", '    for c in cands:\n        r = subprocess.run(["git", "merge-base", c, "HEAD"]', '    for c in cands[1:]:\n        r = subprocess.run(["git", "merge-base", c, "HEAD"]'),
]
for name, o, n in M:
    c = src.count(o)
    if c != 1:
        print(f"NOANCHOR {name} (count {c})", flush=True); continue
    F.write_text(src.replace(o, n))
    try:
        p = subprocess.run([sys.executable, "-I", "tools/ci/selftest_scope.py", "--self-test"], cwd=W/"mwt", capture_output=True, text=True, timeout=200)
        out = (p.stdout + p.stderr).strip().splitlines()[-1:] or [""]
        tag = "SURVIVED" if p.returncode == 0 and " 0 failed" in out[0] else "KILLED"
        print(f"{tag} {name} :: rc={p.returncode} {out[0]}", flush=True)
    except subprocess.TimeoutExpired:
        print(f"KILLED {name} :: timeout", flush=True)
F.write_text(src)
