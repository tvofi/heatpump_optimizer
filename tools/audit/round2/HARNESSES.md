# The harnesses live on a tag, not on main

Every finding's report, panel verdict, judge verdict, quiet-window log and
mutant patch is still here. The **executable** harnesses — 79 files, about
22,000 lines of Python and JavaScript — are not, and are reachable in full at
the annotated tag `audit-round2-evidence`:

    git checkout audit-round2-evidence
    PYTHONPATH=tests/hastub python3 tools/audit/round2/D9/h1_grad_equivalents.py

**That command does not work today.** It is one of ten files that die in
`d9lib.load_stress_prefix`, for the reason in "What is broken" below. Read
that section before trying to re-execute anything here.

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

## What is broken, and how to run these anyway

Measured 2026-09-03 by two sessions working the same problem (#334). Nothing
here was caught when the harnesses were frozen, because nothing re-executes
them: they are evidence, not gated code.

### The numbers are reproducible; the instructions were not

63 of the 69 Python harnesses pin `c398fc84` as their baseline in a docstring,
and `git ls-tree c398fc84 -- tools/audit/round2` is **empty** — none of them
exist in the tree they name. That looks like broken provenance and is not.
The docstrings say `Command (from the export root)`, and that phrase is
load-bearing: these were run from an export root *against* the baseline tree
and committed afterwards. Two trees, one command.

Re-measured this way, `D6/claims.py` lands on its documented numbers exactly —
273 extracted, 4 stale, 1 false, and the single false row is the same `C092`.
The two apparent mismatches are an offline flag moving 8 link rows between the
`true` and `unverifiable` buckets. So: **the round-2 measurements reproduce.**
What was missing was the recipe, which is now in the docstrings.

### Three rot classes, and only two of them fail loudly

A harness that reaches into a production or test file by textual marker breaks
when that file moves. Three shapes exist here, and the difference between them
matters more than the count:

| class | how it fails | instances |
|---|---|---|
| executable-prefix cut | `IndentationError` at import — **loud** | 2 (1 broken, 1 latent) |
| section slicing | `ValueError` / `IndexError` at import — **loud** | 11, all resolving today |
| list drift | a plausible number for a tree that no longer exists — **silent** | at least 1 |

**Do not generalise "it fails loudly, so somebody notices."** The third class
breaks that property, and it is the dangerous one: `coverage_suite.sh`'s
hand-maintained `SCRIPTS` list went stale and produced a believable figure that
made an already-fixed finding look live. A crash costs an hour; a plausible
wrong number costs a decision, and nobody goes looking for it.

**The broken one.** `D9/d9lib.py:111` cuts `tests/stress.py` at the marker
`R.section("Combination sweep")` and executes the prefix. `stress.py` has since
gained an `if __name__ == "__main__":` guard, and the marker now sits four
lines inside it, so the extracted prefix ends mid-block:

    IndentationError: expected an indented block after 'if' statement

The guard is at line 821 at this tag and 830 on current `main` — the same
four-line offset in both, at different absolute positions. Anything keyed to a
line number is the next instance of this class. Ten files are affected:
`d9lib` itself plus `h1_grad_equivalents`, `h1b_dhw_loops`, `h3_gil_hold`,
`h7_stress_gate`, `v2_reachability`, `v2b_f0_identity`, `v2c_consequence`,
`v3_d901_fixscope`, `v3_d903_memo_golden`. `d9lib`'s own docstring still
asserts that "``stress.py`` has no ``__main__`` guard", which is what turned a
one-line break into an expensive one — a reader debugging it is being
misdirected by the file.

**The latent one.** `D6/rolling_learning.py:48` is the same construction
against `tests/rolling.py`, and it runs clean today for exactly one reason:
`tests/rolling.py` has not yet acquired a `__main__` guard. The day it does,
this dies the same death, and `D6/claims.py` reads its output for `C293`, so
the failure propagates.

**Eleven section-slicing sites** (`D10/check_rules.py`, `D10/C/doc_coverage.py`,
`D4/config_flow_ux.py`, `D5/reader_paths.py`) all resolve at the tag and were
executed to confirm it. Note the limit of that evidence: **exit 0 proves a
harness runs, not that it still measures what its finding claims.** These are
executed, not validated, and the second bar is unmet for them.

### One site deliberately left broken-by-design

`D6/claims.py:233-235` slices the README on markers that embed the very counts
the harness checks:

    md_table_rows(README, "### Sensors (55 total)", ...)

Add a sensor and the heading becomes `(56 total)`, `split(marker)[1]` raises,
and the harness that exists to detect documentation drift is broken *by*
documentation drift. It is intact at both SHAs and has been left alone on
purpose: changing what the table reads, without a recorded number to check the
change against, is the one edit that could silently move a measurement.

### If you repair one of these

Land the repaired harness on its **recorded number from the baseline tree**.
That is a null control on the repair itself — a patch that distorted the table
could not hit the old number from the far side. It is strongest where a
per-row table exists to match (as `claims.py` has); where only `RESULT`
scalars are recorded it is weaker, though still far better than "it imports
without raising".
