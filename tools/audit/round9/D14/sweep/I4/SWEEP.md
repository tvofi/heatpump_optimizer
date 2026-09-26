# Class sweep — I4 (round 9, thread S4)

**Property:** two independent parsers or definitions of one concept disagree.

**Enumerator:** `tools/audit/round9/D14/sweep/I4/enumerate.py`, re-running each finding's
own whole-package harness. `PYTHONPATH=tests/hastub python3
tools/audit/round9/D14/sweep/I4/enumerate.py`

## Positive control

| Finding | Command | Recorded value | This sweep |
|---|---|---|---|
| D7-s3-02 | `screen.py --no-property-exclusion --attribute-only` | 11 dead members (9 + 2 HA-read properties) | reproduced exactly (`dead_methods=11`) |
| D11-s1-71 | `l3_frontmatter_parsers.mjs` | 2 of 6 legal shapes divergent | reproduced exactly (`divergent_cells=2 of 6`) |
| D11-s1-72 | `l3_gov_pin.py` | 3 of 3 new-workflow cells escape the GOV pin | reproduced exactly (`escaping_cells=3 of 3`) |
| D13-s1-01 | `enum_gap.mjs` (`--stats` mode) | `stats_window_merges=201 subject_merges=253 gap=52` | **cited** — `policy_lint.mjs:mainRef()` resolves the window's end at the live `origin/main` remote-tracking ref, not at HEAD or the pinned baseline SHA; the cached `window.json.gz` snapshot only covers commits up to the round-9 baseline, so re-running against the *current* `origin/main` (which has since merged #1641-#1643) desyncs the stub from the snapshot and the run degenerates to `stats_window_merges=0`. Temporarily rewriting `refs/remotes/origin/main` to 1936d5ca locally reproduces the shape of the call but the underlying `--stats` git-log walk still needs a live token for parts of the run and timed out at 60s; value taken verbatim from `tools/audit/round9/D13/s1/REPORT.md` instead of asserted here. |
| D14-s2-03 | `i4_roster.py --seams` | 31 reader sites | reproduced exactly (`i4_reader_sites=31`) |

## Every seam, dispositioned

**D7-s3-02**: 11 seams (the reachability census's own list) — all 11 `LISTED` methods
printed by `screen.py` under both flags. **instance** × 11 (one ratchet mechanism,
`tests/structure.py:measure`, blind to properties and to bare-name loads uniformly across
every member it lists — this is the finding's own claimed scope, already whole-package).

**D11-s1-71**: 2 seams — `trailing_comment` and `list_under_other_key` frontmatter shapes,
where `rules_sync.mjs` and `policy_lint.mjs` parse a rule's `paths:` block differently.
**instance** × 2. The other 4 cells (`single_quoted`, `unquoted`, `flow_style`,
`tab_indent`) agree (`divergent=0`) and the null control over the 10 live rule files shows
zero divergence today (`live_rules_divergent=0 of 10`) — **guarded** in the sense that no
currently-committed rule happens to use either divergent shape, but nothing stops a new
one from doing so (the parsers themselves are still two, and still disagree).

**D11-s1-72**: 3 seams — a new governance-adjacent job added to `pr-contract.yml`,
`budget-raise-gate.yml`, or `budget-raise-gate-rerun.yml`, each escaping `entities.py`'s
GOV pin (which reads `governance.yml` only). **instance** × 3. The control cell (a new job
in `governance.yml` itself) is correctly caught (`pin_passes=False`), confirming the pin
does work for the one file it reads.

**D13-s1-01**: 1 seam — `policy_lint.mjs:enumerateMerges`'s API-mode `fetchPullsBySha`,
which treats every commit whose `/commits/<sha>/pulls` answers `[]` as a stamp and drops
it silently. **instance** (cited, not re-run; see above). Its only caller,
`mergedPRsFromWindow`, is used by both `--stats` and `--record`, so the gap propagates to
every consumer of the window, not just the one this finding measured — no additional
distinct reader surfaced by grepping `mergedPRsFromWindow(\|enumerateMerges(` beyond the
finding's own file list (`.claude/workflows/policy_lint.mjs`).

**D14-s2-03**: 31 seams — every reader of a class id / `class_guess` / `bugclasses.json`
entry under `tools/audit` and `.claude/workflows`, exactly as `i4_roster.py --seams`
prints them (list reproduced in full in the enumerator's stdout; not repeated here to
keep this file within its own budget cap). All 31 are **instance**: each is an independent
piece of code that must agree with `tools/audit/bugclasses.json`'s id set and with the
finding-schema's `class_guess` enum, and nothing enforces that agreement except the ones
`check-wave-script.mjs`'s own tests already assert for its own narrow slice (P11 held by
no D14 seat; schema-refused ids admitted at intake — both named in the finding's own
title).

## Count

N = 5 (all five round-9 findings verified, four reproduced, one cited). No new distinct
mechanism surfaced by widening (D11-s1-72's widening to 3 workflow files and D14-s2-03's
31 reader sites are what each finding's own seam_rule already claimed as its scope).
**N = 5, rca = true** (already ≥ 3; matches the judge).

## Barrier proposal

- **One shared frontmatter parser.** `rules_sync.mjs` and `policy_lint.mjs` each hand-roll
  a `paths:` block reader; extracting the one in `policy_lint.mjs:rulePaths` (already the
  more permissive of the two, per the divergent-cell table) into a shared module both
  files import removes the class entirely for this pair, rather than teaching the two
  readers to agree case-by-case.
- **The GOV pin** (`tests/entities.py`) should derive its watched-file list from
  `governance.yml`'s own `workflow_run` dependents (already partly done — the comment at
  `tools/audit/round4/D11/governance_cost.py` derives it once) rather than hardcoding
  `governance.yml` alone; each new dependent workflow is then in-scope automatically.
- **The class-id roster** (D14-s2-03) is the largest and most diffuse; a single
  `tools/audit/class_ids.mjs` (or `.py`) that every one of the 31 sites imports, replacing
  its own copy of the enum/regex, is the only barrier that actually reaches all 31 without
  auditing each call site by hand at every future round.
- Gate cost for all three: each replaces an inline regex/parse with a `require`/`import`
  of a shared module; no new CI job, negligible added wall time.

## Exposure

D13-s1-01's `--stats` reproduction needs a live `origin/main` at the baseline SHA and (for
the parts of `policy_lint.mjs --stats` beyond the stubbed `curl` calls) apparently more
than a stubbed `GITHUB_TOKEN=stub`; not re-run for real per this thread's no-`gh`,
minimal-network-reruns brief. `refs/remotes/origin/main` was rewritten to 1936d5ca and
back for the attempted reproduction; the repository was left exactly as fetched
afterward (`git rev-parse origin/main` confirmed restored to the live tip).
