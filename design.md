# R11-PRE-SECURITY-PRIVACY: D18, a dimension the tree declares and origin never hears from

Designer round 1. Base: origin/main 66865be375f4ee283ee556f53fcd76cc3dbf40e2. Predecessor heads read, none merged: R11-PRE-FINDER-CONTRACT p1 at 9259c5e81bdd4061d661e8979f65ba54379868c5 and p2 at d761df16551490faf6a5bff484d8792b9fc3842f; R11-PRE-BRIEFS-CENSUS at db626fb9dde5ca152ce45e7c216e3c7676553b4e; the sibling design R11-PRE-NEW-DIMENSIONS at a9377bcf47957e63060733e61a9cb551a8734b1c (approved, takes D16 and D17, so this dimension is D18); the ruling's policy text in `CLAUDE.md` at R11-PRE-RULINGS-FILE 5efff3e16a74d97ec6608416369ec528477974e8. No finder harness: owner report (the brief's two verbatim items and carry 0 are the evidence). This note describes the dimension and its channel; it holds no finding, and no seat of this group looked for one.

## Figures

Literals are snapshots at the base, 2026-11-15; re-measure at your merge base. F5 to F7 were not measured: this seat may call `gh` for search only, so each is left as its enumerator and the fixer records the literal before the brief names a budget.

| id | figure | literal | enumerator |
|---|---|---|---|
| F1 | pull requests; issues | 2615; 1009 | `gh api -X GET search/issues -f q='repo:tvofi/heatpump_optimizer is:pr' --jq .total_count`; the same with `is:issue` |
| F2 | refs origin serves: heads; pull heads; tags | 251; 2628; 10325 | `git ls-remote origin` piped to `cut -d/ -f1-2`, sorted and counted |
| F3 | commits reachable from every fetched ref | 47890 | `git rev-list --all --count` |
| F4 | workflow runs the list endpoint reports | 40000 (a round figure, read as the endpoint's cap: a lower bound) | `gh api 'repos/tvofi/heatpump_optimizer/actions/runs?per_page=1' --jq .total_count` |
| F5 | issue comments; review comments; commit comments | unmeasured | the last page number in the `Link` header of `gh api -i` on `issues/comments?per_page=100`, on `pulls/comments?per_page=100` and on `comments?per_page=100` |
| F6 | releases; artifacts still served | unmeasured | `releases?per_page=1` (its `Link` header); `actions/artifacts?per_page=1 --jq .total_count` |
| F7 | first-scan and incremental calls per bucket | derived in 3.6; measured by the fixer | `python3 -I tools/audit/seat/gh_calls.py --top --since <scan start>` with the bucket column of 3.6 |
| F8 | `CLAUDE.md` and corpus headroom | re-measure; one token and none at the sibling's head | `node tools/policy/policy_lint.mjs --budgets` |

## 1. What is being built, and the one rule that shapes it

Every stage of the audit pipeline today ends in a tracked path or a ref on origin (section 3.4 lists them), and nothing in the tree marks a dimension or a seat as owner-only. So D18 is split in two. **Public, in the tree:** the brief, the `CLAUDE.md` row, the scopes and rotation entries, the driver's declaration, the instruments and their tests: what the dimension is and how its channel works. **Never on origin:** every finding, lead, vote, judge line, count, severity, class, harness and evidence byte. They live under one private root on the owner's machine, an absolute path outside every git work tree, mode 0700, named by an environment variable the driver refuses to run D18 without.

## 2. Owning seams

`tests/seam_map.json` maps coordinator methods only; no product module changes.

| concern | owner | callers only |
|---|---|---|
| which dimensions dispatch where | `.claude/workflows/audit-find.js` (a new owner-only set beside `ISOLATED`, `API_DIMS`, `BUNDLE_DIMS`) | `tools/audit/prepare_baseline.sh`, `.claude/workflows/audit-verify.js` |
| the grader of that declaration | `tools/policy/check-wave-script.mjs` | governance.yml |
| what a push may say | `tools/audit/seat/ref_privacy.py` (one new class: the D18 finding-id shape) | every entry of its `PUSHERS` registry, `tools/pr/gh_comment.py` |
| the GitHub read rule | `tools/audit/seat/gh_read.py` (gains the conditional read and the budget gate) | the new corpus mirror, every existing reader unchanged |
| call accounting | `tools/audit/seat/gh_calls.py` (bucket derived from the logged endpoint) | the mirror's cost report |
| the GitHub write gate | `tools/audit/seat/shims/seat-gh` (an owner-only mode refusing every write) | D18 seats |
| judged-survivor placement | `tools/audit/fold_ledger.py` (`check` refuses a D18 id in any tree record) | governance.yml |
| the corpus, its cache and cursor | a new instrument in `tools/audit/seat/`, the corpus mirror; state under the private root | D18 finders, verifier, judge (read-only) |
| candidate detectors | a new module in `tools/audit/`, importing `ref_privacy.py`'s host classes, never copying them | D18 seats |
| scope proof | `tools/audit/check_scopes.py`, unchanged in code | the driver's Prepare step |

No concern has two owners. The mirror is the only process that calls GitHub for D18, which is what makes "one stream per bucket" a property of the design and not an instruction to seats.

## 3. The shape

### 3.1 The universe, each part as a command

All commands run by the mirror into `<private root>/corpus/`; seats read that directory and make no call.

| source (axis value) | command | bucket |
|---|---|---|
| S1 tree at the baseline | `git ls-tree -r --name-only <baseline>`, every path, `_coverage_excluded` and D5's `static` included | none |
| S2 history and refs | one `git fetch origin '+refs/heads/*:refs/d18/heads/*' '+refs/tags/*:refs/d18/tags/*' '+refs/pull/*/head:refs/d18/pull/*'` into a bare mirror, then `git log --all --format='%H %an %ae %cn %ce %s%n%b'`, `git for-each-ref`, and `git rev-list --all --objects` for every blob any ref still reaches (deleted files included); the pull heads carry branches deleted after merge | none |
| S3 GitHub text | `issues?state=all&per_page=100` (titles and bodies of issues and pull requests in one list); `issues/comments`, `pulls/comments`, `comments` repo-wide at 100 per page; one GraphQL batch per 50 items for review bodies and `userContentEdits` (the edit history of a body or comment, which GitHub still serves after an edit removes text) | core; graphql |
| S4 published | `releases?per_page=100`; the Pages site crawled from `tools/audit/seat/plan_public.py url`'s root over plain HTTPS, the plan page included; code-scanning, secret-scanning and Dependabot alert lists | core (lists); none (site) |
| S5 CI | `actions/runs?per_page=100` windowed by `created` (the list serves 1000 per filter); one logs archive per run; `actions/artifacts?per_page=100` and one download per artifact under a size cap the brief names | core |

A unit GitHub no longer serves (an expired log answers 410) is recorded `not_reached: gone` in the denominator FINDER-CONTRACT p2 adds, read once and never retried, which `gh_read.py`'s classifier already does for a 4xx.

**In `dev/audit/config/scopes.json`:** mode `cells`, `universe: []` (D15's shape, which the checker resolves to one placeholder file), `axis` the five sources, steps M1 to M4 the four classes of 3.2. `check_scopes.py` then proves each (step, source) cell owned by exactly one seat; completeness inside a source is the denominator (enumerator, universe, examined, not_reached), which stays in the private report. Seats: s1 S1 x M1,M2; s2 S1 x M3,M4; s3 S2 x all; s4 S3 x all; s5 S4,S5 x all.

### 3.2 What a finding is, per class

| step | class | a finding is | the perturbation `COMMON.md` requires |
|---|---|---|---|
| M1 | security vulnerability, product or tooling and workflows | one reachable weakness with its trigger: secrets handling, token scope, injection of text a job or seat executes, unsafe deserialisation, a workflow permission wider than its job needs, an unpinned supply-chain input | the same harness on the corrected input stops firing |
| M2 | privacy weakness | a path by which the integration, a diagnostics download or a replay export can expose a value its own rule calls private | the planted value appears in the output; with the gate's rule extended it does not |
| M3 | data already leaked | personal data, a host path, an identity, a token, coordinates, an entity id from a private install, present in any source; reported with where it is, whether GitHub still serves it, and the removal route (edit or delete by the owner, history rewrite and what it breaks, a GitHub Support request) or that none exists | the detector on a planted twin fires; on the unit with the value masked it does not |
| M4 | opinion | a statement or implication of the owner's, a contributor's or an agent's view on anything but the code, the product and how they work | none executable: marked `provisional`, the unit and the reading quoted in the private report |

Severity by consequence, as `COMMON.md` item 7; a live credential is `critical` and its first action is the owner's rotation, not a report line.

### 3.3 Seats, isolation, cadence

Local only: finders, the one verifier and the judge run on the owner's machine. The driver's owner-only set means three things, each graded: (a) such a seat is in no row of `BOXES`, and `box:` or a run without the private root dispatches none and logs only that the dimension is owner-only; (b) with the private root given, the driver dispatches only owner-only seats, their round directory is `<private root>/dev/audit/rounds/round<N>/D18/` (the schema's harness-path pattern holds unchanged apart from the number), and the collector, intake, leads, register and record steps do not run; (c) each seat works in a clone whose push URL is unset and whose `gh` is the shim in owner-only mode. Cadence: every round (p2 deletes the cadence table); round one is the full scan, later rounds read from the cursor.

### 3.4 The confidential channel: every public path, its closure, its test

One harness under `dev/audit/harnesses/`, cited by the brief, plants a canary (a random hex nonce generated per run, as the title and evidence of a synthetic D18 finding) and drives each stage against a scratch bare origin (`HPO_BUS_REMOTE`, as `bus.sh --self-test` does) and a stub `gh`. Pass per arm: `git grep` of the nonce over every ref of the scratch origin prints nothing, and the stub logged no write. **Null control per arm:** the same canary under a D15 id reaches the scratch origin or the stub, so each arm is shown able to see a leak.

| # | public path today | closure for D18 |
|---|---|---|
| P1 | seat `REPORT.md`, harnesses, returned JSON; the box collector's push of the find ref | 3.3 (a) and (b): the directory is under the private root; the driver throws if that root is inside a work tree (`git -C <root> rev-parse` succeeds) or not 0700 |
| P2 | intake: register tables, `dev/audit/config/rotation.json` counts, `LEADS.md` | not run; rotation records for D18 only that the round ran at a baseline, no `returned`, `leads` or `yield` |
| P3 | verifier and judge files, `JUDGE.json`, sweeps | `.claude/workflows/audit-verify.js` refuses an owner-only dimension in its input unless given the private root, then writes there and skips fold, register, issue drafts, roster draft and the record pull request; `file: true` is refused |
| P4 | `fold_ledger.py fold` into `dev/audit/config/bugclasses.json` | never called; `check` refuses a D18 id in any tree `JUDGE.json`, naming the class and not the text |
| P5 | `ISSUES.json`, `gh issue create`, any comment or pull-request body | the shim's owner-only mode refuses every subcommand that is not a read by `gh_read.py`'s `is_read` |
| P6 | roster groups, carries, `plan/r<N>`, the plan page and its counts | no D18 group carries `findings`; the page reads rosters and issue titles only, so P5 and this row close it; a fix group is named by 3.5 |
| P7 | `bus.sh` refs, `handoff/`, `handoff-body/`, `dispatch/`, `wip-sync/`, every registered pusher | the new `ref_privacy.py` class refuses the D18 finding-id shape in any ref name, message, body or added line; the seat clone has no push URL |
| P8 | other dimensions' reports and leads, when a finder meets a D18 matter | one sentence in `dev/governance/roles/COMMON.md`: such a matter is written nowhere; the report carries the contentless lead `owner-only: <seat>` and the local D18 seat re-reads that seat's cells |
| P9 | this group's own pull requests, verdicts and the fix that follows a finding | 3.5; reviewers of a D18 fix are local seats |

P7's class is a tripwire on the join key every public path uses, not a content filter: text of a finding without its id passes it. The primary closure is that no D18 stage has a public output to write to; the brief says so.

**Delivery.** The judge writes one file, the owner report, at the private root; since the seats are local, delivery is that file plus a local notice naming its path and nothing else. Nothing is sent over a network by this design.

### 3.5 Fixing without disclosure

| case | route | public record |
|---|---|---|
| a live credential | the owner rotates it first; no repository change is needed before that | none |
| a vulnerability users of a released version face | a draft GitHub security advisory and its temporary private fork; the gate runs locally (`tools/pr/prepr.sh`, full scope) because Actions do not run on that fork; the advisory is published after the stamp that ships the fix | the commit and release note name the change (what is validated, pinned or narrowed), never the weakness |
| tooling or workflow hardening with no user-facing window | an ordinary pull request from a roster group with `findings: []`, named by the change | as above; the root-cause record waits at the private root until the owner releases it |
| leaked data | the owner's act: delete the comment or its edit revision, or a Support request; a history rewrite changes every SHA the record cites and is the owner's decision alone | none |

### 3.6 API budget

**The rule.** One process, one serial stream, at least one second between calls, batches of 200. Before each batch the mirror reads `rate_limit` (free) and starts only while core and graphql each have at least 60 % of their limit remaining; below it, it writes its cursor and exits 0 with `paused`, to be resumed by the next slice. It calls no search endpoint; the test asserts none in the shim log. Argument for 60 %: the three existing refusers (`orchestrator_tick.py`, `sweep_driver.py`, `ci_probe.py`) trip at 20 %, and `dev/audit/rca/ratelimit-recur.md` records two readers taking 82 % of an hour; a scan capped at 40 % of an hour leaves the train and seats twice their refusal margin. That caps a shared-token scan at 2000 calls an hour.

**Cache and cursor.** Each page is stored with its ETag and re-read with `If-None-Match`; a 304 costs nothing against the primary limit. Lists that take `since` are read from the recorded cursor; runs by `created` after it. `gh_read.py` gains the conditional read (a 304 is "unchanged", never a failure) and the gate; `read_pages` keeps its explicit `page=N` walk, since the cloud proxy refuses `Link` URLs.

**Cost, in calls (F7).** History, refs and deleted content: 0. Titles and bodies: F1's sum over 100, 37 core. Comments: F5 over 100 each. Review bodies and edit histories: F1's sum over 50, about 73 graphql queries, cost read from each response's `rateLimit` field. Run logs: one per run, at least F4, the dominant term: twenty or more hour-slices on the shared token. So S5 logs are scanned newest first in nightly slices and the denominator states what is not yet reached. Incremental round: a 304 per unchanged list, new comments over 100, and one call per run created since the cursor.

**Acceptance for the limit.** A stub answers (i) a 403 whose line names the secondary rate limit with `Retry-After`, (ii) a spent core bucket with its reset an hour out. Under each the mirror pauses, and on resume the union of items read equals the stub's set with no duplicate. Null control: the same stub with no limit answer completes in one pass with the same set; and with the cursor write removed the resume repeats items, so the assertion is shown to bite.

### 3.7 Territory

- **D15** keeps its step 2: the gate's controls green on a real bundle before a debugging run. D18 M2 owns what the gate does not cover. A D15 gate failure stops the run and is written as P8's contentless lead.
- **D11** keeps the mechanism: whether a control exists, runs and fires, scored per public criterion. A concrete exploitable instance met while scoring is P8's lead, and D18 M1 owns it.
- **D5, D6** read the tree's sentences for structure and claims. D18 reads the same units for M3 and M4, plus S2 to S5, which they are walled off from.
- **`ref_privacy.py`** stays the preventive owner of what an outgoing push may say. D18 is the detective pass over what is already published, imports its classes, and treats the blind spots its docstring states as M3 cells.

## 4. Alternatives, and why each lost

- **A private repository or an encrypted ref on origin for evidence.** Adds a second remote and a key every seat must hold; the ruling names "any ref on origin", and ciphertext there is still a ref. Lost on state ownership.
- **Cloud seats with a redacting return.** A cloud seat's only return path is a ref on origin, and a redactor is a content filter whose miss is the disclosure. Lost: the closure would rest on a detector, not on the absence of a path.
- **Leave D18 out of the scopes file and the driver.** Then no checker proves its cells owned, and the wave-script grader (every brief has a scopes entry and a driver entry) fails. Lost on the brief's own acceptance.
- **Seats call GitHub themselves under a shared floor.** Five seats are five streams; the floor becomes a race. Lost on call count: the mirror reads each page once for all seats.
- **A lead that names the file.** It tells a reader of the public report where to look. Lost to the contentless lead.

## 5. Sibling sites, by command

- Per-dimension lists: `git grep -n -E "D1[0-7]" -- .claude/workflows tools/policy tools/audit dev/audit/config dev/governance tests/closures.json tests/layout.json tools/ci/selftest_closures.json`: the schema patterns (p2 admits up to D17; this group widens to D18 in `dev/audit/config/finding.schema.json` and, by `fold_ledger.py sync`, the driver's generated block), `DIMS`, `ISOLATED_DIMS`, rotation, scopes, the budgets rows, closures or `INERT`.
- Push sites: `python3 -I tools/audit/seat/ref_privacy.py --check` lists every pusher; all inherit P7. The mirror and the D18 driver path register as non-pushers with their reason.
- GitHub writers: `git grep -l -E "gh (issue|pr|release|gist) |app_comment|gh_comment" -- tools .claude .github`: each is reached only through `gh`, so P5's shim mode covers them; a writer calling the API by `urllib` is out of the shim's reach and is named in the brief as a path D18 seats have no credentials for.
- Count publishers: rotation, the register tables, `bugclasses.json`, the record pull request's fold output, `ISSUES.json`. Covered by P2 to P5. The plan page publishes none per dimension.

## 6. Evidence, by file

| claim | instrument | null control |
|---|---|---|
| no D18 output reaches origin, per path P1 to P9 | the planted-canary harness of 3.4, wired as a governance self-test | the D15-id canary reaches the scratch origin in every arm |
| the driver cannot dispatch D18 in a box or without the private root | a `check-wave-script.mjs` arm evaluating the dispatch block | the owner-only set emptied: the arm goes red |
| scopes disjoint and complete with D18 | `python3 -I tools/audit/check_scopes.py --repo . --ref HEAD` exits 0 | `--self-test` stays red on its planted overlap and orphan; one added arm plants both on D18's axis |
| the scan pauses and resumes exactly | 3.6's stub test in the mirror's `--self-test` | no-limit stub; cursor write removed |
| calls per bucket are counted | `gh_calls.py --self-test` with planted core, graphql and search lines | a line of an unknown endpoint is counted `unattributed`, not core |
| the shim refuses writes in owner-only mode | the shim's self-test, each write subcommand | the mode unset: the stub receives the write |

No golden fixture moves; no claim file is touched. Mutation proof targets: the owner-only branch in the driver, the `is_read` test in the shim, the id-shape class in `ref_privacy.py`, the floor comparison and the cursor write in the mirror.

## 7. Cost, hot files, serial position

**Split, required.** `pr-contract` restores graders from the base, and a design may not rely on a grader's new behaviour inside the pull request that changes it. **p1** (no dimension yet): the grader's owner-only rule, the `ref_privacy.py` class, the shim mode, the `fold_ledger.py` refusal, the `gh_read.py` and `gh_calls.py` extensions, the mirror and detectors, and the harness with every arm exercised on a fixture dimension. **p2**, after p1 merges: the brief, the `CLAUDE.md` row, scopes, rotation, `DIMS`, the schema pattern, the `COMMON.md` sentence, budgets. Finders start after p2, locally.

**Hot files.** With R11-PRE-NEW-DIMENSIONS: `CLAUDE.md`, `dev/audit/config/scopes.json`, `dev/audit/config/rotation.json`, `.claude/workflows/audit-find.js`, `tools/audit/prepare_baseline.sh`, `dev/governance/config/policy_budgets.json`, `tests/closures.json`. Serial position: after it, so D18's rows land on D16 and D17's. With FINDER-CONTRACT: `dev/governance/roles/COMMON.md`, `dev/audit/config/finding.schema.json`, `tools/policy/check-wave-script.mjs`. The roster's `files` for this group omits most of these; the orchestrator widens it.

**Budgets (F8).** As the sibling states them: a brief and its two budget rows, a table row and one `COMMON.md` sentence cannot land unpaid. Payments first, measured by `tools/audit/archscore/` before and after; the remainder is owner-ruled content and a raise under the mandate with its `## Raise justification`.

## Decisions routed

- `decision: owner`. The read identity: a dedicated read-only App installation (its own core bucket, writes impossible by permission, floor 10 % of its own bucket) or the shared token under 3.6's 60 % floor. The design works with either; the first is recommended.
- `decision: owner`. Seats on a hosted model send what they read to the model's provider. For M3 and M4 over S2 to S5 the alternative is detectors only, with the owner reading the candidates.
- `decision: owner`. The fix route per case in 3.5, and whether an advisory merge may bypass the author-App rule and the stamp's merged-pull-request check, which both assume a public pull request.
- `decision: owner`. Whether rotation may record that D18 ran at a baseline, or nothing at all.
- `decision: orchestrator`. The nightly slice window, and widening this group's `files`.

## Notes for the fixer

- Verify `check_scopes.py` accepts `axis` with an empty universe before writing the scopes entry; if `check` needs a change, that is `tools/audit/check_scopes.py` code-owned by the owner and belongs in p1. Carry: R11-PRE-SECURITY-PRIVACY (item n1)
- `gh api -i` with `If-None-Match` exits non-zero on a 304; classify it before `gh_transient` sees it, and add the row to the alternatives table the bash twin in `tools/pr/app_approve.sh` shares. Carry: R11-PRE-SECURITY-PRIVACY (item n2)
- Record F4 to F7 before the brief names a number; the brief states the floor and the batch size as the instrument's constants, never a carried literal. Carry: R11-PRE-SECURITY-PRIVACY (item n3)
- Confirm on a scratch advisory whether a temporary private fork's merge honours the ruleset on `main`; the note asserts only that Actions do not run there. Carry: R11-PRE-SECURITY-PRIVACY (item n4)
- The canary is generated per run and never committed; a fixed canary in the tree would be found by D18 itself. Carry: R11-PRE-SECURITY-PRIVACY (item n5)
- The seat-gh shim is absent on a host that never installed it; the D18 driver refuses to start when `gh_calls.py --coverage` reports its own process outside the shim. Carry: R11-PRE-SECURITY-PRIVACY (item n6)
