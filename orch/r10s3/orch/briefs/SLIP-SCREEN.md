# Audit seat — screen the last 500 merged pull requests for asks that never came

You are screening for one failure class, not reviewing code quality:

> **A commitment recorded somewhere — an owner fold, a reviewer ask, a `## Forward-carry`, a
> "deferred to a later time" — that no later artifact ever delivered.**

The exemplar, found hours ago: fold **(e)** of issue #1955 was added by the owner as an *issue
comment* on 2026-10-04 ("an OPTIONAL thermal power entity …"), written into the round-9 roster
brief, and then silently dropped when pull request #2006 implemented **only (a)–(d)** and closed
the issue. The ask survived nowhere — not in the round-10 roster, not in an open issue, not in any
`Carry:` marker. It was invisible until the owner asked about it.

**LOCAL seat only, and read-only on GitHub**: you write no comments, no issues, no pull requests,
and you do not edit the roster. You report; the orchestrator routes.

## Scope

The **last 500 merged pull requests** on `tvofi/heatpump_optimizer`, newest first. State the window
you actually covered (oldest and newest PR number and merge date) in the report — do not write
"500" if the API gave you fewer.

## Where an ask hides — search all of these

1. **PR bodies**: sections named `## Forward-carry`, `## Known`, `## Deferred`, `## Follow-up`,
   `## Not in this PR`, `## Limits`, `## Owed`; any `Carry: <dest>` marker; sentences with
   *defer*, *deferred*, *later*, *follow-up*, *future*, *another PR*, *not in this PR*, *will be
   addressed*, *owed*, *TODO*, *left for*, *out of scope*.
2. **Issue bodies and comments** for every issue a PR closes: enumerated folds `(a) (b) (c) …`,
   `Phase 2`, `later rounds`, owner comments after the PR opened. This is where #1955's (e) lived.
3. **Review comments on the PR**: a reviewer's "non-blocking" ask that the merge absorbed without
   a follow-up (the design reviews in `probe/design-*` carry these too).
4. **Delivery rows** `dev/programme/delivery/<N>.md` and roster `carry` entries, for a destination
   that was named but never dispatched.

## How to prove a slip — and how to prove you can see a delivery

For every candidate, record **three** things: the ask verbatim with a link, the search that would
have found the delivery, and what that search returned. A candidate with no search is not a
finding.

Every candidate then takes one verdict:

- **CONFIRMED-SLIP** — the ask is recorded, and no later PR, issue, roster group or code change
  delivers it.
- **LANDED-ELSEWHERE** — delivered by a later PR under a different name; give the PR and the line.
- **SUPERSEDED** — a later decision or design replaced the ask; give it.
- **UNPROVEN** — you could not establish either way; say what would settle it.

**Null control, mandatory**: pick five asks you *know* landed — folds (a)–(d) of #1955 in #2006,
and four more of your choosing — and show your method finds them as LANDED-ELSEWHERE. A screen that
cannot see a delivery cannot see a slip.

## Method

- Work from the API, cached to disk: `gh pr list --state merged --limit 100 --json
  number,title,body,mergedAt` page by page (the `--limit 500` single call truncates bodies), and
  `gh api` for issue comments. Keep the cache under your scratch directory so a re-run costs
  nothing.
- Extract candidates with a script, then **verify each by hand against the tree and the record** —
  a grep of the code for the feature, the roster for the group, the issue for the closure. Keyword
  hits are candidates, never findings.
- Beware the two traps this repository has already paid for: a *closed* issue is not evidence of
  delivery (the #1955 case), and a `Carry:` marker naming a destination is not evidence the
  destination did anything with it.
- Bound your own cost: the box runs ten seats. Depth over breadth — if 500 PRs is too many to
  verify properly, screen all 500 for candidates but take the **verification** to a stated depth,
  and say exactly what depth you reached.

## Deliverables

1. `/Users/timmalmstrom/hpo-orch/r10s3/audit/slip-screen.json` — one entry per candidate:
   `{pr, ask, source_url, verdict, delivered_by, evidence, confidence}`.
2. `/Users/timmalmstrom/hpo-orch/r10s3/audit/slip-screen.md` — the report: the window covered, the
   null control, counts per verdict, then the CONFIRMED-SLIPs ordered by how much they matter,
   each with the three proofs and a one-line routing suggestion (a new roster group, a carry into
   an existing group, or "close as superseded").
3. If your extractor is reusable, it belongs in the repository under `tools/audit/` with the
   classification a new tracked file needs (`tests/closure.py` `INERT` or a measured closure, or
   `tests/entities.py` fails) — but **landing it is optional**; the screen is the deliverable.
   Say which you chose and why.

## Rules

- **No host path** in anything that leaves the machine (#2310); in your report write `~/…`.
- Do not modify the roster, do not file issues, do not comment anywhere. The orchestrator routes
  what you find.
- A finding you cannot prove stays UNPROVEN; a wrong CONFIRMED-SLIP costs more than a missing one,
  because it becomes work someone has to refute.
- Eight seats are working in the same tree; do not touch groups whose fixers are live (CI-LAYOUT,
  NIGHT-FOLDS, REPLAY-LANE, TRAIN-HOLD, SAV-REASONS, FREQ-DEFROST, the CodeQL cap, or the plan
  optimizer).

## Environment

- Scratch: `/Users/timmalmstrom/hpo-seats/r10s3/slip-screen` (absolute; create it).
  Checkout at fresh main: `/Users/timmalmstrom/hpo-orch/r10s3/lint-main` (detached at origin/main).
- `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH` (pinned 3.14).
- `gh` is authenticated as the owner; mind the API budget — cache, page, and do not re-query.

## Report back, under 400 words

The window; the null-control result; counts per verdict; the CONFIRMED-SLIPs as one line each with
their PR numbers; and what would have caught each of them at merge time.
