# Hand mutants of tools/audit/seat/review_strength.py, each one textual edit (old, new), outside the sweep's classes.
M = {
 "X1": ('for r in refs(repo, f"refs/remotes/{remote}/probe/") + refs(repo, "refs/tags/archive/probe/"):',
        'for r in refs(repo, f"refs/remotes/{remote}/probe/"):'),            # archived probe tags dropped (BinOp arm)
 "X2": ('(int(m[1]), nonce[:8]) in probes', '(int(m[1]), nonce[-8:]) in probes'),  # probe suffix from the nonce's tail
 "X3": ('if a <= v["t"] < b:', 'if a < v["t"] <= b:'),                       # window half-open on the other side (two nodes)
 "X4": ('max(u for _, _, u in wins)', 'wins[-1][2]'),                         # as-of = last window, not latest
 "X5": ('git(repo, "log", "--format=%H%x09%cI%x09%s", r)', 'git(repo, "log", "--first-parent", "--format=%H%x09%cI%x09%s", r)'),  # inserted arg
 "X6": ('if not f.startswith("dev/programme/delivery/"):', 'if not f.startswith(("dev/programme/delivery/", "tests/")):'),  # size ignores tests/
 "X7": ('confirmed[m[2]] = m[1]', 'confirmed[m[1]] = m[2]'),                  # swap names
 "X8": (r'(?: ([^\s:]+):)?")', r'(?: (\S+?):)?")'),                           # class word charset replaced
 "X9": ('o["real" if v["real"] else "book"] += 1', 'o["book" if v["real"] else "real"] += 1'),  # swapped literals
 "X10": ('.astimezone(timezone.utc)', ''),                                    # UTC normalisation dropped
 "X11": ('groups[g["group"]] = g', 'groups.setdefault(g["group"], g)'),        # first group entry wins
 "X12": ('g = GROUP_RE.search(row)', 'g = ([*GROUP_RE.finditer(row)] or [None])[-1]'),  # last group named in the row
 "X13": ('rid.startswith("cloud")', '"cloud" in rid'),                         # widened cloud predicate
 "X14": ('"finding" if (grp.get("issues")', '"group" if (grp.get("issues")'),   # unrelated literal
 "X15": ('fixer=((grp or {}).get("model") or {}).get("fixer") or "none"', 'fixer=((grp or {}).get("model") or {}).get("reviewer") or "none"'),
 "X16": ('out.sort(key=lambda v: v["t"])', 'out.sort(key=lambda v: (v["t"], -v["pr"]))'),  # tie order
 "X17": ('merges[int(m[1])] = (sha, parents.split()[1], m[2])', 'merges[int(m[1])] = (sha, parents.split()[-1], m[2])'),  # equivalent on 2 parents
 "X18": ('last = {v["pr"]: v["head"] for v in verdicts if v["t"] < until}', 'last = {v["pr"]: v["head"] for v in verdicts if v["t"] < until and v["kind"] == "blocked"}'),
}
