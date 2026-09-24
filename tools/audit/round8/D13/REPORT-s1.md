# D13, round 8, seat s1: process yield and cost

Baseline `cdf82da`. Window `c310541..cdf82da`, from the v6.6.6 stamp (the shallow clone's oldest first-parent commit) to the baseline: 92 first-parent commits, 88 merged PRs and 4 stamps, 3.33 days, `api_failures=0`.
The artifact of record is `report-s1.json`. Its ids follow the task's `D13-s1-NN` form, which the schema's id pattern rejects. That is the only schema error.

## Method
- `s1_gh.py` is a GET-only REST transport installed as `d11lib.api`. This box has no `gh`, and the proxy refuses GraphQL and `/tags`. It is cached and counts failures.
- `s1_window.py` enumerates the window through `/commits/<sha>/pulls`, the API mode of `enumerateMerges`. For each PR it fetches the body, both verdict endpoints (paginated), and `d11lib.check_runs` at the merge commit and at the head.
- `s1_yield.mjs` produces outputs 1, 2, 3 and 6. It evaluates `web-fix-wave.js`'s own `VERDICT_RE`/`VERDICT_CLASSES`/`parseVerdict`, imports `policy_lint.mjs:statsHistogram`/`frictionEntries`, and cross-checks both against production: verdict PRs 80=80, friction entries 69=69.
- `s1_dora.py` produces outputs 4 and 5. It drives `dora_keys.latest_by_name`/`cfr_keyings`/`cfr_by_name`/`load_exclusions` and `governance_cost.dur`/`GOV`, with GOV re-derived from `governance.yml`.

Commands (from the tree root):
```
PYTHONPATH=tests/hastub python3 tools/audit/round8/D13/s1_window.py
TMPDIR=/home/claude/audit-r8/tmp/D13-s1 HPO_PLANDATA=/home/claude/audit-r8/tmp/D13-s1/plandata node tools/audit/round8/D13/s1_yield.mjs
PYTHONPATH=tests/hastub python3 tools/audit/round8/D13/s1_dora.py
```

## Required outputs
1. **Yield:** 77 of the 80 merges that carry a verdict have `merge` as their first verdict, a first-pass yield of 0.963. Rounds per merge: mean 1.25, max 3. All 100 verdicts are issue comments; none arrived as a review. One verdict falls outside the grammar (#1287) and is counted on its own row. The one-round yield is **0.8125** (see D13-s1-01).
2. **Coverage:** 8 of 88 merges carry no verdict. By the brief's title-prefix classes: record-and-chore 5 of 28, fix-and-feature 3 of 59, other lanes 0 of 1, bot cycles 0. By approval path: **owner-approved 8 of 22, app-approved 0 of 66** (see D13-s1-02). No rule exempts either class.
3. **Blocks:** 4 in total. By class: product-tradeoff-regression 1, root-cause-unanswered 1, claims 1, outside grammar 1. By bucket: engineering 1, record-and-body 2, orchestration 0. The buckets are defined in the harness header.
4. **DORA:** 1.2 releases per day. Lead time: median 7.89 h, p90 23.74 h. Change-failure rate at the merge commit: 0.989 unexcluded, 0.102 after exclusions. At the head it is 0.068, all of it delivery-status, a main-state detector answered in all 6 PR bodies. No reverts. Excluding `mutation` moves the merge-commit rate 0.102 -> 0.057 (exactly 4/88), and the head rate does not move.
5. **CI seconds per merge:** governance median 160 s and mean 212 s at the head; the gate median 4041 s and mean 5078 s. Governance share: 0.040 at the head, 0.036 at the merge commit. The re-derived GOV equals the carried set. Dropping `pr-contract` from GOV moves the head share 0.040 -> 0.034.
6. **Friction:** 69 entries. 52 name one file (share 0.754), 0 are ambiguous, 17 are unresolved. The spellings per file are in the harness output. The two re-spelling perturbations behave as the brief states.

## Findings
- **D13-s1-01 (medium).** 15 of the 20 extra review rounds re-verified a head that moved after a `merge` verdict, and all 15 returned `merge`. Why the heads moved: origin/main merged in (6), a bot autofix commit (3), a content commit (6). Production's `head-moved` row reads 19, which is 15 re-verifications plus 3 repairs plus 1 duplicate.
  - Null control: at the first-round block rate, 0.56 catches would be expected, so the finding claims only the cost share, not that these rounds are worthless.
  - Perturbation: `--pin-head 1375` moves the re-verification count 15 -> 14 and production's row 19 -> 18.
- **D13-s1-02 (medium).** All 8 merges without a verdict went through the owner-approval path: 8 of 22 there, against 0 of 66 app-approved. Also, 2 merges (#1444, #1426) carry verdicts, but none names the merged head.
  - Perturbation: `--reshape 1493` moves no-verdict merges 8 -> 9 and production's verdict PRs 80 -> 79.

## Unfinished and gaps
- The window is limited to the shallow clone.
- At 31 heads, two Governance runs started 1 s apart. The cause is not established.
- The round-4 instruments cannot run as committed on this box (no `gh`, no GraphQL, no tags).

## Exposure
- GitHub REST API, read-only, as listed in the JSON.
- main's git history in the tree.
- The GitHub MCP tools were not used.
