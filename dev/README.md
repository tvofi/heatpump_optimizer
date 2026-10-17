# Development in this repository

This is the orientation for a seat doing agentic development here: what lives
under `dev/`, which document binds which part of the work, the order the work
runs in, and what must be in place before a branch is pushed.

**This file is not policy.** `CLAUDE.md` is the index that names every policy
document and the obligation each carries; the named file is the policy, not
this summary. Where this README and a policy file disagree, the policy file
wins.

## The `dev/` layout

```
dev/
  governance/          canonical policy and the record of decisions
    rules/             the rule files (loaded by the harness through .claude/rules/)
    roles/             one contract per role: COMMON, fixer, fix-review, verifier, judge, ...
    dimensions/        D0.md .. D15.md, one brief per audit dimension
    decisions/         ADRs 0001-0013 (identity, merge boundary, verdicts, process)
    config/            policy_budgets.json, policy_known_bad.json, corpus exclusions
  programme/           plan of record, living state, and delivery record
    plan-2026-09-open-issues.md   the plan of record
    HANDOVER.md                   the one living handover (state, not policy)
    delivery/                     one row per pull request: <N>.md
    carries/                      forward-carry files: carry-<N>.json
    rosters/                      wave group rosters: wave-r<N>-groups.json
    register/                     the audit register: audit-2026-09.md
  audit/               audit evidence and re-runnable measurement
    config/            scopes.json, bugclasses.json, finding.schema.json, rotation.json
    harnesses/         re-runnable harnesses; its README.md indexes them
    rounds/            round<N>/D<k>/: reports, harnesses, .out runs and verdicts
    rca/               root-cause documents, R9-* and R10-*
    README.md          the harness contract and the instruments kept live
  archive/             retired plans, rosters, carries, handoffs and audits
```

`dev/archive/` is a record, not a work surface: nothing new lands there except
material being retired. `dev/audit/rounds/` is write-once evidence; a later
round adds its own directory rather than rewriting an earlier one.

## Governing documents

| document | where | one-line purpose |
|---|---|---|
| `CLAUDE.md` | repository root | the index: names every policy file, the obligation each carries, and the role or dimension it binds |
| `AGENTS.md` | repository root | the harness-neutral entry point for ZCode and Codex; it defers to `CLAUDE.md` and states no policy of its own |
| `tools/audit/seat/INSTRUMENTS.md` | `tools/audit/seat/` | the operator's guide to the seat instruments: what each does, when a lane reaches for it, and which refusal saves you (usage, not policy) |
| role contracts | `dev/governance/roles/` | one contract per role: `COMMON.md` (the finder's contract), `fixer.md`, `fix-review.md`, `verifier.md`, `judge.md`, `root-cause.md`, `orchestrator.md`, `nudge.md` |
| rules | `dev/governance/rules/` | the canonical rule files; `.claude/rules/*.md` is generated from them by `node tools/policy/rules_sync.mjs` and loaded when a read matches its `paths:` globs -- never edit the generated copy |
| dimension briefs | `dev/governance/dimensions/` | `D0.md` through `D15.md`, each in the owner's words: what the dimension measures and how |
| decisions | `dev/governance/decisions/` | ADRs 0001-0013: the identity split, the merge boundary, verdict authorship, and process decisions |
| audit contract | `dev/audit/README.md` | the harness contract, the evidence layout, and the instruments a judge still re-runs |
| suite manual | `tests/README.md` | what each gate script pins, how the scoped gate selects, and why a test that re-implements a production formula pins nothing |
| living handover | `dev/programme/HANDOVER.md` | durable state and corrections to the record; volatile state goes on issue #201 instead, never both |
| prose caps | `dev/governance/config/policy_budgets.json` | one-sided caps on the policy corpus: a policy file may shrink, never grow past its cap |

A rule file is canonical; `.claude/rules/*.md` and `.cursor/rules/*.mdc` are
generated for the harnesses. `node tools/policy/rules_sync.mjs --check` refuses
drift between the canonical rules and the generated copies, and
`node tools/policy/policy_lint.mjs` refuses dead citations and uncovered policy
directories.

## The work, in order

### 1. Audit: find, verify, judge

- **Find.** One finder seat per scope of `dev/audit/config/scopes.json`, against
  a pinned baseline. `dev/governance/roles/COMMON.md` is the finder's contract:
  a finding carries a claim, evidence, a harness, a metric, a perturbation and
  a null control, and a report missing any of them is not a finding.
- **Verify.** `dev/governance/roles/verifier.md`: one verifier per dimension,
  carrying three lenses over every finding. A refute sends the finding to the
  judge as `disputed`; it never kills it.
- **Judge.** `dev/governance/roles/judge.md`: dedup across dimensions, re-run
  each harness and its perturbation, and assign a class. A finding whose
  harness does not move under its own perturbation is `void`, whatever the
  votes said.

Evidence lands under `dev/audit/rounds/round<N>/`; causes under
`dev/audit/rca/`; the register is `dev/programme/register/audit-2026-09.md`.
`tools/audit/fold_ledger.py` folds a judge's output into
`dev/audit/config/bugclasses.json` and refuses a register that drifted.

### 2. Fix: fixer, adversarial review, verdict

- **Fixer.** `dev/governance/roles/fixer.md`. One pull-request group; a failing
  test first; a mutation proof; the finder's harness run at both ends; a null
  control for every quantified claim. The handoff freezes the branch.
- **Adversarial review.** `dev/governance/roles/fix-review.md`. A fresh context
  in a detached worktree at the head SHA, using the **finder's** harness, never
  the fixer's; the mutation proof is re-run and the claim files are compared
  with the actual drift.
- **Verdict.** The reviewer publishes through
  `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>`,
  which posts as the `hpo-approver` App, never the author App and never the
  owner's approving review.

### 3. Merge: the merge train

`tools/audit/seat/merge_train.py run` takes a queue file and lands verdicted
pull requests in order; `batch` is the batch form. Per pull request the train
recarries main, waits for every check at the head, carries the verdict,
confirms main is still contained, applies the policy decision, approves as
`hpo-approver`, and merges with `--match-head-commit`. It stops at the first
refusal, because every later pull request would be graded against a `main` the
refused one never joined.

### 4. Record

- The pull request's own row is `dev/programme/delivery/<N>.md`, written by the
  orchestrator through `tools/audit/seat/handoff_push.sh`; rows are updated at
  each merge, not at session end.
- `tools/audit/seat/state_docs.py` regenerates the three handoff state
  documents from a roster in one call.
- `dev/programme/HANDOVER.md` is updated in the same pull request as the merge
  it records. Volatile state (which seats are running, what a resumer does
  next) goes on #201 only.

### 5. Stamp

`tools/release/stamp.py` assigns the version, after the merge. A branch never
touches `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading.
The stamp pushes only over the deploy key.

## Requirements before you push

### Identity

- Pull requests are authored by the `hpo-author` App through
  `tools/pr/app_push.sh` (never `tools/pr/push.sh`, never `tvofi`);
  `pr-contract` refuses any other author.
- Verdicts are posted by the `hpo-approver` App:
  `tools/audit/seat/bus.sh push-verdict` and `tools/pr/app_comment.sh`.
  `tools/pr/app_approve.sh` approves a non-code-owned pull request on a
  `merge` verdict for that exact head.
- Only `@tvofi` reviews code-owned paths named by `.github/CODEOWNERS`. The
  approver App's approval is not that review.
- `tools/pr/approve_held_runs.sh` approves the workflow runs GitHub holds
  `action_required` after an App push, so the gate can start.

### Seat interpreter

`tools/audit/seat/seat_venv.sh` builds the reproducible seat interpreter under
`$HPO_STATE_DIR` (default `~/.local/state/hpo`): `venv-ci` from the CI pins and
`venv-ha` for the typing census. Install its shims first on `PATH`:

```
tools/audit/seat/seat_venv.sh
tools/audit/seat/seat_venv.sh --install-shims <seat bin dir>
```

`--check` reports what the venv holds. Do not run the gate on a system Python.

### Gate lease

`/tmp/hpo-gate.lock` holds two leases; `python3 tests/gate_lock.py needs-lease
<script>` says which a script takes. `lease` is exclusive and belongs to the
scripts that measure the machine (`tests/stress.py`, `tests/harness_headers.py`).
`slot` is a pool of four (`$HPO_HEAVY_SLOTS`) for the multi-minute CPU scripts.
Hold either by hand, never with `mkdir`:

```
python3 tests/gate_lock.py take --label <your-label>
python3 tests/gate_lock.py renew --label <your-label>
python3 tests/gate_lock.py release --label <your-label>
```

### Scoped gate

On a branch, run only what the diff can reach, against the merge base:

```
GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
```

`tests/closure.py` selects from the measured closures in
`tests/closures.json`; an unmeasured changed file, a missing closure, or a gate
file forces `MODE: FULL`. Read the `MODE:` line, never the script count: a
scoped run that selects nothing and a full run print the same `0`, and the line
does not exist at all on a push to `main`, where the gate is forced full.

### Classification and claims

- **Every new tracked file is classified.** It is in a measured closure (a test
  reads it) or on `tests/closure.py`'s `INERT` list (nothing in the gate reads
  it). Anything else is an orphan, and `tests/entities.py` fails with *"these
  force the FULL suite when touched"*.
- **A branch that claims no golden drift leaves `tests/golden/claimed_drift.txt`
  and `tests/golden/card_claimed_drift.txt` byte-identical.** A claim is
  value-bearing; `claims-for:` must equal `VERSION`, and a fixture cannot be
  both claimed and `may-drift`. Install the claim merge driver once per clone:
  `python3 tests/env_drift.py --install-merge-driver`.
- **The structural ratchet may only move down.** `tests/structure.py` measures
  every metric in `tests/structure_budgets.json`; pay by improving code, and
  re-record deliberately with the reason in the commit message.
- **A check that went red on your commits owes an answer** in the pull-request
  body: the cheaper detector that could have caught it, or a recorded finding
  that none exists.

Policy changes need the owner's approving review before they merge: the
documents `CLAUDE.md` names as policy (`CLAUDE.md` itself, the rule sources
under `dev/governance/rules/` and the generated `.claude/rules/`, the role
contracts under `dev/governance/roles/`, and the dimension briefs under
`dev/governance/dimensions/`). Open the pull request and surface it; a seat
cannot obtain that review for itself. `dev/programme/HANDOVER.md` is state, not
policy.
