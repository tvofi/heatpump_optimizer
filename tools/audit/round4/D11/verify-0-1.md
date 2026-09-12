# D11 round 4 — verifier seat 1 report

- **worktree** `/Users/timmalmstrom/.zcode/workspace/default/audit-r4-verify-D11-1`, detached at `0855277` (branch head; 25 commits past the baseline `7dd68dd`, merge of origin/main)
- **date** 2026-09-12, measured 15:24–16:05 UTC
- **interpreter** `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`, `PYTHONPATH=tests/hastub`, from the worktree root; node v20.10.0
- **stance** refute-first; every finding re-measured with a harness I wrote myself (`d11_own_D11-0*.py`, beside the finder's) plus a re-run of every finder harness exactly as its header commands
- **timing** no timing RESULTs exist in this dimension; every number below is a count off the live GitHub API (fetched read-only with `gh`, authenticated as `tvofi`) or a static tree count. `load1`/`thread_factor` do not apply and are not quoted; two `d11_own` harnesses print `api_failures` instead, which is the real control on these figures. All runs reported `api_failures=0`.
- **cache note** the finder harnesses read `~/.cache/hpo-d11-round4` (populated 13:12–13:26Z by the finder; their windows are pinned closed at the baseline, so the cache is the correct reproduction path). My own harnesses fetch fresh into `/tmp/d11-own-verify1-cache`. Where live state had moved I quote both numbers and the timestamp.

## Reproduction of the finder's harnesses (all run at tree head 0855277)

| harness | expected (baseline) | my re-run | verdict |
|---|---|---|---|
| `ruleset_probe.py` | pr_rules=0, bypass_always=1, applies_to_merger=1, ctx=16, **mismatches=8** | all exact except `tree_claim_mismatches=4` | matches; the mismatch drop is the anticipated post-baseline tree movement (below) |
| `merge_census.py` | merged_all=592 reviewed=0 window=164 first_contract_green=139 red_required=28 red_answered=10 disposition=164 | **exact on every line**, SET CHECK graphql=592 rest=592, authors {tvofi:589, claude:3}, review states {COMMENTED:8} | reproduced |
| `untrusted_text.py` | obey=8 guard=0 public, shell_interp=3/0 | exact; `write_permission_blocks` drifted 2→3 (tree grew one declared write block; not load-bearing) | reproduced |
| `mechanism_inventory.py` | mechanisms=73 driven=9 fired=9 inert_in_ci=1 | exact; `--red` arm: rc=1 with `--red 'fast (3.14)'`, rc=0 through CI's list, governance.yml passes `--red` False | reproduced |
| `dora_keys.py` | cfr_any=0.477 cfr_gov=0.441 cfr_tests=0.117 heads=222 record=58/60 | exact on every load-bearing line; lead-time drifted (median 7.13 h n=217 vs 7.41 h n=212) because tags v6.4.3+ landed after the baseline and release more of the window's merges — a tree-state artefact, window closed, cfr figures unaffected | reproduced |
| `governance_cost.py` | gov 75 s / gate 758 s / share 0.058 / rounds 1.63 | exact | reproduced |
| `verdict_sample.py` | sample=41 any=16 merge=16 head_named=15 authors=1 | exact | reproduced |
| `standards_scorecard.py` | 5/1/4, slsa 0, 32 criteria | exact | reproduced |

## D11-01 — critical — merge to main needs no review — **vote: verify**

**My metric**: count of `pull_request`-type rules in the live ruleset and in every version of its history (the only rule type that can require approval), plus merged-PR approval counts from two oracles that share no code path with the finder's GraphQL census (the GitHub search index and direct REST `pulls/{n}/reviews` on a systematic 1-in-10 sample), plus the live bypass table mapped against the authenticated (merging) identity.

**My number (live, 2026-09-12T15:24Z, `d11_own_D11-01.py`, api_failures=0)**:

```
live_ruleset_pr_rules=0        live_ruleset_versions=5   live_history_pr_rules=0
search_merged_prs=602          search_merged_approved=0  (search_merged_changes_requested=0)
rest_merged_census=602         sample=61                 sample_approved_any=0
sample_approved_nonauthor=0    admin_bypass_always=['RepositoryRole:5']
authenticated_admin=1
```

**Attacks and outcomes**
- *Cache hides live state?* No — my fetch is fresh; merged count moved 592→602 (10 merges since baseline), proving the measurement tracks live state, and the conclusion is unchanged on the larger population.
- *GraphQL `reviews` under-reporting?* Refuted by two independent oracles: the search index (`review:approved` → 0 of 602) and REST reviews on 61 PRs (0 APPROVED at all; the only review state GitHub has ever recorded is 8 COMMENTED, per the census re-run).
- *Version history incomplete?* 5 versions live, same as cached; none has ever carried a `pull_request` rule; required set went 18→17→16 with the finder's timestamps reproduced.
- *Bypass arm wrong?* Both arms re-read: `rules/branches/main` = 16 contexts, no bypass field; ruleset object = same 16 + `RepositoryRole 5 bypass_mode: always`; authenticated identity `admin: true`. The disagreement by construction is real.
- *Severity?* Earned: the corpus describes the boundary as guarded, all keyed standards fail on this one fact, and — the amplifier — seats hold merge grants (D11-02) with no second party between them and `main`. The decision being deliberate (0005/0008) is acknowledged in the finding itself; the defect measured is that no instrument would notice the ordered plan stalling, and none exists (no tree file outside audit-round evidence reads the rulesets API — checked, see D11-04).

## D11-02 — critical — seats obey public comment text; zero countermeasure sentences — **vote: verify**

**My metric**: whole-tree walk (not the finder's fixed file list — includes `AGENTS.md` and `.cursor/rules/`, both newer than the finder's corpus list) counting (a) seat-corpus lines directing an agent to read issue/PR bodies or comments and treat them as authority, (b) trust-boundary sentences anywhere in policy+seat corpus under a broader net than the finder's (adds "attacker", "trust boundary", "malicious", bare "not instructions"), (c) live writer population.

**My number (`d11_own_D11-02.py`)**: my deliberately noisy obey-pattern fires 24 lines; every strong site the finder counted is among them (`web-triage.js:153` "comments … override the body", `web-fix-wave.js:242/285/289`, the `pull_request_read` boilerplate ×5) and no new strong-site class appears. Guard hits under the broad net: **2**, both non-countermeasures — `tools/audit/briefs/D11.md:47` (this audit's own dimension brief naming "prompt injection" as a subject to audit, excluded by the finder with a reason that holds) and `orchestrator.md:18` ("not instructions you relay", about relaying role contracts). The 21 "adversarial" mentions are all review-style, none about input trust. `writer_population=public` live (visibility=public, has_issues=True, interaction_limit=None). Scratch-copy perturbation moved guard hits 0→2 on one sentence.

**Attacks and outcomes**
- *Corpus incomplete?* My walk is whole-tree and includes files the finder's list predates; still zero genuine countermeasures.
- *Obey count inflated?* The finder's 8 are genuine instruction sites; my wider net adds only noise (fixture text, code strings), no new class. The claim "8 sites" is conservative and defensible.
- *Is the channel exercised?* Checked live: 0 issues authored by anyone but tvofi/claude; issue #201's comments are all `tvofi`. The exposure is prospective, not yet realised — noted, but the configuration (public, issues open, no interaction limit, obey-sites, write+merge grants, and D11-01's absent second party) is what the standards key on. Critical stands as the amplifier chain is two steps long.

## D11-03 — high — the "enforced" red-check trigger is inert in CI — **vote: verify**

**My metric**: (1) CLAUDE.md carries the enforcement sentence; (2) the same PR body passes rc=0 through the argument list **parsed out of governance.yml's own `Check the body against the contract` step** (not hardcoded) and fails rc=1 with `--red` added; (3) zero workflow steps anywhere invoke policy_lint with `--red`; (4) perturbation: appending a bogus `--red` to the CI list flips rc 0→1 (control that the flip is caused by `--red`, not the fixture).

**My number (`d11_own_D11-03.py`, at head)**: `claudemd_claims_enforced=1` (CLAUDE.md:179), `refusal_fires_with_red_rc=1`, `refusal_with_ci_args_rc=0`, `ci_steps_passing_red=0`, `perturbed_ci_rc=1`. The only executable `--red` caller in the tree is `tools/audit/prepr.sh:133` — and it sits **inside prepr.sh's `--self-test` block**, so even that is a self-test arm of an advisory script. Conformance 10/28 reproduced by the census re-run (all 28 reds are `pr-contract`'s own earlier run at that head).

**Attacks and outcomes**
- *Fixture artefact?* The corpus's own `unnamed-red.md` rot fixture is the designed input for this refusal; the rc flip under an added bogus `--red` name proves the mechanism keys on the flag, not on the fixture's specific check name.
- *Does anything else enforce the obligation?* No: no workflow passes `--red`; the fix-reviewer's `blocked` verdict is prose-level and the verdict sample shows it is self-authored (16/16 by the PR author's account).
- *The finding's own caveat* (naive wiring deadlocks on pr-contract's own red) is sound — the census shows all 28 reds are exactly that.

## D11-04 — high — tree's account of the merge boundary contradicts the live ruleset — **vote: verify (count smaller at head, per the round's caution)**

**My metric**: tree-wide sweep (every text-ish file, `.git` excluded **exactly** — see instrument note below) at my tree's head against the **freshly fetched** live required-context set, counting lines asserting an N-context set or `record`-is-required that the live set contradicts; same sweep re-run against an export of the baseline tree `7dd68dd`.

**My numbers (`d11_own_D11-04.py`)**: live set = **16** (fresh fetch, names listed in the harness output; `record` absent). At head `0855277`: **5 contradictions**, 0 agreeing assertions — `docs/plan-2026-09-open-issues.md:714` (18-claim **and** record-required on one line), `:1142` (18), `docs/decisions/0001-session-policy-merge-grant.md:11` (18, missed by the finder's fixed glob list), `.github/workflows/governance.yml:354` (18, inside the comment block that justified the now-replaced `record-status` job). At baseline `7dd68dd`: my sweep counts **11** (the finder's tighter regex counted 8; the extra three are the same class: `record_status.py:16`, `plan:749`, `decisions/0001:11`) — the finder's 8 was conservative, not inflated. Scratch perturbation rewrites 2 "18 required" claims to 16.

**Post-baseline movement, quantified** (this is the caution's territory): `tests/record_status.py` deleted at `5ae09e5` (#896) — its 2 assertions gone, as the resume state predicted; `docs/HANDOVER.md:52` rewritten to "the required checks its endpoint returns, never a count from here"; `tests/entities.py:15394` rewritten to say the nightly jobs "are not required contexts". So 8 → 4 (finder probe) / 5 (mine, one extra site found). **The finding survives**: the live set is still contradicted by the workflow's own boundary account and three documents, and the structural half holds — I grepped the tree: **no file outside `tools/audit/round*` references the rulesets or rules/branches API**, so `policy_lint`'s `counts` class structurally keys on tree literals and cannot see ruleset drift. `RELEASE_NOTES.md:52` records the drop, so the tree still contradicts itself.

**Instrument note (my own)**: the first run of my harness excluded `.github` because `".github".startswith(".git")` — recorded in the harness header and fixed in place; the same class of bug made my first `uses:` regex miss `- uses:` list lines in D11-07 (also fixed, both re-run clean).

## D11-05 — medium — the disposition rule reddens main on 44 % of pushes — **vote: verify (strengthened)**

**My metric**: same closed window (2026-09-08T00:00Z..2026-09-12T10:44:12Z), my own code, fresh fetch, and a **census** — every one of the 98 red-latest-Governance runs' failing jobs enumerated, not the finder's 60-run sample.

**My number (`d11_own_D11-05.py`, api_failures=0)**: `main_heads=222`, `heads_governance_red=98` → `cfr_governance=0.441`, `heads_tests_red=26` → `cfr_tests=0.117`, `heads_any_red=106` → `cfr_any=0.477` (all exact); failing-job census over 98/98: **`record`=96**, env-matrix=4, policy-docs=4; heads red *because of `record`* = 96/222 = `cfr_record=0.432`. Static: the `record` job's `if:` is `github.event_name != 'pull_request'` (excludes PRs — the finding says this is correct and so do I), and the job still exists unchanged at head.

**Attacks and outcomes**
- *Sample artefact?* Removed: census confirms and slightly strengthens the finder's 58/60.
- *Window artefact?* The window is closed and pinned; the finder's stated perturbation (window start shift) moves the rate, and my census matches the finder's numbers exactly on the same window.
- *"unsatisfiable before a merge" phrasing*: slightly loose — rows CAN precede a merge (#737, #738 did exactly that) — but the operative, measured claim (the check runs only post-merge; the red lands on the next push; ~44 % of pushes red) is exact, and the workflow's own comment block agrees with the mechanism.

## D11-06 — medium (provisional) — the improvement loop measures recurrence and never acts — **vote: verify**

The provisional tag was for timing numbers; **nothing in this finding is a timing number** — every figure is a count, live, at 2026-09-12.

**My metric**: run `policy_lint --stats` live with a token; parse the `blocked` verdict-class count, the printed threshold, the "WOULD OPEN" count and the exit code; check the `|| true` wiring of both `--stats` and `--sunset` in governance.yml; count role-contract lines obliging a seat to read either output; live `search/issues` total for "recurring friction"; corpus headroom from `--budgets`.

**My number (`d11_own_D11-06.py`)**: `stats_exit_code=0`, `stats_would_open=1`, `stats_blocked_count=4`, `stats_threshold=3` (over threshold, opens nothing); perturbation `--since v6.4.0` → `blocked=6` (the number is window-derived, not a constant); `stats_or_true=1` (governance.yml:339), `sunset_or_true=1` (:345); `search_recurring=0` (no such issue has ever existed); `obligation_mentions=0` across every brief except D11's own; `corpus_headroom=0` (`--budgets`: corpus 61378/61378 at head — the finder's 60800/60800 at baseline has since grown, still zero headroom).

**Attacks and outcomes**
- *Would the detector have fired under a different window?* Yes — v6.4.0 gives blocked=6 — which makes "never opened anything" the stronger half: it reports over threshold in multiple windows and `search_recurring=0`.
- *Is some other contract obliging a read?* Whole-brief grep: none (the only mention is D11.md, the dimension's own brief).

## D11-07 — low — no release artefact, no provenance, mutable tags — **vote: verify**

**My metric**: the **10** most recent live releases (finder read 5) with asset counts and provenance-pattern asset names; distinct `uses:` actions across all workflows with my own regex (step-list aware — see D11-04's instrument note) and 40-hex pinning; provenance-tooling mentions in workflows.

**My number (`d11_own_D11-07.py`)**: `recent_releases=10`, `releases_with_assets=0` (v6.3.15…v6.4.2, all `assets=NONE`); `uses_total=9`, `uses_pinned=2` (`hacs/action@1ebf01c…`, `home-assistant/actions/hassfest@a7c616c…`), `uses_mutable=7` (checkout@v5, setup-node@v5, setup-python@v6, cache@v5, cache/save@v5, upload-artifact@v6, download-artifact@v7); `provenance_steps=0`; scratch perturbation pinned 2→3. Exact agreement with the finder on every load-bearing count, on a longer release window.

## Votes

| id | vote | severity | one-line metric |
|---|---|---|---|
| D11-01 | verify | critical | pull_request rules in live ruleset and all 5 history versions (0); merged PRs with an APPROVED review by a non-author (0/592 pinned, 0/602 live, two extra oracles) |
| D11-02 | verify | critical | seat obey-sites vs trust-boundary sentences in a whole-tree corpus walk (8 strong sites / 0 countermeasures), writer population public (live) |
| D11-03 | verify | high | rc of the corpus's unnamed-red body through CI's parsed argument list (0) vs with `--red` (1); workflow steps passing `--red` (0) |
| D11-04 | verify | high | tree assertions contradicting the live 16-context set: 8 at baseline (finder), 11 at baseline (my wider net), **4–5 at head 0855277**; no tree instrument derives the set from the API |
| D11-05 | verify | medium | heads whose latest Governance push run failed (98/222 = 44.1 %), failing-job census record 96/98 (finder sampled 58/60) |
| D11-06 | verify | medium | `--stats` blocked=4 over threshold 3 with would-open=1 and rc=0 under `|| true`; "recurring friction" search total_count=0; corpus headroom 0 |
| D11-07 | verify | low | releases with assets (0 of 10 live); `uses:` pinned by SHA (2 of 9); provenance steps (0) |

No refute and no weaken anywhere: every finder number reproduced exactly under the pinned windows, and every live re-measure (merged 592→602, corpus 60800→61378, stats window 30→39 merges) moved in a direction that leaves the findings intact. The only number that shrank is D11-04's mismatch count, exactly along the path the round's resume state predicted, and the finding survives it with 4–5 live contradictions and its structural half (no API-derived instrument) verified independently.
