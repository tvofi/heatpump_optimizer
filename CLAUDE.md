# Working on this repository

A session loads this file automatically. It exists because a resumability audit
found that every one of its auditors had to be *told* what to fetch before it
could work out what was in force.

Everything in this section is **permanent** — it describes the repository, not
any particular piece of work. Work in progress lives in the fenced block at the
bottom, which is scoped to one programme and deleted when it closes; it names
where the live state is and never restates it, so nothing in this file has a
date to go stale.

**This file is not the whole of what applies.** `.cursor/rules/*.mdc` hold the
`alwaysApply: true` project policies. Cursor loaded them for you; Claude Code
loads only this file, so **list that directory and open every rule in it at
session start** — do not work from a count or a list of names written here,
which goes stale the moment a policy is added. The sections below summarise
some of them and cite them by name; a summary is not the policy.

## Four rules that will refuse your pull request

1. **The gate is scoped by measured dependency closures.** `GATE_SCOPE=auto`
   runs only the scripts your diff can reach, decided from `tests/closures.json`
   rather than from anyone's opinion. A push to `main` forces `full`, and that
   asymmetry is the safety argument: if a closure is ever wrong, main goes red
   within one merge instead of never.
   **`MODE: SCOPED — 0 script(s) run` and `MODE: FULL` both print zero and mean
   opposite things.** Key on the mode line, never the count — but that line
   only exists on a branch; a push to `main` prints no mode line at all,
   because the forced `full` above never calls the code that prints it.
2. **A structural ratchet refuses growth.** `tests/structure.py` measures every
   metric in `tests/structure_budgets.json` — **derive the count, do not carry
   one**: it is the budget file's keys less `recorded_at`, which is metadata
   rather than a metric. This sentence said 22 for some time while the answer
   was 24, and `structure.py`'s own `ok` lines are a third number again (they
   include the counting-rule check and four `const.py` symbol checks). Every
   metric may only move down. Several sit at zero headroom, so a change that adds lines to the wrong
   class fails — and the correct response is to pay for the lines, to re-record
   deliberately with the reason **in the commit message**, or, for a genuine new
   production feature, to **raise the budget with the repository owner's
   explicit confirmation, obtained before the branch is pushed** — never to
   loosen a budget quietly, and never to delete working functionality merely to
   fit. Pay for the lines first; a raise is what you do when the honest answer
   is that you cannot, and an agent that wants one stops and asks rather than
   pushing and explaining. `cross_seam_fraction` is a tolerance metric and is
   never re-recorded.
3. **Value-bearing golden fixtures are claimed, not re-recorded.** Solver floats
   do not reproduce across BLAS builds, so only a canonical environment can
   honestly record one. Drift is declared in `tests/golden/claimed_drift.txt`
   (or `card_claimed_drift.txt`) with its direction, and `claims-for:` must equal
   `VERSION`. A fixture cannot be both claimed and may-drift — `env_drift.py`
   refuses that. Check claims — and any branch-vs-main comparison — three-dot
   (`git diff $(git merge-base origin/main HEAD)...HEAD`), never two-dot:
   two-dot shows main's own newer commits as if the branch had made them.
4. **Versions are assigned after the merge, by `tools/release/stamp.py`.** Never
   touch `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading in a
   branch. The stamp has its own refusal rules, including one that rejects notes
   omitting any merged PR.

A new tracked file must be **deliberately classified** — put in a measured
closure, or on `tests/closure.py`'s `INERT` list — or `tests/entities.py` fails
with *"these force the FULL suite when touched"*.

## Where the policy is — the whole set, and who each part binds

This file is the root, not the whole. Four other places carry rules, and a
session that reads only this one is missing three of them. **Read this section
first and open what applies to you**; nothing below is optional reading that a
seat may skip because a summary exists here.

### Always in force, for every session and every seat

`.cursor/rules/*.mdc` are `alwaysApply` project policies. **Cursor loaded them
automatically; Claude Code does not** — it loads this file and nothing else — so
they are reachable only by being opened deliberately. All five:

| rule | what it binds |
|---|---|
| `brief-citations.mdc` | wave-brief citations must be resolvable by `brief_lint.mjs`; a literal metric value is always an error; extending the plan format extends the linter in the same pull request |
| `ci-autofix.mdc` | `closures-autofix` and `claims-autofix` already repair `UNDER-SCOPED` and `INHERITED CLAIMS` — wait for the bot commit, do not duplicate |
| `defect-root-cause.mdc` | a defect that reached a release, or turned a PR red on a check a cheaper detector could have run, owes a cause, a process state and a countermeasure or a recorded refusal |
| `delivery-status-tracking.mdc` | Delivery-status, roster `resume`, and one #201 comment per state change — at each merge, not at session end |
| `finding-propagation.mdc` | a finding that changes how a later stage must work goes into that stage's own brief before the producing pull request merges |

### Role contracts — open the one you are

Under `tools/audit/briefs/`. Each says what its role owes and what blocks it.

| contract | the role |
|---|---|
| `orchestrator.md` | dispatches seats, merges, holds the freeze, writes the record, stamps, reports to the owner |
| `fixer.md` | owns one fix: failing test first, mutation proof, the finder's harness at both ends, a null control for every quantified claim |
| `fix-review.md` | reviews one fix adversarially, from a detached worktree at the head SHA, with the **finder's** harness and never the fixer's |
| `root-cause.md` | runs beside a fix and never inside it; owes a named cause, a process state, a cost test and a countermeasure or a refusal |
| `judge.md` | decides; a finding whose harness does not move under its own perturbation is **void**, whatever the votes said |
| `verifier.md` | one of three on a panel, receiving findings with claim, evidence, harness, metric and perturbation |
| `COMMON.md` | **the finder's contract** — every audit dimension. An argument is not a finding; a number you did not execute is not a finding |

**There is exactly one `COMMON.md`, and it is the finder's contract.** A running
session may also hand its seats an out-of-tree shared block; that file is named
`SEAT-BLOCK.md` and is **not** policy — it is a convenience copy, and the tree is
what survives the session. The two once shared a basename, which made "read
COMMON.md" ambiguous between a policy document and a session scratch file; the
out-of-tree one was renamed rather than the ambiguity documented, because a
collision a reader must resolve is a defect and not a note.

### Dimension briefs — the audit rounds

One per dimension, under `tools/audit/briefs/`, each carrying the owner's own
words for its scope. Named individually rather than as a range, because a range
reads as complete while covering a fraction — the defect this repository has
paid for more than once:

| brief | dimension |
|---|---|
| `D0.md` | price optimality |
| `D1.md` | robustness and stability — lifecycle, staleness, executor boundaries, store corruption, guards |
| `D2.md` | mathematical and physical sanity |
| `D3.md` | test-suite gaps |
| `D4.md` | UI/UX |
| `D5.md` | docs structure, flow and content; code comments |
| `D6.md` | README and documentation claim verification |
| `D7.md` | architecture and maintainability |
| `D8.md` | sensor verification and ordering |
| `D9.md` | CPU and memory efficiency, Raspberry-Pi-class target |
| `D10.md` | Home Assistant integration quality scale |

### The suite

`tests/README.md` — what each script pins, how the scoped gate selects, and why
a test that re-implements a production formula pins nothing.

### Changing any of it

Everything named in this section is **policy**: `CLAUDE.md`, every
`.cursor/rules/*.mdc`, and everything under `tools/audit/briefs/`. The owner's
approval is required before **merging** a change to any of them — not before
drafting one, so open the pull request and surface it. Every rewrite looks like
a correction from the inside; if the honest description is *"this changes what a
seat must do"*, it is policy however small the diff.

## Programme tracking (#201)

After each programme merge — wave group, tooling the plan tracks, or a closed
tracked issue — the same session or an immediate record PR updates
`docs/plan-2026-09-open-issues.md` Delivery-status (authoritative vs wave
body; if they disagree, fix the table first), the roster `resume` fields in
`.claude/workflows/wave-*-groups.json`, and posts one #201 comment per
meaningful state change (merge, block, wave start). Do not wait for a stamp
to truth the table. See `.cursor/rules/delivery-status-tracking.mdc`.

## Carrying a finding forward

**A finding that changes how a later stage must work is written into that
stage's own brief before the PR that produced it merges** — where the finding is
measured, with the null control that establishes it, and it narrows what the
later stage may do, invalidates an assumption it rests on, or removes an option
it was expected to have.

**A PR comment is not propagation.** The test is where the seat who needs this
will be looking: its own brief, its roster entry, this file, its role
contract — not the comments of a PR that merged several stages earlier. Carry
the control as well as the claim, and state the precondition rather than the
opportunity. A finding that constrains every seat goes in its role contract
under `tools/audit/briefs/` once;
one whose stage has no brief yet goes in the plan row that will become one, and
creating that row is part of the finding.

See `.cursor/rules/finding-propagation.mdc`.

## One living handover

"In the repo" and "always current" pull against each other: an in-tree file
needs a pull request to change, so it is structurally behind. Split the state
rather than asking one file to be both.

**Durable state goes in exactly one `docs/HANDOVER.md`** — no date in the name,
no second copy. Decisions and the measurement behind them, corrections to the
record, traps, owed work. It is updated **in the same pull request as the merge
it records**, riding the per-merge obligation above so it costs no extra pull
request, and its `updated-for:` line names that merge. It links to the
Delivery-status table rather than restating it, and it names a metric rather
than the number `tests/structure_budgets.json` already holds.

**Volatile state goes on #201** — which seats are running, which branches are
unpushed, what a resumer does next. Free to post at any moment, and it survives
an abort, which an unpushed in-tree edit does not.

**Nothing goes in both.** That is what non-redundant means here.

`tests/entities.py` enforces it: exactly one handover under `docs/`, and an
`updated-for:` naming a commit reachable from `HEAD`. Handover files are
deliberately *not* on `tests/closure.py`'s `INERT` list, so editing the living
one selects that script and adding a second forces `MODE: FULL` — either way
the refusal lands on the pull request rather than on the push to main. The
count is by path segment, not filename, so `docs/handovers/` is a second
handover too.

## Programme plans and the brief linter

Load-bearing citations go in `.claude/workflows/wave-*-groups.json` in a form
`node .claude/workflows/brief_lint.mjs` can resolve (that path is what #416
lands; run it locally the same way). The linter does not read `docs/plan-*.md`
or `tools/audit/briefs/`. Extending the plan format means extending the linter
in the same PR.

## Root-cause remediation

A defect that reached a released version, or that turned a PR red on a check a
cheaper detector could have run, owes two things beyond its fix: the cause, and
the **process** that let the cause get that far. The process failure is in one
of four states — the process did not exist, existed and was not followed, was
followed and did not work, or was sound and its preconditions changed — and the
countermeasure differs by state. Build one only when it pays for itself against
the measured recurrence of its class; **recording that none is worth building is
a legitimate result**. Any countermeasure that is a check must be demonstrated
failing on the defect it was written for.

The analysis runs in **its own seat**, beside the fix and never inside it:
`tools/audit/briefs/root-cause.md`. Policy is `.cursor/rules/defect-root-cause.mdc`.
Repository rules and policy change only with the owner's approval.

The red-check trigger is enforced, and only that one. The fixer names any check
its branch turned red in the PR body and answers there — the cheaper detector
and its standing cost, or the finding that none exists; the fix reviewer reads
the PR's checks before returning `merge`, and an unanswered one is
`blocked: root-cause trigger unanswered for <check>`. Naming the trigger is not
the analysis, which stays in its own seat.

## The contracts, when the work is a fix

- `tools/audit/briefs/fixer.md` — failing test first, importing the production
  symbol; the mutation proof pasted; the finding's own harness re-run at both
  ends; a null control for any cost, gain or time claim. After any rebase **or
  merge**, steps 2–4 are re-executed, because the evidence described a different
  tree. The handoff to review **freezes the branch**: update it from
  `origin/main` freely until then; after it, only the orchestrator moves the
  head.
- `tools/audit/briefs/fix-review.md` — the reviewer measures with the
  **finder's** harness, never the fixer's, in a fresh worktree at the head SHA.
  Four implementations here looked right and were wrong, one worse than its bug.
  The head is re-read before the verdict is posted, and one that moved under the
  review is `blocked: head moved under review, measured <sha>`.
- `tools/audit/briefs/judge.md` — a finding whose harness does not move under
  its own perturbation is **void**, whatever the votes said.
- `tests/README.md` — the suite, and why a test that re-implements a production
  formula pins nothing.

## Running it

`./tests/run.sh` is unscoped and long. On a branch, what you almost always want
is the scoped gate against your merge base:

```
GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
```

`/tmp/hpo-gate.lock` serialises anything that runs `tests/stress.py`, which
measures the machine while it solves and is wrong if something else is running.
Take it for a full or stress-selecting run; a scoped run that does not select
`stress.py` does not need it. Use `tests/gate_lock.py` — not `mkdir` and a
shell pid:

```
python3 tests/gate_lock.py take --label <your-label>
HPO_GATE_LOCK_LABEL=<your-label> GATE_SCOPE=auto GOLDEN_MODE=drift \
  GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
python3 tests/gate_lock.py renew --label <your-label>   # between commands
python3 tests/gate_lock.py release --label <your-label>
```

The owner file carries your label and an `expires_at` lease (30 minutes, above
the longest observed gate). Every script under lock renews it; an expired lease
or an abandoned hold (`holding` marker, no live flock) may be taken without
forensics. `run.sh` holds `flock` for the gate run so a crash drops flock and
a waiter can take immediately — the lease covers the window between commands
when nothing holds flock (#404).

Node lanes (`tests/card.mjs`, `tests/card_drift.mjs`) record on Darwin via
`node --import tests/node_fs_trace.mjs` (Node `fs` / loader, not `strace`).
`--single` of an existing node script **unions** into the committed list;
it cannot shrink a Linux `strace` closure. Python closures re-derive locally
as before. Do not Darwin `--single` a CI `UNDER-SCOPED` **while the autofix
job is green and its summary line says `changed`** — it already has the Linux
recordings and the commit is coming. Once that job goes red it has told you it
did not merge them, and re-deriving the script its summary names is then the
only thing that moves the PR. Green on `skip-not-allowed` is the third case:
the loop guard fired after the bot's own push, so no second commit is coming
either.

## CI already repairs two mechanical failures — do not re-implement them

`.github/workflows/tests.yml` jobs `closures-autofix` and `claims-autofix`
already exist on same-repo PRs. Do **not** open a second PR, run Darwin
`--single`, or hand-empty claim files for these. Wait for the bot commit
(`ci: re-record closures` / `ci: drop inherited claims`) and the dispatched
recheck. Loop-guarded: those subjects are not repaired again.

**Wait only while the job reports that it is repairing, and read the summary
line rather than the tick.** It pushes on one status and used to report
success on every other, so a job that repaired nothing looked exactly like one
that did (#523). It now ends by printing its status to the job summary and
going red when UNDER-SCOPED was printed and the repair did not happen —
`skip-failed-recording`, `skip-merge-failed`, `skip-still-fails`,
`skip-unchanged`. **A red autofix job means no bot commit is coming**, and the
rule above stops applying: re-derive the script the summary names. Green does
**not** mean a commit is coming — it covers `changed` (it is), `skip-clean`
and `skip-not-under-scoped` (nothing was owed) and `skip-not-allowed` (the job
never classified), and the conclusion cannot tell them apart. Two paths still
end green with a repair unmade; `.cursor/rules/ci-autofix.mdc` names both
rather than leaving completeness to be inferred.

- **`UNDER-SCOPED`:** `closures` already recorded under strace. Autofix
  merges those recordings into `tests/closures.json` and retriggers Tests.
  Policy: `closure.py` `apply_under_scoped_recordings`.
- **`INHERITED CLAIMS`:** a list identical to `origin/main`. Autofix deletes
  bare claim lines, keeps `claims-for:` and `# may-drift:`. Policy:
  `env_drift.py` `apply_inherited_claims`.

Not automated (still a human/agent judgment): golden drift, structure
budgets, `no-copies`, orphans → `INERT`, briefs lint, a failed recording,
an INERT contradiction. Do not add a third autofix job without a new
mechanical, uniquely-detected failure.

See `.cursor/rules/ci-autofix.mdc` and `tests/README.md` (scoped gate).

## Claim-file conflicts are prevented at the merge, not repaired after it

Every branch writes a note into `tests/golden/claimed_drift.txt` and
`tests/golden/card_claimed_drift.txt` at the same place, so every branch that
merged `main` after another branch merged conflicted in both — five branches,
ten conflicts, in one session. `.gitattributes` now routes both files to the
`claimnotes` merge driver in `tests/env_drift.py`. Install it once per clone;
a worktree shares its checkout's config, so one install covers every worktree:

```
python3 tests/env_drift.py --install-merge-driver
```

The driver unions the note comments and **refuses** — leaving ordinary conflict
markers and a non-zero exit — when both sides rewrote the bare claim list. The
refusal is the point. A claim is value-bearing, and git's free `merge=union`
would silently reinstate a claim the branch deleted, where the inherited-claims
guard cannot see it: that guard fires only on a list *exactly* equal to the
baseline's, and a unioned list carries the branch's own claim too.

Two limits, both measured. Git never clones config, so an uninstalled driver
falls back to the ordinary text merge — the same conflict as today, never worse.
And git reads `.gitattributes` from the branch being merged **into**, so a branch
cut before it landed conflicts once more before it is covered.

**GitHub is one of those uninstalled clones, and that one is not free (#570).**
`mergeStateStatus` is computed on GitHub's side, where the driver cannot run, so
every open pull request flips to `DIRTY` the moment `main` touches a claim file.
GitHub will not build a merge commit for a `DIRTY` pull request, and the
`pull_request` workflows never fire — such a PR does not go red, it **cannot
run**. A run already in flight survives; no new one queues. Merge `main` locally,
where the driver does run, and push. Before treating any conflict as real,
confirm it:

```
git merge-tree --write-tree origin/main HEAD
```

**So a branch that claims nothing does not touch the claim files at all.** The
note is a convention, not a requirement: `inherited_claims_error` compares the
parsed claim map, an empty list always passes, and no check anywhere reads a
note. A branch that leaves both files byte-identical to `main` cannot conflict,
and inherits whatever `stamp.py` last wrote to `claims-for:` — which is also how
you stop hand-editing that line wrong. Edit these files only when you are
actually claiming drift; there a conflict is meaningful, and rare.

**A third autofix job was measured and refused.** A merge conflict means CI never
ran, so no job is red and there is no uniquely-detected failure of the kind the
rule above demands; the trigger would have to be a push to `main` fanning out
over every open PR, and the repair would push to branches frozen for review.

<!-- ▼ PROGRAMME BLOCK. Everything below is scoped to one programme and is
     deleted when it closes. It carries no state of its own — only where the
     state is — so it cannot go stale while the programme is open. -->

## The open-issues programme

Tracking issue **#201**; its newest comment is the live state, and nothing in
the tree competes with it for that job.

Four places carry the rest, and each answers a different question. The plan of
record is `docs/plan-2026-09-open-issues.md`, whose Delivery-status table is
authoritative where it and a wave body disagree — so if that table looks stale
against #201, the table is the bug and fixing it is the first task.
`docs/HANDOVER.md` carries what the code cannot say: decisions and why,
corrections to the record, the traps a previous session hit, and owed work.
`.claude/workflows/wave-*-groups.json` hold the per-group briefs, each with a
`resume` field saying where it restarts — and a brief records what a judge
already **established and refuted**, so reading only the issue body will have
you implement a plan that was overturned. `docs/audit-2026-09.md` is the
evidence register the plan delivers against.

When this programme closes, delete this block. The sections above stand alone.
