# D11 — verifier 2 of 3, stance refute-first

Line of attack assigned: **conformance and measurement integrity** — the
fractions, and whether they mean what they say.

## 0. Where every number below was taken

| thing measured | pinned to |
|---|---|
| anything derived from the tree or git history | worktree `HEAD` = `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1` (the finder's baseline), verified with `git rev-parse HEAD` |
| anything derived from GitHub state (ruleset, reviews, check runs, repository settings) | **live reads on 2026-09-11 between 06:23 and 06:45 CEST**. GitHub state is not a SHA and cannot be pinned to one; it is stated with its clock instead |
| `origin/main` at the time of these reads | **`52b970b`**, **22** first-parent commits ahead of the baseline |

The dispatch said `origin/main` was `dc03619`. That commit exists and is **10**
first-parent commits ahead of the baseline and **12** behind `52b970b`, so
`origin/main` moved again between the dispatch and this seat. Every figure below
is taken at the baseline or stated as a live read; none is taken at `dc03619`.

Box: 8-core Apple M1, `python3` 3.11.5, `node` v20.10.0, `gh` 2.98.0.
`load1` at each run: 17.30, 10.58, 9.55, 9.13, 8.83, 8.39, 7.51, 6.26, 5.76;
`thread_factor` = 1 (`OMP/OPENBLAS/MKL/NUMEXPR/VECLIB_NUM_THREADS=1`, set by the
harnesses and inherited by mine). **Contention reaches nothing here**: every
figure in this report is a count, a set or a fraction of counts. No wall, CPU or
RSS number is claimed, so the `load1` column is recorded for the contract's sake
and is not a caveat on any result.

`gh api rate_limit` read `core: 0 used of 5000` throughout, which the dispatch
correctly says proves nothing. Every harness I wrote prints its own failure
count beside every figure and refuses rather than reporting a fraction it could
not resolve. **Total API failures across this seat's work: 0**, from
`0` in `v2_review_census.py`, `0` in `v2_direct_push.py`, `0` in
`v2_record_required.py` (430 paginated calls), `0` in `v2_pr_heads.py`,
`0` in `v2_approval_census.py`. Where a figure depends on a set, I compared the
set and not the total.

Nothing was created, edited, closed, commented on, merged, pushed, dispatched or
re-run on GitHub. The finder's ten artefacts are byte-identical to how I found
them (`conformance_raw.json` `sha256:5e0b12b8a2b4…`, moved aside and restored
from a backup taken first, verified equal).

---

## 1. Re-running the finder's six harnesses exactly as their headers say

| harness | every `RESULT` line | note |
|---|---|---|
| `conformance.py` | **reproduced** | see §1a — the re-run replays a cache; I forced a live re-fetch as well |
| `approval_gate.py` | **reproduced** | 10/10 globs, arms 1/0, 82/64/0.7805, 50/32/0.6400 |
| `standards.py` | **reproduced** | including `sc_security_policy=0`, `sc_pinned_action_uses=2 of 50`, `corpus_lines_added_per_deleted=3.086` |
| `dora.py` | **reproduced** | 66 releases, 4.71/day, p50 3.00 h, 0.1721, 37 red, `{"record":20,…}`, `red_heads_only_record=11` |
| `mechanisms.py` | **reproduced** | 79 rows, 18 contexts, `ruleset_has_pull_request_rule=0`, `current_user_can_bypass='always'` |
| `mechanisms.py --perturb` | **reproduced, arms move as stated** | B: rule types 3→4, pull_request rule 0→1, approvals 0→1. C: `contexts_skipped_by_construction_on_pr` 1→0 |
| `agency.py` | **reproduced** | 6 reading, 5 read+write, 35 corpus files, `boundary_files=1`, public, 1 issue author, 1 collaborator |

Captured under `verify-2/rerun-*.txt`.

### 1a. The one method problem in the re-runs: `conformance.py` is not reproducible at the baseline

Two of its inputs are **live**, not pinned:

* `record_undispositioned()` shells out to
  `node .claude/workflows/policy_lint.mjs --record --since v6.3.20`, which reads
  the working tree **and live GitHub**. The finder captured
  `record_undispositioned=[749, 751, 753, 755]` (4 pull requests). My run of the
  same command at the same baseline printed **22**:
  `[723, 736, 749, 751, 753, 754, 755, 756, 757, 758, 759, 760, 761, 763, 764,
  765, 766, 767, 769, 770, 771, 772]`.
* `F_disposition_row` is computed from that set, so `F` is a function of when you
  run the harness, not of the baseline.

`F` nevertheless reproduced at `0.9487 (37/39)` — because the intersection of the
drifted set with the 39-pull-request sample is unchanged (`{749, 751}` both
times; `723` and `736` are outside the sample). **That is luck, not design.** I
record it as a reproducibility defect in the instrument, not as a wrong number:
the figure the finder reports is correct, and would have moved silently had a
sampled pull request lost its row overnight. Everything else in
`conformance.py` is pinned to `ae36eff`.

The header discloses that results are cached. Re-running it therefore replays
`conformance_raw.json` rather than measuring GitHub, so I moved the cache aside
and forced a full live re-fetch. Every fraction reproduced, and the two caches
agree **as sets**: identical 40 commit keys, identical 39 check-head keys,
identical 39 pull-request numbers, and 0 pull requests whose
(author, review count, comment count, head SHA, merged) tuple differs. The
finder's cache is a genuine capture, not a transcription.

---

## 2. D11-01 — the load-bearing "0 of 39"

### 2a. What reproduces, and by a second route

`v2_review_census.py` (mine) re-derives the sample through **different
endpoints**: REST `/commits/{sha}/pulls` where the finder used GraphQL
`associatedPullRequests`, and REST `/pulls/{n}/reviews` where the finder used the
GraphQL `reviews` connection.

```
RESULT R4_pr_numbers_from_rest=39 numbers
RESULT R4_commits_with_no_merged_pr=1 ['18d67a2']
RESULT R4_prs_with_reviews_rest=0 of 39 resolved
RESULT R4_set_equal_to_finder=True  rest_only=[] gql_only=[]
RESULT total_api_failures=0
```

So `C_github_review_object = 0/39` is confirmed on a second endpoint, the sample
is the same **set** (not merely the same total), and `18d67a2` is the same single
commit with no merged pull request. The ruleset facts reproduce exactly and are
read from the bypass-aware object, not from `rules/branches/main`:
`rules = [deletion, non_fast_forward, required_status_checks]`, no
`pull_request` rule, `bypass_actors = [{RepositoryRole 5, always}]`,
`created_at 2026-09-09T09:37:08Z`, `updated_at 2026-09-09T09:38:01Z`,
`enforcement active` (live read, 2026-09-11 06:24 CEST).

### 2b. Attack: is the zero a governance fact or an arithmetic consequence?

The dispatch's hypothesis was that a single-identity repository **cannot**
produce a review object, so the zero would say nothing. I measured it over the
**full census of every merged pull request the repository has ever had**, not a
40-merge window:

```
RESULT merged_pull_requests_ever=509 (GraphQL totalCount=509)
RESULT R1_review_object_any_state=0.0118 (6/509)   review_states={'COMMENTED': 7}
RESULT R2_approving_review_by_other=0.0000 (0/509)
RESULT R3_pr_author_accounts={'tvofi': 506, 'claude': 3}
RESULT R3_collaborators=[{"login":"tvofi","push":true,"admin":true}]
```

The six that carry one:

| pull request | review author | state |
|---|---|---|
| #230, #522, #600 | `github-advanced-security` | COMMENTED |
| #419 (×2), #424, #501 | `tvofi` (the pull request's own author) | COMMENTED |

**The hypothesis is half right, and the half it is wrong about matters.**

* A review object **is** reachable here and has happened six times, four of them
  written by the author on his own pull request. GitHub refuses `APPROVE` and
  `REQUEST_CHANGES` from the author but accepts `COMMENT`, and any inline code
  comment creates one implicitly. So `0/39` is a property of the **recent
  40-merge window**, not a law. The repo-wide rate is 1.18 %.
* An **approving** review by another account — the object
  `required_approving_review_count >= 1` actually requires — is `0/509` and is
  **unreachable on 506 of the 509**, because the sole account with push access is
  the author. (The other three, #616–#618, were authored by the `claude` **Bot**
  and merged by `tvofi`, so an approval was possible there and did not happen.)

This is a real defect in the metric's wording. `conformance.py`'s own docstring
calls C "at least one GitHub REVIEW (**the object a ruleset can require**)". Those
are two different objects, and at repository scale they differ: 6/509 against
0/509. Inside the 39-merge sample they happen to coincide at zero. The finder's
prose is more careful than its metric — it says "Reviewer ≠ author is therefore
not provable from GitHub's records", which is the correct reading — but the
headline number is doing work the metric does not support.

### 2c. Attack: the `critical` anchor's second arm

The brief's `critical` anchor is *"a merge to `main` can happen with no review or
with a red required check"*. I tried to find the second arm in the record and
could not.

`v2_pr_heads.py` (mine) reads each merged head's own check-runs listing:

```
RESULT E2_pr_contract_first_green_filter_all=0.8718    (34/39)
RESULT E2_pr_contract_first_green_filter_latest=0.8718 (34/39)
RESULT prs_a_latest_only_view_would_call_clean=[]
```

`E = 34/39` reproduces. But opening the five that fail it (#710, #711, #727,
#738, #743) shows every one of them went **red then green at the same head
before the merge** — e.g. #711: `failure 08:45:44Z`, `success 08:45:57Z`,
`success 08:49:08Z`, merged `09:03:46Z`. Required contexts take the latest
conclusion, so at merge time `pr-contract` was green on all 39. **No merge in the
sample landed with a red required check.** `E` measures churn, not a breach.

(Aside on the dispatch's trap: `filter=latest` gives the *same* answer as
`filter=all` here — the repeated `pr-contract` runs live in different check
suites, so the endpoint's default does not collapse them. The claim "a summary
would have shown 39/39" is about `gh pr checks`-style summaries, not about this
endpoint's default filter.)

The one landing that **was** unchecked is the direct push. `v2_direct_push.py`
widens the window from 40 commits to *every first-parent commit since the ruleset
became active*:

```
RESULT [baseline]        first_parent_since_ruleset=60 commits, api_failures=0
RESULT [baseline]        commits_with_no_merged_pr=1   (18d67a2, 2026-09-10T08:45:09Z)
RESULT [origin/main-live] head=52b970b first_parent_since_ruleset=82 commits
RESULT [origin/main-live] commits_with_no_merged_pr=1   (the same one)
```

`18d67a2` is authored and committed by `tvofi` 23 h 07 m after the ruleset went
active, and at that commit **17 of the 18 required contexts produced a run only
after it had landed** (`pr-contract` and `closure-scope` `skipped`, the rest
`success`) and `CodeQL` produced none at all. So the required checks did not bind
it. That is one commit in 82, and it is the `v*` release stamp that `CLAUDE.md`
itself assigns to `tools/release/stamp.py` after the merge.

Worth recording for the panel: my wider window also shows the finder's
set-comparison instrument earning its keep. At N=60 the subject-suffix heuristic
and the API **disagree** (`api_only=[656, 666]`): `acd3d08` and `da57a2a` carry
no `(#N)` suffix and look like direct pushes, but the API resolves them to merged
pull requests #656 and #666 whose squash subjects were written without the
suffix. A subject-only census would have reported 3 direct pushes instead of 1.
The finder used the API and compared sets; that was the right call, and its
`subject_only=[] api_only=[]` at N=40 is a property of N=40, not of the method.

### 2d. Verdict on D11-01

The mechanism verifies completely and I dispute none of it. What I dispute is
the severity, on two grounds, both measured:

1. The headline consequence figure (`0 of 39`) conflates "no review object" with
   "no approving review", and the first of those is a 40-merge-window property
   (6/509 repo-wide), while the second is unreachable by construction on 99.4 %
   of the corpus. Neither reading gives the number the force of "no review
   happens"; the honest reading is "review is unprovable from the platform",
   which the null control already shows (21/39 carry a verdict comment).
2. The `critical` anchor's second arm is a **capability**, not an event: zero of
   39 merges landed with a red required check, and the single unchecked landing
   in 82 post-ruleset commits is the documented post-merge version stamp.

**Vote: weaken, to `high`.** An always-bypass admin actor, no review rule and a
demonstrated unchecked path to `main` is a genuine and serious governance hole.
It is not carried by the number the report leads with.

---

## 3. D11-02 — "20 of 37", "11 with nothing else"

### 3a. Mechanism

`.github/workflows/governance.yml:224` — `record:` / `if: github.event_name !=
'pull_request'`. The ruleset's 18 required contexts include `record` (confirmed
in the captured `ruleset.json` and in a live read: same 18, same order).

### 3b. My own measurement, at check-**run** level

The finder's definition is workflow-**run** level, taken from the Actions run
listing, which it correctly reports as capped at 1000 runs. Mine reads each
head's own `/commits/{sha}/check-runs` listing, fetched twice per head
(`filter=all` and `filter=latest`, 430 paginated calls, 0 failures), with red
defined as "at least one check run on that commit concluded `failure`" and
attribution by the **set** of failing names.

Over the finder's stated sub-window
(`2026-09-06T00:29:06+02:00 .. 2026-09-10T23:02:51+02:00`, 215 first-parent heads):

| figure | finder | mine |
|---|---|---|
| heads with a run | 215 | 215 |
| red heads | 37 | **38** |
| change failure rate | 0.1721 | **0.1767** |
| heads where `record` failed | **20** | **20** |
| heads where `record` was the only failure | **11** | **11** |
| `nightly-ha (stable)` / `(2025.2.0)` | 5 / 5 | **6 / 6** |
| every other job name | — | identical |

**Both load-bearing numerators reproduce exactly.** The denominator is one
higher: the Actions listing's 1000-run cap dropped one `nightly-ha`-only red
head that the per-commit check-runs listing sees. So the correct fractions are
`20/38 = 0.526` and `11/38 = 0.289`, and the finder's cap disclosure is doing
precisely the job it was written for. `filter=latest` and `filter=all` returned
identical red sets (`red_under_all_not_latest=[]`, `red_under_latest_not_all=[]`)
— on `main` heads the distinction does not bite.

A second window, defined by a governance event rather than by an API cap (all 60
first-parent commits from the ruleset going active to the baseline): 24 red,
`record` failing on 16, `record` alone on 8 — `change_failure_rate = 0.40`. The
finding does not depend on the window choice.

### 3c. The obligation the required context actually discharged

`v2_pr_heads.py`, through REST rather than the finder's GraphQL:

```
RESULT G2_record_skipped_on_pr_head=1.0000 (39/39)
RESULT G3_record_present_at_all=1.0000 (39/39)
RESULT record_conclusions_on_pr_heads={'skipped': 61}
```

Sixty-one `record` check runs across 39 merged heads and **not one** reached any
conclusion other than `skipped`. This is the finding, and it is not marginal.

### 3d. The counterfactual the finding implies

Ranked change #3 offers "drop `record` from the required contexts and require
`record-status` instead". `record-status` carries `if: github.event_name ==
'pull_request'`, so unlike `record` it would genuinely gate. I measured what it
would have gated:

```
RESULT pr_heads_with_a_record_status_run=1 of 39
RESULT record_status_conclusions={'failure': 3}      (head bc76774 = #738)
```

`record-status` exists only from #738 onward, and on the one merged head in the
sample that has it, it concluded `failure` three times. Requiring it would have
refused **#738's own merge** — for a red on `main` that #738's author did not
cause and could not fix from the branch. The workflow's own comment says exactly
this ("requiring it would make one lane's unfixed red refuse every unrelated
merge in the repository") and my number confirms it. The finding is right; the
second half of its remedy is not. The first half (give `record` a pull-request
arm over `merge-base..HEAD`) is untouched by this.

**Vote: verify, `high`.** Numerators exact, denominator one higher and stated,
mechanism unambiguous, obligation measurably discharged zero times out of 39.

---

## 4. D11-03 — "32 of 50"

### 4a. Re-derived without transcribing anything

`v2_approval_census.py` (mine) replaces both of the finder's hand-copied inputs:

* **The globs** are lifted from `.claude/workflows/policy_lint.mjs`'s own source
  text and **evaluated by node**, so the classifying objects are production's
  regexes, not a Python re-spelling. Ten globs, printed in full.
* **The title** is the pull request's real `title` from the GitHub API, not the
  squash subject with ` (#N)` stripped.
* **The verdict** is produced by *executing* production `checkPrBody` 82 times
  (`node .claude/workflows/policy_lint.mjs --pr-body <body with no ## Approval>
  --head … --title <real title>`), not by re-implementing `/^policy:/`.

```
RESULT production_globs_evaluated_by_node=10 globs
RESULT policy_touching_commits=82 commits
RESULT title_api_failures=0 calls
RESULT commits_whose_subject_title_differs_from_pr_title=20
RESULT checkPrBody_exit_codes={0: 64, 1: 18}
RESULT approval_not_required_fraction=0.7805 (64/82)
```

Twenty of the 82 squash subjects are **not** the pull request's title (truncated,
em-dash normalised, or edited after opening) — a real hazard in the finder's
shortcut — and in none of the twenty does the `policy:` classification change.
The shortcut is safe here and is not safe by construction.

### 4b. Set comparison, and the strict subset

`v2_approval_sets.py` builds the finder's classification and mine over the same
484-commit window and compares them commit by commit:

```
RESULT finder_glob_list_equals_production=True
RESULT F_touching=82 F_approval_off=64 (0.7805)
RESULT V_touching=82 V_approval_off=64 (0.7805)
RESULT touching_sets_equal=True     F_only=[] V_only=[]
RESULT approval_off_sets_equal=True F_only=[] V_only=[]
RESULT strict_touching=50 strict_approval_off=32 (0.6400)
```

The strict subset is built here **mechanically** — production's ten globs minus
the four documentation entries (`tools/audit/README.md`,
`tools/audit/harnesses/README.md`, `tests/README.md`, `docs/HANDOVER.md`) —
rather than from a second hand-written list, and it yields exactly **50** and
**32**. The finder's headline is right, by a derivation that shares no
transcription with it.

### 4c. Attack on the harness's own guard — it fires, and it has a hole

Three arms of `approval_gate.py`, each a copy with only `ROOT` re-pointed:

| arm | transcribed globs | guard | census |
|---|---|---|---|
| faithful (control) | 10, unchanged | passes | 82 / 64 / 0.7805 — identical to the original |
| `drop1` (one glob removed) | 9 | **REFUSED: POLICY_GLOBS moved** | not computed |
| `swap1` (`docs/HANDOVER.md` → `docs/NO_SUCH_FILE.md`, count unchanged) | 10 | **passes silently** | **69 / 51 / 0.7391** |

So the refusal is real and not decorative — but it compares **cardinality only**.
A content drift that keeps the count moves the primary census by 13 commits
(–16 %) with the guard green. And the `RULE_RE` subset that produces the headline
`32 of 50` is a **second transcription that the guard does not cover at all**.
Neither hole has bitten: I re-derived both lists from production and both are
exactly right today. Both are worth closing if this harness is ever re-run
against a moved corpus.

**Vote: verify, `high`.** `32/50` and `64/82` reproduce set-for-set through a
derivation that executes the production predicate. `docs/decisions/0007`'s claim
that the section is required "mechanically, on every pull request" is not what
`checkPrBody` does: `const isPolicy = /^policy:/.test(title.trim())`.

---

## 5. D11-04 — half of it is refuted

The file half stands, measured three ways at the baseline and live:

* No `SECURITY.md` anywhere in the tree at `ae36eff` (`git ls-tree -r` for
  `security`, case-insensitive: no hits), so none at the root, in `.github/` or
  in `docs/`.
* `GET /repos/tvofi/heatpump_optimizer/community/profile` returns a `files` block
  with `code_of_conduct`, `contributing`, `issue_template`, `license`,
  `pull_request_template`, `readme` — **and no security entry**.
* The organisation fallback does not exist: `GET /repos/tvofi/.github` → **404**.

So OpenSSF Scorecard's `Security-Policy` would indeed score 0/10, and
`sc_security_policy=0` is correct.

**The second half is false.** The report states: *"GitHub private vulnerability
reporting is also not enabled — the repository's `security_and_analysis` block
lists secret scanning and Dependabot, not `private_vulnerability_reporting`"*.
That is an inference from the absence of a key in a block that **never carries
that key**. The authoritative endpoint says the opposite:

```
$ gh api repos/tvofi/heatpump_optimizer/private-vulnerability-reporting -i
HTTP/2.0 200 OK
{"enabled":true}
```

(live read, 2026-09-11 06:44 CEST). Private vulnerability reporting is **on**.
The finder never called that endpoint — its own §9 Exposure list enumerates
fourteen `gh api` REST paths and `private-vulnerability-reporting` is not among them,
and `grep` over all six harnesses finds the string only in the report's prose.
This is exactly the failure mode the dispatch named: the field is *absent*, not
*false*, and absence was read as a negative.

The consequence for the finding's own framing is direct. "A reporter today has no
non-public channel" is **not true**: the Security tab carries a live *Report a
vulnerability* button, which is the standard non-public channel for a repository
with no security team. And the OpenSSF Best Practices criterion the harness
scores 0 (`vulnerability_report_process`: *"The project MUST publish the process
for reporting vulnerabilities on the project site"*) is arguably satisfied in
substance by that button, though `bp_vulnerability_report_process=0` is defensible
as a file-presence proxy — the harness at least only claims what it executed.

What survives: a public HACS integration that drives a heat pump has a working
private reporting channel that **nothing advertises** — no `SECURITY.md`, no
README pointer, no response-time expectation, and a Scorecard `Security-Policy`
of 0. Exposure context, measured: `visibility=public`, 1 star, 1 watcher, 0
forks, MIT, issues open, community health 57 %.

**Vote: weaken, to `low`.** The remedy shrinks from "there is nowhere to report"
to "add the file that points at the channel that already exists"; the settings
toggle in ranked change #4 is already on.

---

## 6. D11-05 — outside my line, re-run and one control

`agency.py` reproduces every figure (§1). One independent control, since a
detector counting to 1 is the kind that under-fires: I swept the same corpus with
a **wider** net — `not instructions`, `never instructions`, `as data`, `is data`,
`treat … as data`, `untrusted`, `prompt injection`, `injection`, `free text` —
and got **2** files, not 1. The extra one is
`tools/audit/briefs/orchestrator.md`, whose matching sentence is the *opposite*
of a boundary: *"…are not instructions you relay. They are instructions you
follow."* The finder's narrower pattern (`not as instructions`) correctly
excludes it. `boundary_files=1` survives a net built to break it, and the one
file is this audit's own brief, which names OWASP as something to score against
rather than binding a seat.

**Vote: verify, `medium`** — on the counts, which I executed, and explicitly not
on the OWASP framing or the write-authority reasoning, which I did not attack.
The finder's own severity argument (`distinct_issue_authors=1`,
`collaborators=1`: the door is open, nobody has walked through) is the right
reason for `medium` and not higher.

---

## 7. Harnesses I wrote

All under `tools/audit/round3/D11/verify-2/`, each with its metric in its header,
each read-only, each printing its own failure count:

| file | what it measures |
|---|---|
| `v2_review_census.py` | R1/R2/R3/R4 — the review census over all 509 merged pull requests, and the finder's 39 re-derived through REST |
| `v2_direct_push.py` | commits reaching `main` with no merged pull request since the ruleset became active, at two heads |
| `v2_record_required.py` | red heads and their failing-name **sets**, from each head's own check-runs listing, `filter=all` and `filter=latest`, over two windows |
| `v2_pr_heads.py` | `record`'s conclusion and `pr-contract`'s first conclusion on the 39 merged heads, through REST |
| `v2_approval_census.py` | the approval census with production regexes evaluated by node, real pull-request titles, and production `checkPrBody` executed |
| `v2_approval_sets.py` | the finder's classification against mine, compared commit by commit |
| `ag_faithful.py` / `ag_drop1.py` / `ag_swap1.py` | the three-arm perturbation of `approval_gate.py`'s glob guard |

Outputs beside them as `out-v2_*.txt`; the finder's harnesses' re-runs as
`rerun-*.txt`.
