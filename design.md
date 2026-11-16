# R11-PRE-SECURITY-PRIVACY: D18, a dimension the tree declares and origin never hears from

Designer round 3, answering `Design review: revise ba8209b07fecf118894b9e19e37469461b0490c4 class-open` (design-verdict commit 64199f1699671e9c7f39320317e4a43545be0cec); round 2 answered `revise 3637ac0015ca4d0e609ce13bf28da1605d5261a7` and its table is kept below. Base: origin/main 824a016f7562c307b81b30a3c39e3844b1b4b630 (the payload's), re-read for this round; the round-2 base 5825e1346c14eecace5c87c046558774145a94dc and the reviewer's d4968fe08ba0b18f9d96f6ca308edf45f35ca469 are its ancestors. Predecessors at this base: R11-PRE-FINDER-CONTRACT is merged (#3621), and its grader clause is in the base (`tools/policy/check-wave-script.mjs:820` and `:823` carry the `D17-s1` clause beside `DENOM`), while `dev/audit/config/finding.schema.json`'s patterns still stop at D15; R11-PRE-RULINGS-FILE is merged (#3626); R11-PRE-NEW-DIMENSIONS is merged (#3646) with no D16 or D17 brief in the base's dimensions directory, its design taking those two numbers, so this dimension is D18; R11-PRE-BRIEFS-CENSUS handoff fb9b921b98d2434b83f01132051a20e7cb89789d. No finder harness: owner report (the brief's two verbatim items and carry 0 are the evidence). This note describes the dimension and its channel; it holds no finding, and no seat of this group looked for one.

## Answers to the verdict of round 2

| verdict point | answer | where |
|---|---|---|
| 1 `class-open`: the twin-finder path (`tools/audit/seat/finder_overlap.py` `seat_pair` names a twin whose report lands in the tree) | new row P10: `seat` refuses a seat of an owner-only dimension, and `estimate` a pair whose universe is one, both reading the owner-only set from `dev/audit/config/scopes.json`, the file `audit-find.js` dispatches from; the dimension regex is widened to any number so admission is scopes membership alone, and no closure rests on the regex; canary-seat arm and D15 null control; `finder_overlap.py` is in p1 | 3.3 (a), 3.4 P10, sections 2, 5, 6, 7 |
| note dr2-finder-contract-landed | applied: the base above carries FINDER-CONTRACT's grader clause, so p1's switch is written on top of it; the schema patterns are re-read at this base and still stop at D15 | header, section 7 |
| note dr2-fold-ledger-sibling | applied: section 7 names the rebase order with R11-PRE-NO-READ-BUILDERS on `tools/audit/fold_ledger.py` | section 7 |

## Answers to the verdict of round 1 (kept)

| verdict point | answer | where |
|---|---|---|
| 1 `class-open`: App writers mint from key files | owner-only seats run under a separate OS account that cannot read any key; a probe refuses the run otherwise; one canary arm per credentialed writer | 3.3, row P5b, section 5 |
| 2 `class-open`: the driver's return value | the owner-only branch returns a literal status built from its arguments; the launching session is named and holds no credential; an arm reads the return value and every prompt and log line | 3.3, row P1 |
| 3 `architecture-unsound`: the grader's two null controls | p1 moves both to a switch keyed on the D18 brief existing, the form `DENOM` already has | section 7 |
| 4 `harness`: arms claimed where no test can fail | each row names its stage and refuser, or is stated instruction-only with what backs it and what it does not catch | 3.4 |
| decision routed: the `owner-only: <seat>` pointer | no ruling is on record (RULINGS.md at the handoff above has none), so the design takes the branch that publishes nothing: no pointer; section 1 and row P8 agree; the pointer is routed as the owner's to admit | section 1, P8, Decisions |
| notes dr1-driver-part, dr1-ref-namespaces, dr1-github-text, dr1-corpus-untrusted, dr1-m4-judging | each designed, not carried: section 7; 3.1 S2; 3.1 S3 and S5; 3.3; 3.2 | as named |

## Figures

Literals are snapshots at the base, 2026-11-15; re-measure at your merge base. F4 to F7 were not measured: this seat may call `gh` for search only, so each is left as its enumerator and the fixer records the literal before the brief names a budget.

| id | figure | literal | enumerator |
|---|---|---|---|
| F1 | pull requests; issues | 2631; 1011 | `gh api -X GET search/issues -f q='repo:tvofi/heatpump_optimizer is:pr' --jq .total_count`; the same with `is:issue` |
| F2 | refs origin serves: heads; pull; tags | 372; 2649 (18 of them merge refs); 10336 | `git ls-remote origin` piped to `cut -d/ -f1-2`, sorted and counted |
| F3 | commits reachable from every fetched ref | round 1 read 47890; not re-taken | `git rev-list --all --count` in the bare mirror of S2 |
| F4 | workflow runs the list endpoint reports | round 1 read 40000, the endpoint's cap: a lower bound | `gh api 'repos/tvofi/heatpump_optimizer/actions/runs?per_page=1' --jq .total_count` |
| F5 | issue comments; review comments; commit comments; issue events | unmeasured | the last page number in the `Link` header of `gh api -i` on `issues/comments?per_page=100`, `pulls/comments?per_page=100`, `comments?per_page=100`, `issues/events?per_page=100` |
| F6 | releases and their assets; artifacts still served | unmeasured | `releases?per_page=100` (rows and each row's asset list); `actions/artifacts?per_page=1 --jq .total_count` |
| F7 | first-scan and incremental calls per bucket | derived in 3.6; measured by the fixer | `python3 -I tools/audit/seat/gh_calls.py --top --since <scan start>` with the bucket column of 3.6 |
| F8 | `CLAUDE.md` and corpus headroom | re-measure | `node tools/policy/policy_lint.mjs --budgets` |

## 1. What is being built, and the one rule that shapes it

Every stage of the audit pipeline today ends in a tracked path, a ref on origin, or a value returned to a session that holds write credentials (3.4 lists them), and nothing in the tree marks a dimension or a seat as owner-only. So D18 is split in two. **Public, in the tree:** the brief, the `CLAUDE.md` row, the scopes and rotation entries, the driver's declaration, the instruments and their tests: what the dimension is and how its channel works. **Never on origin, and never in a session that can write there:** every finding, lead, pointer, vote, judge line, count, severity, class, harness and evidence byte. They live under one private root on the owner's machine: an absolute path outside every git work tree, mode 0700, owned by an OS account that holds no GitHub credential (3.3). Other dimensions publish nothing about D18 either, not even that a seat's cells hold a matter: D18's own seats cover every source every round, so silence elsewhere loses nothing.

## 2. Owning seams

`tests/seam_map.json` maps coordinator methods only; no product module changes.

| concern | owner | callers only |
|---|---|---|
| which dimensions are owner-only: the one declaration | `dev/audit/config/scopes.json`, a dimension entry's `owner_only: true` (one key; `check_scopes.py` reads only its named keys, `universe`, `mode`, `steps`, `seats`, `axis`, `ledger`, `classify`, `static`, so it passes the new one by; note n10 covers every other reader) | `audit-find.js` (derives its set from `args.scopes`, which Prepare proves equal to the committed file before any seat runs), `finder_overlap.py`, the grader |
| which dimensions dispatch where, and what a run returns | `.claude/workflows/audit-find.js` (the owner-only set beside `ISOLATED`, `API_DIMS`, `BUNDLE_DIMS`, derived, not literal); `.claude/workflows/audit-verify.js` for its own phases (it takes no scopes, so it holds a literal set the grader holds equal to the declaration) | `tools/audit/prepare_baseline.sh` |
| who may be twinned, and what an overlap estimate may print | `tools/audit/seat/finder_overlap.py` (`seat` and `estimate` refuse the owner-only set) | the orchestrator |
| the grader of that declaration | `tools/policy/check-wave-script.mjs` | governance.yml |
| the owner-only environment: account, allow-listed variables, the probe | a new instrument in `tools/audit/seat/`, the owner-only launcher | both drivers' Prepare steps, the owner |
| what a push may say | `tools/audit/seat/ref_privacy.py` (one new class: the D18 finding-id shape) | every entry of its `PUSHERS` registry, `tools/pr/gh_comment.py` |
| the GitHub read rule | `tools/audit/seat/gh_read.py` (gains the conditional read and the budget gate) | the corpus mirror; every existing reader unchanged |
| call accounting | `tools/audit/seat/gh_calls.py` (bucket derived from the logged endpoint) | the mirror's cost report |
| the GitHub write gate for `gh` | `tools/audit/seat/shims/seat-gh` (an owner-only mode refusing every write) | D18 seats |
| judged-survivor placement | `tools/audit/fold_ledger.py` (`check` refuses a D18 id in any tree record) | governance.yml |
| the corpus, its cache and cursor | a new instrument in `tools/audit/seat/`, the corpus mirror; state under the private root | D18 finders, verifier, judge (read-only) |
| candidate detectors | a new module in `tools/audit/`, importing `ref_privacy.py`'s host classes, never copying them | D18 seats |
| scope proof | `tools/audit/check_scopes.py`, unchanged in code | the drivers' Prepare steps |

No concern has two owners. The App writers (`tools/pr/app_mint.sh` and its callers) are not changed: the closure of verdict point 1 is that their keys are out of the seat's reach, which the launcher owns. The mirror is the only D18 process that calls GitHub, which makes "one stream per bucket" a property of the design.

## 3. The shape

### 3.1 The universe, each part as a command

All commands run by the mirror into `<private root>/corpus/`; seats read that directory and make no call.

| source (axis value) | command | bucket |
|---|---|---|
| S1 tree at the baseline | `git ls-tree -r --name-only <baseline>`, every path, `_coverage_excluded` and D5's `static` included | none |
| S2 history and refs | `git ls-remote origin`, then one `git fetch origin '+refs/heads/*:refs/d18/heads/*' '+refs/tags/*:refs/d18/tags/*' '+refs/pull/*:refs/d18/pull/*'` into a bare mirror (pull heads carry branches deleted after merge; merge refs come too); `git log --all --format='%H %an %ae %cn %ce %s%n%b'`, `git for-each-ref`, `git rev-list --all --objects` for every blob a ref still reaches. **Namespace assertion:** a listed ref outside those three namespaces makes its namespace a `not_reached: unmapped namespace` line and the mirror exits non-zero; it is never skipped. **Commits no ref reaches:** the before-SHA of every force-push, from `activity?activity_type=force_push&per_page=100` and the forced-push timeline items of the S3 batch; each absent from the mirror is tried once by `git fetch origin <sha>`: fetched, it is scanned and listed `served by SHA only` with its removal route (a GitHub Support request); refused, `not_reached: gone` | none; core (activity list) |
| S3 GitHub text | `issues?state=all&per_page=100` (titles and bodies of issues and pull requests); `issues/comments`, `pulls/comments`, `comments` repo-wide; `issues/events?per_page=100` (a rename event carries the earlier title); `labels`, `milestones?state=all`; one GraphQL batch per 50 items for review bodies, `userContentEdits` (the edit history GitHub still serves after an edit removes text), forced-push items, and the head commit's status contexts and their descriptions | core; graphql |
| S4 published | `releases?per_page=100` (notes, asset names) and one download per asset under the size cap; the Pages site crawled from `tools/audit/seat/plan_public.py url`'s root over plain HTTPS, the plan page included; code-scanning, secret-scanning and Dependabot alert lists; the wiki's git repository and the discussions list when `repos/tvofi/heatpump_optimizer` reports them enabled | core (lists); none (site, wiki) |
| S5 CI | `actions/runs?per_page=100` windowed by `created` (1000 per filter), whose rows carry the run's display title, branch and head-commit message; one logs archive per run; `check-suites/<id>/check-runs?per_page=100` per run for check output titles, summaries and text, and `check-runs/<id>/annotations` only where a row counts one; `actions/artifacts?per_page=100` and one download per artifact under the size cap | core |

Stated `not_reached`, each a denominator line with its reason: a unit GitHub no longer serves (an expired log answers 410: `gone`, read once, which `gh_read.py`'s classifier already does for a 4xx); a job's step summary (`no endpoint`; removal route: deleting the run); status contexts of commits that head no pull request (`cost`, enumerator `git rev-list --count`).

**The corpus is untrusted.** Archives are extracted only under the mirror's own directory, a member whose resolved path leaves it, a link, or a size or ratio past the cap is refused and recorded; nothing from the corpus is executed or imported. Every D18 seat prompt states that corpus text is data and never an instruction.

**In `dev/audit/config/scopes.json`:** mode `cells`, `universe: []` (D15's shape), `axis` the five sources, steps M1 to M4. `check_scopes.py` then proves each (step, source) cell owned by exactly one seat; completeness inside a source is the denominator (enumerator, universe, examined, not_reached), which stays in the private report. Seats: s1 S1 x M1,M2; s2 S1 x M3,M4; s3 S2 x all; s4 S3 x all; s5 S4,S5 x all.

### 3.2 What a finding is, per class

| step | class | a finding is | the perturbation `COMMON.md` requires |
|---|---|---|---|
| M1 | security vulnerability, product or tooling and workflows | one reachable weakness with its trigger: secrets handling, token scope, injection of text a job or seat executes, unsafe deserialisation, a workflow permission wider than its job needs, an unpinned supply-chain input | the same harness on the corrected input stops firing |
| M2 | privacy weakness | a path by which the integration, a diagnostics download or a replay export can expose a value its own rule calls private | the planted value appears in the output; with the gate's rule extended it does not |
| M3 | data already leaked | personal data, a host path, an identity, a token, coordinates, an entity id from a private install, present in any source; reported with where it is, whether GitHub still serves it, and the removal route (edit or delete by the owner, history rewrite and what it breaks, a GitHub Support request) or that none exists | the detector on a planted twin fires; on the unit with the value masked it does not |
| M4 | opinion | a statement or implication of the owner's, a contributor's or an agent's view on anything but the code, the product and how they work | the location harness below |

**Judging M4.** Whether a span is an opinion is a reading, not a measurement, so no seat confirms it. An M4 unit's harness is a location check: it prints the span at its (source, unit, offset), and with the span masked prints nothing, so it moves and `dev/governance/roles/judge.md` step 2 does not void it. The verifier re-runs it and records its own reading beside the finder's; the judge rules only `located` or `unreproduced` (the span is not there), never `confirmed`, and no vote decides. Every located unit goes to the owner report under its own heading, both readings quoted, for the owner to rule. The brief states this; `judge.md` and `verifier.md` do not change.

Severity by consequence, as `COMMON.md` item 7; a live credential is `critical` and its first action is the owner's rotation, not a report line.

### 3.3 Seats, the environment that owns the closure, cadence

**Who launches.** Only the owner, on the owner's machine, through the launcher, as the **seat account**: an OS account created once for D18 that owns the private root and nothing else. Never the orchestrator, a standing seat, or a cloud session. The session the launcher starts is the workflow's parent, so both drivers, every seat and every reply live inside that account. That session may write under the private root only; it holds no credential with which to write anywhere else.

**What the launcher does.** It starts the mirror first, handing it the read credential on a file descriptor, and only after the mirror exits starts the session with an environment built from an allow-list: a home under the private root, `HPO_IDENTITY_DIR` naming an empty directory there, the shim directory first on the path, the private-root variable, the model credential, and nothing inherited.

**The probe, a refusal and not an instruction.** The launcher runs it before the session and refuses to start on any line; each driver's Prepare step runs it again and the driver throws unless it exits 0, beside the rotation and scopes checks that step already makes. It refuses, naming the path and never a content, when the running account: can read the owner's identity directory (the path `tools/pr/app_mint.sh`'s `mint_identity` resolves, where both App key pairs live) or the stamp's deploy key; gets an answer from `git credential fill` for the origin host; has an agent socket or a private key under its home; has a token variable set or a `gh` that reports a login; resolves `gh` to anything but the shim in owner-only mode; finds the private root inside a work tree (`git -C <root> rev-parse` succeeds) or not 0700; or runs in a cloud session.

**The drivers.** The owner-only set is the dimensions whose `dev/audit/config/scopes.json` entry carries `owner_only: true`; `audit-find.js` derives it from `args.scopes`, `finder_overlap.py` from the `--scopes` file it already loads, and the grader holds `audit-verify.js`'s literal set and the briefs that declare themselves owner-only equal to it. It means, each graded: (a) such a seat is in no row of `BOXES`, no twin of it is seated (P10), and `box:` or a run without the private root dispatches none and logs only that the dimension is owner-only; (b) with the private root given, the driver dispatches only owner-only seats, their round directory is `<private root>/dev/audit/rounds/round<N>/D18/`, each seat's reply schema is a path and a done flag with no other property, and the collector, intake, leads, register, fold, issue, roster and record steps do not run; (c) the value the workflow returns, every line it logs and every message it throws is a literal built from its arguments: that the run was owner-only, the round, the baseline, and the private path. No reply text is copied into it, so the launching session receives no finding even though it is itself inside the wall. Cadence: every round; round one is the full scan, later rounds read from the cursor.

### 3.4 The confidential channel: every public path, its stage, its refuser, its test

One harness under `dev/audit/harnesses/`, cited by the brief, plants a canary: a random hex nonce generated per run, placed in the title and evidence of a synthetic D18 finding and in every reply a stub seat gives. It evaluates the two workflow scripts with a stub of the agent, log and phase calls that records every prompt, label and log line, against a scratch bare origin (`HPO_BUS_REMOTE`, as `bus.sh --self-test` does) and stub `gh`, `curl` and `git push`. **Pass, for an executable arm:** no ref of the scratch origin holds the nonce, no stub logged a write, and where the row says so the named value lacks it. **Null control, per executable arm:** the same canary under a D15 id reaches the place the arm watches, so the arm is shown able to see a leak.

| # | public path today | stage the arm drives | refuser | test |
|---|---|---|---|---|
| P1 | seat `REPORT.md`, harnesses, the reply JSON, the collector's push of the find ref, the value `audit-find.js` returns | `audit-find.js` evaluated with D18 active | the driver's owner-only branch (3.3 a to c) and the probe | executable: nothing under the repository work tree, no prompt whose label is not a D18 seat, no log line, no thrown message (a stub seat that fails is one arm) and not the return value holds the nonce. Null: the D15 run's return value, intake prompt and find-ref push all hold it |
| P2 | intake: register tables, `dev/audit/config/rotation.json` counts, `LEADS.md` | the same evaluation, intake and leads phases | the driver: neither is dispatched; rotation records only that the round ran at a baseline | executable: the stub saw no intake or leads label; `git status --porcelain` is empty. Null: D15 dispatches both |
| P3 | verifier and judge files, `JUDGE.json`, sweeps, the register, issue drafts, the roster draft, the record pull request, the value `audit-verify.js` returns | `audit-verify.js` evaluated with a D18 input | the driver: throws without the private root or with `file: true`; with it, writes there, skips those phases and returns the literal | executable, as P1 over that script. Null: the D15 run returns verdicts and dispatches the register and record labels |
| P4 | `fold_ledger.py fold` into `dev/audit/config/bugclasses.json` | `fold_ledger.py check` over a scratch tree holding a `JUDGE.json` with the canary under a D18 id | `check`: exits non-zero naming the class, and its output lacks the nonce | executable. Null: a D15 id passes `check` and `fold` writes it |
| P5 | `ISSUES.json`, `gh issue create`, any comment or body written through `gh` | the shim in owner-only mode, each write subcommand with the canary | the shim: refuses whatever `gh_read.py`'s `is_read` does not admit | executable: the stub `gh` behind the shim is never called. Null: mode unset, the stub receives the write |
| P5b | writers that never touch `gh`: `tools/pr/app_push.sh`, `tools/pr/app_comment.sh`, `tools/pr/app_approve.sh`, `tools/audit/seat/body_patch.sh`, `tools/audit/seat/remerge_main.sh` (each mints from the identity directory), `tools/audit/seat/bus.sh` (pushes over the ambient git credential and signs with the approver key), `tools/release/stamp.py` (the deploy key) | each writer run with the canary as its body or message, inside the launcher's environment fixture | the probe (no key readable, no credential answered), then each writer's own fail-closed line before any call | executable, one arm per writer: stub `curl` and the scratch origin saw nothing. Null: the same writer with a throwaway key directory, as its own self-test builds, sends the canary to the stub. One more arm for the probe: a fixture account view with a readable key file is refused; null: with it unreadable the probe exits 0 |
| P6 | roster groups, carries, `plan/r<N>`, the plan page and its counts | the roster draft is a phase of P3 and is covered there | none of its own | **instruction-only** for a line written by hand: no D18 group carries `findings`, and a fix group is named by 3.5. Backed by P7's tripwire on the id at push. Not caught: a roster line that describes a weakness without its id |
| P7 | `bus.sh` refs, `handoff/`, `handoff-body/`, `dispatch/`, `wip-sync/`, every registered pusher | the guard `ref_privacy.py --check` runs, with the canary's id in a ref name, a message, a body and an added line; one end-to-end push through `bus.sh` | the new `ref_privacy.py` class on the D18 finding-id shape | executable. Null: a D15 id reaches the scratch origin. Completeness over pushers stays `registry_refusals`' job |
| P8 | another dimension's report, when its finder meets a D18 matter | none | none | **instruction-only**: one sentence in `dev/governance/roles/COMMON.md`, that such a matter is written nowhere, with no pointer. Backed by coverage, not detection: D18 seats read every source every round, and `ref_privacy.py`'s existing value classes still refuse a token or host path in that report's push. Not caught: a weakness described in prose |
| P9 | this group's own pull requests and verdicts, and the fix that follows a finding | none | none | **instruction-only**: 3.5's naming rule; reviewers of a D18 fix are owner-only seats. Backed by P7 on the id. Not caught: prose |
| P10 | the twin finder: `finder_overlap.py seat` names a twin of a scopes.json seat, which the orchestrator dispatches with the same cells, its report at `dev/audit/rounds/round<N>/<dim>/<key>-twin/REPORT.json` in the tree; `estimate` prints n1, n2, m and the estimate for a pair | `finder_overlap.py seat` over a scratch scopes file holding an `owner_only: true` dimension D18 whose one seat is the **canary seat** `D18-s<k>`, `k` a random integer drawn per run; then `estimate` over a hand-written pair naming that seat, with stub reports and a stub judge carrying the nonce | `seat_pair` refuses a seat whose dimension's scopes entry is owner-only, reading the set from the `--scopes` file (never from the dimension regex, which is widened to `D[0-9]+` so membership in scopes.json is the only admission test); `estimate`, which gains a required `--scopes`, refuses a pair whose `universe` is such a seat before it reads any report. Each refusal prints `REFUSED` and that the dimension is owner-only, with no path | executable: `seat` exits 1, writes no `--out` file, and its output holds neither `-twin` nor `round<N>/D18`; `estimate` exits 1 and its output holds no `n1=` and not the nonce; nothing new under the work tree. Null: the same scopes with the flag removed from D18 is admitted (exit 0, the twin path printed, so the arm sees the leak it guards), and a D15 seat of the base's scopes is admitted with its `-twin/REPORT.json` path printed and `estimate` printing `n1=`. One more arm: `seat` with `D18-s1` against the base's scopes, which hold no D18, is refused as no seat of scopes.json, so p1 is green before the dimension exists |

So the acceptance "each closure with a test" is claimed for P1 to P5, P5b, P7 and P10; P6, P8 and P9 are stated as instructions with their backing, and the brief says so in the same words. P7's class is a tripwire on the join key every public path uses, not a content filter. The primary closure is structural: no D18 stage has a public output to write to, and no D18 process holds a credential that writes.

**Delivery.** The judge writes one file, the owner report, at the private root; delivery is that file plus a local notice naming its path and nothing else. The owner reads it as the owner; nothing is sent over a network by this design.

### 3.5 Fixing without disclosure

| case | route | public record |
|---|---|---|
| a live credential | the owner rotates it first; no repository change is needed before that | none |
| a vulnerability users of a released version face | a draft GitHub security advisory and its temporary private fork; the gate runs locally (`tools/pr/prepr.sh`, full scope) because Actions do not run on that fork; the advisory is published after the stamp that ships the fix | the commit and release note name the change (what is validated, pinned or narrowed), never the weakness |
| tooling or workflow hardening with no user-facing window | an ordinary pull request from a roster group with `findings: []`, named by the change | as above; the root-cause record waits at the private root until the owner releases it |
| leaked data | the owner's act: delete the comment or its edit revision, or a Support request; a history rewrite changes every SHA the record cites and is the owner's decision alone | none |

### 3.6 API budget

**The rule.** One process, one serial stream, at least one second between calls, batches of 200. Before each batch the mirror reads `rate_limit` (free) and starts only while core and graphql each have at least 60 % of their limit remaining; below it, it writes its cursor and exits 0 with `paused`, to be resumed by the next slice. It calls no search endpoint and makes no write; its self-test asserts both over the shim log. Argument for 60 %: the three existing refusers (`orchestrator_tick.py`, `sweep_driver.py`, `ci_probe.py`) trip at 20 %, and `dev/audit/rca/ratelimit-recur.md` records two readers taking 82 % of an hour; a scan capped at 40 % of an hour leaves the train and seats twice their refusal margin. That caps a shared-token scan at 2000 calls an hour.

**Cache and cursor.** Each page is stored with its ETag and re-read with `If-None-Match`; a 304 costs nothing against the primary limit. Lists that take `since` are read from the recorded cursor; runs by `created` after it. `gh_read.py` gains the conditional read (a 304 is "unchanged", never a failure) and the gate; `read_pages` keeps its explicit `page=N` walk, since the cloud proxy refuses `Link` URLs.

**Cost, in calls (F7).** History, refs, deleted content and the wiki: 0. Titles and bodies: F1's sum over 100, 37 core. Comments and issue events: F5 over 100 each. Labels, milestones, releases, alerts, the activity list: a page or a few each. Review bodies, edit histories, forced pushes and statuses: F1's sum over 50, about 73 graphql queries, cost read from each response's `rateLimit` field. Runs: two calls per run (its logs, its check runs), at least twice F4, the dominant term: forty or more hour-slices on the shared token. So S5 is scanned newest first in nightly slices and the denominator states what is not yet reached. Incremental round: a 304 per unchanged list, new comments and events over 100, and two calls per run created since the cursor.

**Acceptance for the limit.** A stub answers (i) a 403 whose line names the secondary rate limit with `Retry-After`, (ii) a spent core bucket with its reset an hour out. Under each the mirror pauses, and on resume the union of items read equals the stub's set with no duplicate. Null control: the same stub with no limit answer completes in one pass with the same set; and with the cursor write removed the resume repeats items, so the assertion is shown to bite.

### 3.7 Territory

- **D15** keeps its step 2 unchanged: the gate's controls green on a real bundle, and a failure stops the run, as `dev/governance/dimensions/D15.md` already says in public. D15 writes that the gate failed and nothing of what tripped it. D18 M2 owns what the gate does not cover.
- **D11** keeps the mechanism: whether a control exists, runs and fires, scored per public criterion. A concrete exploitable instance met while scoring is P8's: written nowhere; D18 M1 owns it.
- **D5, D6** read the tree's sentences for structure and claims. D18 reads the same units for M3 and M4, plus S2 to S5, which they are walled off from.
- **`ref_privacy.py`** stays the preventive owner of what an outgoing push may say. D18 is the detective pass over what is already published, imports its classes, and treats the blind spots its docstring states as M3 cells.

## 4. Alternatives, and why each lost

- **The same account with a scrubbed environment** (a scratch home, the identity variable repointed, the push URL unset). The seat's uid still reads the key files by absolute path, and `app_push.sh` run with the variable set back mints and pushes. Lost: the closure would be an instruction; only a second uid makes the key unreadable.
- **A private repository or an encrypted ref on origin for evidence.** Adds a second remote and a key every seat must hold; the ruling names "any ref on origin", and ciphertext there is still a ref. Lost on state ownership.
- **Cloud seats with a redacting return.** A cloud seat's only return path is a ref on origin, and a redactor is a content filter whose miss is the disclosure. Lost: the closure would rest on a detector, not on the absence of a path.
- **The driver returns counts only.** A count per seat, beside the public scopes file, says which cells hold a matter. Lost to the literal status.
- **Leave D18 out of the scopes file and the driver.** Then no checker proves its cells owned, and the wave-script grader (every brief has a scopes entry and a driver entry) fails. Lost on the brief's own acceptance.
- **Seats call GitHub themselves under a shared floor.** Five seats are five streams and five credential holders. Lost on call count and on P5b: the mirror reads each page once, and seats hold nothing.
- **A lead or a pointer in another dimension's report.** Either tells a reader of the public report where to look. Lost to silence plus full coverage, unless the owner admits the pointer.

## 5. Sibling sites, by command

- Per-dimension lists: `git grep -n -E -e "D1[0-7]" -e '1\[0-' -- .claude/workflows tools/policy tools/audit dev/audit/config dev/governance tests/closures.json tests/layout.json tools/ci/selftest_closures.json`: the schema patterns in `dev/audit/config/finding.schema.json` (they stop at D15 at the base; FINDER-CONTRACT p2 admits to D17; this group widens to D18) and, by `fold_ledger.py sync`, the driver's generated block, `DIMS`, `ISOLATED_DIMS`, rotation, scopes, the budgets rows, closures or `INERT`.
- The regex-written dimension lists, the form the first command missed in round 2: `git grep -l -e '1\[0-' -- .claude/workflows tools/policy tools/audit dev/audit/config dev/governance tests tools/ci` returns three files at the base: `dev/audit/config/finding.schema.json` and the block `audit-find.js` generates from it (widened by p2 with the brief), and `tools/audit/seat/finder_overlap.py`, whose regex p1 widens to any number and whose admission becomes scopes membership plus the owner-only refusal (P10). A file this command newly returns is read for a public path before p2 widens anything.
- Push sites: `python3 -I tools/audit/seat/ref_privacy.py --check` lists every pusher; all inherit P7. The mirror, the launcher and the D18 driver path register as non-pushers with their reason.
- GitHub writers through `gh`: `git grep -l -E "gh (issue|pr|release|gist) |gh_comment" -- tools .claude .github`: P5's shim mode.
- GitHub writers that hold their own credential: `git grep -l -E "mint_token|openssl dgst -sha256 -sign|GIT_SSH_COMMAND" -- tools`: the seven of row P5b, plus `tools/pr/app_mint.sh` (sourced) and `tools/audit/seat/remerge_main_selftest.py` (a test), the two the harness exempts by name with that reason. A file this command newly returns owes an arm; the harness compares its arm list to the command's output and fails on a difference.
- Values returned to a launching session: `git grep -n "^return " -- .claude/workflows/audit-find.js .claude/workflows/audit-verify.js`: one in each script at the base, both watched by P1's and P3's arms; a message either script throws reaches the same session, so the arms catch every throw of an owner-only run and read its message too.
- Count publishers: rotation, the register tables, `bugclasses.json`, the record pull request's fold output, `ISSUES.json`. Covered by P2 to P5. The plan page publishes none per dimension.

## 6. Evidence, by file

| claim | instrument | null control |
|---|---|---|
| no D18 output reaches origin or a launching session, for P1 to P5, P5b, P7 | the planted-canary harness of 3.4, wired as a governance self-test | per arm, as 3.4 states it |
| the driver cannot dispatch D18 in a box, without the private root, or past a red probe | a `check-wave-script.mjs` arm evaluating the dispatch block over a fixture owner-only set | the fixture set emptied: the arm goes red |
| the declared owner-only set equals the briefs that declare it | the same grader, deriving the set from the briefs directory as it derives `DIMS` | a fixture brief declaring it with the set unchanged: red |
| no twin of an owner-only seat is seated, and no estimate printed for one | `finder_overlap.py --self-test`, the P10 arms with the canary seat | the flag removed, and a D15 seat: admitted, twin path printed |
| scopes disjoint and complete with D18 | `python3 -I tools/audit/check_scopes.py --repo . --ref HEAD` exits 0 | `--self-test` stays red on its planted overlap and orphan; one added arm plants both on D18's axis |
| the scan pauses and resumes exactly; no write, no search | 3.6's stub test in the mirror's `--self-test` | no-limit stub; cursor write removed |
| an unmapped ref namespace is never skipped | the mirror's `--self-test` with a fourth namespace in a scratch origin | three namespaces: exit 0, no such line |
| a hostile archive stays inside the corpus | the mirror's `--self-test` with a traversing member and a link | a well-formed archive extracts whole |
| calls per bucket are counted | `gh_calls.py --self-test` with planted core, graphql and search lines | a line of an unknown endpoint is counted `unattributed`, not core |

No golden fixture moves; no claim file is touched. Mutation proof targets: the owner-only branch and the literal return in each driver, each probe line, the `is_read` test in the shim, the id-shape class in `ref_privacy.py`, the owner-only test in `seat_pair` and in `estimate`, the namespace assertion, the floor comparison and the cursor write in the mirror.

## 7. Cost, hot files, serial position

**Split, required.** `pr-contract` restores graders from the base, so a part may not rely on a grader change it makes itself.

**p1** (no dimension yet):
- `tools/policy/check-wave-script.mjs`: both null controls that refuse `D18-s1` (lines 820 and 823 at the base, the scope pattern and the lead's owner seat) become a switch keyed on whether the D18 brief exists, the form `DENOM` has at line 83: with no brief the schema must refuse that id, with the brief it must admit it. p1's tree has no brief, so the base's grader and p1's agree; p2 adds the brief and the pattern together, and the grader restored from p1 then demands exactly that. At this base those two lines already carry FINDER-CONTRACT's `(!DENOM || ... 'D17-s1')` clause, so the switch is added beside it, not in place of it; re-read both lines at the merge base.
- the owner-only rule in the same grader, graded on a **fixture** set and fixture scopes until p2; the real set is asserted equal to the briefs that declare it, which is empty in p1 and so green.
- `.claude/workflows/audit-find.js` and `.claude/workflows/audit-verify.js`: the owner-only branch and the literal return, with the real set empty. The harness arms P1 to P3 drive these scripts with the fixture set injected.
- `tools/audit/seat/finder_overlap.py` (code-owned): the widened regex, the owner-only refusal in `seat` and `estimate`, `estimate`'s required `--scopes`, the P10 arms in its own `--self-test` (governance.yml already runs it), and its instrument page under `tools/audit/seat/instruments/`. The base's scopes hold no flag, so the real refusal is inert in p1 and the arms run on a scratch scopes file.
- the launcher and its probe, the `ref_privacy.py` class, the shim mode, the `fold_ledger.py` refusal (R11-PRE-NO-READ-BUILDERS adds a `yield` subcommand to the same file; whichever lands second rebases its subcommand over the other's and re-runs `fold_ledger.py`'s self-test), the `gh_read.py` and `gh_calls.py` extensions, the mirror and detectors, and the harness with every arm.

**p2**, after p1 merges: the brief (with its owner-only declaration), the `CLAUDE.md` row, scopes, rotation, `DIMS` and the owner-only set's one member, the schema patterns, the `COMMON.md` sentence, budgets. Finders start after p2, locally.

**Hot files.** With R11-PRE-NEW-DIMENSIONS: `CLAUDE.md`, `dev/audit/config/scopes.json`, `dev/audit/config/rotation.json`, `.claude/workflows/audit-find.js`, `tools/audit/prepare_baseline.sh`, `dev/governance/config/policy_budgets.json`, `tests/closures.json`. Serial position: after it, so D18's rows land on D16 and D17's. With FINDER-CONTRACT, merged at this base: `dev/governance/roles/COMMON.md`, `dev/audit/config/finding.schema.json`, `tools/policy/check-wave-script.mjs`, read at the merge base rather than re-ordered. With R11-PRE-NO-READ-BUILDERS: `tools/audit/fold_ledger.py`, either order. `tools/audit/seat/finder_overlap.py` is new to this group's list and shared with no open design. The roster's `files` for this group omits most of these, the two workflow scripts' p1 edit and `finder_overlap.py`; the orchestrator widens it.

**Budgets (F8).** As the sibling states them: a brief and its two budget rows, a table row and one `COMMON.md` sentence cannot land unpaid. Payments first, measured by `tools/audit/archscore/` before and after; the remainder is owner-ruled content and a raise under the mandate with its `## Raise justification`.

## Decisions routed

- `decision: owner`. The seat account: creating it once, and making the identity directory and the deploy key unreadable to it, is an act only the owner can take. Without it the probe refuses and D18 does not run; the design offers no weaker mode (section 4, first alternative).
- `decision: owner`. Whether another dimension's public report may carry the contentless pointer `owner-only: <seat>`. The design assumes no; admitting it is one `COMMON.md` sentence and changes nothing else.
- `decision: owner`. The read identity the mirror holds: a dedicated read-only App installation (its own core bucket, writes impossible by permission, floor 10 % of its own bucket) or the shared token under 3.6's 60 % floor. The first is recommended; with the second, the mirror is the one D18 process holding a token that can write, and its no-write assertion is what stands between.
- `decision: owner`. Seats on a hosted model send what they read to the model's provider. For M3 and M4 over S2 to S5 the alternative is detectors only, with the owner reading the candidates.
- `decision: owner`. The fix route per case in 3.5, and whether an advisory merge may bypass the author-App rule and the stamp's merged-pull-request check, which both assume a public pull request.
- `decision: owner`. Whether rotation may record that D18 ran at a baseline, or nothing at all.
- `decision: orchestrator`. The nightly slice window, and widening this group's `files`.

## Notes for the fixer

- Verify `check_scopes.py` accepts `axis` with an empty universe before writing the scopes entry; if `check` needs a change, that is `tools/audit/check_scopes.py` code-owned by the owner and belongs in p1. Carry: R11-PRE-SECURITY-PRIVACY (item n1)
- `gh api -i` with `If-None-Match` exits non-zero on a 304; classify it before `gh_transient` sees it, and add the row to the alternatives table the bash twin in `tools/pr/app_approve.sh` shares. Carry: R11-PRE-SECURITY-PRIVACY (item n2)
- Record F3 to F7 before the brief names a number; the brief states the floor and the batch size as the instrument's constants, never a carried literal. Carry: R11-PRE-SECURITY-PRIVACY (item n3)
- Confirm on a scratch advisory whether a temporary private fork's merge honours the ruleset on `main`; the note asserts only that Actions do not run there. Carry: R11-PRE-SECURITY-PRIVACY (item n4)
- The canary is generated per run and never committed; a fixed canary in the tree would be found by D18 itself. Carry: R11-PRE-SECURITY-PRIVACY (item n5)
- The seat-gh shim is absent on a host that never installed it; the probe's shim line covers it, and `gh_calls.py --coverage` reports a mirror process outside the shim. Carry: R11-PRE-SECURITY-PRIVACY (item n6)
- This seat could not call the activity list, the issue-events list or the check-suite endpoint (search only): confirm each one's shape and paging on its first call, and where one does not serve what 3.1 says, record the unit `not_reached` with the reason; never drop the row. Carry: R11-PRE-SECURITY-PRIVACY (item n7)
- A CI runner has one account, so the probe's arm reads a fixture view of what the account can reach, and the two-account behaviour is proved once on the owner's machine: record that run's probe line in the private root, not in the pull request. Carry: R11-PRE-SECURITY-PRIVACY (item n8)
- The session's own transcript and the workflow's persisted script and replies are written under the seat account's home; keep that home under the private root so they inherit its mode, and check the model credential is the only thing the allow-list carries in. Carry: R11-PRE-SECURITY-PRIVACY (item n9)
- Before writing `owner_only` into scopes.json, list every reader of that file (`git grep -l "scopes.json" -- tools .claude tests`) and confirm none refuses an unknown key; one that does gains the key in p1, never a second declaration elsewhere. Carry: R11-PRE-SECURITY-PRIVACY (item n10)
- `finder_overlap.py`'s refusal output names no path because the twin path itself says which seat of a public dimension would have run; keep the `seat` and `estimate` refusals to the seat id and the words owner-only. Carry: R11-PRE-SECURITY-PRIVACY (item n11)
