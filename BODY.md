# fix(closures): list the round-9 pre-study refit in harness_headers.py's inert_reads

Main at `969c3a5c8` (merge of #2109, the round-9 pre-study documents under
`dev/audit/rounds/round9/prestudy/`) has a red required `closures` check. Its
own output names the defect:

```
INERT READS UNDER-APPROXIMATED: a recording opened an INERT file the
  committed `inert_reads` does not list for it; the merge fast path
  would treat a change to it as unread (R9-F10.9d). Re-derive:
  ./tests/derive_closures.sh --single <script>
    tests/harness_headers.py: dev/audit/rounds/round9/prestudy/boost_drift_refit.py
```

`closures-autofix` on main read **skipped**, so no bot commit is coming.

## The change

One line added to `tests/closures.json`, in `inert_reads`'s entry for
`tests/harness_headers.py`, in that entry's existing ASCII sort order
(`round9/fixplan/` < `round9/prestudy/` < `round9/rca/`):

```
   "dev/audit/rounds/round9/prestudy/boost_drift_refit.py",
```

Nothing else in the file changes. This is a data-file repair — exactly what
the autofix bot would have pushed — not a behaviour change. No `VERSION`,
manifest version or `RELEASE_NOTES.md` heading is touched.

## Figures

- **The scoped gate at this head** (`D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`):
  `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` — `RUN tests/entities.py`,
  32 SKIPs. Ran it: `PYTHONPATH=tests/hastub python3.13 tests/entities.py`
  → `ALL 2250 ENTITY CHECKS PASSED`, rc=0. (Local `python3` is 3.11.5 and
  cannot parse the tree's nested f-strings; `python3.13` needed `pyyaml`
  installed to the user site for this run.)
- **`closure.py check --partial` was NOT runnable locally**: the command CI
  runs is `python -u tests/closure.py check --in-dir "$RUNNER_TEMP/closures"
  --partial` (`.github/workflows/tests.yml`), and `--in-dir` is the
  strace-based Linux recording directory, which `gate-scoping.md` forbids
  reproducing off Linux (`derive_closures.sh` not run, per the same rule). CI
  is the authority; its failure text itself names the missing entry, which is
  the measurement this commit satisfies. Local structural verification that
  was possible: `tests/closures.json` parses, the entry now holds 541 paths,
  the added path is present, and the list remains fully sorted.
- **`python3 tests/structure.py`** at this head: `STRUCTURE RATCHET PASSED`
  (`seam_cut_total 762 <= 762`).

## Second-finding check

`python3 tests/layout.py --guard` at this head: `layout: GUARD: 0 refusal(s)
against d3dbf2c3fc42` — clean; no pre-study path citation is refused.

## Not a mutation proof

No production line is added or deleted; the diff is one data row the CI
recording already measured as opened-and-unlisted. A mutation of the row
(delete it) is precisely main's current red state, quoted verbatim above.

## Head

`fdb05e622648e0d0ade13bd7521934b67b3813cf` on `fix/closures-inert-prestudy`
(worktree `/Users/timmalmstrom/hpo-seats/r9fix-closures/wt`), measured against
`origin/main` at `969c3a5c84d0ee6fb403ecebd18d16c810b3e40c`, 2026-10-10.

## Red checks

The red this PR clears is main's required `closures` check, failing with
`INERT READS UNDER-APPROXIMATED` naming
`tests/harness_headers.py: dev/audit/rounds/round9/prestudy/boost_drift_refit.py`
(quoted verbatim above). The fix adds exactly that entry; the check is
answered by CI's own re-run of the recording comparison at this head — the
only environment that can run it (see `## Figures`).

## Mutation proof

n/a: no production line is added or deleted; the diff is one data row in
`tests/closures.json`. The row's absence *is* the mutation, and main is
currently red on exactly that mutant — quoted verbatim at the top.

## Null control

n/a: no performance, cost or gain claim is made. The one count in `## Figures`
(541 paths in the entry) states its rule (the `inert_reads` list for
`tests/harness_headers.py` after this commit) and its falsifying result would
have been a parse error or a `sorted(l) != l`.

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
