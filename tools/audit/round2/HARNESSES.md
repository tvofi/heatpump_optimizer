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

## Which SHA, exactly

`audit-round2-evidence` has moved once, and it moved by name only: this
section names the three SHAs the move is between, so a reader has one to
cite instead of the tag name alone. Three SHAs matter and they are not
interchangeable:

- **`c398fc84`** -- where the round-2 numbers were **recorded**. It contains
  no `tools/audit/round2/` at all; that absence is exactly why the harnesses'
  docstrings say `Command (from the export root)` and why re-executing one
  needs the two-tree recipe below, not a single checkout.
- **`de668be`** -- where the tag pointed originally, the **archived** state:
  the harnesses as frozen, B5-broken, unrepaired. Still reachable directly by
  SHA even though the tag no longer names it.
- **`757e164`** -- where `audit-round2-evidence` points **today**, the
  **runnable** state: five harnesses repaired (`D6/claims.py`,
  `D1/lifecycle_realloop.py`, `D8/matrix.py`, `D9/h6_payload_bytes.py`,
  `D10/check_rules.py`) against the `entry.runtime_data` migration (`3da0e27`,
  #207). `git diff --stat de668be 757e164` is exactly those five files.

Cite the SHA you actually ran, not just the tag name. The tag will move
again; a bare name will not tell a future reader which of these three trees
produced the number they are looking at.

## Why

These are fuzzers, mutation drivers, file walkers and browser rigs. By the
nature of what they do they carry `eval`, `exec`, `urlopen`, `subprocess` and
`shutil.rmtree` — `eval(` in 5 files (`D10/A/ast_checks.py`,
`D10/icons_harness.py`, `D5/comment_numbers.py`, `D5/reader_paths.py`,
`D6/claims.py`), `exec(` in 3, `urlopen` in 4, `subprocess.` in 16 (`.py`/
`.mjs` only; the count is different if the four `.sh` harnesses are folded
in, since two of those call `subprocess.run` from an embedded Python child).
That is not a defect in them; a mutation tool that rewrites source files is
supposed to rewrite source files.

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

Measured 2026-09-03 by two sessions and the judge working the same problem
(#334), re-verified 2026-09-04 against a later `main` head (below). Nothing
here was caught when the harnesses were frozen, because nothing re-executes
them: they are evidence, not gated code.

### The numbers are reproducible; the instructions were not

57 of the 69 Python harnesses pin the `c398fc84` baseline in a docstring --
44 spelling out the full 8-char SHA, the rest abbreviated to `c398fc8` -- and
`git ls-tree c398fc84 -- tools/audit/round2` is **empty** — none of them
exist in the tree they name. That looks like broken provenance and is not.
The docstrings say `Command (from the export root)`, and that phrase is
load-bearing: these were run from an export root *against* the baseline tree
and committed afterwards. Two trees, one command.

Re-measured this way, `D6/claims.py` lands on its documented numbers exactly —
273 extracted, 4 stale, 1 false, and the single false row is the same `C092`.
The two apparent mismatches are an offline flag moving 8 link rows between the
`true` and `unverifiable` buckets. So: **the round-2 measurements reproduce.**
What was missing was the recipe, which is now in the docstrings.

### Four rot classes, and only one of them fails silently

A harness that reaches into a production or test file by textual marker
breaks when that file moves (the fourth class, below, breaks a different
way). Four shapes exist here, and the difference between them matters more
than the count:

| class | how it fails | instances |
|---|---|---|
| executable-prefix cut | `IndentationError` / `StopIteration` at import — **loud** | 2, both currently latent on current `main` -- see below |
| section slicing | `ValueError` / `IndexError` at import — **loud** | several, all resolving today -- see below |
| list drift | a plausible number for a tree that no longer exists — **silent** | at least 1 |
| interpreter-version cut | `SyntaxError` at parse, before the harness's own code runs at all — **loud, and earlier** | 1 known -- see below |

**Do not generalise "it fails loudly, so somebody notices."** The third class
breaks that property, and it is the dangerous one: `coverage_suite.sh`'s
hand-maintained `SCRIPTS` list (`D10/coverage_suite.sh:65`, tag-only --
`coverage_suite.sh` does not exist on `main`) went stale and produced a
believable figure that made an already-fixed finding look live. A crash costs
an hour; a plausible wrong number costs a decision, and nobody goes looking
for it.

The list is missing **three** scripts, not one -- an earlier pass here caught
only `tests/config_flow_steps.py`. `tests/run.sh`'s lanes carry three scripts
the frozen `SCRIPTS` list does not: `tests/config_flow_steps.py` and
`tests/structure.py`, both unconditional in the `lane_units` lane, and
`tests/env_drift.py`, which runs once per golden mode inside `lane_golden`.
Named by lane rather than by line on purpose: an earlier draft of this
paragraph cited absolute `run.sh` line numbers, and every one of them
drifted in the very `origin/main` merge that produced this sentence --
anything keyed to a line number is the next instance of the class this
section is about. The first two scripts postdate the `c398fc84` baseline
the list was frozen against; `env_drift.py` predates it and was left out
anyway -- for the reason `coverage_suite.sh:64` itself records: it needs
git, and is not run in a git-less export. Adding just the first back moved
`coverage_config_flow_pct` **+9.8** points and the total **+1.2** -- so
every figure `coverage_suite.sh` has produced against a post-baseline tree
is a **lower bound**, not a point estimate. The fix is to
derive `SCRIPTS` from `tests/run.sh` rather than hand-restate it, since a
restated copy is exactly what froze this list while `run.sh` kept moving --
but `coverage_suite.sh` lives only at the tag, so that derivation is work for
whoever next moves it, not something a docs-only `main` change can do.

**The one that stopped reproducing, and is not repaired.** `D9/d9lib.py:111`
cuts `tests/stress.py` at the marker `R.section("Combination sweep")` and
executes the prefix. `stress.py` gained an `if __name__ == "__main__":` guard
that put the marker four lines inside it, and at `origin/main` `4b6e076`
(measured by the judge on #334, 2026-09-03) that broke every dependent
harness identically:

    IndentationError: expected an indented block after 'if' statement
    on line 1020 (stress.py, line 1024)

`d9lib`'s own docstring still asserts "``stress.py`` has no ``__main__``
guard", which is what turned a one-line break into an expensive one for
whoever debugged it there — the file was misdirecting its reader.

**That specific reproduction no longer holds on `main`.** #388 (`32f309f`,
merged after `4b6e076`) added the single-scenario detection statistic to
`stress.py`'s `__main__` block, ahead of the cut marker: `git diff --stat
4b6e076 <a post-#388 main head> -- tests/stress.py` -> **971** insertions,
13 deletions -- not the 642 an earlier draft of this sentence gave, which
was measured against a `main` that has since moved twice, the exact kind of
staleness this file exists to catch. Naming a single base SHA here would
only set up the next one: `tests/stress.py` has not moved since **#388**
(`32f309f`) -- byte-identical (blob `2d27b210`) at `09ca88f`, `48f4263`,
`00953c2`, `b5b652e` and at this document's own head -- so the comparison
holds against any of them without re-anchoring to whichever happens to be
"the base" this week. The truncated
prefix now ends after real statements instead of immediately inside an empty
`if`, so `compile()` no longer raises.

Verified both ways with the same copied `d9lib.py`: reproducing against a
`4b6e076` checkout of `tests/stress.py` still raises the `IndentationError`
above; against the current blob (`2d27b210`) it does not, and
`load_stress_prefix()` returns a namespace with `reference_solve`,
`Calibration`, `build_case`, `SEASONS` and `BUILDINGS` all present. Running
the ten dependent harnesses end
to end: `d9lib` itself, `h1_grad_equivalents`, `h1b_dhw_loops`, `h3_gil_hold`,
`v2b_f0_identity` and `v2c_consequence` complete cleanly with full `RESULT`
output; `v2_reachability`,
`v3_d901_fixscope` and `v3_d903_memo_golden` were still producing clean
`RESULT` lines when a generous timeout was reached, with no error, so they
are read as slow rather than broken, not confirmed complete. `h7_stress_gate`
still fails, but on a different, semantic cause: it reads `stress["combinations"]`
from the returned namespace, and `combinations` is now assigned by
`combinations = sweep_combinations()` on line 1879 -- two lines **after** the
`R.section("Combination sweep")` cut marker at line 1877, inside the sweep
the harness is cutting away specifically to avoid running:

    KeyError: 'combinations'

**Do not read this as a repair.** Nobody edited `d9lib.py` or its cut marker;
`stress.py`'s tail moved again, coincidentally, in the harness's favour this
time. The class this section is about -- a harness that reaches into
production or test code by a textual marker rather than a stable interface --
is exactly as fragile as it was at `4b6e076`. The next edit to `stress.py`'s
`__main__` block can put an empty block back ahead of the marker as easily as
`#346` removed one, and `h7_stress_gate`'s new `KeyError` is that same class
finding a new way to bite: the prefix compiles, but what it defines has
drifted out from under a caller that assumed a fixed shape. Anyone re-running
this owes it a fresh check against their own `main` HEAD, not this paragraph.

**The latent one.** `D6/rolling_learning.py:48` is the same construction
against `tests/rolling.py`, and it runs clean today for exactly one reason:
`tests/rolling.py` has not yet acquired a `__main__` guard -- it still ends in
a bare module-level `sys.exit(R.close(...))`. Confirmed by injecting one: this
cuts by line prefix (`next(i for i,l in enumerate(src) if
l.startswith("R.section("))`), not by substring the way `d9lib` does, so it
dies louder -- `StopIteration`, not `IndentationError` -- but it dies the day
the guard lands, and `D6/claims.py` reads its output for `C293`, so the
failure propagates.

**The section-slicing sites** (`D10/check_rules.py`, `D10/C/doc_coverage.py`,
`D4/config_flow_ux.py`, `D5/reader_paths.py`) all resolve at the tag and were
executed to confirm it. Deliberately not given as a count: a plain
`.split(`/`.index(` grep across the four files returns a different number
depending on whether a helper call and its caller count as one site or two,
and no rule here is claimed to settle that -- "these four files, executed"
is the honest statement, a digit in front of it is not. Note the limit of
that evidence: **exit 0 proves a harness runs, not that it still measures
what its finding claims.** These are executed, not validated, and the second
bar is unmet for them.

### A fourth rot class the table above needed a row for

`D6/claims.py` cannot even be **parsed** on this box's own interpreter:
Python 3.11.5 raises `SyntaxError: f-string expression part cannot include a
backslash` at `claims.py:1147` (PEP 701 nested-quote f-strings, Python
`>=3.12` only). This is not one of the three shapes above -- it fails before
any of the harness's own code runs, so "at import" undersells it, and it is
about as loud as a failure gets, `python3` refuses to even start. Getting
past it needs a `>=3.12` interpreter in addition to the two-tree recipe and
the entry point given elsewhere on this page; "the round-2 measurements
reproduce" (further up) is true only once that interpreter is in hand, and
this page did not say so until now.

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
