# Root-cause seat brief RC1: a check that goes red only on main (the #1589 class)

Before doing any work, read `CLAUDE.md` in the repository and all related rules files (`.claude/rules/`, and the role contract for your seat under `tools/audit/briefs/`), and follow them. Pass this rule on in every sub-agent brief you write.

Never refer to the project owner as "Tim" anywhere, especially on the public repository (PR bodies, commits, comments, issues, delivery notes). Call them "tvofi". A PR body's attribution line is `_Requested by **tvofi**_` and carries no claude.ai project link. Pass this rule on in every sub-agent brief you write.

Role: root-cause seat, `tools/audit/briefs/root-cause.md`, executing `.claude/rules/defect-root-cause.md`. You run beside the fix, never inside it. Cloud seat: no GitHub writes (no PRs, comments, approvals, issues). If you build a countermeasure, hand it off as a fixer would: push to `handoff/r9-rc1-<topic>` with a last commit adding the PR body at `tools/audit/handoff/r9-rc1-<topic>.md` (strip before push), body per `.github/PULL_REQUEST_TEMPLATE.md`, passing `tools/audit/prepr.sh`. Report back as text through the coordinator to the round-9 orchestrator (session_01WgT4h2uvK9kbxQbWc5MJis).

## The defect
Round-9 readiness PR R1a (#1633, branch `handoff/r9-r1a-find-checker`, blocked head `a897272a`, fixed head `c6ca4132`): a leads fixture in `.claude/workflows/check-wave-script.mjs` quoted `custom_components/heatpump_optimizer/boost.py`. `codeowners_gap.py` treats a path quoted in a file holding `new Function(` as executed, so `codeowners_gap.py --check` at a897272a printed REFUSED, uncovered_files=2 (boost.py, datetime.py); base 81f2c18c had 0. The PR's own CI stayed green because `policy-docs` restores `.claude/workflows/*.mjs` from the base; on the push to main (PINNED=github.sha) it would have gone red. Caught only by the fix reviewer running the check by hand. The fixer states `codeowners_gap.py --check` takes about 0.8 s and `tools/audit/prepr.sh` never calls it. This is claimed to be the same class as #1589 (merge b891be9e, "pin check scripts"): verify that claim from git history, don't take it.

## Owed (root-cause.md §1–5)
1. Reproduce at a897272a and at 81f2c18c (null control).
2. Process state (a)–(d) with evidence (the pinning to the base's check scripts, decision 0013 / #1589, is itself a process; did its precondition change, or was a local path never given?).
3. Class reach: every check whose PR grading uses the base's copy while main's push uses the head's — list them, and for each whether a local path (prepr.sh, a hook, run.sh) runs it before the push. Count the historical instances (git log, RELEASE_NOTES.md, closed issues) for P(recurrence).
4. Cost test with numbers (standing seconds per push vs defect cost × P).
5. If it passes: the countermeasure (likely wiring the pinned checks, or at least codeowners_gap.py --check, into prepr.sh or the pre-edit hook), demonstrated failing on a897272a and passing on c6ca4132, not firing on 81f2c18c. Touching prepr.sh / hooks / policy needs tvofi's approval (the Mac seat holds a mandate until 2026-09-26T09:35Z); say so in the body.

A second, separate root-cause case (bug 5 "all toggles on after reboot", reached a release) will be briefed as RC2 when its fixer names a cause; do not start it.
