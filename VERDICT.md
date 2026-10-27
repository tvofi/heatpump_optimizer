Fix review: merge 012b795d930ba31e164c1b9a6a6021221007e84d

bus-nonce: 4c5b1ea4d901e1522d94e23be7110ffb

Round 1. Reviewed at a fresh detached worktree at `012b795d930ba31e164c1b9a6a6021221007e84d`, with a second worktree at the merge base `4f3c7302046eccd1f869724a6de2cbf6f8183418`. The fixer's harnesses are not used for the proof below: the fixtures, the mutation deletions and the scoping are mine. `dev/governance/roles/` is unchanged on origin/main against the merge base.

The head is one commit over the authored code head `b13dc43bd994d685a5dd5ff40b08f53af877c6ba`, and that commit touches only `dev/programme/delivery/2874.md`, as the body says.

## The change, as I measured it

`pick()` and the `t==0` live admission both sort on `priority() = (tier, sav, -height, -dur_min, name)`. Tier 0 is `critical_path()` over the open-group graph, computed inside `build_plan` on every call; tier 1 is `roster_lane()` in `PRODUCTION`; tier 2 is ranked by a roster `savings` field (absent last). An unmeasured `size` raises `PlanError` where the base raised `KeyError`.

## Evidence — my own harness, base and head, same fixtures

Written from the roster brief's semantics, not from `selftest()`. Each fixture is driven through `build_plan` loaded from both trees in one process.

```
RESULT total=18 failed=5
  RED [base] a 2h production group starts before an 8h non-production one
  RED [base] the short live production group is the one admitted at t==0
  RED [base] tier 2 orders by savings, absent savings last
  RED [base] an unmeasured XS size does not crash as a bare KeyError
  RED [base] the refusal names the group, the size and the roster
```

All nine head-side arms are `ok`; the null control (two identical builds byte-identical) is `ok` at both ends. The five reds are the before/after the PR claims, reproduced independently. A control on my own harness: my first draft placed groups by the roster's `lane` field and both ends failed — `roster_lane()` derives the lane from `kind` and the name and ignores `lane`, so the fixture was wrong, not the fix; the corrected fixtures are what the RESULT above measures.

On the full live roster (208 groups, `XS` mapped to `S` so it builds) `check_plan` is clean at both ends — 0 violations at base, 0 at head — and the head's tiers over the 70 open groups are `{0: 5, 1: 23, 2: 42}`, so the tiers are populated from the real graph and not a degenerate split.

## Mutation proof — the body's seven rows, deleted by me

I did not re-run the fixer's table. I deleted each row's production text myself, scoped by the enclosing function's `ast` line span (the anchors also occur inside `selftest()`'s own mutation table, so a naive `str.replace` mutates the table; function scoping is required), and required the named check to appear in a `FAIL` line of the mutated copy's own `--self-test`.

```
null control (unmodified copy): rc=0
ok   critical-path-tier  rc=1 assertion=True crash=False
ok   production-tier     rc=1 assertion=True crash=False  (both named checks)
ok   savings             rc=1 assertion=True crash=False
ok   height-tiebreak     rc=1 assertion=True crash=False
ok   live-admission-key  rc=1 assertion=True crash=False
ok   savings-validated   rc=1 assertion=True crash=False
ok   size-refusal        rc=1 assertion=True crash=False
RESULT red=0
```

`crash=False` on every row is the claim the body makes for the two former crash-only kills: both refusal arms now fail on their own assertion, not on a traceback. None of the seven is a no-op — each deletion changes behaviour and each is caught by the check it names. The other six in-file mutants (`earliest-attempt`, `coordinator-cap`, `stamp-cadence`, `ci-formula`, `freshness`, `gate-cancellation`) are base mutants and still die; the in-file harness reports 13/13 non-zero with its own null control at rc=0.

## The external harness

`dev/audit/harnesses/r10_plan_page_mutants.py` re-run in an isolated worktree: `RESULT survived=0` over 19 mutants plus `M0` (`verdict=null`). The new `tier-column` mutant dies on `FAIL every open group's tier is shown, and a merged group's is not`, not on a crash.

## The gate really did measure nothing

Re-derived, not quoted: `tests/closure.py select --diff <merge-base>` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out` and `scope.run` is empty. The body is right that this is zero coverage, not a pass. What actually executes the change is `governance.yml:531` (`python3 -I tools/plan/replan.py --self-test`) plus the `plan_table`/`plan_page` steps at 651 and 658, all three green at this head. That arm does catch a revert: restoring the base `pick()` key and the base admission key fails exactly the three priority fixtures above, so a regression is not invisible.

## Cost of re-deriving the critical path

`critical_path()` is called once per `build_plan`, as it was at the base (it moved, it did not multiply), and the roster is parsed once by `load_roster` before `build_plan` is entered. Measured on the live roster (208 groups, XS mapped to S so it builds): median 56.45 ms at base and 55.72 ms at head over interleaved 20-run batches — flat, ratio 0.987. No D9 cost.

## Class

One seam: the dispatch order. Both sites that order dispatch (`pick()` and the `t==0` admission) are changed and no `-height` key survives in production code. The body names no enumeration rule; the class is one seam, so there is nothing for a rule to return and I do not treat the absence as compliance.

## Friction

- The external mutant harness writes its mutant into the tree it measures and restores it only on the `finally` path. My first run was cut at a tool timeout and left `tools/plan/replan.py` carrying the `E-explicit-ref-wins` mutant; the retry then refused with `tools/plan/replan.py has uncommitted edits`. I restored the file, verified its sha256 against `HEAD:tools/plan/replan.py`, and re-ran every head measurement since in a clean or isolated worktree. Carry: dismissed: the harness restores on every path that is not SIGKILLed, the dirty file was my tool's timeout rather than the harness's defect, and no figure in this verdict was taken from the dirty tree (the stray line is in `stale_reason`, which none of my measurements enters).

## Forward-carry

- The size refusal and the savings refusal both name an arbitrary member of a Python set (`for n in open_`), so the message is not reproducible: over ten runs at `-I` the live roster refused naming three different XS groups (`R10-FLY-WORKTREE-GC`, `R10-FLY-LEDGER-SAMPLE`, `R10-FLY-DAEMONIZE-ARGV`, and once `R10-FLY-SUITE-ENV-FLAKES`, which is the line the body quotes). The plan JSON itself is byte-identical across ten hash seeds with `savings` populated, so only the refusal text moves. Carry: dismissed: the message still names a genuinely unmeasured group on every run, it is strictly better than the base's `KeyError: 'XS'` which named none, nothing in the tree parses it, and the fix would be a one-line `sorted()` with no defect behind it.
- `savings` is a new roster field that no group in `dev/programme/rosters/wave-r10-groups.json` carries (0 occurrences), so tier-2 ordering is exercised only by the fixtures and production behaves as the base inside tier 2. `roster_edit.py` has no op that sets it on an existing group, though `append-group` accepts a JSON body that carries it. Carry: dismissed: the owner's brief defines the field, the selftest pins its ordering and its absent-last rule, and the roster is the owner's to populate.
- Inside the same hunk that refuses an unmeasured size, a *missing* size is still defaulted to a measured `M` (`size = G[n].get("size") or "M"`), which is the same invented duration the refusal exists to prevent. Carry: dismissed: the only roster group without a size is `done` so it never reaches the check, and the default is base behaviour this change does not introduce.

## Residual

- `durations.json`'s new sentence says "no XS duration is derivable from recorded data". I could not check it: the 25-group sample lives in `wave-data.md`, which is not in the tree. What I could measure is that all four done XS groups carry a `commit` that is on `origin/main` and none carries a `branch`, so a merge instant is recorded but the PR's earliest commit — the other half of the stated method — is not. The statement is defensible for the data the roster records; it is not something I verified. Carry: dismissed: a provenance string in a data file, not a figure any check reads, and the refusal it describes is proven above.
- The body's `## Forward-carry` dismissal cites a root-cause seat ("coordinator, 2026-10-27"). Nothing in the tree evidences it, and a dismissal that names an unstarted seat is not a control. It does not bear on this change's correctness, which is why it is a note and not a block. Carry: dismissed: the underlying roster-vocabulary gap is the roster's, not this diff's, and this change closes its own side by refusing the unmeasured size at the boundary.
