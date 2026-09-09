---
description: What a sentence in the development record must carry to stay; README and user-facing docs are outside it
paths:
  - "docs/HANDOVER.md"
  - "docs/plan*.md"
  - "tools/audit/briefs/**"
  - ".claude/workflows/*-groups.json"
  - ".github/PULL_REQUEST_TEMPLATE.md"
---
# Every sentence earns its place

**Scope: the development record, not the product.** This governs what one agent
writes for another — pull-request bodies, issues, comments, commit messages,
briefs, roster entries, reports, and `docs/HANDOVER.md`, whose reader is a
resuming agent. It does **not** govern `README.md` or the rest of `docs/`: a
user did not run the command, cannot see the diff, and has no context to
supply, so they need the explanation this rule cuts.

**Precision outranks concision, always.** Where the two pull against each
other, precision wins and the artifact gets longer. **A short artifact missing
a control is a defect; cutting evidence is never compliance with this rule.** If
you are unsure whether something is filler, keep it — a redundant sentence costs
a reader a second, a dropped control ships a defect.

Given that: a sentence stays only if it carries a **measurement**, **the rule or
control behind one** (`fixer.md` step 8), a **decision and why**, a **constraint
on someone downstream**, or a **refusal and what refused it** — **and is the
only place in the artifact that carries it**. Everything else is cut, not
shortened: restating the ask, narrating the route, summarising your own diff,
preamble, and any adjective whose deletion changes no fact.

Uniqueness does the work a delete-and-see test cannot. A recap made of numbers
carries measurements, so no list of banned shapes reaches it; it is cut because
the numbers are already stated. An invariant whose terms are all on the page —
`views < fetch < dhw < grid < learning` — survives, because a reader can derive
the ordering and still not have been told it must hold.

## One living handover

"In the repo" and "always current" pull against each other: an in-tree file
needs a pull request to change, so it is structurally behind. Split the state
rather than asking one file to be both.

**Durable state goes in exactly one `docs/HANDOVER.md`** — no date in the name,
no second copy. Decisions and the measurement behind them, corrections to the
record, traps, owed work. It is updated **in the same pull request as the merge
it records**, riding the per-merge record obligation in
`delivery-status-tracking.md` so it costs no extra pull request, and its
`updated-for:` line names that merge. It links to the
Delivery-status table rather than restating it, and it names an instrument — a
metric, a cap, `--budgets` — never the figure that instrument prints.

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
