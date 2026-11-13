# BLOCKED: r10-advisor-steady-start, round 5: body_push.sh exit 4, REFUSED CARRY-LANDED

The code is handed off: refs/heads/handoff/r10-advisor-steady-start is 41b9a070615ab2c6e383204f47ae21642548687c, the head `tools/pr/prepr.sh` passed with rc=0 (`PRE-PR: 41b9a070615ab2c6e383204f47ae21642548687c ... rc=0`). This ref's tip is that tree with this file added. The body is not on handoff-body/r10-advisor-steady-start: `bash tools/audit/seat/body_push.sh r10-advisor-steady-start <body.md>` refused it and kept it at handoff-wip/r10-advisor-steady-start-body d49e998236e193103b1f9368e6069d4bc4a2fbba.

Question: will the relay land body item 526f4054 on the round's roster branch for R10-HOTFIX-LEGACY-CONTROL-DATA (carry_audit.py land-ops) and re-run body_push.sh with the kept body?

## body_push.sh output, verbatim

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-ADVISOR-STEADY-START at 41b9a070615a, 8 live, 8 dispatched carries, 0 refused
CARRY-MISSING R10-HOTFIX-LEGACY-CONTROL-DATA body item 526f4054: not in its brief or carries: '- tools/policy/brief_lint.mjs `assertLegacyControl` reads a legacy carry as repaired when its contro'
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-advisor-steady-start-body d49e998236e193103b1f9368e6069d4bc4a2fbba
```

## The carry

The item is the survey of the files left in `LEGACY_CONTROL_FILES` of tools/policy/brief_lint.mjs for a control citation that resolves only by line-number accident. R10-HOTFIX-LEGACY-CONTROL-DATA's brief already names that survey as its part 2 and cites this branch's earlier item id 00444e5b for it; the body's item text was re-worded this round, so its id is now 526f4054 and the roster holds no entry under that id. The seat may not write the roster branch.

## State at 41b9a070615ab2c6e383204f47ae21642548687c

- 815f99a3f is reverted (d5d65b490) and origin/main e59e21fee is merged (deb1d2afc); origin/main has since moved to f47250150a, `git merge-tree --write-tree origin/main HEAD` exits 0, not merged again.
- `tests / briefs` stays red at this head by the ruling that gives its repair to R10-HOTFIX-LEGACY-CONTROL-DATA (#3525); the body's Red checks answers it and the CPU-budget red (`tests / replay`).
- prepr at this head: no refusal; two warnings, `diff mutants` (13 survivors of the narrow block command, each driven against tests/features.py whole and killed, listed in the body's Mutation proof) and `push order` (a push must follow the body edit).
- Nothing else is owed by this seat; the step ref is left in place because the body push did not succeed.
