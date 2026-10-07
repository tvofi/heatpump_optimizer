# D11 — verifier seat 3 of 3

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`, working tree a standalone
copy at that SHA. Box: 8-core Apple M1, node v20.10.0, python3 3.11.5, gh 2.98.0.
`load1` at the start of the harness re-runs was **5.27–7.29**; at the close,
**8.46**. `thread_factor` is **not applicable to any figure in this report**:
every number below is a count, a set, a fraction or a process exit status, which
`COMMON.md` classes contention-immune. No wall, CPU or RSS number is claimed.

Instruments I wrote are under `tools/audit/round3/D11/verify-3/`:
`title_gate.py`, `regime.py`, `required_contexts.py`, `skipped_required.py`,
`arms.sh`. Each runs from the single command in its own header.

**GitHub exposure**, read-only, every call's return code checked and printed —
no figure here rests on a call that failed: `rulesets/22628467` (one live read),
`repos/tvofi/heatpump_optimizer`, `commits/{sha}/check-runs` (16), `commits/{sha}/status`,
`commits/{sha}/pulls` (6), `pulls/{n}` (3), plus whatever the finder's
`conformance.py` and `dora.py` issue, both of which printed `api_failures=0`.
Nothing was created, edited, closed, commented on, merged, pushed or dispatched.

## 0. Every harness reproduced, to the digit

| harness | agreement |
|---|---|
| `approval_gate.py` | exact: `arm_policy_title_exit=1`, `arm_docs_title_exit=0`, `policy_touching_commits=82`, `approval_not_required=64` (0.7805), `rule_text_commits=50`, `rule_text_approval_not_required=32` (0.6400) |
| `mechanisms.py` | exact: `mechanism_rows=79`, `required_contexts=18`, `contexts_no_producing_job=4`, `contexts_skipped_by_construction_on_pr=1`, `ruleset_has_pull_request_rule=0`, `ruleset_required_approvals=0`, `ruleset_bypass_actors=1`, `policy_lint_classes=14` |
| `standards.py` | exact, all 26 RESULT lines |
| `agency.py` | exact: `prompts_reading_github_text=6`, `read_and_write_prompts=5`, `boundary_files=1`, `api_failures=0` |
| `conformance.py` | exact: `A=0.5385`, `B=0.0000`, `C=0.0000`, `D=0.5128`, `E=0.8718`, `F=0.9487`, `G=1.0000`, `api_failures=0`, `subject_only=[]`, `api_only=[]` |
| `dora.py` | exact: `0.1721` change failure rate, `red_heads_only_record=11`, `red_heads_resolved=37 of 37`, `api_failures=0` |

All three `--perturb` arms move as their headers claim, so **no detector under
review here is dead code**: `mechanisms --perturb` arm B injects a `pull_request`
rule and `ruleset_has_pull_request_rule` 0→1 with `ruleset_required_approvals`
0→1, arm C sets `record`'s `if:` to `always()` and
`contexts_skipped_by_construction_on_pr` 1→0; `standards --perturb` 0→1→0 on a
written-then-removed `SECURITY.md`; `agency --perturb` `boundary_files` 1→2.

## 1. Derive the count, do not carry one

Two numbers, two globs, two commands that each print the number alone:

    # the policy corpus, as POLICY_GLOBS (.claude/workflows/policy_lint.mjs:228,
    # ten regexes) matches the tracked tree at the baseline            -> 36
    node .claude/workflows/policy_lint.mjs 2>/dev/null \
      | sed -n 's/^TOTAL: .* across \([0-9]*\) policy file(s)$/\1/p'

    # the cap keys policy_budgets.json carries                          -> 37
    python3 -c "import json;print(len(json.load(open('.claude/workflows/policy_budgets.json'))['files']))"

`36 → 37` is those two, not a growth figure. The 37th key is
`.claude/workflows/fixtures/policy-rot/budgets.md`, a fixture matched by no
`POLICY_GLOBS` pattern and capped at 1 line on purpose (`_acceptance` in that
file: it is how the budgets check is shown refusing). `verify-3/title_gate.py`
re-derives the 36 by parsing the ten regex literals out of the linter's source
rather than transcribing them, and the pairing holds at every revision the
mechanism has existed: `28/29` at `2b5e416` (policy_lint lands, 8 globs),
`29/30` at `118fcf2` (the approval gate lands, 9 globs), `36/37` at the
baseline (10 globs).

**One carried count found.** `agency.py:65` enumerates the corpus from a
hand-written `CORPUS` array, not from `POLICY_GLOBS`, and that array omits
`tools/audit/harnesses/README.md` — the file the archive pass added to the globs
and whose comment in `policy_lint.mjs` says exactly why. So `corpus_files_scanned=35`
should read **36**. The omitted file carries 0 boundary matches, so
`boundary_files` stays 1 and D11-05's claim is untouched; the denominator alone
is wrong. My own count over the derived corpus, with a wider boundary regex:
`v3_corpus_files=36`, `v3_boundary_files=1 ['tools/audit/briefs/D11.md']`.

## 2. My own measurement: D11-03, whole history, my own metric

**The finder's metric:** the fraction of first-parent commits on `main` in a
14-day window that changed a `POLICY_GLOBS` file while carrying a subject that
does not start with `policy:`.

**Mine (`verify-3/title_gate.py`, `verify-3/regime.py`):** over **all** 571
first-parent commits reachable from the baseline — no window — the number whose
subject matches `/^policy:/` (the gate's own key, the only thing that switches
the requirement on), set against the number that changed a path matched by a
`POLICY_GLOBS` regex extracted from the linter's source; then the same fraction
restricted **per regime**, because a commit merged before the mechanism existed
cannot be evidence that the mechanism was evaded.

    RESULT policy_glob_literals=10          RESULT policy_corpus_files=36
    RESULT first_parent_commits_all_history=571
    RESULT subjects_matching_isPolicy_all_history=23
    RESULT policy_touching_commits_all_history=90   approval_off=72  (0.8000)
    RESULT rule_text_commits_all_history=50         approval_off=32  (0.6400)

The gate has fired 23 times in this repository's history, so it is a live
mechanism and not dead code. And the rule-text subset is **50/32 over all
history**, identical to the finder's 14-day figure — that subset is entirely
inside the window, so on the stricter population the window is not a slice at
all and the grid attack has nothing to bite on.

### The attack that landed: the denominator predates the mechanism

`POLICY_H2 = ['Approval']` and `isPolicy` entered `policy_lint.mjs` at
`118fcf2`, **2026-09-08T06:26:23+02:00** (`git log -S POLICY_H2`). The finder's
window opens 2026-08-27. `main-protect` went live 2026-09-09T11:38+02:00, which
is when `pr-contract` first became a *required* context.

| regime | policy-touching | off | rule-text | off |
|---|---|---|---|---|
| T1 all history | 90 | 72 (0.8000) | 50 | 32 (0.6400) |
| T2 finder's 14-day window | 82 | 64 (0.7805) | 50 | 32 (0.6400) |
| T3 after the gate landed | 24 | 16 (0.6667) | 14 | 6 (0.4286) |
| **T4 after the ruleset went live** | **11** | **6 (0.5455)** | **6** | **1 (0.1667)** |

The phenomenon survives every regime — it is never zero — but the headline
`32 of 50` becomes **6 of 14** once the mechanism exists and **1 of 6** once it
binds. The per-ISO-week cells are `W34 5/5`, `W35 6/6`, `W36 34/34`, `W37 27/45`,
and dropping the most favourable cell gives 1.0000; that leave-one-out is
uninformative here precisely because W34–W36 predate `118fcf2`. The regime split
is the correct decomposition and it moves the rule-text number by a factor of
about four.

The concrete instances, since a fraction is not an instance. In T4, one:
`0b66857` / PR #675, which edited **`CLAUDE.md`** under the title
`docs: the handover was 24 merges stale and could not take a line; the owner
raised its cap`. In T3, five more, editing `tools/audit/briefs/fixer.md`,
`fix-review.md`, `orchestrator.md`, `judge.md`, `D1.md`, `D7.md`, `D8.md`,
`COMMON.md`, `.claude/rules/brief-citations.md` and
`.claude/workflows/web-fragments.md` under `fix:`, `gate:`, `briefs:` and
`archive:` titles.

**The subject-as-title proxy holds.** Subject minus the `(#N)` suffix equals the
pull request's own title for 3 of 3 sampled (#675, #672, #641), read from the
API at rc=0. #677's trap does not bite.

**The key is wrong in both directions.** 5 of the 23 `policy:`-titled commits
touched no `POLICY_GLOBS` file at all (4 of them after the gate landed): the
gate also demands an `## Approval` section from changes that are not policy.

## 3. The null control for D11-03 — the arm that separates a hole from dead code

This is what the finding needed and did not have: the finder's arms differ only
in a string, with no policy diff anywhere near them. `verify-3/arms.sh` clones
the tree into a scratch directory, applies **one real loosening edit** —
deleting `**raise the budget with the repository owner's explicit confirmation,
obtained before the branch is pushed**` from `CLAUDE.md`, the clause that makes a
ratchet raise the owner's decision — and then runs the actual `pr-contract`
command line from `.github/workflows/governance.yml:176` twice over that tree.

    RESULT arm_miss_exit=0   (title 'fix: ...',    policy diff present)
    RESULT arm_fire_exit=1   (title 'policy: ...', same diff, same body)
    RESULT policy_docs_steps_refusing_the_mutation=0 of 6 steps

Both arms are present, so this is a hole and not dead code. And nothing else
catches it: all six `policy-docs` steps — `rules_sync --check`, the corpus lint
(`TOTAL: 0 error(s) across 36 policy file(s)`), `policy_lint_mutants.mjs`,
`fragments_sync.mjs` and its self-test, `--hooks` — exit 0 on the mutated tree.
`git grep Approval` over `.claude`, `tools` and `.github` returns exactly two
hits, one of which is prose in `orchestrator.md`; the enforcement lives in one
place, `policy_lint.mjs:3089/3135`, and there is no `CODEOWNERS` file in the tree.

The ratchet does not catch it either, and cannot: `--budgets` reports `CLAUDE.md`
at **198 lines / ~3214 tokens** clean and **197 / ~3191** mutated. The caps are
one-sided by design (`policy_budgets.json:_comment`), so deleting a policy
sentence *buys* headroom in the cap that has 14 tokens of it left.

**The single-line mutation the check misses, and its file:**
`CLAUDE.md` lines 29–30, the `**raise the budget with the repository owner's
explicit confirmation, obtained before the branch is pushed**` clause. The line
that misses it is `.claude/workflows/policy_lint.mjs:3135`,
`const isPolicy = /^policy:/.test(title.trim())`.

**Perturbation.** Rewriting that one line to
`... || execFileSync('git',['diff','--name-only','HEAD'],…).some(f => POLICY_GLOBS.some(re => re.test(f)))`
moves `arm_miss_exit` **0 → 1**. Over-fire control, which this repository's
history says to run: the same perturbed linter against a diff touching only
`README.md` and `policy_lint.mjs` (neither in `POLICY_GLOBS`) stays at **exit 0**.
So the proposed fix fires on what it should and not on what it should not.

**What the gate protects when it does fire.** A `policy:`-titled body whose
`## Approval` section reads `the owner said yes` exits **0**. The content is
compared with nothing — `checkPrBody` tests presence, non-emptiness and
bare-`n/a` only. The assurance the title switches off is a sentence the author
types about themselves.

## 4. My own measurement: D11-02, the whole partition

`verify-3/required_contexts.py` derives, for each of the 18 required contexts,
the workflow job that produces it and that job's `if:`:

    RESULT required_contexts=18
    RESULT contexts_runnable_on_pull_request=13
    RESULT contexts_excluded_from_pull_request_by_own_if=1   (record)
    RESULT contexts_with_no_workflow_job=4   (CodeQL + 3 Analyze)

which confirms the finder's `1`. Then `verify-3/skipped_required.py` asks what
actually concludes `skipped` at a head, over the 12 most recent first-parent
commits (`api_failures=0`):

    RESULT required_contexts_skipped_per_head_min=2   max=5
    RESULT heads_with_at_least_one_skipped_required=12 of 12
    RESULT skipped_required_by_context={'closure-scope': 12, 'pr-contract': 12,
                                        'briefs': 2, 'browser': 2, 'typing': 2}

**`skipped`-satisfies-required is load-bearing for the entire gate, not a quirk
of `record`.** `closures` — also a required context — is skipped on a pull
request whenever `closure-scope` outputs `case == 'skip'`
(`.github/workflows/tests.yml:748`). Every head carries at least two skipped
required contexts. So the remedy "make `skipped` not satisfy" would break scoped
gating outright, and only the finder's own alternatives survive: give `record` a
pull-request arm, or take it out of the required list.

**Where I attacked the finder and failed.** I read `CodeQL` as never reporting,
because at the squash heads on `main` (`ae36eff`: 24 check runs, no `CodeQL`) it
does not. At the **pull-request heads**, which is where a ruleset evaluates
required contexts, it does: `CodeQL=success` at #750's head `450b9c6`, #738's
`bc76774` and #749's `7e5f389`. The finder's non-finding is right and my
objection was measured at the wrong commit; recorded because a verifier's failed
attack is evidence too.

## 5. Where I attacked D11-01, and what the probe found

I re-read the ruleset live rather than trusting the captured `ruleset.json`:

    RESULT live_matches_captured=1          RESULT live_required_contexts=18
    RESULT live_ruleset_has_pull_request_rule=0
    RESULT live_bypass_actors=[{'actor_id': 5, 'actor_type': 'RepositoryRole',
                                'bypass_mode': 'always'}]
    RESULT live_updated_at=2026-09-09T11:38:01.674+02:00   (gh rc=0)

The capture is faithful and the object has not moved since it was created.

**The direct-push arm, measured over the whole binding regime rather than a
40-commit sample.** Three first-parent commits after the ruleset went live carry
no `(#N)` subject suffix; the API says two of them (`da57a2a`→#666,
`acd3d08`→#656) do have merged pull requests and only their subjects lack the
suffix. Exactly **one**, `18d67a2` (`v6.3.20: stamp …`), returns `pulls=[]`. At
that commit the required context `pr-contract` concluded `skipped` — it cannot
run without a pull-request event — and the commit is on `main` regardless. That
is the brief's `critical` anchor demonstrated on a real commit, not inferred.

The other arm is demonstrated too: `main`'s head at the baseline carries
**1 failure among 24 check runs, and it is `record`**, one of the 18 required
contexts. Read directly, rc=0.

## 6. Votes

**How these votes were arrived at, because the order matters.** Every number
above was executed before I opened either of the other seats' reports, as the
contract requires. I first wrote `medium` for D11-02, `medium` for D11-03 and
`verify/medium` for D11-04. Reading the other reports at the close — which the
contract permits, to state where definitions differ — did two things, and I
record both rather than quietly re-deriving: it pointed me at an endpoint for
D11-04 I had not probed, which I then queried myself (§6.4), and it made me
re-test D11-02 and D11-03 against the brief's ladder, which is categorical
rather than continuous. On that re-test two of my three severity downgrades did
not survive my own reasoning and I withdrew them. The measurement corrections
below are unchanged by that and are the part of this report the judge most needs.

### D11-01 — **verify**, severity **critical**

Executed: `ruleset_has_pull_request_rule=0`, `ruleset_required_approvals=0`,
one `RepositoryRole 5` bypass actor at `bypass_mode: always`,
`C_github_review_object=0.0000` (0 of 39), and exactly **1** commit on `main`
after the ruleset went live with no pull request at all. D11.md's `critical`
anchor is "a merge to `main` can happen with no review or with a red required
check"; the first arm is 0/39 and the second is `18d67a2`, which landed with the
required context `pr-contract` concluding `skipped` because there was no
pull-request event for it to run on.

For the judge, the honest bound on consequence: `docs/decisions/0005` records
that with one identity a review rule would be a lock rather than enforcement,
because GitHub refuses self-approval. So the durable content of this finding is
(a) reviewer ≠ author is not provable from the platform — NIST AI 100-1 GOVERN
2.1 — and (b) the direct-push arm. It is `critical` on this dimension's own
ladder and would not be on `COMMON.md`'s user-impact ladder; D11.md governs here
and the finder used its words rather than inflating.

### D11-02 — **verify**, severity **high**

I derived the `1 of 18` independently from the workflow files, and
`G_record_required_context_skipped=1.0000` reproduced. I set out to weaken this
to `medium` on the ground that the record is *honest* about it — the
`record-status` comment added by the baseline commit itself says "This does not
prevent that merge" and names the root cause (#541 comment 5622000848, home
#678, state (c)). That attack fails, and the reason is a number I had already
taken: **`record_in_contexts=True` in the live ruleset**. Listing a context in
`required_status_checks` *is* the claim that it gates, and it is the operative
artifact rather than prose about it. The obligation is discharged 0 times out of
39 at the point the ruleset says it gates. That is the `high` rung.

Two corrections that do not move the severity but do move the remedy:

1. **`skipped`-satisfies-required is load-bearing for the whole gate.** Two to
   five required contexts conclude `skipped` at every one of 12 recent heads
   (`closure-scope` 12/12, `pr-contract` 12/12, `briefs`/`browser`/`typing`
   2/12), and `closures` — also required — is skipped on a pull request whenever
   `closure-scope` outputs `case == 'skip'` (`.github/workflows/tests.yml:748`).
   So no remedy of the shape "make `skipped` stop satisfying a required context"
   is available; it would break scoped gating outright. Only the finder's own
   two survive: give `record` a pull-request arm, or take it out of the list.
2. The cost figure is window-dependent: `red_heads_by_job record=20` and
   `red_heads_only_record=11` are over `dora.py`'s 215-head effective
   sub-window, not the 484-commit window the harness names first.

Single-line mutation the check fails to notice, and its file: delete this pull
request's row from the Delivery-status table in
`docs/plan-2026-09-open-issues.md`. `policy_lint.mjs --record` refuses it; no
pull-request run ever executes that refusal, because of
`.github/workflows/governance.yml:225`, `if: github.event_name != 'pull_request'`.

### D11-03 — **verify** the claim and the severity, **correct the magnitude**

The mechanism claim is confirmed and strengthened. I reproduced both arms with a
**real policy diff in the tree** — the finder's arms differ only in a string,
with no policy change anywhere near them — showed all six `policy-docs` steps
green on the mutated tree, showed the one-sided cap *rewarding* the deletion
(`CLAUDE.md` 198→197 lines, ~3214→~3191 tokens), and showed the perturbation
moving `arm_miss_exit` 0→1 with an over-fire control that stays at 0. It is a
hole and not dead code, and `.claude/workflows/policy_lint.mjs:3135` is the line.

`docs/decisions/0007` — accepted by the owner, dated — says `pr-contract`
"refuses a body without an `## Approval` section … mechanically, on every pull
request". I executed the arm that shows it does not, with a real policy diff
present. Nothing else in the tree enforces it: `git grep Approval` over
`.claude`, `tools` and `.github` returns two hits, one of them prose, and there
is no `CODEOWNERS` at this baseline. That is the `high` rung verbatim, and I
tried and failed to argue my way below it: my counterweight was that the section
the gate protects is only checked for presence, which I confirmed — a
`policy:`-titled body whose `## Approval` reads `the owner said yes` exits 0 —
but the rung asks whether the record claims an enforcement that does not exist,
not how much the enforcement would have been worth.

**The magnitude is wrong and the judge must see the corrected figure.**
`POLICY_H2`/`isPolicy` landed at `118fcf2`, 2026-09-08T06:26:23+02:00; the
finder's window opens 2026-08-27, so `64 of 82` and `32 of 50` count commits
merged before the requirement existed. Restricted to the regime where the
mechanism existed: **6 of 14** rule-text commits (0.4286). Restricted to the
regime where `pr-contract` is a required context: **1 of 6** (0.1667), and that
one is `0b66857` / PR #675, editing `CLAUDE.md` under a `docs:` title whose own
text reads "the owner raised its cap". The claim stands; the number that reaches
the register should be the regime-restricted one, with the population stated.

### D11-04 — **weaken**, severity **low** (finder: medium)

Half of this finding is refuted by a call I executed:

    gh api repos/tvofi/heatpump_optimizer/private-vulnerability-reporting
      -> {"enabled":true}            rc=0

The finder's parenthetical — "GitHub private vulnerability reporting is also not
enabled — the repository's `security_and_analysis` block lists secret scanning
and Dependabot, not `private_vulnerability_reporting`" — is an inference from a
key's absence in a payload that never carries that key, and it is false. I
reproduced that same inference from `security_and_analysis` myself before
probing the endpoint that answers the question; I record that as my own error of
exactly the class D11.md's "what has fooled people before" names for the
branch-rules endpoint, caught only when another seat's report sent me to the
right arm. `standards.py:184` never queries it, so no RESULT line ever stood
behind the sentence.

What survives, on my own numbers: no `SECURITY.md` in the tracked tree
(`git ls-tree -r --name-only HEAD | grep -ci 'security\.md'` → **0**), GitHub's
own community-profile endpoint answering `security_policy: null` — which is what
Scorecard's `Security-Policy` check reads — and `repos/tvofi/.github` → 404, so
the organisation fallback route is closed. `sc_security_policy=0` and Scorecard
0/10 stand. The detector has a live arm (`--perturb` 0→1→0).

What does not survive is the consequence sentence that carried the `medium`: "a
reporter today has no non-public channel". With private reporting enabled,
GitHub renders a "Report a vulnerability" control on the Security tab, which is
also a fair reading of the Best Practices wording the finding quotes ("publish
the process … on the project site"). I would call `bp_vulnerability_report_process`
contested rather than 0. One missing file and one Scorecard check at 0/10, with
a working private channel, is hygiene — the brief's `low`.

No single-line mutation applies: this is an absence, not a check that misses
something, and no check in the tree looks for a `SECURITY.md` (it matches none
of the ten `POLICY_GLOBS` patterns, so `named-docs` never sees it).

### D11-05 — **verify**, severity **medium**, denominator corrected

`read_and_write_prompts=5` and `boundary_files=1` reproduced, and I confirmed
the grant by hand: `.claude/workflows/web-triage.js:11-14` lists
`issue_read (get / get_comments)` in the same block as `merge_pull_request
(squash)`, `create_pull_request`, `update_pull_request` and `issue_write`. The
repository is public with issues open, both read live at rc=0. The perturbation
arm moves `boundary_files` 1→2.

Correction: the denominator is **36**, not 35 — `agency.py:65` enumerates from a
transcribed `CORPUS` array that omits `tools/audit/harnesses/README.md`, which
`POLICY_GLOBS` matches. That file has 0 boundary matches, so the claim reads
**1 of 36** and is otherwise unchanged.

Severity earned: D11.md's `critical` rung includes "a job executes text a seat
did not write", and no job does — `sc_dangerous_workflow_sites=0` reproduces, no
`pull_request_target`, no event text in a `run:`, and `governance.yml` passes the
title through `env:` with the reason written down. A *seat* may obey such text,
and with `distinct_issue_authors=1` and `collaborators=1` none has yet arrived.
`medium` is correct and is not inflated.

No single-line mutation applies: nothing in the tree checks for a
data/instruction boundary, so there is no check to miss one. `agency.py` is the
first instrument that measures the absence, and saying so is more useful than
inventing a mutation for a check that does not exist.

## 7. Costed, against the finder's ranked list

Ranked change #5 (one boundary sentence in
`.claude/rules/writing-for-agents.md`) is correctly costed: `--budgets` on the
clean tree reads `always-loaded ~3214, cap 3228`, so **14 tokens** of headroom —
the sentence must be paid for by a deletion. Ranked change #2 is the one my own
perturbation executed end to end, in both directions, and it is the cheapest
real improvement on this panel. Ranked change #3's second half — "drop `record`
from the required contexts and require `record-status` instead" — is refused by
§4: `record-status` is red on heads its own author did not cause, and the
workflow says so; only the first half (a pull-request arm over
`merge-base..HEAD`) survives.

## 8. Where my metric definitions differ from the other two seats

Read only after everything above was executed.

- **Population for D11-03.** I use `POLICY_GLOBS` as the ten regexes parsed out
  of `policy_lint.mjs` at the baseline (36 files). Seat 1 uses
  `.github/CODEOWNERS`' path list (6 paths), which does not exist at my
  baseline — it lands in #756, after it. The two populations are not comparable
  and the judge should not read one as a correction of the other.
- **Regime versus window.** Neither other seat splits the population at
  `118fcf2`, where the mechanism was introduced. That split is this report's
  unique contribution and it is what moves `32 of 50` to `1 of 6`. Seat 1's
  complementary metric — how many gate-off commits carried an `## Approval`
  section *voluntarily* — attacks the same overstatement from the other side
  and reaches the same qualitative place.
- **Pin.** My numbers are all at `ae36eff`. Seat 1 reports at a later pin where
  `main` has moved (CODEOWNERS, decision 0008), so its line numbers for
  `policy_lint.mjs` (`3223`) and `governance.yml` (`261`) differ from mine
  (`3135`, `225`). Seat 1 is right that a line-number citation to these files
  goes stale within a day; the predicate text is the stable citation.
- **D11-02's cost figure.** Seat 1 reports `red_heads_only_record=25` over a
  134-head population; I reproduced the finder's `11` over `dora.py`'s 215-head
  sub-window. Different windows, not different measurements.
