You are closing open issues in `tvofi/heatpump_optimizer` that do NOT belong to
the 2026-09 governance/policy programme. A separate session is rewriting the
policy corpus at the same time. Your two standing obligations are: **follow the
policy as it stands at the moment you act**, and **interfere with that session
minimally**.

## The policy is a moving target, and that is the point

A parallel session is merging policy changes continuously. `CLAUDE.md`, the
rules under `.claude/rules/`, the role contracts under `tools/audit/briefs/`, the
CI jobs and the pull-request body contract have all changed today and will change
again while you work.

So, before you open **each** pull request — not once at session start:

```
git fetch origin && git log --oneline -15 origin/main
git diff --name-only HEAD@{1} origin/main -- CLAUDE.md .claude/rules/ .github/workflows/
```

and re-read `CLAUDE.md` and any rule whose file changed. A rule you read an hour
ago may not be the rule that refuses you now. If a check refuses something you
believe is correct, **read the check** before arguing with it: in this repository
the refusal is usually right and the prose is usually the stale half.

## Scope

Work only on issues that are **not** part of the governance programme. The
governance work is tracked on **#201** and in the Delivery-status table of
`docs/plan-2026-09-open-issues.md`, which is authoritative where it and any issue
body disagree. Anything labelled `policy`, anything about `policy_lint`, the
corpus, the caps, the briefs, the hooks or the ADRs is not yours.

`CLAUDE.md`'s standing ruling binds you: **fix it; if you cannot, verify it
independently; only then file it.** Filing is not neutral — an issue enters the
Delivery-status table, needs a disposition, and is read by later seats as
established fact. Four issues filed in one day once needed three refutation seats
and a judge to establish that one was largely false.

## Paths to leave alone

Not because they are sacred, but because the other session is rewriting them and
a collision costs both of you a cycle:

```
docs/HANDOVER.md              <- AT ITS CAP, zero headroom. See below.
docs/decisions/**
.claude/**                    (rules, workflows, hooks, settings, skills)
.github/workflows/governance.yml
tools/audit/**
docs/plan-2026-09-open-issues.md   EXCEPT adding your own disposition row
```

**`docs/HANDOVER.md` deserves its own warning.** It sits at exactly its line cap
with zero headroom, and both prefixes involved are INERT, so the only thing that
measures it is a workflow that runs on the push to `main`. That means **two
branches can each be green alone and turn `main` red together** — which is
exactly what happened on 2026-09-07, leaving `main` red on `policy-docs` until a
later pull request cut the lines back. If you have something durable to record,
put it on **#201** and let the other session fold it in.

Everything else is yours: `custom_components/**`, `tests/**`, the golden
fixtures, `tests/structure_budgets.json`, `README.md`, the rest of `docs/`. The
governance queue touches **no production code at all**, so you cannot collide
there.

## Two things will change under you mid-flight

1. **A `PreToolUse` hook appears.** It refuses edits to `VERSION`, the manifest
   version, a `RELEASE_NOTES.md` heading off `main`, and anything under
   `.cursor/rules/`. All four are things you must not do anyway. It fails open on
   anything it cannot parse. When it refuses you, it is right — do not work
   around it.
2. **A `record` CI job appears.** From then on, every merged pull request must
   have its number appear in `docs/plan-2026-09-open-issues.md` or
   `docs/HANDOVER.md`, or the push to `main` goes red. **Start doing this now,
   before the job exists**, so nothing breaks when it lands.

   The check needs only the bare token. This is enough:

   ```
   - [#650](https://github.com/tvofi/heatpump_optimizer/pull/650) — merged, adds a thermostat schedule sensor.
   ```

   Add it in the pull request itself, naming your own number, which you know as
   soon as the pull request is open. It cannot run on the pull request — the
   commit is not on `main` yet — so a forgotten row turns `main` red *after* you
   merge. The remedy is one line, but you find out at the wrong end.

## The obligations that already bind you today

- **The scoped gate.** `GATE_SCOPE=auto` runs only what your diff can reach.
  `MODE: SCOPED — 0 script(s) run` and `MODE: FULL` both print zero and mean
  opposite things: key on the mode line, never the count.
- **The structural ratchet.** `tests/structure.py` measures every metric in
  `tests/structure_budgets.json`; several sit at zero headroom. Pay for the
  lines. Never loosen a budget quietly, and never delete working functionality to
  fit. A genuine new feature may raise one **only with the owner's explicit
  confirmation obtained before the branch is pushed** — stop and ask rather than
  push and explain.
- **Claim files.** Solver floats do not reproduce across BLAS builds. Compare
  three-dot (`git diff $(git merge-base origin/main HEAD)...HEAD`), never
  two-dot, which shows `main`'s own newer commits as if your branch made them.
- **Versions are assigned after the merge** by `tools/release/stamp.py`. Never
  touch `VERSION`, the manifest version or the `RELEASE_NOTES.md` heading in a
  branch — **and take no release stamp at all while the governance programme is
  running**, because two sessions stamping collide and the stamp has eleven
  refusal rules that will not save you from that one.
- **A new tracked file must be deliberately classified** — into a measured
  closure or onto `tests/closure.py`'s `INERT` list — or `tests/entities.py`
  fails.
- **`pr-contract` is live on `main` now.** Your pull-request body must carry
  these headings, each with content or an explicit `n/a: <reason>`:
  `## Head`, `## Mutation proof`, `## Null control`, `## Red checks`,
  `## Forward-carry`, `## Friction`. `## Head` must name the head SHA CI actually
  ran on, so **write the body naming the new commit before you push it**.

## Rebase, do not fight

`main` moves several times an hour. Rebase onto `origin/main` before every push.
Never rebase or force-push a branch that is not yours. If you hit a conflict in a
file on the leave-alone list, you are in the other session's lane — back out and
say so on #201 rather than resolving it.

## How to coordinate

**#201 is the live state**, and its newest comment wins. Post there when you
merge something, when you need a path on the leave-alone list, or when a
governance change breaks your work. Do not open a competing tracking issue.

If something the other session landed is wrong, **say so on #201 with the command
that shows it** — that session has been blocked twice today by exactly that and
both blocks were correct. A finding with a reproduction is welcome; an opinion
about the policy is not your lane.

## Start here

1. `git fetch origin && git checkout -B <your-branch> origin/main`
2. Read `CLAUDE.md` in full. It is the index; the rules it names are the policy.
3. Read the newest comment on **#201** for live state, and the Delivery-status
   table in `docs/plan-2026-09-open-issues.md` for what is done.
4. Pick one non-policy issue. Fix it, or verify it independently, or — last —
   file what you found.
