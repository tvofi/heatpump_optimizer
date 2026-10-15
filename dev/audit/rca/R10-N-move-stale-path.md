# RCA: a file move leaves an executable consumer resolving the old path

Seat: round-10 root-cause, class `N-move-stale-path` (#2227). R10 has 36 instances (1
judged, 35 beyond the finding), which meets the per-round trigger. Tree:
`handoff/audit-r10-register` at `2c3272eb7`. This seat fixes nothing.

## Root cause

### Cause, reproduced

The repository reorganisation (lane RO, 17 `fix/r9-ro-*` pull requests) moved files by
`tests/layout.json`. Its barrier, `tests/layout.py`, checks text references. Its
`reference` arm refuses *"a live text file [that] cites a retired `old` path as a path
token"*, and it skips the `historical` prefixes. `layout.json` says they *"keep the paths
that were true when they were written (tvofi's D2)"*. `dev/audit/rounds/` is one of those
prefixes.

An executable reference is different from a citation. A
`sys.path.insert(0, dirname(__file__))` sibling import, or a path literal the program
opens, breaks when either end moves. No arm executes or resolves it. When a consumer and
its dependency land on opposite sides of the historical line, the consumer stops running
and no check notices.

The judged instance shows this. `de46d8da9` (2026-10-07, R9-RO-8, *"move audit evidence one
segment under dev/audit"*) moved `dora_keys.py` into `dev/audit/rounds/round4/D11/`. Its
library `d11lib.py` stayed live under `tools/`, pinned by
`tests/closure.py:639` and `governance.yml:607`. D13's brief names `dora_keys.py` as a
live instrument (`dev/governance/dimensions/D13.md` step 4), so the D13 round runs it.

Reproduced at `2c3272eb7`:

- `python3 -I dev/audit/rounds/round10/D14/sweep-N-move-stale-path/probe_import.py dev/audit/rounds/round4/D11/dora_keys.py 89 d11lib`
  prints `STALE No module named 'd11lib'` and exits 1 in 0.05 s.
- The judge row reads *"dora_keys_loads=0 (ModuleNotFoundError d11lib)"*. With the import
  fixed and the exclusions path registered, it gives 0 -> 1.
- `dora_keys.py:103` also opens `cfr_exclusions.json` at its old `.claude/workflows` home. That file moved to
  `dev/governance/config/cfr_exclusions.json` (`bc0f17ddb`, 2026-10-06), so the instrument
  is broken twice.
- `python3 -I dev/audit/rounds/round10/D14/sweep-N-move-stale-path/enumerate.py .` reports
  `seams=2871 broken=369` in 5.88 s. The R10 sweep measured `seams=2859 broken=367` at
  `9355f107d`.

### Class search

The R10 sweep (`dev/audit/rounds/round10/sweep-N-move-stale-path.md`) gave all 367 listed
seams a disposition:

- 36 instances: 8 sibling imports and 28 path literals;
- 46 guarded: 43 sibling imports by a `tests/` path setup, and 3 literals by a fallback;
- 84 `tools/` and `.claude/` literals, either guarded by move-aware resolvers (`locate()`,
  `at()`, `canon()`, the `layout.json` remap in `policy_lint.mjs`, old-then-new tuples) or
  not applicable as classifier test inputs;
- the remaining 201 not applicable, as fixture data, labels, baseline arguments or output
  paths.

**All 36 instances are under `dev/audit/rounds/`**, a historical prefix. No production or
live-tool seam is unguarded: the live tools already carry the resolver.

The class splits in two. Its counted size depends on which half is a defect:

- **Live-cited.** An executable under a historical prefix that live policy names as an
  instrument to run. `git grep` over `dev/governance`, `.claude/workflows/*.js`,
  `.claude/skills` and `CLAUDE.md` finds two such citations:
  - `dev/audit/rounds/round4/D11/dora_keys.py` (D13.md:35), which is broken;
  - `dev/audit/rounds/round4/D12/units.py` (COMMON.md:52), which the enumerator does not
    flag.
- **Evidence-only.** A round's harness re-runs at that round's baseline, where its paths
  were true. That is D2's rule. The other 35 seams are this kind. At HEAD they fail by
  design, and they cost nothing until someone runs them at HEAD.

### Process state: (c) followed and did not produce the intended result

The move process existed and was followed. Each RO pull request ran `tests/layout.py`, and
the citation was even repaired. `7706f1dad` (2026-10-14, a fix-review round of #2207)
re-pointed D13.md's citation to *"dora_keys.py where [it] lives (dev/audit/rounds/round4/D11/)"*,
so `brief_lint.mjs` resolves it. Every one of these checks keys on whether the **cited
path exists**, not on whether the **cited program runs**. A repaired citation of a broken
instrument passes all of them.

The `historical` exemption is D2's ruling and is right for evidence text. Its precondition
is that nothing under a historical prefix is executed live. D13's brief broke that
precondition when it named a round-4 harness as its standing instrument, and no check
compares the two.

This is not (b): every step was obeyed. It is not (d) alone either, because the brief that
cites the harness predates the move (`61f943011`, 2026-09-16). The precondition was false
at the moment of the move, and the move's checks could not see it.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock per release.

- **Standing cost, two forms.**
  - (i) The whole-tree enumerator as a gate arm: 5.88 s x 18.5 PRs per release
    (314 PRs over 17 release intervals, `v6.7.1..v7.0.0`) = 109 s per release. It also
    needs a reasoned allow-list of the 331 non-instance seams, which churn with every
    new round directory.
  - (ii) A narrow arm that probes only live-cited executables under a historical prefix
    (2 today, at 0.05 s each): 0.1 s x 18.5 = 2 s per release.
- **P(recurrence).** One live-cited instrument broke across 17 move PRs in 122 release
  intervals (`v4.0.0..v7.0.0`), so 0.008 per release. The lane is finished, so a new
  break needs a new move or a new live citation of a historical harness.
- **cost(defect).** The lower bound is the round-9 per-finding fix cost, 4.35 h (#1718:
  21.75 h over 5 findings). The direct cost is the D13 seat's DORA metric
  (*"dora_keys_loads=0"*): one dimension's standing instrument is unavailable for a round.
- **Verdict.**
  - (ii): 1/122 x 4.35 h = 128 s per release against 2 s, so it passes by about 60x.
  - (i): 128 s against 109 s, before any allow-list upkeep is priced. That passes by
    1.2x at best, and (ii) covers the same defective half for 2 s, so (i) is dominated.
  - The 35 evidence-only seams have a field and process cost of about zero while D2
    holds, so a barrier over them buys nothing.

### Countermeasure (a class barrier for the live-cited half, proposed; not built)

It addresses (c). The check moves from "the citation resolves" to "the cited program
runs".

1. **A `tests/` arm (form (ii)).** For every executable path cited from live policy text
   that sits under a `layout.json` `historical` prefix, it does three things:
   - executes the file's own prelude and each sibling import (the R10 `probe_import.py`
     technique);
   - checks that each path literal the file opens resolves;
   - refuses on failure.

   The arm must show:
   - red on this tree (`dora_keys.py`, two reasons);
   - green once it is fixed;
   - null control: `units.py` passes;
   - non-vacuity: at least 2 cited executables are found.

   The arm is policy-adjacent only by what it reads. It changes no rule.
2. **The fix for the instance.** Move `dora_keys.py` back out of the historical prefix,
   next to `d11lib.py` (a live instrument belongs in `tools/`), or import through a
   resolver. Do not hand-patch a path inside historical text. The fixer chooses.
3. **Recorded refusal (form (i)).** No whole-tree barrier over evidence-only harnesses. It is
   dominated in the cost test above, and it would contradict D2.

## Needs tvofi

1. **The disposition of the 35 evidence-only seams.** They break by design under D2. If
   tvofi confirms that, the ledger's instance count for this class overstates the defect
   population about 36-fold, and the class owes the narrow barrier only. This seat changes
   no ledger instance; it records the question.
2. **Optional, policy:** a sentence in `dev/governance/rules/` saying that a standing
   instrument a brief names lives outside the `historical` prefixes. This addresses the
   precondition. It is optional because the arm in point 1 of the countermeasure enforces
   the same thing without a rule.
