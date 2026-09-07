# Working on this repository

A session loads this file automatically, and it is the **index**: it names every
policy file and the obligation each carries, and states in full only what no
other file states. It exists because a resumability audit found that every one of
its auditors had to be *told* what to fetch before it could work out what was in
force. The project policies live in `.claude/rules/` and the harness loads each
when you read a file its `paths:` globs match, so they arrive when they bind
without being opened by hand. A citation below is not the policy; the file is.

## Four rules that will refuse your pull request

1. **The gate is scoped by measured dependency closures.** `GATE_SCOPE=auto`
   runs only the scripts your diff can reach, decided from `tests/closures.json`
   rather than from anyone's opinion. A push to `main` forces `full`: if a
   closure is ever wrong, main goes red within one merge instead of never.
   **`MODE: SCOPED — 0 script(s) run` and `MODE: FULL` both print zero and mean
   opposite things.** Key on the mode line, never the count — but that line
   only exists on a branch; a push to `main` prints none at all, because the
   forced `full` never calls the code that prints it. Commands, the gate lease
   and the re-derivation trap: `gate-scoping.md`.
2. **A structural ratchet refuses growth.** `tests/structure.py` measures every
   metric in `tests/structure_budgets.json` — **derive the count, do not carry
   one**: it is the budget file's keys less `recorded_at`, which is metadata,
   and `structure.py`'s own `ok` lines are a third number again because they add
   the counting-rule check and the `const.py` symbol checks. Every metric may
   only move down, and several sit at zero headroom, so a change that adds lines
   to the wrong class fails. Pay for the lines; failing that, re-record
   deliberately with the reason **in the commit message**; and for a genuine new
   production feature, **raise the budget with the repository owner's explicit
   confirmation, obtained before the branch is pushed** — never loosen one
   quietly, never delete working functionality merely to fit, and stop and ask
   rather than push and explain. `cross_seam_fraction` is a tolerance metric and
   is never re-recorded.
3. **Value-bearing golden fixtures are claimed, not re-recorded.** Solver floats
   do not reproduce across BLAS builds, so only a canonical environment can
   honestly record one. Drift is declared in `tests/golden/claimed_drift.txt` (or
   `card_claimed_drift.txt`) with its direction, `claims-for:` must equal
   `VERSION`, and a fixture cannot be both claimed and may-drift — `env_drift.py`
   refuses that. Check claims — and any branch-vs-main comparison — three-dot
   (`git diff $(git merge-base origin/main HEAD)...HEAD`), never two-dot, which
   shows main's own newer commits as if the branch had made them. When to touch
   either claim file at all: `claim-files.md`.
4. **Versions are assigned after the merge, by `tools/release/stamp.py`.** Never
   touch `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading in a
   branch. The stamp has its own refusal rules, including one that rejects notes
   omitting any merged PR.

A new tracked file must be **deliberately classified** — put in a measured
closure, or on `tests/closure.py`'s `INERT` list — or `tests/entities.py` fails
with *"these force the FULL suite when touched"*.

## Where the policy is — the whole set, and who each part binds

Everything named here is **policy**, and so is this file. The owner's approval is
required before **merging** a change to any of it, not before drafting one — so
open the pull request and surface it. Every rewrite looks like a correction from
the inside; if the honest description is *"this changes what a seat must do"*, it
is policy however small the diff.

### The project policies, loaded when they bind

A rule about claim files arrives when you touch one and costs nothing otherwise.
`.cursor/rules/*.mdc` is the same text with Cursor's frontmatter, generated for
Cursor seats by `node .claude/workflows/rules_sync.mjs` and never a second
source; never edit it — `--check` refuses drift and an `.mdc` with no source.

| rule | what it binds |
|---|---|
| `brief-citations.md` | wave-brief citations must be resolvable by `brief_lint.mjs`; a literal metric value is always an error; extending the plan format extends the linter in the same pull request |
| `ci-autofix.md` | `closures-autofix` and `claims-autofix` already repair `UNDER-SCOPED` and `INHERITED CLAIMS` — wait for the bot commit, do not duplicate; read the summary line, not the tick; add no third job |
| `claim-files.md` | the `claimnotes` merge driver and its refusal; a branch that claims nothing leaves both claim files byte-identical; a `DIRTY` pull request does not go red, it cannot run |
| `defect-root-cause.md` | a defect that reached a release, or turned a PR red on a check a cheaper detector could have run, owes a cause, a process state and a countermeasure or a recorded refusal |
| `delivery-status-tracking.md` | Delivery-status, roster `resume`, and one #201 comment per state change — at each merge, not at session end; the table outranks any wave body that disagrees |
| `finding-propagation.md` | a finding that changes how a later stage must work goes into that stage's own brief before the producing pull request merges — a PR comment records it, it does not propagate it |
| `gate-scoping.md` | how to run the scoped gate, the `gate_lock.py` lease, and never a full `derive_closures.sh` off Linux — that path replaced the Linux recordings and cost one lane most of its closure |
| `writing-for-agents.md` | what a sentence in the development record must carry to stay; `README.md` and the rest of `docs/` are outside it; and the one living handover, durable in the tree against volatile on #201 |

### Loaded when a pull-request event arrives

`.claude/skills/steward/SKILL.md` — read before acting on a CI failure or a
review comment; only where this repository differs from a session's default, and
nothing in it loosens a rule stated here. There is deliberately no `babysit/`
counterpart: a session prefers `steward/` where both exist, so the second would
bind nobody and drift. `.claude/workflows/web-fragments.md` — the MCP mapping
for a seat whose container has no `gh` binary, the one policy file allowed to
name those commands.

### Role contracts — open the one you are

Under `tools/audit/briefs/`. Each says what its role owes and what blocks it.

| contract | the role |
|---|---|
| `orchestrator.md` | dispatches seats, merges, holds the freeze, writes the record, stamps, reports to the owner |
| `fixer.md` | owns one fix: failing test first, mutation proof, the finder's harness at both ends, a null control for every quantified claim; steps 2–4 re-execute after any rebase or merge, and the handoff to review freezes the branch |
| `fix-review.md` | reviews one fix adversarially, from a detached worktree at the head SHA, with the **finder's** harness and never the fixer's; a head that moved under the review is a blocked verdict |
| `root-cause.md` | runs beside a fix and never inside it; owes a named cause, a process state, a cost test and a countermeasure or a refusal |
| `judge.md` | decides; a finding whose harness does not move under its own perturbation is **void**, whatever the votes said |
| `verifier.md` | one of three on a panel, receiving findings with claim, evidence, harness, metric and perturbation |
| `COMMON.md` | **the finder's contract** — every audit dimension. An argument is not a finding; a number you did not execute is not a finding |

**There is exactly one `COMMON.md`, and it is the finder's contract.** A running
session may also hand its seats an out-of-tree shared block, named
`SEAT-BLOCK.md`; that one is **not** policy but a convenience copy, renamed out
of a shared basename rather than the ambiguity documented, because a collision a
reader must resolve is a defect and not a note.

### Dimension briefs — the audit rounds

One per dimension, under `tools/audit/briefs/`, in the owner's own words. Named
individually, because a range reads as complete while covering a fraction:

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

### The suite, the register, the handover

- `tests/README.md` — what each script pins, how the scoped gate selects, why a
  test that re-implements a production formula pins nothing.
- `tools/audit/README.md` — how a round is run and where its evidence lands.
- `docs/HANDOVER.md` — the single durable handover; its rules and the split
  against #201 that keeps it non-redundant are in `writing-for-agents.md`, and
  `tests/entities.py` refuses a second one anywhere under `docs/`.

## Fix it; if you cannot, verify it independently; only then file it

The owner's ruling, and it binds **every seat**, not only the orchestrator. The
order is a fallback chain rather than a menu.

An issue is what you write when you cannot act, not a way of recording that you
noticed. Filing is not neutral: an issue enters the Delivery-status table, needs
a disposition, and is read by later seats as established fact — it propagates
further than a wrong pull request, because nothing gates it. Four issues filed
in one day needed three refutation seats and a judge to establish that one was
largely false and that a mechanism another asked for was already in the tree,
landed by a pull request listed in its own evidence table.

**A recurring error is not a third issue.** At roughly the third instance it is
`tools/audit/briefs/root-cause.md`, whose product is a named cause, a named
process state, a cost test with numbers, and a countermeasure *or a recorded
decision not to build one*.

**Out of scope is not a licence to file.** A real finding you must not touch
goes to that stage's own brief, by `finding-propagation.md`; an issue is not
the instrument for propagation.

This rule is stated here and again in `tools/audit/briefs/orchestrator.md`
section 8. That duplication is deliberate and is the owner's call: it binds every
seat, so it belongs where every seat reads, and it binds the orchestrator
hardest, so it belongs in that contract too. **If the two ever disagree, this
one is the rule** and the other is the bug.

## Root-cause remediation

A qualifying defect owes its cause and the **process** that let the cause get
that far, established in its own seat beside the fix and never inside it. The
two triggers, the four process states, the cost test, why recording that no
countermeasure is worth building is a legitimate result, and the demonstration a
check-shaped countermeasure owes are in `defect-root-cause.md` and
`root-cause.md`. Only the red-check trigger is enforced: the fixer names the
check in the pull-request body and answers it there, and the fix reviewer
returns `blocked` on one the body left unanswered.

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
