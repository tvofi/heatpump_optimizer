You are resuming the 2026-09 governance/policy programme in `tvofi/heatpump_optimizer`,
taking over from a cloud session that ran out of the privileges it needed. Read
`tools/audit/session-2026-09-08/HANDOVER-policy-programme.md` on the branch
`audit/handover-2026-09-08` first — it is the state, the queue, the traps and the
per-merge ritual. This prompt is only what you do before you read it.

**Re-measure everything.** Every SHA in that document goes stale within the hour
because the chain is rebased after each merge; prefer branch names. Three figures
in its predecessor were later measured false, which is why it says so.

## The first thing to settle, before you merge anything

**The policy-merge grant does not carry over.** `docs/decisions/0001-session-policy-merge-grant.md`
is scoped to the session that received it. You do not inherit it. Ask the owner
to re-grant it explicitly, or merge policy pull requests only with per-pull-request
owner approval. Merging under 0001 without that is the exact failure this audit
was called in to examine.

## Then

1. `git fetch --prune origin` and confirm the queue is intact:
   `audit/queue-06-hooks` → `07-loop` → `08-envmatrix` → `09-verdicts` →
   `10-adr-corpus`, plus `audit/session-evidence-2026-09-08` (an archive cut
   from an older main — never merge it).
2. Nothing is open. `main` is `03af74b` (#623), sixteen merges, no completed
   gate run ever failed.
3. Verify the chain-tip invariant on `queue-10`: `policy_lint` must report
   **76 pins across 10 check classes**. Fewer means the chain is mispointed, and
   that number is the only thing that has ever caught a mis-rebase.
4. Read the newest comment on **#201** for live state.

## What you can do that the previous session could not

Tag creation, branch deletion and ruleset creation were all proxy-refused in the
cloud container. Each is now available, and each has a condition:

- **Deletes:** `audit/queue-01`..`05` are merged and can go. Leave `06`..`10`,
  `session-evidence` and `handover-2026-09-08` until each is done with.
- **The ruleset: LAST.** Its payload is on #609. A required check that does not
  exist on `main` blocks every merge permanently, and `env-matrix` and `record`
  do not exist there until `08` and `07` land.
- **Tags:** a release tag resets the `record` window. Take no release stamp
  without the owner saying so.

## The trap that turns `main` red

`07-loop` lands a `record` job that refuses any merged pull request whose number
appears in neither `docs/plan-2026-09-open-issues.md` nor `docs/HANDOVER.md`.
**Build `audit/queue-06b-record3` between `06-hooks` and `07-loop`** carrying the
missing rows, and rebase `07/08/09/10` onto it. At handover the window held 28
merges with one missing. The handover document's appendix has the drafted rows.

## Standing discipline

One worker per role. Every pull request needs an adversarial fix-review verdict
at its own head SHA, from a seat that is not the author, working in a detached
worktree. If review seats keep dying the queue **stalls rather than loosens** —
tell the owner instead of merging unreviewed.

Exit status from the command, never from a pipe. Assert the occurrence count
before any string replacement. Derive a body's counts by mutating the artefact
and reading the detector — a count taken the easy way is this queue's recurring
defect, and it has been caught four times.

Never raise a cap to fit; pay by cutting.

## Note

A second session is closing non-policy issues in parallel. It has been told to
stay out of `docs/HANDOVER.md`, `.claude/**`, `docs/decisions/**`,
`governance.yml` and `tools/audit/**`, to add a disposition row per merge, and to
coordinate on #201. Its pull requests will move `main` under you; rebase and
re-point **by commit subject, never by position**.
