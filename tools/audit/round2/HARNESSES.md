# The harnesses live on a tag, not on main

Every finding's report, panel verdict, judge verdict, quiet-window log and
mutant patch is still here. The **executable** harnesses — 79 files, about
22,000 lines of Python and JavaScript — are not, and are reachable in full at
the annotated tag `audit-round2-evidence`:

    git checkout audit-round2-evidence
    PYTHONPATH=tests/hastub python3 tools/audit/round2/D9/h1_grad_equivalents.py

## Why

These are fuzzers, mutation drivers, file walkers and browser rigs. By the
nature of what they do they carry `eval`, `exec`, `urlopen`, `subprocess` and
`shutil.rmtree` — `eval(` in 4 files, `exec(` in 3, `urlopen` in 4,
`subprocess.` in 16. That is not a defect in them; a mutation tool that
rewrites source files is supposed to rewrite source files.

On `main` it is a permanent dangerous-pattern surface in a repository that
users clone, and it had a concrete cost: a pre-push security scanner flagged
21 high findings across `D1`–`D9` and `quiet/`, and refused **every** push and
**every** release stamp from the session that ran it — regardless of branch or
of what that session had actually changed, because the scan keys on repository
state rather than on a diff. One session could not ship at all.

Hardening was considered and rejected as the primary fix: for the fuzzer and
the mutation driver the flagged behaviour *is* the intended behaviour, so the
sites cannot all be made to look safe without making the tools useless.

`tools/` never reaches a Home Assistant install — HACS ships
`custom_components/` — so nothing here was ever running on a user's system.
The exposure was to anyone cloning the repository and to anything scanning it.

## What stays, and why it is enough

`docs/audit-2026-09.md` is the register and cites no harness path. `JUDGE.md`
carries every re-measured number with the exact command that produced it. Each
finding's GitHub issue quotes its decisive number, its command and its harness
path. So a reader can follow any finding end to end from `main`; only
*re-executing* one needs the tag.
