# D11 round 4 — verifier 2 report

- **verifier** 2 of 3, panel D11-0, audit round 4
- **worktree** `/Users/timmalmstrom/.zcode/workspace/default/audit-r4-verify-D11-2`, detached at `0855277edc49cb3cce3b1095fa1e5edcda7663c8` (branch head; baseline `7dd68dd` is an ancestor)
- **measured** 2026-09-12T15:10–15:37Z. Live GitHub state re-read with a **fresh private cache** (`D11_CACHE=/tmp/d11v2/cache`), never the finder's `~/.cache/hpo-d11-round4`, so every API number below is my own read, not the finder's.
- **box** load1 2.93 at close (quoted, not gated). **No number below is a timing or memory figure**: all are API counts, static counts, or durations GitHub itself reports, so no `thread_factor` applies and none is quoted. `api_failures=0` on every harness run.
- **stance** refute-first. Attacks in the contract's order: gate mode (not applicable — no finding rests on the golden/mutant gate), aggregate artefact (the scorecard reports per-criterion, never the aggregate), null control (driven for every harness that declares one), reachability (the seat scripts and CI steps are read in-tree and traced to their callers), severity (judged per finding below).

## Method summary

Every finder harness re-run from the worktree root with `PYTHONPATH=tests/hastub`, fresh cache. My own instruments, written for this panel:

1. `/tmp/d11v2/my_review_census.py` — REST-only (`pulls?state=all` + `pulls/{n}/reviews`), stratified 30-PR sample across all merged PRs, counting APPROVED reviews (any and non-author). Independent of the finder's GraphQL `reviews` connection.
2. `/tmp/d11v2/my_claims.py` — whole-tree scan (every text file in the tree at a given SHA, no fixed glob list, wider `record`-required patterns) for required-context assertions contradicting the live set; run at both `7dd68dd` and `0855277`.
3. Direct `gh api` reads: `branches/main/protection`, `rulesets`, `rules/branches/main`, `collaborators/{u}/permission`, `releases`, `search/issues`, `interaction-limits`.

Perturbations driven in-place and reverted (`git status --porcelain` empty at close, before this file was written).

---

## D11-01 — merge to `main` needs no review — **verify, critical**

Finder: `pull_request_rules=0`, no version of ruleset 22628467 has ever had one, 0/592 merged PRs carry a non-author APPROVED review, RepositoryRole 5 bypasses always.

**My re-measure (2026-09-12T15:11Z, fresh cache):** `required_contexts=16` (both arms agree), `pull_request_rules=0`, `ruleset_versions=5`, `ruleset_versions_with_pull_request_rule=0`, `bypass_actors_always=1` (`{actor_id: 5, actor_type: RepositoryRole, bypass_mode: always}`), `bypass_applies_to_merger=1`. `merge_census`: `merged_all=602` (live moved: +10 merges since baseline), **`reviewed_by_non_author=0`, `approved_any=0`** over all 602 — review states across every merged PR: `{COMMENTED: 8}`. Authors `{tvofi: 599, claude: 3}`. Window (pinned at baseline) identical: `window_merges=164`, `first_contract_green=139`, `merges_with_red_required=28`, `red_answered=10`, `merges_missing_a_required_context=0`.

**My own instrument:** REST-only census, 30-PR stratified sample of all 602 merged PRs: `v2_approved_any=0`, `v2_approved_nonauthor=0`, **0 reviews of any state returned on the sample**. Two independent endpoint families agree with the finder's GraphQL.

**Attack 1 — required reviews could live outside the rulesets API (legacy branch protection).** `GET /repos/tvofi/heatpump_optimizer/branches/main/protection` → **404 "Branch not protected"**. Classic branch protection does not exist, so no `required_pull_request_reviews` can be hiding there. `GET /rules/branches/main` (the endpoint that would surface a classic pull_request rule as a `pull_request` rule type) returns exactly `['deletion','non_fast_forward','required_status_checks']`. The rulesets list shows one ruleset total (`22628467 main-protect`, active). Attack fails; no second arm exists.

**Attack 2 — is RepositoryRole 5 really admin, and does the bypass bind the merger?** GitHub does not document the built-in role IDs, so I chased it. `github/rest-api-description#4406`: the issue author states "across all repositories I've checked the *Repository admin* role is `5`", and a commenter gives the Terraform provider's mapping `maintain→2, write→4, admin→5`. A search-summary claiming "Admin=1" conflates `OrganizationAdmin`'s documented `actor_id 1` — which the docs say "is not applicable for personal repositories"; this is a personal repo. `collaborators/tvofi/permission` → `role_name: admin, permissions.admin: true`; PR #906's `merged_by` is `tvofi`. So the identity performing the merges holds the role the bypass list names. Residual: the mapping is officially undocumented, so this arm rests on community attestation plus the API's role_name read — I could not separate it further without perturbing the live ruleset, which the brief forbids. Note the bypass is an aggravator only; the primary fact (no `pull_request` rule, 0 approvals in 602 merges) does not depend on it.

**Attack 3 — could approvals exist but be invisible?** The finder's GraphQL reads `reviews(first:20)` per PR; a PR with >20 reviews would truncate. My REST sample returned **zero** reviews (not fewer than 30), so no truncation can hide an approval; DISMISSED reviews would have been returned by both endpoint families and appear in neither.

**Severity:** earned. The boundary's central control is absent by configuration and by record (602 merges, zero approvals), while the tree and every standard keyed on it describe a guarded boundary. Critical stands.

## D11-02 — seats obey publicly-writable text, no countermeasure — **verify, critical (with one tempering note)**

Finder: 8 obey sites, 0 guard sentences, writer population = public.

**My re-measure:** `seat_obey_sites=8`, `seat_guard_sites=0`, `shell_interpolations=3` (all constrained: one `type: boolean` input, two 40-hex SHAs — now at tests.yml:124,915,916), `dangerous_triggers=0`, `writer_population=public`. Live: `visibility=public`, `has_issues=true`, `interaction-limits` → `{}` (no limit) — any GitHub account can write issue and PR comments.

**My own instrument:** whole-tree grep (no corpus list) for `prompt injection|untrusted|do(es) not trust|data, not instruction|not instructions|as data|injection attack|adversar|malicious comment|spoof|forge` over every `.md/.js/.mjs/.py/.json`. **Zero countermeasure sentences in the policy or seat corpus.** The only "untrusted"/"prompt injection" hits in the tree are round-3 audit artifacts (`tools/audit/round3/**`) — the previous round's own harnesses — and this dimension's brief. `seat_guard_sites=0` is not a regex artefact.

**Metric definition difference (both recorded):** the finder's OBEY regex counts 8 lines; 5 of them are one boilerplate sentence ("read each body with pull_request_read", in the *stamper*'s prompt — reading PR bodies to write release notes). Under my stricter definition — a site instructing a seat to treat comment/body text as *authority* — there are **3**: `web-triage.js:153` ("the comments carry judge verdicts, corrections and claims that override the body"), `web-fix-wave.js:242` ("the comments carry corrections that override the body"), and the merge/reconcile grammar. Both definitions sustain the finding.

**Reachability attack (does any seat actually key a decision on comment text?):** driven into the source. `web-fix-wave.js:103-111` — the merge seat's prompt, holding `GH_READ + GH_WRITE + GH_MERGE`, reads: *"Merge PR #N only if ALL of: … the newest 'Fix review:' comment says merge and post-dates that head"*. **No authorship check appears anywhere in that prompt**, and the reconciler (`:285`) reads "the most recent comment starting `Fix review:`" straight from the PR, with stage `merge` skipping the reviewer entirely. The verdict grammar is therefore publicly forgeable and consumed by the seat that holds the merge grant. `GH_WRITE` at `:16-18` is `add_issue_comment, issue_write, create_pull_request, update_pull_request` — the finder's "write and merge grants" is accurate.

**Tempering note for the judge:** the attacker cannot push code — branches need write access — so what a forged `Fix review: merge` comment can land is a *merge of code a seat already wrote and CI already passed*, plus injected instruction text into seat prompts (the `blocked … <why>` grammar feeds repair text onward). That is still a complete loss of the human checkpoint by one unauthenticated comment (with D11-01 removing the boundary), and the repo's own reviewer contract says implementations that "looked right" have been wrong. I keep critical; high is arguable if the judge weighs the no-attacker-code-path fact heavier. Round 3 adjudicated a weaker version of this exposure (no merge-grammar, no countermeasure) at medium/hygiene — in-tree at `tools/audit/round3/reports/ruling-tranche-2.md` — but the comment-keyed merge logic is the sharper fact this round.

**Perturbation driven:** one guard sentence appended to `tools/audit/briefs/COMMON.md` → `seat_guard_sites` 0→1; reverted.

## D11-03 — the "enforced" red-check trigger is inert in CI — **verify, high**

**My re-measure:** `controls_inert_in_ci=1`, `mechanisms=73` (derivation re-added and matching), all 9 self-tests rc=0, `mutation_lane_functions=12`. My own drive of the `--red` arm on the corpus's own fixture `unnamed-red.md`: CI's exact argument list (`--pr-body --head --title --paths-file`) → **rc=0, "PR-BODY: 0 error(s)"**; adding `--red 'fast (3.14)'` → **rc=1**, `[pr-body] … check 'fast (3.14)' is red and '## Red checks' does not name it`. `grep -- --red .github/workflows/*` → no hit; the only in-tree caller is `tools/audit/prepr.sh:133`, which CI runs only as `--self-test` (governance.yml "Show the pre-PR self-check refusing its own fixtures"). CLAUDE.md:179-181 does say "Only the red-check trigger is enforced".

**Attack — is it really "enforced by nothing"?** CLAUDE.md's sentence has a second clause: "and the fix reviewer returns `blocked` on one the body left unanswered". That clause exists (`tools/audit/briefs/fix-review.md` rule 11, `root-cause-unanswered` class) but is a seat that must happen to run — precisely the "advisory" class this dimension counts. The tree itself agrees with the finder: `docs/HANDOVER.md:150-153` — "The red-check refusal has never once fired … it is honour-only, enforced by whichever reviewer looks." Where the obligation bites, my census re-run gives 18 of 28 window merges with an unanswered red required context (all 28 reds are `pr-contract`'s own earlier run — the deadlock caveat the finder states is real and I confirm it from the check-run listings). Attack fails; the CI-inertness claim is exact and the tree corroborates it.

**Perturbation driven:** `--red` added to governance.yml's body-contract step in-place → `controls_inert_in_ci` 1→0 and "governance.yml passes --red: True"; reverted. The number reads the workflow, not a constant.

## D11-04 — tree assertions contradict the live required-context set — **verify, high (count shrank; the live-set facts re-confirmed)**

Live set re-measured 2026-09-12T15:15Z: **16 contexts**, `record` **not** in it, `fast (3.13)` **not** in it. History: 18 (09-09T09:37Z) → 17 (09-11T21:24Z) → 16 (09-12T09:18Z), no `pull_request` rule in any version.

**Finder's harness at my head:** `tree_claim_mismatches=4` (baseline 8). The caution anticipated this: `tests/record_status.py` (2 of the 8) is deleted on main, and `docs/HANDOVER.md:52` + `tests/entities.py:15394` were also fixed. Remaining per the finder's regex: `governance.yml:354` (claims 18), `plan…open-issues.md:714` (claims 18 **and** `record` required), `:1142` (claims 18).

**My own instrument (whole tree, no glob list, wider record-patterns):**

- baseline `7dd68dd`: **10** mismatch lines — the finder's 8 plus `docs/decisions/0001-session-policy-merge-grant.md:11` and `plan…:417`, both outside the finder's fixed `CLAIM_GLOBS`/`RECORD_RE` (its glob list is a carried constant; mine re-scans everything).
- head `0855277`: **6** — `governance.yml:354`, `decisions/0001:11`, `plan:433` (record required), `plan:714` (18 + record required), `plan:1142`.

**Judgement per line:** `governance.yml:354` is a **live** contradiction and the load-bearing one — it is the *stated justification for the `record-status` job* ("The defect is that `record` is one of `main-protect`'s 18 required contexts while reporting `skipped`…"), a premise false since 2026-09-11T21:24Z. The plan rows are dated historical narratives (the tree's own convention: "the record stands as what was true when the decision was taken"), so my 6 is an upper bound and 2–3 of them are history, not live assertion. The finder's derivation-gap claim also re-verified: `policy_lint`'s `counts` class is "a literal count matches its derivation" (`policy_lint.mjs:2111`) and **nothing outside `tools/audit/round*` reads the rulesets API** — no instrument can see this class of drift.

**Per the round's caution I do not refute on the two deleted lines.** The finding survives at head with 4 (finder's regex) to 6 (mine, minus 2–3 history rows) contradicting lines, including the one that justifies a job running on every PR. High stands on that premise line; the judge may read the shrinkage (main fixed 4–5 of the sites inside two days) as medium.

**Perturbation driven:** `governance.yml:354` "18"→"16" in-place → `tree_claim_mismatches` 4→3; reverted.

## D11-05 — the disposition rule reddens `main` on 44 % of pushes — **verify, medium**

**My re-measure (fresh cache, window pinned 2026-09-08T00:00Z..2026-09-12T10:44:12Z):** `main_heads=222`, **`cfr_governance=0.441`** (98 heads), `cfr_tests=0.117`, `cfr_any=0.477`, failing-job sample `record=58, policy-docs=4, env-matrix=4` of 60, `ttr_median_h_Governance=0.61` (22 episodes, max 8.95), `ttr_median_h_Tests=1.11`. `governance_cost.py`: 164 merges, 75 s/merge governance vs 758 s code gate, share 0.058, body rounds mean 1.63 / max 8 — all exact. The actions/runs listing is at the 1000 cap with oldest visible run 2026-09-07T16:50:57Z, still before W0, so the window is complete. (`lead_time_median_h` 7.13 vs the finder's 7.41 and n 217 vs 212 — five previously-unreleased merges found a tag after baseline; CFR figures unaffected.)

**Job semantics re-read in-tree:** `record`'s `if: github.event_name != 'pull_request'` (governance.yml:290) with the only failing step `policy_lint --record --since <last tag>`; `--stats`/`--sunset` both `|| true` in the same job. The workflow's own comments argue the `if:` is correct (a pull_request checkout is not in main's history) — agreed, and the finder says so.

**Attack — "cannot be satisfied before a merge" is imprecise:** the *row* can precede the merge (plan rows for #737/#738: "row written before the merge, and it is this pull request"); what cannot run pre-merge is the *check* — #541 measured 5 false refusals per true one for a naive pre-merge arm, which is why CM-1 was refused. The measured consequence (44.1 pp of the 47.7 pp CFR is Governance, 58/60 sampled failures are `record`) is exact and is the finding; the wording quibble does not move it. Medium stands.

**Perturbation driven:** `D11_WINDOW_START=2026-09-11T00:00:00Z` → `cfr_governance` 0.441→**0.745** (98 heads) — the rate moves with the window and is even higher on the busiest day; not a constant.

## D11-06 — the improvement loop measures recurrence and never acts — **verify, medium (provisionality resolved)**

**My re-measure (2026-09-12T15:30Z):** `node .claude/workflows/policy_lint.mjs --stats --since v6.4.1` → 39 merged PRs in window (finder had ~30–31; live moved), verdict class **`blocked` at 4 — "at or over threshold"** (threshold 3), `WOULD OPEN: 1 issue(s)`, "Not opened here: a seat measures and files, a report does not." `gh api search/issues …"recurring friction"` → **total_count=0**; `…recurring friction in:title` → 0; a scan of all issue titles/bodies for the exact phrase → 0 (the word "friction" alone appears in 242 bodies — the detector's exact issue title has never been used). Both CI invocations of `--stats`/`--sunset` are `|| true` (governance.yml:339,345 — the only two in `.github/workflows/`). No role contract obliges reading either: my grep over `tools/audit/briefs/*.md` finds `--stats` named only in `D11.md` (this audit's own dimension brief) and `orchestrator.md` §3 sets a third-time trigger a seat counts in-session, reading no instrument.

**Budgets:** the finder's `60800/60800` has moved — now `corpus: ~61378 tokens, cap 61378`, `always-loaded: ~3343, cap 3343` — i.e. **still exactly zero headroom**; the structural claim holds, the specific number is stale by one corpus revision.

**Timing note:** nothing here is a wall/CPU number — API counts, static grep, GitHub-reported durations — so the "quiet window" provisionality does not attach; I resolve it. Medium stands.

## D11-07 — no release artefact, no provenance, mutable tags — **verify, low (hygiene)**

**My re-measure:** last five releases `v6.4.3, v6.4.2, v6.4.1, v6.4.0, v6.3.20` carry **0 assets each** (live moved one tag past the finder's five; same result). `release.yml` has `gh release create` and no upload/attest step. Distinct `uses:` across `.github/workflows/` (my own list-form-aware extraction — a naive `awk` missed list-form entries and undercounted 7; corrected): **9 distinct, 2 SHA-pinned** (`hacs/action@1ebf01c…`, `home-assistant/actions/hassfest@a7c616ce…`), 7 mutable tags (`checkout@v5, setup-node@v5, setup-python@v6, cache@v5, cache/save@v5, upload-artifact@v6, download-artifact@v7`). Tags are lightweight (`git tag -v` → "cannot verify a non-tag object") and target commits are `unsigned/unverified`. `standards_scorecard.py` RESULTs reproduce exactly: `scorecard 5/1/4`, `slsa_build_level=0`, `criteria_scored=32`, `bestpractices 8 pass/1 fail`, `owasp 1 pass/2 fail`, `api_failures=0`.

**Attack — is "SLSA Build level 0" the right category when there is no artefact at all?** With zero assets one could argue the level is undefined rather than 0; but the repo *does* ship a release (the source tree at the tag, which HACS installs) and nothing about it is attested or signed, so "L1 unmet, level 0" is the honest reading and the finder's per-check reasoning is sound. One-line-fix costing is plausible from the workflow text. Low/hygiene stands.

---

## Panel-level notes for the judge

- **The finder's fixed `CLAIM_GLOBS` list in `ruleset_probe.py` is a carried constant** (it says it re-greps; it does not — it iterates a fixed list). It missed `docs/decisions/0001:11` and the `plan:433/417` record-required pattern at both baseline and head. My whole-tree numbers (10 at baseline, 6 at head) are the wider net; both agree in direction.
- **All declared perturbations were driven and fired** (ruleset_probe tree edit, mechanism_inventory `--red` wiring, untrusted_text guard sentence, dora_keys window move, merge_census heading-case control → `red_answered` 10→0 with `merges_with_red_required` unchanged at 28). governance_cost's declared perturbation was verified by reading the `GOV` name-set split rather than editing the harness.
- **Live state moved under us** as expected: `merged_all` 592→602, `lead_time` 7.41→7.13 h (n 212→217, unreleased 5→0), budgets 60800→61378, `--stats` window 30→39 PRs, last-five releases shifted one tag. Every window-pinned figure (164 merges, 28 reds, 222 heads, 44.1 pp) reproduced exactly.
- **No timing-based refutes anywhere**; nothing was measured under contention that could move a number, and no refute of mine rests on load.
