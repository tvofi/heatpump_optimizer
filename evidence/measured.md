head e1ac127d3237d54392def9a9b763b4cc43421825 measured from detached worktree rev2251 (python 3.14.7 seat shims).
- fold_ledger.py check: 0 violation(s) (42 classes, 734 instances, 121 survivors, rounds 8,10).
- 47 non-refuted CATCHUP-JUDGE verdicts: each has a JUDGE.json row (own id or register_id), a register row, and exactly one class issue in ISSUES.json plan.findings; merged rows point at a target in an issue; ARCH2-s2-P5 is _unclassified by design.
- Live issues #2247-#2250 open, titles and labels equal ISSUES.json. #2239 plan.findings lacks D2-s3-73; #2241 sev:medium.
- Six reconciled rulings equal CATCHUP-JUDGE.md/json (verdict, severity, class); one field differs, see verdict.
- Body and commit messages carry no closing keyword form; merge-tree against origin/main clean; fix-review.md unchanged on main.
- Required checks (ruleset 23698884, 17) all success at head; pr-contract latest run 116438484642 success after the earlier failure 116435032119 (answered in body).
