# D11 — verifier 1 of 3, refute-first, own-harness seat

Stance: assume each finding is wrong until my own executed number says
otherwise. I received the five claims with their harnesses, metrics and
perturbations, and nothing else. I did not open `docs/audit-*.md` or any other
verifier's output.

## Where every number was taken

Three different trees are involved and the report says which one each figure
comes from, because `main` moved twice while I worked.

| name | SHA | what it is |
|---|---|---|
| baseline | `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1` | the finder's baseline; my worktree's `HEAD`; where I re-ran the finder's six harnesses |
| pin | `da43c9da5fddfc0ded0f538edae4a41311cc4b01` | `origin/main` as `git ls-remote` returned it at 2026-09-11T06:33+02:00, committer date `2026-09-11T06:31:05+02:00`; **every number of mine below is at this SHA unless it says baseline** |
| orchestrator's re-measurement | `dc03619` | an ancestor of the pin, and `52b970b6` (the pin's parent chain) is too — verified with `git merge-base --is-ancestor` |

The baseline is **23 first-parent merges** behind the pin, not 10; `main`
advanced twice during this seat (`52b970b6` → `da43c9d`). Live GitHub state was
read between 06:24 and 06:47 CEST on 2026-09-11. `gh` 2.98.0, python3 3.11.5,
node v20.10.0, 8-core Apple M1.

Every figure here is a count, a set or a fraction. No wall, CPU or RSS number is
claimed, so contention reaches none of them; `load1` ran 5.76–11.38 and
`thread_factor` 0.39–0.99 across the runs and is quoted, not gated, per
`tools/audit/README.md`.

**Rate limiting.** `gh api rate_limit` reported `core: used 0, remaining 5000`
at 06:24 and again at 06:36, and the search endpoint refused with HTTP 403
"secondary rate limit" at 06:38 while ordinary REST calls kept working. My
harness printed `v5_non_owner_authored_issues=null` and
`v5_api_failures=2 (['search:issues','search:prs'])` for that run rather than a
zero. Every RESULT line in `v1gov.py` carries an `api_failures` count beside it
for exactly this reason, and the PR/issue authorship census below was re-taken
over GraphQL, which has a separate quota, and compared as **sets of numbers**,
not totals.

## Files

- `verify-1/v1gov.py` — my harness. Shares no code with the finder's; its
  metric definitions are in its header and are deliberately different.
- `verify-1/out-v1gov-full.txt`, `out-v1.txt`, `out-v1-wide.txt`, `out-v2.txt`,
  `out-v3-pin.txt`, `out-v4-v5.txt`, `out-perturbations.txt` — captured runs.
- `verify-1/rerun/*.txt` — the finder's six harnesses re-run at the baseline.
- `verify-1/ruleset-live.json`, `verify-1/v1cache/` — raw API responses.
- `verify-1/PINNED_MAIN.txt` — the pin.
- The two trees the filesystem metrics ran against are reproduced with
  `git archive <sha> | tar -x -C <dir>` and passed to the harness as `--root`
  (no worktree is created, so no shared repository state is touched). They are
  26 MB and were deleted once the runs were captured; the one command above
  rebuilds either of them.

## Step 1 — the finder's harnesses, re-run at the baseline

All six run clean and **every figure reproduces exactly**; zero mismatches,
`api_failures=0` on each.

`mechanism_rows=79`, `required_contexts=18`, `contexts_no_producing_job=4`,
`contexts_skipped_by_construction_on_pr=1`, `ruleset_has_pull_request_rule=0`,
`ruleset_required_approvals=0`, `ruleset_bypass_actors=1`,
`current_user_can_bypass='always'`, `policy_lint_classes=14`,
`classes_with_acceptance_pin=11`, `mutated_entry_points=12`,
`structure_metrics=24`; `arm_policy_title_exit=1` / `arm_docs_title_exit=0`,
`rule_text_approval_not_required=32` of `rule_text_commits=50` (0.6400);
`sc_security_policy=0`, `bp_vulnerability_report_process=0`,
`sc_branch_protection_tier=1`, `corpus_lines_added_per_deleted=3.086`;
`prompts_reading_github_text=6`, `read_and_write_prompts=5`, `boundary_files=1`
(`tools/audit/briefs/D11.md`), `distinct_issue_authors=1`, `collaborators=1`;
conformance `A=0.5385 B=0.0000 C=0.0000 D=0.5128 E=0.8718 F=0.9487 G=1.0000`
with `subject_only=[] api_only=[]`; dora `red_main_heads=37`,
`red_heads_by_job={"record":20,…}`, `red_heads_only_record=11`.

Two caveats on the re-run, not defects: `conformance.py` and `dora.py` read
their own cached raw JSON (`conformance_raw.json`, `dora_runs.json`), so that
arithmetic reproduces but the fetch does not. My own instrument re-fetched
everything independently, which is what the numbers below rest on.

---

# D11-01 — `critical`. **verify.**

## My metric

> Of the rules the live `main` ruleset carries, how many can **refuse** a push
> or merge by an account that actually holds write access, after subtracting
> the ruleset's own bypass actors — plus the required approving review count,
> plus two behavioural arms that need no role-name assumption.

The finder counted rules and a role name. I counted what the acting identity
can do, because the finding's force is a capability claim.

## My numbers (pin, live GitHub at 2026-09-11 06:24–06:47 CEST)

```
v1_ruleset_rules=3                                 (deletion, non_fast_forward, required_status_checks)
v1_pull_request_rules=0
v1_required_approving_reviews=0
v1_current_user_can_bypass='always'
v1_binding_rules_for_the_merging_identity=0        of 3
v1_accounts_with_push=1                            (['tvofi:admin'])
v1_required_contexts=18
v1_merges_with_no_github_review_object=134 of 134  (72 h window)
v1_main_commits_without_a_merged_pr_after_ruleset=1 of 83 first-parent commits since the ruleset went live
v1_api_failures=0
```

And, enumerated over the **whole repository** by GraphQL with 0 refusals and
compared as sets of pull-request numbers rather than totals:

```
merged pull requests = 510
merged_by = {"tvofi/User": 510}          -- 1.0000, one identity, no exceptions
pull request authors = {"tvofi/User": 523, "claude/Bot": 3}   over 526
```

## Attacks I ran

**1. Establish what RepositoryRole 5 is, rather than assuming it.** GitHub's
REST documentation for ruleset bypass actors gives only *"The ID of the actor
that can bypass a ruleset. Required for Integration, RepositoryRole, Team, and
User actor types"* — **no id→role map is published**, and `gh ruleset view`
renders the entry as the bare `RepositoryRole (ID: 5)`. The finder's gloss
"RepositoryRole 5 (admin)" is therefore not looked up. It is nonetheless
**derivable**, and my harness derives it and prints its premises:
`repos/tvofi/heatpump_optimizer/custom-roles` returns 404, so a user-owned
repository has no custom roles; the sole push account holds exactly one role
(`role_name=admin`); the ruleset has exactly one bypass actor; and GitHub
itself answers `current_user_can_bypass: "always"` for that account. Role 5
resolves to `admin`. **Outcome: the gloss is unsupported as written and true as
derived; it changes nothing, because `current_user_can_bypass` answers the
operative question without it.**

**2. Test both halves of the `critical` rubric independently.** The brief's
anchor is *"a merge to `main` can happen with no review or with a red required
check"* — verified verbatim in `tools/audit/briefs/D11.md`.

*Arm 1, no review.* Unconditional and not a sampling claim: 0 `pull_request`
rules, 0 required approving reviews, so the ruleset cannot ask for a review
from **any** actor, bypassing or not. The consequence is measured twice
independently: 134 of 134 merged pull requests in my 72 h window carry no
GitHub review object (the finder got 0/39 on a different sample), and 510 of
510 merges across the repository's whole history were performed by one account,
`tvofi`, which also authored 523 of the 526 pull requests — the other three
being the `claude` Bot's, merged by `tvofi` as well. Arm 1 alone satisfies the
rubric.

*Arm 2, a red required check.* This is where I attacked hardest, and twice my
own instrument was wrong before it was right.

**3. My first arm-2 number was a tie-break artefact, and I caught it.** The
first run reported `v1_merges_with_a_failing_required_context_at_head=1` — PR
#770, `pr-contract` failing. False. Two workflow runs of `governance.yml` exist
at that head (`34556668466`, `34556668732`) with `pr-contract` started in the
**same second** `2026-09-11T02:58:41Z`, one `failure` and one `success`;
ordering on `startedAt` alone picks whichever the JSON listed last. GitHub
orders by creation, and the check-run ids settle it — `103130684653` failure,
`103130685520` success, so the latest is green. I changed `latest_per_context`
to order on `(startedAt, id)` and re-ran: **0**. All timestamps are parsed
timezone-aware, so this box's CEST never shifts a UTC `startedAt`.

**4. My wider arm-2 number was a window artefact, and I caught that too.** Over
all 134 merged pull requests in the window, 21 had a **required context that
produced no check run at all** — which per GitHub's documentation stays
pending and blocks a merge for a non-bypassing actor, a stronger result than
"red". Splitting them on the ruleset's own `created_at`
(`2026-09-09T11:37:08+02:00`): **21 of 21 merged before the ruleset existed**,
the latest at `2026-09-08T23:22:44Z`. Post-ruleset: **0**. The finding gains
nothing from them and I discard them.

**5. So what does arm 2 actually rest on?** Two things, and I state both:

- *Capability, from GitHub's own answer, not an inference:*
  `current_user_can_bypass: "always"` for the identity that performed 510 of
  510 merges. `bypass_mode: always` exempts that actor from every rule in the
  ruleset, so `v1_binding_rules_for_the_merging_identity=0`.
- *One behavioural instance:* `18d67a2`, `v6.3.20: stamp …`, authored and
  committed by `tvofi`, pushed to `main` at `2026-09-10T10:45:09+02:00` — one
  day **after** the ruleset went live — **with no pull request at all**, 1 of
  83 first-parent commits since activation. Its 23 check runs all executed
  *after* the push, and two of the eighteen required contexts (`closure-scope`,
  `pr-contract`) concluded `skipped` because they only run on a
  `pull_request` event. A change reached `main` with the required contexts
  never consulted as a gate — strictly stronger than reaching it over a red one.

What I could **not** establish, and say so: no merged pull request in the
post-ruleset window merged over a *failing* required context. Arm 2 is a
capability plus one direct push, not a pattern of red merges.

**6. Does `required_status_checks` bind a non-bypassing actor?** Structurally
yes — the ruleset carries exactly one bypass actor and it is a repository role,
so a hypothetical write-level collaborator would be bound. In practice there is
no such actor: 1 account with push, 510 of 510 merges by it, and the three
pull requests authored by the `claude` Bot (`CONTRIBUTOR`) were merged by
`tvofi` too. **The 18 required checks bind nobody who merges: 0 of 510.** The
finding's premise that there is exactly one identity is measured, not assumed.

**7. Perturbation, re-run under my own splice.** A local copy of the ruleset
JSON with the bypass actor removed and a `pull_request` rule
(`required_approving_review_count: 1`) added:
`binding_rules 0 → 4`, `required_approvals 0 → 1`, direction **up**. GitHub was
not touched.

## Vote

**verify**, severity **critical**. Arm 1 meets the brief's own `critical`
anchor on its own and is not a sampling claim. Arm 2 is a capability
established by GitHub's own field plus one post-activation direct push. I would
ask the judge to note that the finding's sentence "its 18 required checks do
not bind the only actor who merges" is a capability statement — correct — and
should not be read as "merges over red checks were observed", because over 134
post-window merges they were not.

---

# D11-02 — `high`. **verify.**

## My metric

> Over a window stated in the output and measured through the **per-commit**
> check-runs listing (not the Actions run listing, which caps at 1000), the
> number of first-parent `main` commits whose latest check run for some context
> concluded a failure, and the subset where `record` is the only such context;
> plus the conclusion `record` reaches on a pull-request head.

## My numbers

Window, stated: **`2026-09-08T06:31:05+02:00 .. 2026-09-11T06:31:05+02:00`**,
72 h, first-parent on the pin, **136 heads**, tz-aware throughout.

```
v2_window_heads=136
v2_heads_with_a_check_run=136 of 136        (truncated_suites=0; the 1000-run cap is not in this path)
v2_red_main_heads=49
v2_change_failure_rate=0.3603
v2_red_heads_by_context={"record":36,"fast (3.13)":12,"fast (3.14)":12,
                         "nightly-ha (2025.2.0)":8,"nightly-ha (stable)":8,
                         "closures":6,"env-matrix":4,"policy-docs":4,"slow":1}
v2_record_share_of_red_heads=0.7347
v2_red_heads_only_record=25
v2_record_conclusions_on_pr_heads={"skipped": 70}   over 40 PR heads, 0 with no `record` run
v2_record_satisfied_without_running_on_pr=1.0000    (70/70)
v2_api_failures=0
```

## Attacks I ran

**1. Re-derive the window, because a count over a sliding window decays.** The
finder's "20 of 37" is over `2026-09-06T00:29+02:00 .. 2026-09-10T23:02+02:00`,
215 of that window's 484 heads, reached through the Actions run listing after
it capped at 1000 — a contiguous recent suffix, which the harness prints
(`run_listing_capped=1`). My window is different (72 h, ending at the pin), my
instrument is different (per-commit check-runs, no cap, `truncated_suites=0`),
and my count is **36 of 49 red heads**, with **25** where `record` is the only
red context. So: the *absolute* count does not survive the window change — it
grew — but the claim that matters, that `record` is the **single largest cause
of a red `main`**, reproduces and reproduces larger (0.5405 → 0.7347 share).
The finding should be read as an ordinal claim with a dated count beside it.

**2. Is `skipped` really satisfying?** Confirmed from GitHub's own
documentation rather than assumed: *"Required status checks must have a
`successful`, `skipped`, or `neutral` status before collaborators can make
changes to a protected branch"*, and a check that never reports stays pending
and blocks. `record` is one of the 18 required contexts (read from the live
ruleset) and concluded `skipped` in **70 of 70** runs across 40 pull-request
heads.

**3. The one place I would narrow the finding's wording.** Because the only
merging identity bypasses every rule (D11-01), `skipped`-satisfies is not in
fact what lets these merges through — the bypass is. The mechanism sentence
therefore overstates for *this* repository while being correct about GitHub.
The finding's measured consequence does not depend on it: `record` is a
post-hoc detector, its verdict arrives only after the merge it was meant to
gate, and 25 of 49 `main` heads in 72 h were red with nothing wrong but a
missing disposition row. `main` is red at the pin itself (`da43c9d`) for
exactly that reason, as it was at the baseline.

**4. Does #738 close it?** No, and I quantified why. `record-status`, the
pull-request-side reporter #738 added deliberately **not** as a required
context, exists at 23 of the 134 heads (it is that new) and was **failing at
merge on 15 of those 23 (0.6522)**. Every one merged. A reporter that is red on
two thirds of the merges it observes and gates none of them converts "nobody
looks" into "everyone sees", exactly as the finding says.

**5. Perturbation.** Strike `record` from the failing contexts and
re-aggregate: `v2_red_main_heads 49 → 24`, direction **down**, and the
difference **25** equals `v2_red_heads_only_record=25` — **MATCH**. The metric
moves under the one-line change and moves by exactly the predicted amount.

## Vote

**verify**, severity **high**. The finding's anchor — an obligation the record
calls enforced that nothing enforces before the merge — is met. I would carry
forward the wording narrowing in attack 3 and the fact that the "20 of 37"
figure is window-dependent.

---

# D11-03 — `high`. **verify.**

## My metric

> How many **independent** mechanisms can refuse a merge that rewrites text the
> repository's own `.github/CODEOWNERS` declares the owner's, when the
> pull-request title does not begin `policy:` — each candidate executed or
> read, never assumed. The population of "policy text" is CODEOWNERS' own path
> list, not `policy_lint`'s `POLICY_GLOBS`.

## My numbers (pin)

```
v3_arm_policy_title_exit=1        (names `## Approval`: True)
v3_arm_docs_title_exit=0          (names `## Approval`: False)
v3_gate_switched_off_by_title_alone=1
v3_mechanisms_that_can_refuse_an_unapproved_policy_change=0   of 5 candidates
v3_codeowner_owned_paths=6        (/CLAUDE.md /.claude/rules/ /.cursor/rules/
                                   /tools/audit/briefs/ /docs/decisions/ /.github/CODEOWNERS)
v3_codeowner_path_commits=24                       (72 h window)
v3_codeowner_path_commits_with_the_gate_off=11     (0.4583)
v3_gate_off_bodies_with_voluntary_approval_section=7 of 11   api_failures=0
```

Both arms are one body file, one `--head`, and a title differing only in its
prefix.

## Attacks I ran

**1. The commissioned attack: does anything *else* enforce the obligation?**
Five candidates, each executed or read; **all five score zero**:

| candidate | what I found |
|---|---|
| `checkPrBody`'s `## Approval` | refuses only when the **author's** title matches `/^policy:/` — the two arms above |
| ruleset `required_approving_review_count` | 0 `pull_request` rules exist, so there is no count |
| ruleset `require_code_owner_review` | needs a `pull_request` rule; none exists |
| `.github/CODEOWNERS` | **exists now** (merged in #756, after the finder's baseline) with 6 owned paths — and is inert |
| any other `policy_lint` check class keyed on approval | classes matching `/approv/`: **none of 14** |

CODEOWNERS is the candidate that could have made this belt-and-braces, and it
refutes itself in its own header: *"Only once `main-protect` carries a
`pull_request` rule with `require_code_owner_review`: such a pull request cannot
merge without the owner's approval on GitHub. Until that rule exists this file
claims nothing."* That is the repository's own statement, and the live ruleset
confirms `v1_pull_request_rules=0`. **The title-keying is the only mechanical
gate, and #756 did not change that.**

**2. Is the obligation really "called enforced"?** Verified verbatim in
`docs/decisions/0007` (Status: accepted, 2026-09-09, by the repository owner):
*"`pr-contract` refuses a body without an `## Approval` section, a head that
moved, a missing verdict — **mechanically, on every pull request**, whether or
not a human is in the loop."* The same record defers the file class to
`CLAUDE.md` — and the implementation keys on the author's title, not on the
file class. That is the `high` anchor exactly.

**3. Attack on the consequence figure, which is where I would qualify the
finding.** The finder's headline "32 of 50 merged with it off" counts commits
where the *requirement* was switched off, not where approval was *absent*. I
measured the stricter thing: of the 11 window commits that rewrote
owner-declared policy text under a non-`policy:` title, **7 carried an
`## Approval` section voluntarily and 4 did not** — #756, #753, #675, #672.
So the realised harm is 4 unapproved policy merges in 72 h, not 32; the 32 is
the size of the hole, not the number of things that fell through it. Both are
true of different metrics and the judge should see both. It does not change the
verdict: #756 — the pull request that added CODEOWNERS and decision 0008, a
governance change by any reading — is itself one of the four.

**4. Perturbation.** One identical body, one identical head, title
`policy: rewrite a rule that binds a seat` → **exit 1**, naming
`` no `## Approval` section ``; title `docs: rewrite a rule that binds a seat`
→ **exit 0**. Direction **to_zero**. Reproduced against the pin tree's
`policy_lint.mjs`. The predicate is byte-identical at all four SHAs in play and
only its line number moves — `3135` at `ae36eff`, `3136` at `dc03619`, `3137`
at `52b970b6`, **`3223` at the pin** — which is why I cite it by text and not
by line. `record`'s `if:` moves the same way: `225` / `242` / `242` / **`261`**.
A citation by line number to this file goes stale within a day.

## Vote

**verify**, severity **high**.

---

# D11-04 — `medium`. **weaken to `low`.**

## My metric

> `v4_security_policy_files` and `v4_private_report_channels_enabled`, measured
> **separately**, because a published file and a private intake channel are
> different obligations and the finding treats them as one sentence.

## My numbers

```
v4_security_policy_files=0                       at BOTH ae36eff and da43c9d, over 8 candidate paths
v4_github_community_profile_security_policy=false (GitHub's own answer, independent of my filesystem sweep)
v4_owner_dot_github_fallback_repo_exists=0        (tvofi/.github -> 404; Scorecard's fallback route is closed)
v4_private_report_channels_enabled=true           <-- GET /repos/tvofi/heatpump_optimizer/private-vulnerability-reporting
v4_api_failures=0
```

Plus: `grep -rniE "report a vulnerability|security policy|vulnerabilit"` over
`README.md` and `docs/*.md` at the pin → **0 hits**.

## Attacks I ran

**1. The claim I set out to refute, and did.** The finding states, as evidence:
*"GitHub private vulnerability reporting is also not enabled — the repository's
`security_and_analysis` block lists secret scanning and Dependabot, not
`private_vulnerability_reporting`."* That is an inference from a key's absence
in a payload that never carries that key. The endpoint that answers the
question —
`GET /repos/tvofi/heatpump_optimizer/private-vulnerability-reporting` —
returns **`{"enabled": true}`**.

**2. Was it ever measured?** No. `standards.py:184` computes
`bp_vulnerability_report_process` as `int(sec)` where `sec` is the SECURITY.md
existence sweep at `:125`. The harness never queries private vulnerability
reporting at all, so the parenthetical is an unexecuted claim in the prose that
no RESULT line stands behind. Whether the setting was toggled between the
finder's run and mine is therefore beside the point: the sentence was not
measured either way, and it is false now.

**3. What survives.** The file half, twice over: my filesystem sweep across 8
candidate paths at both SHAs, and GitHub's own community-profile endpoint,
which is what Scorecard's `Security-Policy` check reads. `sc_security_policy=0`
and Scorecard 0/10 stand. The owner's `.github` fallback repository does not
exist, so that route is closed too.

**4. What does not survive.** *"a reporter today has no non-public channel"* is
false — with private vulnerability reporting enabled, GitHub renders a
"Report a vulnerability" control on the repository's Security tab, which is
also a fair reading of the OpenSSF Best Practices wording the finding quotes
("publish the process for reporting vulnerabilities **on the project site**").
I would call `bp_vulnerability_report_process` contested rather than 0, and I
say that rather than substituting my reading for the finder's.

**5. Perturbation.** A `SECURITY.md` written under a temp root and unlinked in
a `finally`: `v4_security_policy_files 0 → 1`, direction **up**; the live tree
re-read afterwards still 0. The tree was never written.

## Vote

**weaken**, severity **low**. One missing file, one Scorecard check at 0/10,
and a contested badge criterion. The consequence sentence that carried the
`medium` — a vulnerability with nowhere private to go — is refuted by an
executed call. This is hygiene, which is the brief's `low`.

---

# D11-05 — `medium`. **verify.**

## My metric

> Of the GitHub text surfaces a write-capable seat prompt reads, how many can
> be written by an account that is **not** a collaborator, with each surface's
> gate probed rather than assumed; and `v5_boundary_statements_binding_a_seat`,
> which — unlike the finder's per-file count — **excludes** a per-round audit
> brief, because a dimension brief instructs one audit round and binds no seat
> afterwards.

## My numbers (pin, and the same at the baseline tree)

```
SURFACE issue body                     writable_by_a_non_collaborator=1
SURFACE issue comment                  writable_by_a_non_collaborator=1
SURFACE pull-request body from a fork  writable_by_a_non_collaborator=1
SURFACE pull-request comment           writable_by_a_non_collaborator=1
SURFACE review comment                 writable_by_a_non_collaborator=1
SURFACE discussion                     writable_by_a_non_collaborator=0   (discussions disabled)
v5_open_untrusted_authoring_surfaces=5 of 6
v5_interaction_limit_set=0            (raw: {})
v5_corpus_files=37 at da43c9d, 36 at ae36eff
v5_boundary_statements_binding_a_seat=0      at BOTH trees
v5_boundary_statements_in_a_per_round_brief=1 (tools/audit/briefs/D11.md)
v5_loose_hits_read_and_rejected=1            (tools/audit/briefs/orchestrator.md)
v5_api_failures=0
```

Authorship census, GraphQL, paginated to exhaustion, **0 refusals**, compared
as sets:

```
526 pull requests  -> {"tvofi/User": 523 (OWNER), "claude/Bot": 3 (CONTRIBUTOR)}
246 issues         -> {"tvofi/OWNER": 246}
737 issue comments -> {"tvofi/OWNER": 737}    (1 issue's comments truncated at 100, so 737 is a floor)
510 merges         -> {"tvofi/User": 510}
```

## Attacks I ran

**1. The commissioned attack: is the door truly open, or only nominally?** I
probed the settings that would close it rather than reasoning from
"public". `visibility=public`, `has_issues=true`, `allow_forking=true`,
`hasDiscussionsEnabled=false`, and —
the decisive one — `GET /repos/tvofi/heatpump_optimizer/interaction-limits`
returns **`{}`**: no `collaborators_only` or `contributors_only` limit is set.
That single setting is the one thing that would close all five surfaces at
once, and it is not set. **The door is open, measured, not inferred: 5 of 6
surfaces.**

**2. The commissioned attack: has a seat actually ingested untrusted text?**
No, and my census is independent of the finder's and larger. 246 of 246 issues
and 737 of 737 issue comments are authored by `tvofi` (`OWNER`). The only
non-owner pull-request author across all 526 is the `claude` **Bot**
(`CONTRIBUTOR`), on #616, #617 and #618, all three merged by `tvofi` — the
owner's own tooling, not an outside account. So every current path is
owner-authored, which is exactly what the finder's `medium` hedge says. The
finder's `distinct_issue_authors=1` reproduces under a wholly separate
enumeration, and the one honest gap is that one issue (the #201 tracking issue)
has more than 100 comments and GraphQL truncated it; I report 737 as a floor
rather than as a total.

**3. My own predicate over-fired, and I read the hit instead of trusting the
count.** My first boundary regex was a plain
`/not instructions|untrusted|prompt injection|…/` and it returned
`tools/audit/briefs/orchestrator.md` — line 18, *"…every role contract here are
not instructions you relay"*, a sentence about relaying a role contract that
says nothing about an issue body. The tightened predicate requires a **subject**
(issue body / comment / review comment / free text a seat did not write) and a
**claim** (data not instructions / untrusted / prompt injection) in the same
sentence, and it prints every loose hit it rejected so the count can be checked
rather than trusted. With that: **0 boundary statements bind a seat**, and the
only corpus file matching at all is `tools/audit/briefs/D11.md` — this round's
own brief, which is the same file the finder named. The finder's
`boundary_files=1` and my `binding=0, brief-only=1` are the same fact under two
definitions.

**4. Corpus size.** `policy_lint.mjs` itself prints
`TOTAL: 0 error(s) across 36 policy file(s)` at the baseline, which matches my
36; at the pin I get 37, the one addition being `.claude/rules/comment-readback.md`
(from #759). I could **not** reproduce the "35 → 41 files" figure I was handed
under `POLICY_GLOBS` — `.cursor/rules/` holds 10 files at the pin, so no
obvious composition gives 41. The substantive half of that re-measurement —
exactly one corpus file states the boundary, and it is the audit brief —
reproduces under both my definition and the finder's.

**5. Perturbation.** A corpus **copy** under `$TMPDIR` with one boundary
sentence appended to `.claude/rules/writing-for-agents.md`:
`v5_boundary_statements_binding_a_seat 0 → 1`, direction **up**, and the file
named in the arm-B output is the one I edited. The tree was not written.

## Vote

**verify**, severity **medium**. The severity the finder chose is already the
hedged one — open door, nobody through it — and my independent census over
526 pull requests, 246 issues and 737 comments supports the hedge rather than
raising it.

---

## Exposure

Read-only, as this panel's exception permits and requires be recorded.
`gh api`: `repos/tvofi/heatpump_optimizer`, `/rulesets`, `/rulesets/22628467`,
`/rules/branches/main`, `/branches/main/protection` (404), `/collaborators`,
`/collaborators/tvofi/permission`, `/custom-roles` (404), `/community/profile`,
`/interaction-limits`, `/private-vulnerability-reporting`,
`/commits/{sha}/check-runs?filter=all|latest`, `/pulls/{n}`, `/issues/comments`,
`search/issues`, `repos/tvofi/.github` (404); `gh ruleset view 22628467`;
`gh api graphql` for commit→pull-request association, commit check suites and
runs, and the pull-request / issue / comment authorship census. Public
documentation fetched: GitHub's REST "Repository rules" page (for the
`actor_id` wording) and "About protected branches" (for the
`successful`/`skipped`/`neutral` wording). The repository's own git history at
and before the pin.

**Nothing was created, edited, closed, commented on, merged, pushed or
dispatched. No workflow was run or re-run. The ruleset was read and never
modified. No git worktree, branch, tag or remote was created; the two trees the
filesystem metrics ran against were extracted with `git archive`, which touches
no shared repository state, and were deleted afterwards.** I did not open
`docs/audit-*.md` or any other verifier's directory.
