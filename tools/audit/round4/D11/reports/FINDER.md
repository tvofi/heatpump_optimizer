# D11 — Governance mechanisms and policy (round 4)

- **baseline** `7dd68dd327fe3dbfb09f3bd0fe38910c58877697` (2026-09-12T10:44:09Z)
- **tree** `/Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-r4-D11` (a real checkout, `.git` present, because the subject is the process)
- **harnesses** `tools/audit/round4/D11/*.py`, each runnable by the single command in its header
- **interpreter** `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`, `PYTHONPATH=tests/hastub`, from the repository root; node v20.10.0
- **limits observed** `main` never perturbed, the live ruleset never perturbed, no comment posted on any live pull request. Every perturbation was run against a scratch copy under `/tmp/claude-501/d11/pert`.

## exposure

Sources read that other dimensions are walled off from:

| source | what was read |
|---|---|
| `gh api repos/tvofi/heatpump_optimizer/rulesets` and `/rulesets/22628467` and `/history` and `/history/{version}` | the ruleset object, its bypass actors, and all five versions |
| `gh api repos/tvofi/heatpump_optimizer/rules/branches/main` | the other arm of the same question |
| `gh api repos/tvofi/heatpump_optimizer` , `/interaction-limits`, `/code-scanning/default-setup`, `/releases` | visibility, issues, CodeQL default setup, release assets |
| GraphQL `pullRequests(states:MERGED)` + REST `pulls?state=all` | 592 merged pull requests, their authors, merge commits, head OIDs and reviews |
| `gh api .../commits/{sha}/check-runs` | the CHECK-RUNS LISTING at 592 merged heads — never the checks summary |
| `gh api .../actions/runs?branch=main&event=push` and `/actions/runs/{id}/jobs` | 1000 push-event runs on `main`, and the failing job of 60 of them |
| `gh api .../issues/{n}/comments` | `Fix review:` verdicts on a 1-in-4 sample of the window |
| `gh api search/issues?q=…"recurring friction"` | whether the friction detector has ever opened anything |
| the git history of `main` | 761 commits, 113 tags, tag dates |
| `docs/plan-2026-09-open-issues.md`, `docs/HANDOVER.md`, `docs/decisions/` | required by the brief: disposition rows, staleness, the decision record. **Not read:** `docs/audit-*.md`, `docs/backlog.md`, and no round-3 issue body for its verdict. |
| standards texts, fetched 2026-09-12 | `raw.githubusercontent.com/ossf/scorecard/main/docs/checks.md`; `slsa.dev/spec/v1.1/levels`; `bestpractices.dev/criteria/0`; `genai.owasp.org/llm-top-10/`; NIST AI 100-1 GOVERN subcategory text. **ISO/IEC 42001 clause 10 could not be fetched** — iso.org returned HTTP 403 on both the standard page and the OBP viewer — so that row is scored against the clause as commonly published (10.1 continual improvement, 10.2 nonconformity and corrective action) and is flagged in the scorecard. |

---

## 1. Mechanism inventory

**The row count is derived, not carried.** `mechanism_inventory.py` re-adds it at
every run and prints the addition:

```
ruleset rules on main                  3
required status-check contexts        16
policy_lint check classes             14
brief_lint carry fixtures              4
structure_budgets.json metrics        24   (keys less recorded_at)
wired hook events                      3
self-testing scripts driven here       9
----------------------------------------
mechanisms                            73
```

Nine controls were **driven by hand** (a self-test's green tick is not a control
until the program has been run): all nine refused nothing on a healthy tree and
exited 0, which is their null control; `policy_lint_mutants.mjs` empties 12
named functions and each turns the acceptance red.

| # | family | mechanism | refuses where | positive control (executed) | what it leaves uncovered |
|---|---|---|---|---|---|
| 1 | ruleset | `deletion` | `main` | `ruleset_probe.py` reads it present in all 5 versions | admin bypass `always` |
| 2 | ruleset | `non_fast_forward` | `main` | same | admin bypass `always` |
| 3 | ruleset | `required_status_checks` (16 contexts) | `main`, PR head | `merge_census.py`: 0 of 164 window merges merged with a required context absent | **the merging identity holds `bypass_mode: always`**; a `skipped` conclusion satisfies the rule |
| 4–19 | required check | `fast (3.14)`, `browser`, `briefs`, `closure-scope`, `closures`, `typing`, `hassfest`, `validate-hacs`, `policy-docs`, `wave-script`, `pr-contract`, `env-matrix`, `CodeQL`, `Analyze (actions)`, `Analyze (javascript-typescript)`, `Analyze (python)` | PR head | present on every window merge | `record`, `record-status`, `slow`, `nightly-*`, `coverage`, `mutation` are **not** required; `record` was removed 2026-09-11T21:24Z and four files still say it is required |
| 20–33 | `policy_lint.mjs` | `citations`, `counts`, `no-gh`, `budgets`, `index`, `duplicates`, `pr-body`, `named-docs`, `coverage`, `provenance`, `record`, `render`, `stats`, `sunset` | PR + push to main (`policy-docs`), `record` on push/cron only | driven: `node policy_lint.mjs` → 0 errors over 38 files; the fixture acceptance holds 73 errors / 110 pins across 12 classes; `policy_lint_mutants.mjs` empties 12 functions and each turns it red | `stats` and `sunset` run with `\|\| true` and **cannot fail anything**; `pr-body`'s `--red` arm is never passed by CI (finding D11-03); `table` is pinned by the acceptance but is not a row in the `CHECKS` table the tool prints |
| 34–37 | `brief_lint.mjs` | four `carry-99000*.json` acceptance fixtures | PR (`briefs`) | driven: 10 errors pin the carry acceptance, and the correct fixture produces none | nothing lints a wave brief that is absent rather than malformed |
| 38–61 | `structure.py` | 24 budget metrics (`structure_budgets.json` keys less `recorded_at`) | PR (`fast`) + push to main | count derived by the harness; deleting one metric drops `mechanisms` to 72 | metrics may only move down, so a genuine feature needs an owner-approved raise; no metric measures the governance corpus itself |
| 62–64 | hooks | `SessionStart`, `PreToolUse`, `Stop` | the seat's own session | driven: `policy_lint --hooks` → 3 wired hooks, 5 / 16 / 19 self-test assertions pass | `.claude/hooks/always-fails.sh` is present and wired to nothing; a hook binds only a session that loads `.claude/settings.json`, so a cloud seat or a human merging in the UI meets none of them |
| 65–73 | self-tests | `rules_sync --check`, `policy_lint` corpus, `policy_lint_mutants`, `fragments_sync --self-test`, `policy_lint --hooks`, `gh_comment.py self-test`, `prepr.sh --self-test`, `push.sh --self-test`, `check-wave-script.mjs` | PR (`policy-docs`, `pr-contract`) | all nine driven here, all rc=0 | `prepr.sh` and `push.sh` are advisory: a seat that never runs them meets no refusal, and the CI step runs only their `--self-test` |

**Mechanisms whose control fires only outside CI: 1.** `pr-body`'s `--red` arm.
Driven by hand on the corpus's own `unnamed-red.md` fixture:

```
with --red 'fast (3.14)'                                   rc=1   (refusal fires)
--pr-body --head --title --paths-file  (governance.yml's)  rc=0   (same body passes)
governance.yml passes --red                                False
```

---

## 2. Standards scorecard

`standards_scorecard.py`, 32 criteria, one executed check each. The OpenSSF
Scorecard binary cannot run on this box (`which scorecard docker go` → none), so
each check is evaluated against the criterion text fetched from
`ossf/scorecard/docs/checks.md` using the inputs the tool reads. **Per check with
its reason, never the aggregate.**

| standard | criterion | verdict | executed check | gap |
|---|---|---|---|---|
| Scorecard | Branch-Protection | **FAIL** | ruleset read both arms; tier1=True, tier2=False, tier3=True, tier5(include administrators)=False | no `pull_request` rule in any of 5 versions; admin holds `bypass_mode: always`. Scorecard stops at the first unmet tier, so tier 3's points are not earned |
| Scorecard | Code-Review | **FAIL** | census of 592 merged PRs | **0** carry an APPROVED review by an account other than the author |
| Scorecard | Dangerous-Workflow | PARTIAL | `untrusted_text.py` over 5 workflows | no `pull_request_target`/`workflow_run`; 3 `${{ }}` do reach a `run:` line (`tests.yml:124,907,908`), all three GitHub-constrained (one `type: boolean` input, two 40-hex SHAs) — the pattern without the risk |
| Scorecard | Token-Permissions | PASS | 4 of 5 workflows have a read-only top-level block; 3 job-level write declarations, each commented | `release.yml`'s top-level `contents: write` is workflow-wide rather than job-level |
| Scorecard | Pinned-Dependencies | **FAIL** | 2 of 9 distinct `uses:` pinned by SHA | `actions/checkout@v5`, `setup-node@v5`, `setup-python@v6`, `cache@v5`, `cache/save@v5`, `upload-artifact@v6`, `download-artifact@v7` are mutable tags |
| Scorecard | CI-Tests | PASS | check runs present on every merged head; 16 required contexts | — |
| Scorecard | SAST | PASS | `code-scanning/default-setup` state=configured, 5 languages, `extended` suite | — |
| Scorecard | Maintained | PASS | commits in 4 distinct ISO weeks over 90 days; not archived | — |
| Scorecard | Security-Policy | PASS | SECURITY.md, 71 words, https advisory link, disclosure text | — |
| Scorecard | Signed-Releases | **FAIL** | last 5 releases carry **0** assets | nothing to sign; `release.yml` uploads no artefact |
| SLSA v1.1 | Build L1 (provenance exists) | **FAIL** | release path `stamp.py` → `vN.N.N` tag → `gh release create` | no provenance is generated for any artefact |
| SLSA v1.1 | Build L2 | **FAIL** | L1 unmet | the producer half is met (GitHub-hosted runner); the platform half is not |
| SLSA v1.1 | Build L3 | **FAIL** | L1/L2 unmet | next level costs one step: `actions/attest-build-provenance` in `release` |
| BestPractices | repo_public / repo_track / version_unique / release_notes / release_notes_vulns | PASS ×5 | public; git history; `stamp.py` sole assigner; 111 `## v` sections quoted verbatim into the release; no CVE assigned | — |
| BestPractices | test_policy + tests_are_added | PASS | CLAUDE.md rule 2, `fixer.md`, the 24-metric ratchet | — |
| BestPractices | vulnerability_report_process / _private | PASS ×2 | SECURITY.md names the private advisory form | — |
| BestPractices | vulnerability_report_response | **FAIL** | SECURITY.md contains no response-time commitment; no advisory exists | the ≤14-day criterion cannot be evidenced |
| NIST AI 100-1 | GOVERN 1.2 | PASS | measurement discipline, null controls, perturbation and stop rules are binding in the corpus | — |
| NIST AI 100-1 | GOVERN 1.5 (monitoring and periodic review) | PARTIAL | `--stats`/`--sunset` weekly + on push, both `\|\| true` | the histogram reports `blocked` at **4** against its own threshold of **3**, and `search/issues …"recurring friction"` returns `total_count=0` — the detector has never opened anything |
| NIST AI 100-1 | GOVERN 2.1 (accountability, documented roles) | PARTIAL | 7 role contracts exist; 0 of 592 merges reviewed by a second account; 2 distinct PR authors (589 `tvofi`, 3 `claude`) | reviewer ≠ author is not provable from GitHub's records for any merge |
| NIST AI 100-1 | GOVERN 3.2 (human oversight) | PARTIAL | `.github/CODEOWNERS` names the owner for the policy set | inert without a `require_code_owner_review` rule; no version has one, so the oversight point exists only in prose |
| NIST AI 100-1 | GOVERN 4.3 (testing, incidents, sharing) | PASS | `defect-root-cause.md` + `root-cause.md`: trigger, four process states, cost test | only the red-check trigger is claimed enforced, and it is not (D11-03) |
| NIST AI 600-1 | GV-1.2 / GV-4.1 (generative-AI risk documented) | **FAIL** | `untrusted_text.py`: 0 countermeasure sentences in the whole policy + seat corpus; 8 seat instructions read issue/PR comments as authority | the generative-specific risk class is absent from the governance corpus |
| ISO/IEC 42001 | clause 10, improvement | PARTIAL | corrective-action mechanism present; one-sided size ratchet present; corpus at **60800/60800 tokens, zero headroom** | the measurement half is missing: nothing reads the loop's own output. *(Clause text could not be fetched — iso.org 403.)* |
| OWASP LLM 2025 | LLM01 Prompt Injection | **FAIL** | public repo, issues open, no interaction limit; 8 obey-sites; 0 guard-sites | any GitHub account can write text a seat treats as authority |
| OWASP LLM 2025 | LLM05 Improper Output Handling | PASS | `pr-contract` passes the body through `env:` to a file; `figure_lint.mjs` RESOLVES rather than executes the commands a body names | — |
| OWASP LLM 2025 | LLM06 Excessive Agency | **FAIL** | seats hold push, `issue_write`, `add_issue_comment` and merge; 0 approving reviews in 592 merges | no human checkpoint between an injected instruction and `main` |

Counts: Scorecard 5 PASS / 1 PARTIAL / 4 FAIL; SLSA Build level **0**;
Best Practices 8 PASS / 1 FAIL; NIST AI 100-1 2 PASS / 3 PARTIAL; NIST AI 600-1
1 FAIL; ISO 42001 1 PARTIAL; OWASP 1 PASS / 2 FAIL.

---

## 3. DORA's four keys

Window **2026-09-08T00:00:00Z .. 2026-09-12T10:44:12Z** (4.45 days), closed at the
baseline commit. The window starts one day inside the API's 1000-result cap on
`actions/runs`, which this repository hits in five days; a longer window would
silently under-count reds.

| key | measured | band | how |
|---|---|---|---|
| deployment (release) frequency | **1.12 releases/day** — 5 `vN.N.N` tags (v6.3.19, v6.3.20, v6.4.0, v6.4.1, v6.4.2) | Elite/High | tag committer dates |
| lead time for changes (merge → released tag) | **median 7.41 h**, p90 21.2 h, n=212; 5 merges unreleased at baseline | Elite (<1 day) | first `vN.N.N` whose history contains the merge commit |
| change failure rate | **47.7 %** any workflow (106 of 222 `main` heads) — **44.1 pp Governance**, **11.7 pp Tests** | Low band (46–60 %) on the combined figure; Elite on Tests alone | latest push-event run per workflow per `main` head |
| time to restore | **median 0.61 h** (Governance, 22 episodes, max 8.95 h); **1.11 h** (Tests, 8 episodes, max 3.14 h); Validate and Hassfest 0 episodes | Elite (<1 h) | first failing push run → `updated_at` of the next success |

**The change-failure rate is a governance artefact, not a code artefact.** Of 60
sampled Governance failures on `main`, **58 are the `record` job** (4 `policy-docs`,
4 `env-matrix`). `record` refuses a merge that has no disposition row, and it can
only run after the merge — its `if:` excludes `pull_request` for a stated and
correct reason. So the disposition rule turns `main` red roughly two pushes in
five and the red lands on whoever pushes next.

**Governance cost per merge** (`governance_cost.py`, 164 merges): median **75 s**
of check-run time against **758 s** for the code gate — **5.8 %** of CI seconds.
Body rounds, counted as `pr-contract` runs at the merged head: mean **1.63**,
median 1, max 8; 68 of 164 merges took more than one round.

---

## 4. Conformance table

Population: every merge into `main` between the instant `main-protect` first
became active (**2026-09-09T09:37:08Z**) and the baseline commit — **164 merges**,
drawn as the full set, not a sample, from GraphQL `pullRequests(states:MERGED)`
and cross-checked against REST `pulls?state=all` by **set of numbers** (the free-text
subject enumerator is never used here; it misses 4 of the last 30 merges, see
non-findings). The review row uses the whole repository (**592 merges**) because a
review obligation does not begin with the ruleset. The verdict row is a systematic
1-in-4 sample of the window (n=41).

| obligation | source of the obligation | conformance | note |
|---|---|---|---|
| an approving review by an account other than the author | NIST AI 100-1 GOVERN 2.1; Scorecard Code-Review | **0 / 592** | no `pull_request` rule has ever existed; 589 of 592 merges authored by `tvofi` |
| a `Fix review: merge` verdict at the merged head by a seat other than the author | `fix-review.md`; `web-fix-wave.js` verdict grammar | **16 / 41** carry a verdict; **15 / 16** name the merged head; **0 / 16** by a different GitHub account | the protocol binds fix-wave PRs, so 16/41 is coverage, not failure; `0/16` is the conformance claim |
| the first `pr-contract` run at the merged head is green | the S10 commit → body → push order in `steward/SKILL.md` | **139 / 164** (84.8 %) | read from the check-runs listing; the checks summary shows all 164 green |
| no required context red at the merged head | `main-protect` | **136 / 164** (82.9 %) | all 28 reds are `pr-contract`'s own earlier run; **0 / 164** merged with a required context absent |
| a red required check named and answered under `## Red checks` | CLAUDE.md "Root-cause remediation"; `defect-root-cause.md` | **10 / 28** (35.7 %) | 164/164 carry the heading (the template supplies it); 8 of the 18 unanswered say "none" or "None at the time of opening" |
| a disposition row in the plan or the handover | `delivery-status-tracking.md`; the `record` job | **164 / 164** | the repository's own `--record` enumerator agrees (0 without a disposition) |

---

## 5. Findings

### D11-01 — `critical` — a merge to `main` needs no review, and no ruleset version has ever required one

`main-protect` (22628467) carries three rules: `deletion`, `non_fast_forward`,
`required_status_checks`. **No `pull_request` rule exists in any of its five
versions**, so `required_approving_review_count` is unset and
`require_code_owner_review` is unset; `.github/CODEOWNERS` therefore requests a
review and blocks nothing, which its own header states. Measured against the
record rather than the configuration: **0 of 592 merged pull requests carry an
APPROVED review by an account other than the author**, and 0 carry an APPROVED
review at all — the only review states GitHub has ever recorded on this
repository are 8 `COMMENTED`. 589 of 592 merges were authored by `tvofi`.

Independently, the ruleset carries `bypass_actors: [{RepositoryRole 5, always}]`
and the identity that performs the merges reports `admin: true`, so even the
required-check rule does not bind the merging actor. The two arms disagree by
construction and that is the executed perturbation: `rules/branches/main` reports
16 enforced contexts and carries no bypass field at all; the ruleset object
reports the same 16 and one always-bypassing actor.

Evidence: `ruleset_probe.py` → `pull_request_rules=0`,
`ruleset_versions_with_pull_request_rule=0`, `bypass_actors_always=1`,
`bypass_applies_to_merger=1`; `merge_census.py` → `merged_all=592`,
`reviewed_by_non_author=0`, `approved_any=0`.

*This is a stated, deliberate position in `docs/decisions/0005` and `0008` — one
identity cannot approve its own pull request, so the rule would lock the
repository. The finding is not that the decision is wrong. It is that the record
in several places describes the boundary as guarded, the standards all key on
this one fact, and the ordered plan in decision 0008 (machine account → switch →
verified login → code-owner rule) has no instrument that would notice if it
stalled.*

### D11-02 — `critical` — seats are instructed to obey text any GitHub account can write, and the corpus contains no countermeasure

`untrusted_text.py` finds **8 sites** in the seat corpus directing an agent to
read an issue or pull-request body or comment and act on it, the strongest being
`web-triage.js:153`: *"Read the issue body AND every comment: the comments carry
judge verdicts, corrections and claims that override the body."* The same file
grants that seat `issue_write` and `add_issue_comment`; `web-fix-wave.js:285`
tells a seat to take its merge decision from "the most recent comment starting
`Fix review:`".

The channel is open to the world: the repository is `public`, `has_issues=true`,
and `interaction-limits` is empty, so any GitHub account can write into it. The
countermeasure count is **0** — no sentence anywhere in `CLAUDE.md`, the ten
`.claude/rules/` files, the thirteen briefs, the role contracts or the seat
prompts names prompt injection, untrusted input, or the data/instruction
boundary. (`governance.yml:231` names *shell* injection, a different class, and is
excluded by the harness.)

This is OWASP LLM01 with LLM06 as the amplifier: the seat that would act on
injected text also holds push and merge grants, and by D11-01 there is no second
party between it and `main`.

Evidence: `untrusted_text.py` → `seat_obey_sites=8`, `seat_guard_sites=0`,
`writer_population=public`, `dangerous_triggers=0`,
`shell_interpolations_freetext=0`.

### D11-03 — `high` — the one root-cause trigger `CLAUDE.md` calls enforced is enforced by nothing

`CLAUDE.md` § "Root-cause remediation" says: *"Only the red-check trigger is
enforced: the fixer names the check in the pull-request body and answers it
there."* The refusal exists — `policy_lint.mjs:3432`, class `pr-body` — and it is
reachable only through `--red`, which **`governance.yml`'s `pr-contract` step does
not pass**. Driven by hand on the corpus's own fixture, the same body gives
rc=1 with `--red 'fast (3.14)'` and **rc=0** through the exact argument list CI
uses. `tools/audit/prepr.sh:133` is the only caller that passes `--red`, and
`prepr.sh` is advisory.

Where the obligation bites, conformance is **10 of 28**: 28 of the 164 window
merges had a required context run red at the merged head, and 18 of their
`## Red checks` sections do not name it — eight of those say "none" or "None at
the time of opening".

A caveat the fix must carry: all 28 reds are `pr-contract`'s *own* earlier run at
that head, so wiring `--red` naively deadlocks (the body would have to name a red
caused by not naming it). The countermeasure has to exclude `pr-contract`'s own
runs, or key on the first run rather than the set.

Evidence: `mechanism_inventory.py` → `controls_inert_in_ci=1`;
`merge_census.py` → `merges_with_red_required=28`, `red_answered=10`.

### D11-04 — `high` — the tree's account of the merge boundary contradicts the live ruleset in eight places, and nothing derives it

`record` was removed from `main-protect`'s required contexts at
2026-09-11T21:24:43Z and `fast (3.13)` at 2026-09-12T09:18:56Z; the set went
18 → 17 → **16**. At the baseline, eight lines in the tree still assert
otherwise:

```
tests/record_status.py:13        `record` is a required context      (it is not)
tests/record_status.py:15        18 required contexts                (16)
tests/entities.py:15394          18 required contexts                (16)
.github/workflows/governance.yml:354  18 required contexts           (16)
docs/HANDOVER.md:52              18 required status checks           (16)
docs/plan-2026-09-open-issues.md:667  18 required contexts + `record` required
docs/plan-2026-09-open-issues.md:1091 18 required status checks      (16)
```

`RELEASE_NOTES.md:29` records the drop, so the tree contradicts itself. This is
not cosmetic: the whole stated justification for the `record-status` job — "the
defect is that `record` is one of `main-protect`'s 18 required contexts while
reporting `skipped`" — rests on a premise that is now false, and `record-status`
is a required-adjacent check on every pull request. `policy_lint`'s `counts` class
checks a literal against *a derivation in the tree*; **no derivation reads the
API**, so the class structurally cannot see this.

Evidence: `ruleset_probe.py` → `tree_claim_mismatches=8`, `required_contexts=16`,
`ruleset_versions=5`.

### D11-05 — `medium` — the disposition rule is unsatisfiable before the merge and turns `main` red on 44 % of pushes

`record`'s `if: github.event_name != 'pull_request'` is correct and the workflow
argues it well. The consequence is measured here for the first time as a rate:
over 222 distinct `main` heads in the DORA window, **98 had a failing Governance
run**, and 58 of 60 sampled failures are the `record` job. That is a change
failure rate of **44.1 pp of the 47.7 pp total**, against 11.7 pp for the actual
code gate. The existing countermeasure (`record-status`, #738) converts "`main` is
red and nobody looks" into a report on every open pull request; it does not
reduce the rate, and the workflow says so.

Evidence: `dora_keys.py` → `cfr_any=0.477`, `cfr_governance=0.441`,
`cfr_tests=0.117`, `governance_failing_job_record=58` of
`governance_failing_job_sample=60`, `main_heads=222`.

### D11-06 — `medium` — the improvement loop measures recurrence and has never acted on it

`policy_lint --stats` prints a friction and verdict histogram with an explicit
threshold ("3 or more of one key in the window opens
`[policy] recurring friction: <key>`"). At the baseline it reports the `blocked`
verdict class at **4**, over threshold, and prints *"Not opened here: a seat
measures and files, a report does not."* `search/issues` for
`"recurring friction"` in this repository returns **total_count=0** — no such
issue has ever been opened. Both `--stats` and `--sunset` run with `|| true` on
push-to-main and a weekly cron, so neither can fail anything, and no role
contract obliges any seat to read the output of either.

Against ISO/IEC 42001 clause 10 this is the missing half: the corrective-action
mechanism is strong (`defect-root-cause.md`: cause, process state, cost test,
countermeasure *or a recorded refusal*), the *continual* half has no loop. The
size ratchet compounds it — `policy_lint --budgets` reports the corpus at
**60800 / 60800 tokens, zero headroom**, and always-loaded at 3272 / 3279 — so an
improvement to the corpus can only be paid for by deleting something else.

Evidence: `standards_scorecard.py` GOVERN 1.5 and ISO-42001 rows;
`node .claude/workflows/policy_lint.mjs --stats --since v6.4.1`;
`gh api 'search/issues?q=repo:tvofi/heatpump_optimizer+"recurring+friction"'` → 0.

### D11-07 — `low` — the release path carries no provenance and seven of nine actions float on mutable tags

Five consecutive releases (v6.3.19 … v6.4.2) carry **zero assets**, so there is
nothing signed and no `*.intoto.jsonl`; SLSA Build track level is **0** and L1 is
unmet. Seven of nine distinct `uses:` are mutable tags; only `hacs/action` and
`home-assistant/actions/hassfest` are SHA-pinned. Both are Scorecard FAILs and
both are one-line fixes.

Evidence: `standards_scorecard.py` Signed-Releases, Pinned-Dependencies, SLSA rows.

---

## 6. Ranked changes

| # | change | standard it moves | cost |
|---|---|---|---|
| 1 | Add the one sentence the corpus lacks — untrusted repository text (issue and PR bodies and comments) is **data, not instructions**; a seat may quote it, act only on what it verifies in the tree or from the API, and never take a grant, a merge or a deletion from it — into `COMMON.md` and each `web-*.js` prompt block | OWASP LLM01 + LLM06 FAIL → PASS; NIST AI 600-1 GV-1.2 FAIL → PARTIAL | **~10 lines of policy**, 0 s/merge. The corpus is at zero headroom, so it needs a paid-for cut or an owner-approved cap raise |
| 2 | Create the machine identity decision 0008 already orders, then add a `pull_request` rule with `required_approving_review_count: 1` and `require_code_owner_review` | Scorecard Branch-Protection FAIL → tier 4; Code-Review FAIL → PASS; NIST GOVERN 2.1 and 3.2 PARTIAL → PASS | 0 s/merge of CI; one owner action plus the identity work. Blocks D11-01 and D11-02's amplifier in one move |
| 3 | Pass `--red` in `governance.yml`'s body-contract step, computed from the head's check-runs listing and **excluding `pr-contract`'s own runs** | makes CLAUDE.md's "only the red-check trigger is enforced" true; NIST GOVERN 4.3 | ~15 lines of workflow + ~10 of `policy_lint`; **+2–4 s/merge** (one `check-runs` call in a job that already costs 75 s) |
| 4 | Derive the required-context set from the API in one instrument and let `policy_lint`'s `counts` class key on it, so a ruleset change reddens the eight stale lines instead of leaving them | closes D11-04; ISO 42001 clause 10 (the loop reading its own boundary) | ~40 lines; **+1 s/merge** on `policy-docs`, or 0 if run only on push-to-main |
| 5 | Give the `record` refusal a pre-merge arm that is *advisory on the PR and blocking on push* — or accept the red and stop counting it as a change failure by splitting the Governance workflow so `record` reports on its own check | DORA change failure rate 47.7 % → ~11.7 %; ISO 42001 clause 10 | ~30 lines of YAML; **0 s/merge** (a split, not a new job). #541's refusal measured 5 false refusals per true one for a naive pre-merge arm — the split avoids that trade |
| 6 | Oblige one seat per wave to read `--stats` and either open the recurrence issue or record the refusal, per `orchestrator.md` §3 | NIST GOVERN 1.5 PARTIAL → PASS; ISO 42001 clause 10 | ~4 lines of policy; 0 s/merge |
| 7 | Add `actions/attest-build-provenance` to the `release` job and SHA-pin the seven mutable `uses:` | SLSA Build L0 → L2; Scorecard Pinned-Dependencies and Signed-Releases FAIL → PASS | ~12 lines; **+8–15 s per release**, 0 s/merge |

---

## 7. Non-findings

| claim checked | command | value |
|---|---|---|
| no merge bypassed a *missing* required context | `merge_census.py` | `merges_missing_a_required_context=0` over 164 window merges, judged against the set in force at each merge |
| every merge has a disposition row | `merge_census.py`; `policy_lint --record --since v6.4.1` | `disposition_rows=164/164`; the repository's own enumerator reports 0 without one |
| no workflow checks out untrusted code | `untrusted_text.py` | `dangerous_triggers=0` — no `pull_request_target`, no `workflow_run` |
| no free-text value reaches a shell line | `untrusted_text.py` | `shell_interpolations_freetext=0`; the 3 pattern matches are a `type: boolean` input and two 40-hex SHAs |
| the autofix jobs cannot be driven from a fork | `.github/workflows/tests.yml:1053-1060,1157+` | both guard on `head.repo.full_name == github.repository` and on `github.event_name == 'pull_request'` |
| every wired hook passes its own self-test | `policy_lint --hooks` | 3 wired, 5 / 16 / 19 assertions pass, 0 fail |
| every check class the mutation lane drives turns the acceptance red when emptied | `policy_lint_mutants.mjs` | 12 functions, all 12 red |
| the corpus lints clean | `policy_lint.mjs` | 0 errors across 38 policy files; 73 fixture errors hold 110 pins across 12 classes |
| the record enumerator's set matches the API in CI | `policy_lint --record` with and without `GITHUB_TOKEN` | with a token `RECORD_ENUM: api`, 30 merges, set identical to the API's. **Without one it falls back to the free-text subject and finds 26** — it misses #884, #888, #890, #898, whose merge subjects carry no `(#N)` suffix. It announces the mode on its own first line and CI always supplies the token, so this is a local-run trap rather than a defect |
| the two loop enumerators agree | `--record` vs `--stats`, both `--since v6.4.1` at the same head | 30 vs 31 merged pull requests. Not chased; recorded so a later seat does not read either as the window's size |
| CodeQL covers the languages present | `code-scanning/default-setup` | configured, `extended` suite, actions + javascript(-typescript) + python + typescript |
| the release workflow's tag input cannot inject | `release.yml:43-70` | passed through `env:`, then `[[ =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]`, which anchors the whole string including newlines |

---

## 8. What I could not finish

- **ISO/IEC 42001 clause 10's text could not be fetched.** `iso.org/standard/42001` and the OBP viewer both returned HTTP 403. That row is scored against the clause as commonly published rather than against its own wording, and is the one scorecard row whose bar is remembered rather than fetched.
- **The OpenSSF Scorecard binary was not run.** No docker and no go toolchain on this box. Each check is evaluated by hand against the fetched criterion text and the same API inputs; a judge with the binary should re-run it and compare the reason strings, not the scores.
- **The two `critical` findings' strongest perturbations were not run**, by the brief's own limits: adding a `pull_request` rule to the live ruleset, and posting an injected comment on a live pull request. Both findings rest on read-only evidence instead — the ruleset's five versions and the 592-merge census for D11-01, the static obey/guard counts and the repository's openness for D11-02 — and both carry a perturbation that WAS executed (the two-armed ruleset read; the scratch-copy guard sentence, which moved `seat_guard_sites` 0 → 1).
- **`Fix review:` verdicts are a 1-in-4 sample, not a census.** One API call per pull request and the figure is a proportion. Comment bodies also stay editable and a deletion leaves no trace, so that row is weaker than the check-run rows and says so.
- **Round-3 verdicts were not read**, per the brief; `docs/audit-2026-09.md` and `docs/backlog.md` were never opened. Where this report's findings overlap something the tree already records — `docs/HANDOVER.md:152-153` already names the `--red` gap — that is noted in the finding rather than claimed as new.
