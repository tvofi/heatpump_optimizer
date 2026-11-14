"""Reviewer's mutants over tools/audit/check_scopes.py at the head: one unique-string edit each,
--self-test run, file restored and its sha checked. Killed = self-test exits non-zero."""
import subprocess, hashlib, pathlib, sys
F = pathlib.Path("tools/audit/check_scopes.py"); orig = F.read_text(); h = hashlib.sha256(orig.encode()).hexdigest()
M = [
 ("R1 value without enumerator accepted", 'elif "value" in row and not str(row.get("enumerator", "")).strip():', 'elif False:'),
 ("R2 non-numeric value accepted", 'elif "value" in row and not (isnum(v) or', 'elif False and not (isnum(v) or'),
 ("R3 dict value may hold non-numbers", 'isinstance(v, dict) and v and all(isnum(x) for x in v.values())', 'isinstance(v, dict) and v'),
 ("R4 empty dict value accepted", 'isinstance(v, dict) and v and all(', 'isinstance(v, dict) and all('),
 ("R5 untracked enumerator accepted", 'elif "value" in row and not enumerates(row["enumerator"], tree):', 'elif False:'),
 ("R6 enumerates: any token tracked", 'return tok in tree\n    return False', 'return True\n    return False'),
 ("R7 enumerates: interpreter-only is fine", 'return tok in tree\n    return False', 'return tok in tree\n    return True'),
 ("R8 NO-READ needs only would_read", 'for k in ("would_read", "builder") if not full(row.get(k))]', 'for k in ("would_read",) if not full(row.get(k))]'),
 ("R9 NO-READ needs only builder", 'for k in ("would_read", "builder") if not full(row.get(k))]', 'for k in ("builder",) if not full(row.get(k))]'),
 ("R10 card: builder not checked", 'if b not in cards:\n            gaps.append(f"{prev} term', 'if False:\n            gaps.append(f"{prev} term'),
 ("R11 round/reads mismatch accepted", 'if ev.get("round") != rnd or ev.get("reads") != prev:', 'if False:'),
 ("R12 raw name compare", 'seat, rev = (norm(ev.get(k, ""))', 'seat, rev = (str(ev.get(k, ""))'),
 ("R13 same seat accepted", 'or seat == rev or "orchestrator" in seat', 'or "orchestrator" in seat'),
 ("R14 orchestrator reviewer accepted", ' or "orchestrator" in rev:', ':'),
 ("R15 orchestrator evaluator accepted", 'or "orchestrator" in seat or', 'or'),
 ("R16 any review verdict", 'rv.get("verdict") != "approve"', 'not rv.get("verdict")'),
 ("R17 review sha unchecked", 'elif not (full(rv.get("sha")) and merged(rv["sha"])):', 'elif not full(rv.get("sha")):'),
 ("R18 graded objects unchecked", 'if graded != rows:', 'if False:'),
 ("R19 row outside the object set", 'for f in sorted(rows) if f not in objects]', 'for f in sorted(rows) if False]'),
 ("R20 verdict set unpinned", 'row.get("verdict") not in VERDICTS:', 'not row.get("verdict"):'),
 ("R21 evidence not owed", 'elif not str(row.get("evidence", "")).strip():', 'elif False:'),
 ("R22 remove on NO-READ", 'elif row["verdict"] == "remove" and str(row["evidence"]).strip().startswith("NO-READ"):', 'elif False:'),
 ("R23 change/remove needs no card", 'elif row["verdict"] != "keep" and row.get("card") not in cards:', 'elif False:'),
 ("R24 undecided card", 'if card.get("decision") not in DECISIONS:', 'if False:'),
 ("R25 ruling not owed", 'if not full(card.get("ruling")):', 'if False:'),
 ("R26 accepted not merged", 'if not (c and merged(c)):', 'if not c:'),
 ("R27 merged may predate review", 'elif revsha and anc(c, revsha):', 'elif False:'),
 ("R28 accepted names no file", 'elif not want:\n', 'elif False:\n'),
 ("R29 merged changes nothing of the card", 'elif not want & changed(c):', 'elif False:'),
 ("R30 card paths ignored", 'want = {x for x in (card.get("object"), *(card.get("paths") or ())) if x}', 'want = {x for x in (card.get("object"),) if x}'),
 ("R31 unset threshold uncarded", 'if th.get("value") is None and k not in carded("threshold"):', 'if False:'),
 ("R32 unset criterion uncarded", 'if p is None and d not in carded("criterion"):', 'if False:'),
 ("R33 criterion path untracked", 'elif p is not None and p not in tree:', 'elif False:'),
 ("R34 NO-READ axis needs no builder", 'for k in ("no_read", "builder") if ax.get("kind") is None', 'for k in ("no_read",) if ax.get("kind") is None'),
 ("R35 NO-READ axis needs no reason", 'for k in ("no_read", "builder") if ax.get("kind") is None', 'for k in ("builder",) if ax.get("kind") is None'),
 ("R36 unowned count uncarded", 'and n < u["value"]:', 'and False:'),
 ("R37 unowned off by one", 'and n < u["value"]:', 'and n < u["value"] - 1:'),
 ("R38 previous record missing accepted", 'if prev not in tree:\n        gaps.append', 'if False:\n        gaps.append'),
 ("R39 evaluation missing accepted", 'if path not in tree:\n        return gaps + [f"{path} is not in the tree: the start evaluation has not run"]', 'if path not in tree:\n        return gaps'),
 ("R40 missing term accepted", 'if not isinstance(row, dict):\n                gaps.append(f"{prev} has no term {t}")', 'if not isinstance(row, dict):\n                pass'),
 ("R41 neither read nor NO-READ", 'elif "value" not in row and not str(row.get("no_read", "")).strip():', 'elif False:'),
 ("R42 object globs first only", 'for g in ([v] if isinstance(v, str) else v)]', 'for g in ([v] if isinstance(v, str) else v[:1])]'),
 ("R43 binary axis one level", 'sizes += [2] * len(lv)', 'sizes += [1] * len(lv)'),
 ("R44 pairs not halved", '- sum(n * n for n in sizes)) // 2}"', '- sum(n * n for n in sizes))}"'),
 ("R45 pairs count same-axis pairs", '(sum(sizes) ** 2 - sum(n * n for n in sizes)) // 2', '(sum(sizes) ** 2 - sum(sizes)) // 2'),
 ("R46 empty axis is fine", 'if not lv:\n                raise ValueError("no level found")', 'if False:\n                raise ValueError("no level found")'),
 ("R47 UNREADABLE keeps ok", 'ok = False\n            lines.append(f"UNREADABLE', 'ok = ok\n            lines.append(f"UNREADABLE'),
 ("R48 untracked source file", 'if f not in tree:\n            raise ValueError(f"{f} is not tracked at the ref")', 'if False:\n            raise ValueError(f"{f} is not tracked at the ref")'),
 ("R49 In-compare not read", 'elif isinstance(op, ast.In) and isarg(l)', 'elif False and isarg(l)'),
 ("R50 dict axis reads values", 'elts = node.keys', 'elts = node.values'),
 ("R51 starred not expanded", 'if isinstance(e, ast.Starred):\n                    out += strs(lookup(e.value.id) if isinstance(e.value, ast.Name) else e.value)\n                    continue', 'if isinstance(e, ast.Starred):\n                    continue'),
 ("R52 levels not deduplicated", 'lv = sorted(set(levels(ax)))', 'lv = sorted(levels(ax))'),
 ("R53 NO-READ axes uncounted", 'noread += 1', 'noread += 0'),
]
surv = 0
for name, a, b in M:
    if orig.count(a) != 1:
        print(f"SKIP {name}: anchor count {orig.count(a)}"); continue
    F.write_text(orig.replace(a, b))
    r = subprocess.run([sys.executable, str(F), "--repo", ".", "--self-test"], capture_output=True, text=True)
    F.write_text(orig)
    bad = [l.strip() for l in r.stdout.splitlines() if "FAIL" in l or "not held" in l or "False" in l][:2]
    k = r.returncode != 0
    surv += not k
    print(f"{'killed  ' if k else 'SURVIVED'} {name} rc={r.returncode} {bad}")
assert hashlib.sha256(F.read_text().encode()).hexdigest() == h
r = subprocess.run([sys.executable, str(F), "--repo", ".", "--self-test"], capture_output=True, text=True)
print(f"RESULT unmutated rc={r.returncode}; mutants {len(M)}, survivors {surv}; file sha256 restored {h[:16]}")
