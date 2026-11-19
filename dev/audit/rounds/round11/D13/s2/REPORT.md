# D13-s2 — round 11, process yield and cost: steps M3 and M6

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, box B8 (shared, light seat). Cells:
`check_scopes.py --seat D13-s2` prints `M3+M6  -  (any file: no file axis)`.

## Window and population

- Window: `v7.1.0..92d38ecb` (the minor stamp that followed decision 0016's
  rule 2, through round 10's closeout v10.0.0 and round 11's pre-round merges).
  612 first-parent commits; 569 map to a merged pull request by
  `/repos/<slug>/commits/<sha>/pulls` (rows kept only where `merge_commit_sha`
  equals the commit); 43 are stamps or direct pushes; **api_failures 0**.
- Snapshot: `window.json` (`fetch_window.py`): per PR the title, author, body
  and every issue comment and review over all pages. Comment and review bodies
  are kept whole only when their trimmed first line starts `Fix review`; any
  other comment keeps its first line, all the verdict walk reads of it. Both
  harnesses run offline over it, so every number below is a count over a fixed
  set and the judge can re-run it, or re-fetch with `fetch_window.py`.

## Method

**M3** (`block_classes.mjs`). Every blocked verdict is classified by
`policy_lint.mjs:statsHistogram` over the snapshot, with the class words from
`blockClasses()` and the grammar from `waveVerdictRe()`, both read out of
`web-fix-wave.js`. A word the vocabulary lacks keeps its own row. The rows are
bucketed into engineering, record-and-body and orchestration. The mapping is
stated in the harness header: taught words by what the class names, untaught
words by the reasons written beside them. Arm (c) reads the same window through
`fetchWindow` itself, with a stub `curl` that serves the snapshot under GitHub's
paging.

**M6** (`friction_keys.mjs`). Every `## Friction` entry `frictionEntries`
accepts is resolved by D13.md's rule against the `--budgets` paths
(`sizes(policyFiles())`, 55 paths): one path, several (ambiguous) or none. The
production key for each entry comes from `policy_lint.mjs
--normalize-friction-keys` (frictionKey). A self-check asserts that the per-entry
keys equal `statsHistogram`'s own friction cells (`SELFCHECK ... yes`).

## Results

### M3: block classes, three ways (448 blocked verdicts, 647 merge verdicts, 0 outside the grammar)

| bucket | verdicts | share |
|---|---|---|
| engineering | 259 | 0.578 |
| orchestration | 95 | 0.212 |
| record-and-body | 94 | 0.210 |

Taught classes: class-open 84, mutation-vacuous 79, carry-missing 21,
root-cause-unanswered 12, root-cause-detectable 11, root-cause-unrecorded 7,
harness 7, architecture-unsound 5, metric-gamed 5, head-moved 2, conflict 1.
These seven are 0: null-control, claims, version, preflight-mismatch, other,
product-tradeoff-regression and the bare form. **Untaught words: 214 verdicts,
93 words.** The largest is ci-red at 63, then mutation-survivor 9, introduced-red 8,
body-stale 7 and others; the full rows are in `block_classes.out`.

Severity check (D13.md): the body-figure words come to 17 verdicts
(figure-wrong 3, figures-uncited 3, figure-mislabelled 1, figure-false 1,
body-stale 7, body 1, body-not-applied 1). The largest engineering class is
class-open at 84, so the `high` bar is not met. The whole record-and-body bucket
is 94, which is above any single engineering class but below the engineering
bucket's 259.

### M6: the friction histogram's keys (174 accepted entries, 0 unparsed)

- One file: **69 (share 0.397)**. Ambiguous: 0. No file: 105 entries, 84 distinct ids.
- Spellings per file:
  - `tools/audit/briefs/fixer.md`: 38 entries over 20 PRs, spelled `fixer.md` 32, `fixer` 5 and `fixer.md#2` 1.
  - `finding-propagation.md`: 5, spelled `.md` 3 and bare 2.
  - `gate-scoping.md`: 5, spelled bare 3 and `.md` 2.
  - `ci-autofix.md`: 4, spelled bare 2, `.md` 1 and the full path 1.
  - `orchestrator.md`: 3, spelled `.md` 2 and bare 1.
  - `defect-root-cause.md`: 3, spelled bare 2 and `.md` 1.
  - `ratchet-budgets`, `designer` and `brief-citations`: 2 each, one bare and one `.md`.
  - `design-review.md`, `fix-review.md`, `writing-for-agents`, `standing.md` and `claim-files.md`: 1 each.
- Where the brief's rule and frictionKey disagree (12 entries): `fixer` 5 and
  `orchestrator` 1 name one file by the rule but keep their verbatim key in
  production, because of frictionKey's briefs carve-out. In the other direction,
  frictionKey's prefix walk resolves 6 entries (`fixer.md-step-3` and similar) that
  the rule leaves without a file. One file reaches the threshold of 3 PRs only
  under the rule: `orchestrator.md` has 3 PRs by the rule and 2 under its best
  production key.

## Findings

- **D13-s2-01** (M3, medium, N-vocabulary-drift). 214 of the 448 blocked
  verdicts (0.478) carry a class word that VERDICT_CLASSES lacks. 71 of them are
  words that bus.sh's MECHANICAL_CLASSES and fixer.md:311 teach, and 9 of bus.sh's
  12 mechanical words are absent from VERDICT_CLASSES. Perturbation:
  `--perturb teach-ci-red` takes the count from 214 to 151.
- **D13-s2-02** (M6, medium, N-vocabulary-drift). Only 69 of the 174 accepted
  friction entries (0.397) name a policy file. checkPrBody refuses an entry's
  shape, never an id that names no rule. Perturbation: `--perturb readme`
  re-spells #3185's entry as `README.md`, which moves one_file from 69 to 68 and
  ambiguous from 0 to 1. `bare` and `unticked` move no file's count.

## Non-findings

- 0 `Fix review:` first lines fall outside VERDICT_RE over the window
  (`block_classes.mjs`, RESULT outside_grammar=0).
- All 448 blocked verdicts arrived as issue comments and none as reviews
  (`block_classes.mjs --list | awk '{print $2}' | sort | uniq -c`).
- fetchWindow reads one page of 100 per endpoint without paging. In this window
  no PR carries more than 100 comments or reviews, so it loses 0 verdicts
  (arm (c): fetchwindow_lost_verdicts=0, prs_over_one_page=0). The defect is
  latent; it is passed on as a lead.
- The `high` severity bar (body figures above any engineering class) is not met:
  17 against 84.
- The friction contract and the histogram agree: 0 accepted entries go unparsed,
  and the self-check holds.
- The `orchestrator.md` threshold split (3 PRs by the rule, 2 in production)
  follows frictionKey's documented briefs carve-out. Its bare `orchestrator`
  entry (#3625) records a seat's own cost, not the contract, so the carve-out's
  reading holds on this window's evidence.

## Unfinished

None. M3 examined 448 of 448 blocked verdicts and M6 examined 174 of 174
accepted entries.

## Harnesses

`fetch_window.py` (network, writes `window.json`), `block_classes.mjs`,
`friction_keys.mjs`; outputs in `block_classes.out` and `friction_keys.out`.

## Exposure

The brief's GitHub sources, read through `gh api`:

- `/repos/tvofi/heatpump_optimizer/commits/<sha>/pulls` for the 612
  first-parent commits of `v7.1.0..92d38ecb`.
- `/pulls/<n>`, `/issues/<n>/comments` and `/pulls/<n>/reviews`, all pages, for
  the 569 merged PRs.
- main's first-parent history (`git log --first-parent`).

The verdict and friction text is used as population and was not read for
direction.
