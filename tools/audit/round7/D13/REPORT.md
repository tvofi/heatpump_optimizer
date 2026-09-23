# D13 — process yield and cost (round 7)

Baseline `f9d6f78243fa65f6fa128d2357752a2ae7f60648`, worktree
`/Users/timmalmstrom/audit-r7-D13`. Machine: Apple M1, 8-core, 8 GB, macOS
25.6.0 — the shared audit box, during fan-out. Every number below is a **count**
(call counts, shape counts, exit codes) and therefore final under fan-out
contention; no wall/CPU/RSS number is reported, so none is provisional.

## Method

D13 audits what the process *pays* per merge and how often a pull request passes
first time. The brief's six required outputs are mostly GitHub-sourced (merged
PRs, check runs, reviews). Reading GitHub is out of scope for this seat (`gh` is
forbidden and the API is not reachable), so outputs 1–4 could not be taken; that
is recorded under **Exposure**. What *is* measurable offline is the process's own
readers of that data, and those are production code: the `policy_lint.mjs` window
modes (`--record`, `--stats`, `--sunset`) that the `record` job of
`.github/workflows/governance.yml` runs on every push to `main`. Three instruments
in that path could not compute their own metric; each is proved with a committed
harness, a named production symbol, and a perturbation that moves the number.

Two harnesses, both under `tools/audit/round7/D13/`:

| harness | hooks | perturbation |
|---|---|---|
| `window_api_ledger.mjs` | `policy_lint.mjs:fetchWindow` (driven through the real CLI) | add the reviews fetch; exit non-zero on a failed enumeration |
| `verdict_grammar.mjs` | `policy_lint.mjs:statsHistogram` + `web-fix-wave.js:VERDICT_RE` | drop the case-insensitive flag from the histogram's regex |

`window_api_ledger.mjs` puts a stub `curl` first on `PATH`. `policy_lint.mjs:ghGet`
shells out to `curl` (`execFileSync('curl', ['-sS','-w','\n%{http_code}','-K','-', URL])`),
so every API path the production reader asks its transport for lands in a ledger
the harness reads back. Nothing touches the network. Window: `v6.6.9..origin/main`,
**C = 31** first-parent merge commits, all enumerated as distinct pull requests
(**N = 31**) by the stub. Both perturbation edits are applied in place to the
pinned file and restored byte-for-byte in a `finally`; the harness returns the
tree unchanged (`git status --porcelain .claude/workflows/policy_lint.mjs`
empty after every run, verified).

## Findings

### D13-01 — `fetchWindow` never reads `pulls/<n>/reviews`, so a review-posted verdict is invisible to the yield and coverage metrics

The brief defines a verdict as "an issue comment **or** a pull-request review".
`fetchWindow` fetches two endpoints per pull request — `/pulls/<n>` and
`/issues/<n>/comments` — and never `/pulls/<n>/reviews`. A verdict posted as a
review is therefore not merely unweighted, it is *invisible*: the pull request
reads as one that "carried none", and `statsCoverageLine` reports it as a gap in
the histogram's population.

    node tools/audit/round7/D13/window_api_ledger.mjs
    RESULT api_calls_stats_total=93 count
    RESULT commits_map_requests_stats=31 count
    RESULT pull_body_requests_stats=31 count
    RESULT issue_comments_requests_stats=31 count
    RESULT reviews_endpoint_requests_stats=0 count
    node tools/audit/round7/D13/window_api_ledger.mjs --perturb reviews
    RESULT reviews_endpoint_requests_PERTURBED=31 count   # <-- moves 0 -> 31
    RESULT reviews_endpoint_requests_unperturbed=0 count

The count is keyed on the request the seam makes, not on any attribute of the
data: the only way to move it is to ask for the endpoint. The null control is in
the same ledger — `issue_comments_requests=31` and `pull_body_requests=31` are
non-zero, so the zero on the reviews row is a missing request, not a dead ledger.
Severity **medium**: an instrument that cannot compute its own metric. It would
be `high` if any merged pull request in the window actually carried a verdict as
a review; that prevalence is GitHub-sourced and this seat could not measure it.

Property: *the histogram's verdict population is the set of verdicts its reader
can see, and that reader must see every endpoint a verdict can arrive on.* Seam
rule: the reader's own transport calls — enumerate them from the ledger this
harness produces. Files: `.claude/workflows/policy_lint.mjs` (`fetchWindow`).

### D13-02 — the histogram's verdict grammar diverges from the wave's `VERDICT_RE` on four axes, and the two arms of the same function disagree about the SHA

`cmdStats` prints its histogram under the header `verdict grammar ["blocked","merge"] read from .claude/workflows/web-fix-wave.js`, and `statsHistogram`
builds its matcher as `new RegExp('^Fix review:\\s*(merge|blocked)\\b', 'i')`.
The grammar it claims to have read is `web-fix-wave.js`'s:

    ^Fix review:\s+(?:(merge)\s+([0-9a-f]{40})|(blocked)\s+([0-9a-f]{40})(?:...)|...))$

The two differ on four axes, and every difference is one-directional — the
histogram accepts, the wave refuses:

| shape | wave | histogram |
|---|---|---|
| `Fix review:merge <40hex>` | refuses (`\s+` required) | counts `merge` |
| `Fix review: MERGE <40hex>` | refuses (case-sensitive) | counts `merge` |
| `Fix review: merge` (no SHA) | refuses (40 hex required) | counts `merge` |
| `Fix review: merge <12hex>` | refuses | counts `merge` |
| `Fix review: merge <40hex> please` | refuses (anchored) | counts `merge` |
| `Fix review: BLOCKED <40hex> mutation-vacuous: why` | refuses | counts `mutation-vacuous` |

    node tools/audit/round7/D13/verdict_grammar.mjs
    RESULT shapes_unperturbed_total=12 count
    RESULT shapes_counted_by_histogram_but_refused_by_wave_unperturbed=7 count
    RESULT control_shapes_in_both_grammars_unperturbed=2 count   # a 40-hex merge, a 40-hex blocked+class
    RESULT control_shapes_refused_by_both_unperturbed=3 count     # the documented "Fix review: PASS — merge <sha>" among them
    RESULT hist_accepts_sha_less_merge_unperturbed=1 bool
    RESULT hist_accepts_sha_less_blocked_unperturbed=0 bool
    node tools/audit/round7/D13/verdict_grammar.mjs --perturb
    RESULT shapes_counted_by_histogram_but_refused_by_wave_..._PERTURBED=4 count   # moves 7 -> 4

Both symbols are driven, not re-implemented: `statsHistogram` is imported and
called per shape; the wave's `VERDICT_RE` is built by evaluating the expression
`web-fix-wave.js` itself writes (the read-the-literal-from-the-file technique
`verdictClasses`/`blockClasses` already use for the two halves of this grammar);
the `classes` input is parsed from the production CLI's own header line. The
`--perturb` arm drops the regex's `'i'` flag — a one-line production edit — and
the count falls by exactly the three case-only shapes. The two control shapes are
counted by both grammars in both arms, so the divergence count is not "everything
refuses everything".

The last two RESULT lines are the sharper half: **within one function**, the
`merge` arm counts a SHA-less line while the `blocked` arm sends the analogous
line to `unclassified`. The first-pass-yield numerator and the coverage line's
`N of M` both count comments the wave's own parser would throw on. Severity
**medium**: a wrong published value, but one this seat could not show to have
occurred in a real window (the window is GitHub-sourced; prevalence unmeasured).

Property: *a reader that claims to classify by another module's grammar must
classify exactly that grammar.* Seam rule: every call site that builds a
`Fix review:` matcher outside the wave — enumerate with the production reader's
own header line and the harness's battery. Files: `.claude/workflows/policy_lint.mjs`
(`statsHistogram`), `.claude/workflows/web-fix-wave.js` (`VERDICT_RE`).

### D13-03 — the record job's summary reads the exit code alone, so an unenumerable window is reported as a clean one

The `record` job's refusal step runs `--record`, and the report step that follows
maps the step outcome to the run's headline
(`.github/workflows/governance.yml:599-602`):

    if [ "$REFUSAL_OUTCOME" = "failure" ]; then
      VERDICT="REFUSED -- merged pull request(s) with no disposition"
    else
      VERDICT="clean -- every merged pull request in the window has a disposition"

When `/commits/<sha>/pulls` will not answer, `mergedPRsFromWindow` falls back to
subject mode, the fallback enumerates nothing, and `cmdRecordDispositions`
**exits 0**. Measured with the transport forced to HTTP 500 on that endpoint:

    node tools/audit/round7/D13/window_api_ledger.mjs
    RESULT record_exit_code_api_failure=0 count
    RESULT record_exit_code_healthy_window=1 count
    RESULT record_enumeration_skipped_marker_on_failure=1 bool
    RESULT record_reported_merged_prs_on_failure=0 count
    node tools/audit/round7/D13/window_api_ledger.mjs --perturb exitcode
    RESULT record_exit_code_api_failure_PERTURBED=2 count   # moves 0 -> 2
    RESULT record_exit_code_api_failure_unperturbed=0 count

The window that could not be read is reported **cleaner** (0, which the report
step renders "clean -- every merged pull request in the window has a
disposition") than a window that was read and holds a violation (1, "REFUSED").
The loud `enumSkipLine` marker *is* printed into the step log and captured into
`record.txt`, but the headline reads the exit code and nothing else, so the
sentence a seat opening the run first sees asserts a measured clean window over
a window the same run says is UNCHECKED.

The perturbation is the one-line edit that makes `--record` exit non-zero when
the enumeration failed. Note for the fixer: that edit also reddens the job on a
transient outage, which is the documented reason rc=0 stays
(`requireToken`/`enumSkipLine`'s comments; the step has no `continue-on-error`).
The cheaper route is the report step: key the headline on the UNCHECKED marker
as well as the exit code, so an outage reads UNCHECKED rather than clean.
Severity **medium**. This sits near D11's lane (a refusal that does not fire on
an outage); it is filed here as D13 because the defect is the *outcome the
process reports*, not the firing of the check.

Property: *a window the run could not enumerate must not be reported as clean.*
Seam rule: every consumer of a mode's exit code — enumerate the summary/report
steps in `.github/workflows/`. Files: `.github/workflows/governance.yml`
(the report step), `.claude/workflows/policy_lint.mjs` (`cmdRecordDispositions`,
`enumSkipLine`, `requireToken`).

## Non-findings (checked, held)

1. **The friction-key resolver behaves as the brief describes** (brief output 6).
   A rule id resolves by exact name, then minus `.md`, then longest `-` prefix,
   with an ambiguity guard; `--normalize-friction-keys` is a stdin filter over
   the production `frictionKey`. Driving it over the brief's own perturbation
   cases:

       printf 'ratchet-budgets\nratchet-budgets.md\nREADME.md\n#ratchet-budgets\n' \
         | node .claude/workflows/policy_lint.mjs --normalize-friction-keys
       ratchet-budgets      .claude/rules/ratchet-budgets.md
       ratchet-budgets.md   .claude/rules/ratchet-budgets.md
       README.md            README.md                      # ambiguous -> names no file
       #ratchet-budgets     #ratchet-budgets                # the anchor spelling keeps no path

   `ratchet-budgets` and `ratchet-budgets.md` name the same file, so re-spelling
   one as the other moves no file's count; `README.md` is the ambiguous row. The
   last line is recorded as an observation, not a finding: `frictionKey` strips
   `#`-to-end-of-line, so a bare `#k` reduces to `''`, falls back to the raw
   string, and becomes its own unresolvable row. The brief's table does not claim
   `#k` resolves to a file, and no reviewer template writes that spelling, so no
   defect is asserted. `rc=0`.
2. **The redundant window reads are a cost, not a defect with a perturbation.**
   Each of `--stats` and `--sunset` independently calls `mergedPRsFromWindow`
   and `fetchWindow` over the identical window, and `--record` enumerates it a
   third time. Over `v6.6.9..origin/main` the three-step beat pays
   `RESULT api_calls_record_job_total=217 count` (93 + 93 + 31) where one
   enumeration (31) plus one fetch (62) = 93 would serve — **124 redundant API
   calls per beat, 2.33×**, on the shared token, on every push to `main`. It is
   *not* returned as a finding because this seat could not build the required
   perturbation: the redundancy is across three separate processes, and no
   one-line production edit changes the cross-process total the harness measures
   (a module-scope cache in `mergedPRsFromWindow`/`fetchWindow` would move it
   only if the three modes shared a process, which they do not). Harness gap,
   named. Command: `node tools/audit/round7/D13/window_api_ledger.mjs`.
3. **`cfr_exclusions.json` exists beside `policy_budgets.json`** with a reason
   and a citation per excluded check-run name — brief output 4's "JSON file beside
   `policy_budgets.json` that your first round creates" is already created
   (recorded as D13-03/#1407). Command: `ls .claude/workflows/cfr_exclusions.json`;
   value: present, 2704 bytes.
4. **The 16 recorded required contexts each name a job that exists** in the
   workflow files, so keying DORA by check-run name against
   `.claude/workflows/fixtures/required-contexts.json` names no dead job.
   Command: `grep -c '"' .claude/workflows/fixtures/required-contexts.json` /
   `ls .github/workflows/`; value: 16 contexts, all matched to live jobs.
5. **The `policy_lint_mutants.mjs` lane holds**: `PIN`/`SKIP`/`DRIVEN` verdicts
   do not fail the lane and `ACCEPTED` does, so the "a check that survives its
   own deletion" arm is not vacuous. Command:
   `node .claude/workflows/policy_lint_mutants.mjs --self-test`; value: `rc=0`,
   `MUTANTS ok: every check this clone could drive turns the acceptance red when
   it is emptied` — 11 corpus checks and 10 record checks named, including
   `checkRecord`, `enumSkipLine`, `checkPrBody`, `frictionEntries`, `frictionKey`.
   (The `PIN ... FIXTURE VACUOUS:` lines above it are the *why* text of correct
   `PIN` verdicts — a check whose fixture cannot produce its refusal — not a
   failure.)
6. **The two `--stats`/`--sunset` modes agree on the window they read.** Both
   print `31 merged pull request(s)` and make identical ledgers (93 calls, the
   same three endpoint classes, 0 reviews), so no second divergence hides behind
   the first. Command: `node tools/audit/round7/D13/window_api_ledger.mjs`.

## What I could not finish

- **Brief outputs 1–4** need GitHub. First-pass yield and rounds per merge
  (`/commits/<sha>/pulls`), verdict coverage by class, the three-way block-class
  buckets with `VERDICT_CLASSES`, and DORA's four keys by check-run name
  (`d11lib.py:check_runs`) all require the API. Not taken.
- **Brief output 5 (`governance_cost.py` and its `GOV` set)**: the base
  instrument is not present in the export. `tools/audit/round4/D11/` is not in
  this tree (`find tools/audit -name governance_cost.py -o -name d11lib.py -o
  -name dora_keys.py` returns nothing), so `GOV` could not be re-derived from the
  workflow files at this window as the brief asks. The job set itself is local
  and enumerable; the seconds per merge are check-run data and are not.
- **Prevalence of D13-01 and D13-02 in a real window.** Both findings are
  instrument defects whose *magnitude* depends on how many verdicts were posted
  as reviews (D13-01) and how many `Fix review:` comments fell outside the
  wave's grammar (D13-02). Both need the API. Each finding's severity would rise
  to `high` if a non-zero count were established.

## Exposure

- `tools/audit/finding.schema.json`, `tools/audit/briefs/COMMON.md`,
  `tools/audit/briefs/D13.md`, `tools/audit/README.md` — the contracts; D13's
  brief names the earlier instruments it inherits (`round4/D11/dora_keys.py`,
  `governance_cost.py`, `d11lib.py`), none of which are in this export.
- GitHub's own records would carry earlier findings; this seat did not read
  GitHub, so no exposure from there.
- `.claude/workflows/policy_lint.mjs` carries many inline comments citing
  `D13-nn` ids from earlier rounds (`#1405 D13-01`, `#1406 D13-02`, `#1407
  D13-03`, `#1240 D13-03`). Those were read as context only; no earlier round's
  findings were looked for, and no id below reuses an earlier round's numbering.

---

# D13, second pass — the GitHub-sourced measurements (round 7, appended)

The first pass was barred from GitHub and left **outputs 1–5 untaken**. This pass
takes them, at the same baseline `f9d6f78243fa65f6fa128d2357752a2ae7f60648`,
from the same sources D11 reads: `/commits/<sha>/pulls`, check runs, issue
comments, pull-request reviews, bodies, and the workflow files. Everything below
is a **count or a duration GitHub reported**, so none is provisional under
fan-out and no `load1`/`thread_factor` is quoted. `RESULT api_failures=0` on
every harness; the numbers are the sets the API answered with, not differences
of totals.

**Window.** `v6.6.9..f9d6f782` — the round-6 fix wave's merges.
`RESULT first_parent_commits_both=31`; `/commits/<sha>/pulls` resolved **all 31**
to a pull request (`commits_with_no_pull_request_both=0`,
`distinct_pull_requests_both=31`), so the window contains no stamp and the git
first-parent set and the API's pull-request set are the same set — compared as
sets, per the brief.

| harness | drives | command |
|---|---|---|
| `yield_rounds.py` | `/commits/<sha>/pulls` (the API mode of `policy_lint.mjs:enumerateMerges`), `/issues/<n>/comments`, `/pulls/<n>/reviews` | `PYTHONPATH=tests/hastub python3 tools/audit/round7/D13/yield_rounds.py --perturb` |
| `cfr_by_job.py` | `d11lib.py:check_runs` at the merge commit and the head; `tools/audit/round4/D11/dora_keys.py` as the base | `PYTHONPATH=tests/hastub python3 tools/audit/round7/D13/cfr_by_job.py --perturb` |
| `gov_cost.py` | `tools/audit/round4/D11/governance_cost.py` and its `GOV` set, re-derived from `.github/workflows/` | `PYTHONPATH=tests/hastub python3 tools/audit/round7/D13/gov_cost.py --perturb` |
| `class_vocabulary.mjs` | `policy_lint.mjs:statsHistogram` + `web-fix-wave.js:parseVerdict`/`VERDICT_CLASSES` | `node tools/audit/round7/D13/class_vocabulary.mjs --perturb` |

All four run from `/Users/timmalmstrom/audit-r7-D13` with
`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` and
`node v20.10.0`; `d13lib.py` is their shared plumbing (cached, failure-counted
`gh api`, importing `d11lib.py`'s `check_runs` **verbatim** so a D13 figure and
a D11 figure cannot disagree about the same commit). Both `--perturb` arms edit
the pinned production file in place and restore it byte-for-byte in a `finally`;
`git status --porcelain .claude/workflows/` is empty after every run (verified
for `web-fix-wave.js` and `governance_cost.py`; `RESULT wave_script_restored=true`).

`RESULT load1=2.19..2.56` and `RESULT thread_factor=1.000` are quoted by each
harness's footer because COMMON.md asks for them beside every measurement — not
because anything here has a timing to protect. `thread_factor` is 1.000 by
construction (no BLAS, no second thread): every number is a count or a duration
GitHub reported, both contention-immune under fan-out, so nothing below is
provisional and no quiet-window re-take is owed.

## Required outputs 1–5 — the measurements

**1. First-pass yield and rounds per merge.**

    RESULT window_merges_both=31
    RESULT verdicts_total_both=30   verdicts_from_comments_both=30   verdicts_from_reviews_both=0
    RESULT merges_with_a_verdict_both=25   merges_with_no_verdict_both=6
    RESULT first_pass_yield_both=0.92            # over the 25 that carried a verdict
    RESULT first_pass_yield_over_window_both=0.742   # over all 31 merges
    RESULT first_pass_failures_both=2
    RESULT rounds_mean_over_window_both=0.97   rounds_mean_over_verdict_merges_both=1.2
    RESULT rounds_max_both=3
    RESULT api_failures=0

Every verdict came from `/issues/<n>/comments`. **`verdicts_from_reviews=0`**:
across all 31 pull requests, no review's first line matches
`^Fix review:\s*(merge|blocked)`. The reviews the window does carry are of two
shapes and neither is a verdict — `hpo-approver[bot]`'s *echo* of a verdict
comment (`Approved by \`hpo-approver\` at <sha> on the verdict <url>
(\`Fix review: merge <sha>\`)`) and `tvofi`'s **owner review**
(`Owner review (code-owned: <path>). … Approve.`, `Approved as codeowner (owner
mandate, session-only, 12h). …`). The perturbation arm confirms the endpoint
question is live rather than moot:

    node … yield_rounds.py --arm comments      # fetchWindow's endpoint set
    RESULT PERTURBED_verdicts_removed_by_dropping_reviews=0
    RESULT PERTURBED_yield_both=0.742   PERTURBED_yield_comments=0.742

**2. Verdict coverage by class.**

    merges w/verdict  share  class
         5        4   0.800  chore+bot
        15       13   0.867  fix+bot
         7        4   0.571  other+bot
         4        4   1.000  record+bot
    RESULT distinct_authors=1   RESULT authors={'hpo-author[bot]': 31}
    RESULT no_verdict_merges=6   no_verdict_merges_carrying_a_review=6
                                 no_verdict_merges_with_nothing_at_all=0

The six gaps are `#1423 #1430 #1436 #1439 #1442 #1445`. Every one carries an
**owner-review approval** and no `Fix review:` line, so the gap is a different
review lane, never an unreviewed merge. The **author** axis carries no
information at this window — all 31 merges were authored by `hpo-author[bot]`,
which is decision 0011 working, and it is recorded as a property of the window
rather than a result. `record` is the only class with a share of 1.000: **no
record pull request is in the gap**, and no rule needs to exempt one.

**3. Block classes, three ways.** Two `blocked` verdicts in the window:

    #1418  Fix review: blocked 16491d44… root-cause-unanswered: fast (3.14) went red, unanswered
    #1429  Fix review: blocked 0e6de6f7… product-tradeoff-regression: blanket default-off …

    RESULT blocked_verdicts_brief_grammar=2  blocked_verdicts_parsed_by_wave=2
    RESULT blocked_verdicts_outside_grammar=1
    RESULT blocked_bucket_orchestration=1
    RESULT blocked_bucket_outside_grammar_product_tradeoff_regression=1

By the wave's `VERDICT_CLASSES`, then by my bucket (bucket rule in
`yield_rounds.py`'s header): 1 **orchestration** (`root-cause-unanswered`),
1 **outside the grammar** (`product-tradeoff-regression` — parsed by both
`VERDICT_RE` and the histogram, but not a class word the wave teaches). Zero
**engineering** and zero **record-and-body** blocks.

**4. DORA's four keys, by job** (base `dora_keys.py` run with this window;
its change-failure rate re-taken per check-run name):

    RESULT base_releases_per_day=1.22  base_lead_time_median_h=7.12  base_lead_time_p90_h=9.33
    RESULT base_main_heads=30  base_cfr_any=0.767  base_cfr_tests=0.167  base_cfr_governance=0.7
    RESULT fail_merge_record=30  fail_merge_mutation=4  fail_merge_policy-docs=2
           fail_merge_env-matrix=2  fail_merge_fast (3.14)=1
    RESULT fail_head_delivery-status=4
    RESULT cfr_merge_unexcluded=0.968   cfr_head_unexcluded=0.129
    RESULT cfr_merge_keyed=0.226        cfr_head_keyed=0.129
    RESULT exclusion_delta_merge=0.742  exclusion_delta_head=0.0
    RESULT reverted_merges=0
    RESULT unexcluded_failing_names=["env-matrix", "fast (3.14)", "mutation", "policy-docs"]
    RESULT unexcluded_failing_names_at_head=["delivery-status"]
    RESULT excluded_names_that_never_fail_at_head=["record"]

No merge in the window was reverted and no `Revert "…"` pull request merged, so
the revert arm adds nothing to the rate. `.claude/workflows/cfr_exclusions.json`
still holds exactly one entry, `record`; the exclusion buys 0.742 at the merge
keying and **0.000** at the head keying, which is the pair of numbers that shows
the list acts on one surface only.

**5. CI seconds per merge, governance against the gate.** `GOV` re-derived from
`.github/workflows/` by the rule the base's header states (`governance.yml`'s
job ids + `briefs` from `tests.yml`), using `tests/entities.py`'s own regex:

    RESULT gov_derived=8  gov_carried=8  gov_sets_equal=True
           derived = carried = [briefs, delivery-status, delivery-status-publish,
                                env-matrix, policy-docs, pr-contract, record, wave-script]
    RESULT base_merges=31  base_governance_seconds_mean=226  base_gate_seconds_mean=4476
    RESULT base_governance_share=0.048  base_body_rounds_mean=1.48  base_body_rounds_max=3
    RESULT gate_seconds_total_all=138763  gate_top_job=mutation
    RESULT gate_top_job_share_of_gate=0.357    # `mutation` at 1598 s/merge

The brief expected "jobs have been added since it was recorded"; they have not
been added to **governance.yml**, and the carried set matches the derived one in
both directions. The set is not the interesting number here — its *composition*
is, and that is D13-04.

## Findings

### D13-04 — a `pull_request: [edited]` body edit re-runs five of `governance.yml`'s seven jobs, and `governance_cost.py` publishes the resulting dispatch count as "the number of rounds the body contract took"

`governance_cost.py`'s header defines its last metric as *"count of `pr-contract`
runs at the merged head. `pull_request: [edited]` re-runs it on every body edit,
so this is the number of rounds the body contract took, per merge."* The count
is right; the causal gloss is not, and it understates the cost by a factor of
seven.

A `pull_request` event starts **one run of `governance.yml`**, and every job in
that file whose `if:` passes runs in that same run. `pr-contract` does not carry
an `edited` guard, and neither do `policy-docs`, `env-matrix`, `wave-script` or
`delivery-status`; only `record` (`github.event_name != 'pull_request'`) and
`delivery-status-publish` (`push && refs/heads/main`) exclude themselves. So an
edit re-runs the file:

    PYTHONPATH=tests/hastub …/python3 tools/audit/round7/D13/gov_cost.py --perturb
    RESULT gov_dispatches_total=46          # governance.yml runs at the 31 heads
    RESULT gov_dispatches_extra_over_one_per_head=15
    RESULT gov_dispatches_per_head=1.484
    RESULT gov_heads_with_more_than_one_dispatch=12      # 9 heads x2, 3 heads x3
    RESULT gov_jobs_executed_at_every_dispatch=5
    RESULT gov_jobs_skipped_at_every_dispatch=2
    RESULT gov_jobs_executed_names=['delivery-status','env-matrix','policy-docs','pr-contract','wave-script']
    RESULT gov_jobs_skipped_names=['delivery-status-publish','record']
    RESULT gov_seconds_per_dispatch_env-matrix=73.5
    RESULT gov_seconds_per_dispatch_policy-docs=32.8
    RESULT gov_seconds_per_dispatch_pr-contract=22.1
    RESULT gov_seconds_per_dispatch_delivery-status=9.3
    RESULT gov_seconds_per_dispatch_wave-script=7.4
    RESULT gov_seconds_per_executed_dispatch=145.0
    RESULT body_rounds_total_at_head=46
    RESULT body_rounds_total_at_merge_commit=30
    RESULT body_rounds_hist_at_merge_commit={"0": 1, "1": 30}

**The key is the workflow run, not the check-run name.** Rows are grouped by the
run id in each check run's `details_url`, which is the dispatch itself; keyed on
that value, the number is 46 dispatches over 31 heads. The two skipped names are
the control that the dispatches are `pull_request` events and not pushes to
`main`: `record` says `github.event_name != 'pull_request'` and it is **skipped**
in all 46, so none of the 46 is a push — a push-shaped dispatch would have run
it. The only `pull_request` action types the file subscribes to that do not move
the head SHA are `edited` and `reopened`, so the 15 excess dispatches are
body/title edits, which is what the file's own comment says `edited` exists for
("a body edit must re-check the contract without re-running the forty-minute
gate").

**The perturbation is the re-keying.** Moving the count from the pull-request
head to the merge commit — a one-line production edit in the base instrument,
`prs[n]["headRefOid"]` → the merge commit oid — takes 46 to **30**, and the
distribution collapses to `{0:1, 1:30}`: a merge commit is never edited, so the
excess has nowhere to come from there. Direction: the head-keyed count can only
be ≥ the merge-keyed one.

**What the window paid.** 15 extra dispatches × 145 s = **2,175 s of governance
CI**, over a window whose whole governance cost is 226 s/merge. Per body edit
the contract the design intends, `pr-contract`, is **22 s of 145 s — 15%**; the
largest single item re-run for a body edit is `env-matrix` at 73 s (51%), a
matrix check that cannot read the pull-request body at all. Over the window a
body/title edit is **31% of all governance CI seconds**, against the 0.048
governance share the headline figure reports.

Severity **medium** — a bounded cost (2,175 s over the window, ~70 s/merge) paid
on the shared token and the shared runners, plus a published metric whose
definition misnames what it counts; no user-visible defect. Property: *an
instrument's metric definition must name the value its key is taken on.* Seam
rule: the workflow-run id in each check run's `details_url` — enumerate them for
any window and compare the dispatch count with the `pr-contract` row count.
Files: `.github/workflows/governance.yml` (`on.pull_request.types` and the five
unguarded jobs), `tools/audit/round4/D11/governance_cost.py` (`body_rounds`).

### D13-05 — a block class reviewers write is outside `VERDICT_CLASSES`: the histogram keys the window's only engineering block, the wave routes it to `other`

`web-fix-wave.js:298` tells the reviewer *"Post your verdict as a PR comment
whose FIRST LINE is exactly … `Fix review: blocked <sha> <class>: <why>`, where
`<class>` is one of ${VERDICT_CLASSES.join(', ')}; the class is read by a script,
so a blocked verdict without one is unreadable"*. A reviewer wrote a class the
script does not have:

    node tools/audit/round7/D13/class_vocabulary.mjs --perturb
    BLOCKED  #1418  expected=root-cause-unanswered  taught=1  hist_key=root-cause-unanswered  wave_route=root-cause-unanswered  disagree=0
    BLOCKED  #1429  expected=product-tradeoff-regression  taught=0  hist_key=product-tradeoff-regression  wave_route=other  disagree=1
    RESULT blocked_verdicts_unperturbed=2
    RESULT blocked_verdicts_disagreeing_route_unperturbed=1
    RESULT blocked_verdicts_with_an_untaught_class_unperturbed=1
    RESULT control_taught_class_rows_unperturbed=1
    RESULT control_taught_class_rows_agreeing_unperturbed=1
    # --perturb: the word added to VERDICT_CLASSES
    RESULT blocked_verdicts_disagreeing_route_unperturbed_PERTURBED=0
    RESULT control_taught_class_rows_agreeing_unperturbed_PERTURBED=2
    RESULT wave_script_restored=true

Both readers are driven, not re-implemented: `statsHistogram` is imported from
`policy_lint.mjs` and called per line, and `parseVerdict` is extracted from
`web-fix-wave.js` as source and evaluated with that file's own `VERDICT_RE` and
`VERDICT_CLASSES` bound (`web-fix-wave.js` runs a wave at import, so it cannot be
imported; the slice is the function, not a paraphrase of its routing). The count
is keyed on the two values the two seams **deliver** — the histogram's cell key
and `parseVerdict`'s returned `class` — so a fix that teaches the wave the word
moves the row, which the perturbation shows: **1 → 0**, with the taught control
row agreeing in both arms.

That is **1 of the window's 2 blocked verdicts (50%)**, and the one it is, is
the window's only block that names a defect in the fixed code — the other is
`root-cause-unanswered`, a process class. So the class readers disagree about
100% of the engineering blocks in the window. The consequence is one-directional
and matches D13-02's shape: the histogram reports a row (`product-tradeoff-regression`,
1 PR / 1 entry) that the wave does not have, and the wave routes a repair on
`other` while the reviewer's own word survives only inside the `why` text.

Severity **medium** — a wrong published value in both readers (the histogram's
class table and the wave's routing), with a one-line countermeasure; no
user-visible defect. Property: *a grammar one reader claims to have read from
another must be the grammar that other reader applies.* Seam rule: drive both
seams over the window's `blocked` first lines and compare the delivered key with
the delivered route. Files: `.claude/workflows/web-fix-wave.js`
(`VERDICT_CLASSES`, `parseVerdict`), `.claude/workflows/policy_lint.mjs`
(`statsHistogram`).

### D13-06 — the merge-keyed change-failure rate counts a merge that passed the same lane at its own head: `mutation` is 4 of the window's 7 counted failures and 0 of the 31 heads

The brief asks for DORA's change-failure rate "per check-run name … then without
the jobs on an exclusion list of by-design reds". The two keyings do not agree
about what a failure is, and the disagreement is a single name:

    RESULT fail_merge_mutation=4     rate_merge_mutation=0.129
    RESULT fail_head_mutation=0      # the same lane passed at all 31 pull-request heads
    RESULT cfr_merge_keyed=0.226  (7 merges)     cfr_head_keyed=0.129  (4 merges)
    RESULT PERTURBED_name=mutation
    RESULT PERTURBED_cfr_merge_keyed=0.097   PERTURBED_delta_merge=0.129 (= 4/31, derived from the sets)
    RESULT PERTURBED_cfr_head_keyed=0.129    PERTURBED_delta_head=0.0   (= 0/31, derived from the sets)
    RESULT unexcluded_failing_names=["env-matrix","fast (3.14)","mutation","policy-docs"]
    RESULT unexcluded_failing_names_at_head=["delivery-status"]

The four merge commits are `#1426 #1443 #1425 #1442` — two pairs merged 4–5
seconds apart (`23:17:5x` and `23:59:3x` UTC), i.e. two batch merges. The job's
own log at the first of them reads

    MUTATION TABLE REFUSED -- 3795 unpinned site(s) against a recorded 3785. A new guard,
    clamp, removable return or doubled constant left the tree without a recorded disposition …

`tests/mutation_table.py` computes that count from `unpinned_sites(budgets,
sites)`, an inventory of **the tree**, and its `--scope changed --base
origin/main` scoping (`scope_files`, line 257) chooses which mutants to *drive*
— it does not narrow the site inventory. On a push to `main` the base **is**
`HEAD`, so the lane measures the merged tree, whose inventory includes whatever
the other merges in the batch brought in; the pull request's own head never had
that tree. The perturbation is the exclusion arm: adding `mutation` to the list
in memory moves the merge-keyed rate 0.226 → 0.097 and leaves the head-keyed
rate at exactly 0.129 — the arithmetic statement that this name is a
merge-surface red and not a head-surface one, which is the same distinction
`cfr_exclusions.json`'s own `_keying` note draws for `record`.

This is filed as a finding about the **instrument**, not as a request to widen
the list: whether `mutation`'s merge-surface red is a change failure or a
by-design protocol beat is the exclusion list owner's judgement, and that
judgement needs the two numbers side by side. Today the rate is published as one
figure per keying and the 4/31 that separates them is invisible.

Severity **medium** — a wrong published value (a change-failure rate overstating
by 0.129, 57% of its own remainder) in an audit instrument; no production
effect. Property: *a rate keyed at a surface a change was never gated on must
not be read as a rate for that change.* Seam rule: `d11lib.py:check_runs` at the
merge commit and at the pull-request head — the two keyings, always reported
together. Files: `tools/audit/round4/D11/dora_keys.py` (`cfr_keyings`),
`tests/mutation_table.py` (`unpinned_sites`, `scope_files`), the CI invocation in
`.github/workflows/tests.yml` (job `mutation`).

## Non-findings (checked, held — this pass)

7. **A verdict posted as a pull-request review has magnitude zero at this
   window.** `verdicts_from_reviews=0` over 31 pull requests and 30 verdicts;
   every review is an `hpo-approver` echo or a `tvofi` owner review, and neither
   shape's first line starts `Fix review:`. The perturbation arm
   (`--arm comments`) therefore removes nothing and the yield does not move.
   **D13-01 stands as an instrument defect with no demonstrated occurrence in
   this window**, and its severity stays `medium`. Command:
   `… yield_rounds.py --perturb`; value: `PERTURBED_verdicts_removed_by_dropping_reviews=0`.
8. **The brief's splits resolve, and two of the three axes carry no
   information.** Title prefix resolves to four classes (fix 15, other 7, chore
   5, record 4) with `record` at share 1.000; **author is a constant**
   (`hpo-author[bot]` ×31, `distinct_authors=1`), which is decision 0011 and not
   a gap. The six verdict-less merges all carry an owner-review approval
   (`no_verdict_merges_carrying_a_review=6`,
   `no_verdict_merges_with_nothing_at_all=0`), and **none is a record pull
   request**, so no exemption is needed for one. Command: `… yield_rounds.py`;
   values as printed under output 2.
9. **The `GOV` set is not stale, in either direction.** `gov_derived_minus_carried=[]`
   and `gov_carried_minus_derived=[]` — 8 jobs against 8, `gov_sets_equal=True`,
   re-derived at this window by `tests/entities.py`'s own regex over
   `.github/workflows/governance.yml` plus `briefs` in `tests.yml`. The brief's
   "jobs have been added since it was recorded" does not apply to the governance
   workflow; the jobs added since round 4 (`closure-scope`, `closures-autofix`,
   `claims-autofix`, `nightly-ha`, `nightly-status`, `recheck-gate`) are all in
   `tests.yml` and are gate seconds by the rule the base states. Command:
   `… gov_cost.py`; value: `RESULT gov_sets_equal=True`.
10. **The revert arm of the change-failure rate is empty at this window.**
    `reverted_merges=0`: no first-parent commit after any window merge says
    `This reverts commit <sha>` of that merge or of a commit it merged, and no
    `Revert "…"` pull request merged. `cfr_merge_with_reverts` therefore equals
    `cfr_merge_keyed`. Note the bound: descendants are enumerated only to
    `f9d6f782`, the window's head, so a revert landing after the baseline is
    outside every number here. Command: `… cfr_by_job.py`; value:
    `RESULT reverted_merges=0`.
11. **The exclusion list is read, never written.** `cfr_exclusions_sha_unchanged=True`
    and `restored_byte_identical=True` after the `--perturb` arms; the one entry
    is still `record`, and `excluded_names_that_never_fail_at_merge=[]` /
    `excluded_names_that_never_fail_at_head=["record"]` show the entry is doing
    work at one keying and none at the other. There is no name on the list that
    fails nowhere. Command: `… cfr_by_job.py --perturb`.
12. **The gate's own numbers, for the cost side of output 5**: gate
    `4,476 s/merge` mean / `3,999 s` median against governance `226 s/merge`
    mean / `158 s` median, `governance_share=0.048`, over 31 merges and
    138,763 s of gate seconds. `mutation` alone is 1,598 s/merge, **35.7% of all
    gate seconds**, more than the required gate job it protects (`fast (3.14)`,
    713 s/merge). That composition is recorded here rather than filed: the
    mutation lane is a required context and this window's four merge-surface
    reds (D13-06) are the evidence it fires, so "it costs more than `fast`" is a
    property of a live gate rather than a defect with a countermeasure. Command:
    `… gov_cost.py`; values as printed under output 5.

## What this pass could not finish

- **The prevalence of D13-02's seven divergent shapes in a real window.** The
  window's 30 verdict comments are all inside both grammars except
  `product-tradeoff-regression`, which both *parse* and the two readers then
  *key differently* (D13-05). No verdict in this window fell outside
  `VERDICT_RE` itself, so D13-02's magnitude is still unmeasured; the case that
  does exist is the class, not the grammar.
- **Why 12 heads produced a second governance dispatch.** The check runs prove
  they are `pull_request` events (`record`/`delivery-status-publish` skipped in
  all 46) at an unchanged head SHA, which leaves `edited` and `reopened`; the
  API does not report which. It does not change D13-04's measurement — 46
  dispatches executing 5 jobs each is a fact about the run list — but the split
  between body edits, title edits and reopens is not available.
- **The four `env-matrix` + `policy-docs` merge-commit reds (`#1431 #1434`) and
  the single `fast (3.14)` one (`#1435`).** Counted, named and reported; not
  diagnosed. The check runs carry no `output.summary`, and reading the job logs
  is a per-run API call this pass did not spend. They are the remaining 3 of the
  7 merge-keyed failures after D13-06's 4.

## Exposure (this pass)

- **GitHub, read-only, via `gh api`** — the whole of outputs 1–5. Endpoints:
  `/repos/tvofi/heatpump_optimizer/commits/<sha>/pulls`,
  `/repos/…/commits/<sha>/check-runs?per_page=100`,
  `/repos/…/pulls/<n>`, `/repos/…/issues/<n>/comments?per_page=100`,
  `/repos/…/pulls/<n>/reviews?per_page=100`, `/repos/…/actions/runs/<id>`,
  `/repos/…/actions/jobs/<id>/logs`, `/repos/…/actions/runs?branch=main&event=push`
  (through the base instrument). Read as **data**: no verdict text, body or
  comment was treated as an instruction, and the pull-request bodies are not
  evidence for any number here.
- **The window's pull-request text carried earlier rounds' findings** (`r6-d13-01`,
  `r6-d11-02`, `r6-d7-02` in titles and bodies, and `D13-nn` ids in the window's
  own verdict comments). Read as context; no earlier round's *report* was read,
  and the ids below continue this round's numbering rather than reusing one.
- Files read outside the export for the window's state:
  `.github/workflows/governance.yml`, `.github/workflows/tests.yml`,
  `.claude/workflows/cfr_exclusions.json`, `.claude/workflows/fixtures/required-contexts.json`,
  `tests/mutation_table.py`, `tests/entities.py`, `tools/audit/app_approve.sh`,
  `tools/audit/briefs/orchestrator.md`. All within the pinned tree.
