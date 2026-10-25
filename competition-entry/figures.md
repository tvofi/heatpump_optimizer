# Figures and their sources

These are the numbers in inlagg.md and the images that are not in draft-owner.txt.

- Repository commands were run from the main checkout on 2026-10-22, after `git fetch origin`.
- `$SRC` is a `git archive v7.0.4` extracted into the seat's scratch directory.
- `$PRCLASS` is the per-PR classification table described in the "PR classification" section below.

Every number in the owner's own draft is the owner's, and none is restated here. Those numbers are the September and October savings, the 0.28 °C error, 95 %, 9 out of 10, 50/50 and round 10.

## Versions and the contest period

| figure | value | command |
|---|---|---|
| current release | 7.0.4 | `git show origin/main:VERSION` |
| v7.0.0 tag date | 2026-10-14 | `git for-each-ref --format='%(refname:short) %(creatordate:short)' refs/tags \| grep ^v7` |
| releases since 16 Oct | v7.0.1 (10-19), v7.0.2 (10-20), v7.0.3 and v7.0.4 (10-22) | same command |
| commits since 16 Oct | 2 768 | `git log origin/main --since=2026-10-16T00:00 --oneline \| wc -l` |
| merged PRs since 16 Oct | 256 | `gh api 'search/issues?q=repo:tvofi/heatpump_optimizer+is:pr+is:merged+merged:>=2026-10-16&per_page=1' --jq .total_count` |
| production diff v7.0.0..v7.0.4 | 45 files, +4 445 / −2 250 | `git diff --shortstat v7.0.0 v7.0.4 -- custom_components` |
| strutsfarm's commits before August | 13 | `git log origin/main --before=2026-08-01 --format='%ad %an \| %s'` (all strutsfarm-era authors) |
| tvofi's first commit | 2026-08-20 | `git log origin/main --reverse --after=2026-08-01 --format='%ad %an' \| head -1` |

## Image 05: the repository in numbers

| figure | value | command |
|---|---|---|
| commits on main | 8 970 | `git rev-list --count origin/main` |
| merged PRs | 1 612 | `gh api 'search/issues?q=repo:tvofi/heatpump_optimizer+is:pr+is:merged&per_page=1' --jq .total_count` |
| issues | 908 | `gh api 'search/issues?q=repo:tvofi/heatpump_optimizer+is:issue&per_page=1' --jq .total_count` |
| branches on origin | 1 409 | `git ls-remote --heads origin \| wc -l` |
| branch prefixes | wip-sync 582, review 170, verdict 169, probe 160, handoff 157, handoff-body 143 | `git ls-remote --heads origin \| sed 's#.*refs/heads/##' \| cut -d/ -f1 \| sort \| uniq -c \| sort -rn \| head -6` |
| tags | 755 | `git ls-remote --tags origin \| grep -v '\^{}' \| wc -l` |
| archive tags | 602 | `git ls-remote --tags origin \| grep -v '\^{}' \| grep -c 'refs/tags/archive/'` |
| release tags | 152 | `git ls-remote --tags origin \| grep -v '\^{}' \| grep -c 'refs/tags/v[0-9]'` |

The prompt shown in the terminal image is a rendered stand-in. It contains no account name or host path.

## Image 06: commits per day

- **Series:** `git log origin/main --format=%ad --date=short | sort | uniq -c`
- **Total:** 8 970, which is the sum of the series and equals the `rev-list` count.
- **Peak:** 644 on 2026-10-18, the series maximum.

## Image 07 and the round-10 figures: PR classification

Build the PR list:

```
git log origin/main --first-parent --format='%H|%ad|%s' --date=short \
  | grep -E 'Merge pull request #|\(#[0-9]+\)$'
```

This gives 1 570 PR commits.

Classify each commit:

- **production:** `git diff --name-only $H^1 $H` lists any path under `custom_components/`.
- **dev flow:** no path under `custom_components/`.
- **status rows (bot):** the subject contains `record/autofix`.

Weekly counts (Monday, production, dev flow, bot):

| week of | production | dev flow | bot |
|---|---|---|---|
| 08-17 | 26 | 5 | 0 |
| 08-24 | 53 | 4 | 0 |
| 08-31 | 100 | 127 | 0 |
| 09-07 | 88 | 212 | 0 |
| 09-14 | 41 | 122 | 0 |
| 09-21 | 80 | 119 | 0 |
| 09-28 | 44 | 91 | 0 |
| 10-05 | 20 | 62 | 11 |
| 10-12 | 21 | 113 | 64 |
| 10-19 | 15 | 71 | 81 |

Round 10 runs from 2026-10-14, when it opened according to `dev/programme/HANDOVER.md` on origin/main.

- **All PRs:** 332, of which 33 are production (9.9 %).
- **Without bot rows:** 188, of which 33 are production (17.6 %).
- **Command:** `awk -F'|' '$1>="2026-10-14"' $PRCLASS`

## Image 08: CI checks on PR #2563

- **Head:** `git rev-parse <merge of #2563>^2` = 4276bf8e7b5f769b5595f35232161ed963501961
- **Check runs:** `gh api "repos/tvofi/heatpump_optimizer/commits/<head>/check-runs?per_page=100"`
- **Counts:** total_count 50, success 33, skipped 16, failure 1 (nightly-status).
- **Mutation job:** 49 min 11 s, from started_at to completed_at.
- **Wall time:** 52 min 57 s from the first start to the last completion. The image rounds it to 53 minutes.
- **Production check:** the merge touches 5 paths under custom_components/, from the classification above.

## Image 09: the policy corpus

The script is `policy_series.sh` in the seat's scratch directory. For the last first-parent commit of each day it runs `git ls-tree -r -l` and sums the file count and bytes.

It counts these files:

- CLAUDE.md
- AGENTS.md
- the rules: dev/governance/rules/*.md, or .claude/rules/*.md where no canonical copy exists yet
- .claude/skills/*/SKILL.md
- .claude/workflows/*.md
- dev/governance/**/*.md
- tools/audit/briefs/*.md
- tools/audit/README.md, dev/audit/README.md and tests/README.md
- docs/decisions/*.md
- .github/PULL_REQUEST_TEMPLATE.md

Values:

| date | files | bytes |
|---|---|---|
| 2026-08-21 (first) | 1 | 2 215 |
| 2026-09-24 | 52 | 326 990 |
| 2026-10-21 | 54 | 367 945 |

The dates of decision 0012 come from `git show origin/main:dev/governance/decisions/0012-process-diet-and-round-cadence.md`:

- recorded 2026-09-24
- the moratorium runs "Until 2026-10-31"
- revoked 2026-10-21 by decision 0014

## Image 10 and the line counts

All counts were taken on `$SRC` (v7.0.4):

| part | lines | command |
|---|---|---|
| integration | 78 267 | `find custom_components -type f \( -name '*.py' -o -name '*.js' \) -print0 \| xargs -0 cat \| wc -l` |
| tests | 192 613 | `find tests -type f \( -name '*.py' -o -name '*.mjs' -o -name '*.js' -o -name '*.sh' \) -print0 \| xargs -0 cat \| wc -l` |
| tools | 74 096 | the same command over `tools`, excluding node_modules |
| dev/ Markdown | 91 276 | `find dev -name '*.md' -print0 \| xargs -0 cat \| wc -l` |
| workflows | 7 352 | `cat .github/workflows/*.yml \| wc -l` |

## The hurdles text

| figure | value | source |
|---|---|---|
| structure budget metrics | 18 | `python3 -c "import json;d=json.load(open('tests/structure_budgets.json'));print(len([k for k in d if k!='recorded_at']))"` on `$SRC` |
| "flera ligger på noll marginal" | qualitative | CLAUDE.md rule 2: "several sit at zero headroom" |
| BLAS spread | 60.54 to 63.48 SEK across four kernels | `git show v7.0.4:tests/README.md`, lines 265 to 270 (#1725) |
| commits touching claimed_drift.txt | 327 | `git log origin/main --oneline -- tests/golden/claimed_drift.txt \| wc -l` |
| secondary rate limit: 403 while 5 000 remain | quoted fact | `git show origin/main:tools/audit/round4/D11/d11lib.py`, docstring |
| flat-price null control: 20 % gain at flat prices; −37.6 % for a fixed heuristic | | `git show origin/main:dev/archive/backlog.md`, lines 2239 to 2250 |
| five measurement designs failed the flat-price control | 5 | the owner's memory note `measurement-discipline.md` in the Claude project memory directory. The repository's backlog lists three of them with figures; the other two (+2.95 and +9.52) are only in that note. |

## Product images

- **01:** the v7.0.4 `docs/index.html` opened from `$SRC` with playwright 1.56.1, the pinned lockfile in `tests/pwlane`, at 1280×800 and scale 2.
- **02 to 04:** made by the repository's own harness with `HPO_PAGES_OUT` and `HPO_HERO_OUT`, running `node tests/card_browser.mjs` on `$SRC`. The plan payload comes from `PYTHONPATH=tests/hastub python3 tests/plan_view.py`, which is fixture data and not a real house. The only change in the scratch copy was an `executablePath` for an existing local Chromium.

## Not calculated

On the owner's instruction, no token or cost figure appears in any file here. One local transcript sum was run before that instruction arrived; its result was discarded and is recorded nowhere.
