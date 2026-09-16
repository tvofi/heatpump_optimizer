# 0010 — Merge commits, not squashes, are how `main` takes a pull request

Status: recorded 2026-09-16 from the repository owner's ruling, taken in session
on that date. **Unlike 0008 and 0009, nothing here is owed on GitHub**: the
change this record describes already happened, on 2026-09-14, and went
unrecorded for two days. This file is the record catching up with the tree, and
the pull request that adds it repairs the instructions the tree still carried.

## Context

`main`'s first-parent history stopped carrying squash subjects on 2026-09-14,
between `0e3da75` (`feat: … (#1019)`, 16:30 CEST, the last squash) and
`3b82c13` (`Merge pull request #1018 from tvofi/fix/996-fail-fast`, 19:20
CEST, the first merge commit). Every first-parent commit since is a merge
commit. The enumerator, which is what to re-run rather than to read a number
off this page:

    git log --first-parent --format='%ad|%s' --date=short v6.4.4..origin/main \
      | awk -F'|' '{print ($2 ~ /\(#[0-9]+\)[[:space:]]*$/) ? "squash" : "merge"}' \
      | uniq -c

**Nothing in the tree recorded the change.** `docs/decisions/` held nine
records and none was about the merge method; five seat instructions still said
`merge_method squash`; `.claude/workflows/policy_lint.mjs` still asserted
"Squash-only `main` is the same set either way"; and three independent
enumerators of `main`'s merged-pull-request set were keyed on a trailing
`(#N)` that no longer appears.

That unrecorded precondition change is the shared cause behind four instrument
defects fixed in parallel this round. The root-cause analysis is on **#1041**,
comment `5693093076`: it names the process state as **(d) — the process was
sound and its preconditions changed underneath it** — and states the choice
this record settles, without taking it: restore squash-only merges, or repair
the instructions.

`gh api repos/tvofi/heatpump_optimizer` shows `allow_squash_merge` and
`allow_merge_commit` both true, so the shape is a per-merge choice that no
repository setting pins. The merge method is therefore a **convention**, and a
convention with no record is what produced the four defects.

## Decision

**The repository owner's ruling, 2026-09-16: merge commits are correct. The
instructions are what is wrong, and they are to be repaired.**

The four instrument fixes in flight widen their patterns to accept both shapes,
which is right under either answer, so none of them changes.

## What the tree must now not assume

Each of these was true under squash-only `main`, is false now, and is the form
in which the assumption was actually written down somewhere in this tree.

1. **That a first-parent subject on `main` ends `(#N)`.** It does not. An
   enumerator keyed on that suffix matches nothing, and its zero is
   indistinguishable from *no merges* — the silent-zero class the #1041
   analysis is about. A merged-pull-request enumerator reads
   `^Merge pull request #(\d+) ` as well, or asks the API per first-parent
   commit.

2. **That the branch's commits are discarded at merge.** They are not. They
   land on `main` whole, with their own SHAs, as the merge commit's second
   parent. A branch SHA now becomes reachable from `origin/main` after its
   merge, where a squash deleted it. Two consequences, both of which some text
   in this tree was reasoning from:

   - The argument "a branch SHA does not survive the squash" no longer holds
     **after** the merge. What still holds is that it is not an ancestor of
     `origin/main` **before** it, which is when `tests/structure.py`'s
     `recorded_at` and `tests/entities.py`'s `updated-for:` checks run, and it
     is still rewritten by the next `--amend`. Both checks keep their value;
     only the reason printed beside them changed.
   - Every branch commit message is now text on `main`. Where a squash
     concatenated those messages into one commit, a merge keeps them as
     separate commits.

3. **That the merge commit's message is the pull-request body.** It is not, and
   it was not under squash either.
   `gh api repos/tvofi/heatpump_optimizer --jq '{merge_commit_title,merge_commit_message}'`
   returns `MERGE_MESSAGE` and `PR_TITLE` — the subject is
   `Merge pull request #N from <branch>` and the body is **by default** the
   **pull-request title**.

   **Measure it per merge commit, not by grepping the history**, and do not
   read a count off this page — the window slides and this record is
   permanent. The enumerator: for each first-parent commit in a window whose
   subject is `Merge pull request #N …`, compare `git log -1 --format=%b` on
   that commit against that pull request's `.title` and against the first line
   of its `.body`, and print the API failure count beside the result. Measured
   over `v6.5.0..c662274`, **16 of 20** merge bodies equalled the title and
   **0 of 20** contained the body's first line, 0 API refusals — and the
   `0` is the durable half: it was 0 at every base this was taken at, while
   the `16 of n` grows its denominator with every merge.

   **"By default" is load-bearing, not hedging.** A merger may supply the body
   at merge time, and **four** had by `c662274` — #1053, #1055, #1056 and
   #1057, each hand-written, one more than a day earlier. So the title is the
   surface to check, and it is not the only one; re-run the enumerator rather
   than reading either number off this page.

   **Why the grep form of this measurement is no longer sound**, which is
   point 2 biting its own evidence: searching `main`'s *concatenated* commit
   messages for a pull-request body's first line now finds branch commit
   messages too, because those land on `main`. The clearest case is **#1055**,
   whose seat wrote the same sentence in its commit message `a8ea8e4` and in
   its pull-request body; `a8ea8e4` is not first-parent, and the merge commit's
   own body does not carry that sentence.

   **This record states no count for the grep form, because it has none.** How
   many pull requests it "finds" is a function of how many leading characters
   of the body the search happens to compare, and nothing else. Over
   `v6.5.0..c662274`, comparing the first *n* characters of each body's first
   line against `git log --format=%B` for that window gives **6** hits at
   *n*=20, **2** at 30 and 40, **1** at 55, and **0** at 80, 120 and for the
   whole first line. The first draft of this record reported the *n*=55 answer
   as though it were the answer; a reviewer using a different prefix got 2 and
   could not reproduce it, which is how the defect surfaced. **Compare the
   merge commit's own body, not the history** — that measurement has no free
   parameter.

   So a closing keyword in a pull-request **title** now reaches `main` as a
   commit message, and a seat that writes `tools/audit/briefs/orchestrator.md`
   section 4's negated form into a title has the same problem the section was
   written for.

4. **That "squash-merge" is a safe synonym for "the merge".** It was, for as
   long as the two coincided. Text that uses it as one now instructs or asserts
   something false; text that recounts a specific past squash is still correct
   and is left alone.

## What stays true, and is worth writing down because it survived the change

- **The commit message reaches `main`; the pull-request body does not.** True
  under both methods, by the measurement in point 3 above. This is the
  method-independent reason a `--allow-regression` justification belongs in the
  commit message, and it replaces "the squash keeps the commit" wherever that
  was the reason given.
- **A commit that lands on `main` is a closing surface**, and GitHub discards
  the negation in it. The demonstration is `8bc4c661`, whose message says
  it does not shut #224 and which shut it anyway — the `closed` event on that
  issue carries `commit_id` `8bc4c661…`. That commit is itself a
  squash, so the mechanism was never about the method.
- **Ancestry of `origin/main` is the property that survives any merge method.**
  `tests/entities.py` already says so in as many words, above the
  `updated-for:` check.

## Consequences

- The seat instructions that said to squash are repaired in the pull request
  that lands this record: `.claude/workflows/web-fragments.md` and its four
  `web-*.js` copies (`fragments_sync.mjs` refuses drift between them, and prints
  the count itself: `across 4 script(s)`),
  `.claude/workflows/audit-merge.js`, and
  `tools/audit/briefs/orchestrator.md` section 4.
- `tools/audit/briefs/fixer.md` and `tests/structure.py` keep the instruction
  to put a re-record reason in the commit message, and lose the squash reason
  for it, per point 2 and the first bullet above.
- **Residual sites, named here rather than filed as an issue**, because a
  later seat reading this record is where they will be looked for. Each states
  the old mechanic in a place the pull request that landed this record judged
  out of its scope. **Cited by the sentence, never by the line**, for the
  reason point 3 gives about counts: a line number in a file under active edit
  is the same self-invalidating figure in a different shape, and these were
  written as line numbers first — six of them, correct at `d1a531b` and wrong
  the moment this branch's own 15 added lines to that file displaced them, in
  the commit that added this record. The enumerator that finds all of them
  wherever they have moved to, and which is the citation:

      git grep -nF -f - <<'PATTERNS'
      deleted by the squash that lands it
      branch is open and stays on it after the squash
      A ledger stamped from a branch head names a SHA the squash deletes
      a suffix-less squash is invisible
      A ledger stamped from HEAD names a SHA the squash deletes
      by the next --amend and deleted by the squash-merge that lands it
      and reachable from origin/main, so a squash cannot orphan it
      wrong even while it passes the check above, and a squash then deletes it
      PATTERNS

  **Run as given it returns ten hits, and two of them are not residual sites**:
  this bullet itself, which is unavoidable and harmless, and
  `docs/plan-2026-09-open-issues.md`'s `#616` row, which the first pattern also
  matches and which is *history* — a record of a merged pull request, correctly
  left alone under this record's own three-way rule. Stated rather than tuned
  away: a pattern narrowed until it matches exactly the set someone had in mind
  is the shape that later matches nothing and reports a confident zero.

  The first five hits are in `.claude/workflows/policy_lint.mjs` — the
  `recorded_at`
  provenance messages and two fixture-vacuous strings; the sixth is the same
  sentence in `tests/features.py`; the last two are in `tests/entities.py`, a
  check **name** and its failure message, a pinned surface with the
  method-independent statement already in the comment above them. Two more have
  no sentence worth grepping and are named by file: `.claude/workflows/carry-752.json`,
  whose brief uses "a squash" as the name for what `git merge-tree` simulates —
  the simulation it prescribes is right under either method, and the file is
  another seat's carry — and `docs/decisions/0003`'s closing sentence, *"none of
  the branch SHAs survives its squash, which is why this file cites none of
  them"*, a true account of why 0003 cites no SHA and a misleading rule read
  forward, since a branch SHA does now survive. Amending another decision record
  is its own act and is not done here. **None is a defect**: each describes a
  check or a procedure whose behaviour is unchanged. All are wrong as prose.
- **This list is a human reading, and nothing in the tree keeps it honest.**
  The pull request that landed this record sorted every tracked line matching
  `/squash/i` into live instruction, standing assertion, or historical record,
  and its enumerator's two assertions — that the three buckets sum to the
  population, and that every named line is in it — **cannot detect a
  mis-bucketing**, because the historical bucket is the residue and the sum is
  therefore true by construction. Its round-1 review proved that by dropping a
  live instruction out of the table and watching both assertions stay green,
  and then found two lines that had fallen through it (`main` squash-merges,
  and a prescription resting on the squash's three-way merge — both in
  `docs/plan-2026-09-open-issues.md`, both repaired in that pull request's
  round 2). A later seat re-running the enumerator gets the population and
  the buckets it is handed; the reading is what it must redo.
- This record is excluded from the policy corpus by name in
  `.claude/workflows/policy_lint.mjs`'s `CORPUS_EXCLUDED`, which is the line an
  ADR owes the moment a capped file cites it — and a capped file cites this
  one, which is the point. `docs/decisions/` is `@tvofi`'s in
  `.github/CODEOWNERS`.
