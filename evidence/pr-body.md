Roster for round 10, at the roster tip `1e9180dc9113b85354e5a03737f6dd4b9d4bb686` on `handoff/audit-r10-roster`: 95 commits over main `6fe5170cd7ce01e60ffebfc93e598c216e628fa3`, counted by kind under Figures. Part of #201. It closes nothing by keyword and leaves #201 open.

The pull request was cut as batch 22 at `b15f2633943e8be2ca9f2e7233b199f7c969b34c` and the branch has since taken batch 23, so this body describes the head it is pushed with. Two of the commits are the record beat: five delivery rows that still read `**open**` for merged pull requests (#2834, #2858, #2862, #2864, #2865) are flipped, and #2866's own row is added. Neither is hand-written; the flips come from `record_row.py --enumerate --plan --apply`, and the rows the generator exempts as record-class (#2856, #2863) are left alone.

### The ops, oldest first, by kind

- `roster_edit.py` (27):

```
09e8e857f roster_edit set-stage R10-ORCH-DISPATCH-REG (tools/audit/seat/roster_edit.py)
e1d772cdd roster_edit append-group R10-PLAN-PRIO (tools/audit/seat/roster_edit.py)
b15f26339 roster_edit append-group R10-STORE-RACES (tools/audit/seat/roster_edit.py)
c6c00b7bd roster_edit wire-issue R10-FLY-LEDGER-SAMPLE (tools/audit/seat/roster_edit.py)
d424c5d17 roster_edit wire-issue R10-FLOW-POSTMERGE (tools/audit/seat/roster_edit.py)
b5d8c338b roster_edit wire-issue R10-DEPENDABOT-SETUPTOOLS (tools/audit/seat/roster_edit.py)
65aec1b87 roster_edit set-after R10-RECORD-HOLD-APPROVE (tools/audit/seat/roster_edit.py)
ae4283ebc roster_edit set-after R10-ERREXIT-COUNTERMEASURES (tools/audit/seat/roster_edit.py)
87b08975c roster_edit set-after R10-HOUSE-GRADE (tools/audit/seat/roster_edit.py)
7ee0a54e1 roster_edit set-after R10-FLY-LEDGER-SAMPLE (tools/audit/seat/roster_edit.py)
cb0fda5fd roster_edit set-after R10-IMMERSION-LATCH (tools/audit/seat/roster_edit.py)
1f440eba4 roster_edit set-after R10-ADVISOR-WHATIF (tools/audit/seat/roster_edit.py)
81a622a9c roster_edit set-after R10-FLY-SUITE-ENV-FLAKES (tools/audit/seat/roster_edit.py)
11909994b roster_edit set-after R10-UX-HEALTH (tools/audit/seat/roster_edit.py)
336a11ff6 roster_edit append-carry R10-ORCH-BEATD (tools/audit/seat/roster_edit.py)
d764dd01b roster_edit append-carry R10-ORCH-REVIEW-PACKET (tools/audit/seat/roster_edit.py)
6bd810715 roster_edit append-carry R10-ORCH-REVIEW-PACKET (tools/audit/seat/roster_edit.py)
78bafe8be roster_edit append-carry R10-ORCH-REVIEW-PACKET (tools/audit/seat/roster_edit.py)
c3d17f0e5 roster_edit append-carry R10-ORCH-BEATD (tools/audit/seat/roster_edit.py)
0e1506e07 roster_edit append-carry R10-ORCH-BEATD (tools/audit/seat/roster_edit.py)
2adcc5287 roster_edit set-after R10-FLOW-BODY-ONLY (tools/audit/seat/roster_edit.py)
4d44dcbf0 roster_edit append-carry R10-FLOW-BODY-ONLY (tools/audit/seat/roster_edit.py)
071c715da roster_edit append-group R10-RECORD-HOLD-APPROVE (tools/audit/seat/roster_edit.py)
9fba58840 roster_edit append-carry R10-FLOW-BODY-ONLY (tools/audit/seat/roster_edit.py)
e85ed7ddf roster_edit append-carry R10-996-RUNNER-CLAIMS (tools/audit/seat/roster_edit.py)
28f827e58 roster_edit set-stage R10-996-RUNNER-CLAIMS (tools/audit/seat/roster_edit.py)
f7430f731 roster_edit set-stage R10-HOTFIX-BATCH-ERREXIT (tools/audit/seat/roster_edit.py)
```
- `roster_sync.py` (6):

```
46ef8448f roster_sync: derive stages from pull requests (tools/audit/seat/roster_sync.py)
d7c7f66fb roster_sync: derive stages from pull requests (tools/audit/seat/roster_sync.py)
561508e9a roster_sync: derive stages from pull requests (tools/audit/seat/roster_sync.py)
92b1be071 roster_sync: derive stages from pull requests (tools/audit/seat/roster_sync.py)
e6a19b022 roster_sync: derive stages from pull requests (tools/audit/seat/roster_sync.py)
3e5300557 roster_sync: derive stages from pull requests (tools/audit/seat/roster_sync.py)
```
- Issue wirings (6):

```
11b53fbd7 roster: wire #2271 (redaction on the owner's exported day) to R10-REPLAY-REAL-DAY
f4ff4cc13 roster: wire #2494 (merge-subject writer-scan residual) to R10-MERGE-SUBJECT-CASEARM, split from #2697
d880e8d3c roster: wire #2499 (plan vs relaxed DP overbook residual) to R10-BUFFER-STORE, whose carry holds it
5ad2092f7 roster: wire #2258 (envelope band residual, item 2c) to R10-HOUSE-GRADE
883139539 roster: wire #2260 (Health-tab learner hints residual) to R10-UX-HEALTH, brief item 5
a07420b26 roster: wire #2855 (carry-missing friction) to R10-RCA-FRICTION-RESIDUE, whose brief names the carry-missing key
```
- Group appends under the completion rule (tvofi, 2026-10-26 20:20Z) (6):

```
15168182b roster: append-group R10-DEPENDABOT-SETUPTOOLS (completion rule, tvofi 20:20Z)
9df0e4266 roster: append-group R10-ADVISOR-WHATIF (completion rule, tvofi 20:20Z)
12b594b51 roster: append-group R10-DIAG-AGES (completion rule, tvofi 20:20Z)
26e700952 roster: append-group R10-FRICTION-GATE-SCOPING (completion rule, tvofi 20:20Z)
ad18ee080 roster: append-group R10-FRICTION-MUTATION-SURVIVOR (completion rule, tvofi 20:20Z)
51060018d roster: append-group R10-FRICTION-REGRESSION (completion rule, tvofi 20:20Z)
```
- Orchestrator and seat resume, stage, carry and file edits (48):

```
1e9180dc9 roster: R10-CEILING-PROBE files widened to the seven its design names
8fa0c7e28 roster: R10-COP-GATE carries the learned top's consumer (design-verdict 3a261d86473f)
6d7b39bce roster: R10-UX-HEALTH carries forward item 8 of batch 23
7a0f1cb0c roster: R10-IMMERSION-LATCH carries forward item 7 of batch 23
2d52fd4de roster: R10-FLOW-JIDOKA carries forward item 6 of batch 23
1a12f0afa roster: R10-FLOW-JIDOKA carries forward item 5 of batch 23
8666d29d5 roster: R10-FLOW-JIDOKA carries forward item 4 of batch 23
c95dff979 roster: R10-FLOW-JIDOKA carries forward item 3 of batch 23
8b5342695 roster: R10-DIAG-AGES carries forward item 2 of batch 23
fd309e764 roster: R10-REPLAY-REAL-DAY carries forward item 1 of batch 23
5062425f9 roster: R10-CEILING-PROBE next step
5f1b633a5 roster: R10-CEILING-PROBE last step
eea8b07ed roster: R10-CEILING-PROBE branch
4b31cb075 roster: R10-CEILING-PROBE in progress, at its design revision
1be6eb056 roster: R10-FLOW-JIDOKA next step
e7013da0b roster: R10-FLOW-JIDOKA branch
0955bdcb7 roster: R10-FLOW-JIDOKA in handoff, at its p2 PR head
8bcbfb19a roster: R10-SAV-COMFORT next step
8cda5b450 roster: R10-SAV-COMFORT branch
d7abca50a roster: R10-SAV-COMFORT in handoff, at its PR head
c647b5317 roster: R10-HEAT-METER next step
4421f7c3c roster: R10-HEAT-METER branch
de6e3fb02 roster: R10-HEAT-METER in handoff, at its PR head
6de8d5611 roster: R10-ARCH-SHAPES next step
1fbea077b roster: R10-ARCH-SHAPES in handoff, at the handoff ref
dbaf9b59f roster: R10-ORCH-REVIEW-PACKET next step
bfd774597 roster: R10-ORCH-REVIEW-PACKET names the ref that carries its work
08f171177 roster: R10-ORCH-REVIEW-PACKET fixing, at its fixer's commit
de0354ada roster: R10-COP-PARTLOAD next step
09a1b6736 roster: R10-COP-PARTLOAD names the ref that carries its work
e2d15a48a roster: R10-COP-PARTLOAD fixing, at its fixer's commit
a90a36530 roster: R10-BUFFER-STORE next step
371521e29 roster: R10-BUFFER-STORE names the ref that carries its work
8f2dbdd2a roster: R10-BUFFER-STORE fixing, at its fixer's commit
01e12ca1d roster: R10-DIAG-AGES next step
46a276e3a roster: R10-DIAG-AGES names the ref that carries its work
9937317d8 roster: R10-DIAG-AGES fixing, at its fixer's commit
663d90d27 roster: R10-HOUSE-GRADE next step
29dd54640 roster: R10-HOUSE-GRADE names the ref that carries its work
160573f68 roster: R10-HOUSE-GRADE fixing, at its fixer's commit
6e3996e50 roster: R10-ORCH-DISPATCH-REG stage holds its --at-sha flag inside the value
7f5039478 roster: R10-CEILING-PROBE in-progress (fixer)
7427950d5 roster: R10-CEILING-PROBE design approved r2, carries 7-8
55a265413 roster: R10-CEILING-PROBE resume next_step
7a9a766b4 roster: R10-FLOW-BODY-ONLY resume next_step
1cd291cbb roster: R10-CEILING-PROBE needs design
09bbf7f0a roster: R10-CEILING-PROBE design-blocking findings (fixer seat, measured)
aa4a11e31 roster: R10-FLOW-ROSTER-FREEZE arms (a) #2792 and (b) #2779 merged; arm (b2) + review_freeze mutant R1 remain
```
- Record (2):

```
218bf4067 record: the merged rows for #2834 #2858 #2862 #2864 #2865
891085e9d record: the delivery row for #2866
```

## Head

`4180a7d01c3e8e4b34d746c4bccba452cf415d25` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2871.md`. The authored code head is `46df1de62c866cc72c55ebce287a78cd19fe249a`.

`3453cb819b5852cb1c8dd735c5a7aa84988fec97` merges origin/main `d620369fa` into the authored code head `46df1de62c866cc72c55ebce287a78cd19fe249a` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

The authored head is `1e9180dc9113b85354e5a03737f6dd4b9d4bb686`, the tip of `handoff/audit-r10-roster`. Its merge base with origin/main (`6fe5170cd7ce01e60ffebfc93e598c216e628fa3` at this reading) is `6fe5170cd7ce01e60ffebfc93e598c216e628fa3` itself, so the three-dot diff carries only this branch's commits. `git merge-tree --write-tree 6fe5170cd7ce01e60ffebfc93e598c216e628fa3 1e9180dc9113b85354e5a03737f6dd4b9d4bb686` prints the tree `8a25ac669cfe5f9352e5e20d35ca3e73ab39b23e` and no conflict.

The head the pull request is pushed at merges this tip into `fix/audit-r10-roster-pr`; the previous head `6f42fc12b066c93e91cf98764018725cb48623c0` merges the earlier tip `09e8e857f320002a1a521f13099ce5b5030690ec`, which this head contains.

`git diff --numstat 6fe5170cd7ce01e60ffebfc93e598c216e628fa3...1e9180dc9113b85354e5a03737f6dd4b9d4bb686` prints:

```
1       1       dev/programme/delivery/2834.md
1       1       dev/programme/delivery/2858.md
1       1       dev/programme/delivery/2862.md
1       1       dev/programme/delivery/2864.md
1       1       dev/programme/delivery/2865.md
1       0       dev/programme/delivery/2866.md
461     62      dev/programme/rosters/wave-r10-groups.json
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The roster blobs come from `git show <ref>:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin`: origin/main `6fe5170cd7ce01e60ffebfc93e598c216e628fa3` prints `53414799bdd5549578172f1c101f0ecd4807aed4`, the batch-22 head `b15f26339` prints `0886357f4d90a6fe489b4212d1e5b8cc1db047b5`, and this head prints `852ec7bdd3d719395863d021e4f0df17fb1b44f7`.

A script that loads both trees as JSON and keys groups by `group` printed `groups 199 208`, added 9 (R10-ADVISOR-WHATIF, R10-DEPENDABOT-SETUPTOOLS, R10-DIAG-AGES, R10-FRICTION-GATE-SCOPING, R10-FRICTION-MUTATION-SURVIVOR, R10-FRICTION-REGRESSION, R10-PLAN-PRIO, R10-RECORD-HOLD-APPROVE, R10-STORE-RACES), removed 0, and `changed 27`, each with the keys that moved: R10-996-RUNNER-CLAIMS (carry, resume); R10-ADVISOR-RESIDUE (resume); R10-ARCH-SHAPES (resume); R10-BUFFER-STORE (issues, resume); R10-CEILING-PROBE (carry, files, resume); R10-COP-GATE (carry); R10-COP-PARTLOAD (resume); R10-ERREXIT-COUNTERMEASURES (after); R10-FLOW-BODY-ONLY (after, carry, resume); R10-FLOW-JIDOKA (carry, resume); R10-FLOW-POSTMERGE (issues); R10-FLOW-ROSTER-FREEZE (resume); R10-FLY-LEDGER-SAMPLE (after, issues); R10-FLY-OPENPR-ATOMIC (resume); R10-FLY-SUITE-ENV-FLAKES (after, carry); R10-HEAT-METER (resume); R10-HOTFIX-BATCH-ERREXIT (resume); R10-HOUSE-GRADE (after, issues, resume); R10-IMMERSION-LATCH (after, carry); R10-MERGE-SUBJECT-CASEARM (issues); R10-ORCH-BEATD (carry); R10-ORCH-DISPATCH-REG (resume); R10-ORCH-REVIEW-PACKET (carry, resume); R10-RCA-FRICTION-RESIDUE (issues); R10-REPLAY-REAL-DAY (carry, issues); R10-SAV-COMFORT (resume); R10-UX-HEALTH (after, carry, issues). No other group moved.

`node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` from a fresh origin/main checkout exits 0 and prints `TOTAL: 0 error(s) across 1 file(s)`; `roster_edit.py` ran it behind every push above.

## Figures

`git log --no-merges --format=%s 6fe5170cd7ce01e60ffebfc93e598c216e628fa3..1e9180dc9113b85354e5a03737f6dd4b9d4bb686` prints 95 subjects; piping it through `grep -cE '^roster: wire'` prints 6, `'^roster: append-group'` 6, `'^roster: '` 60, `'^roster_edit'` 27, `'^roster_sync'` 6 and `'^record: '` 2.

`env -u BASH_ENV python3 -I tools/audit/seat/roster_sync.py --self-test` at this head prints `roster_sync self-test: 55 checks, 0 failed` -- the line `governance / instrument-self-tests` greps, run with the workflow's own command and `BASH_ENV` unset so the venv cannot make it pass vacuously.

The structural flag-text scan over every roster and carry file at this head (stage vocabulary and every `resume`, `files`, `after` and `issues` value) found no field holding command-line text. It found one before this batch: `resume.stage` of R10-ORCH-DISPATCH-REG held `done --at-sha bfc4a1e297fb2899be1c4643ae9d75b8a5829208` instead of `done`, with the sha already in `resume.commit`; `roster_edit.py set-stage R10-ORCH-DISPATCH-REG done --at-sha bfc4a1e2...` rewrote it as the two fields the tool means.

## Red checks

`governance / instrument-self-tests` is green at this head: `roster_sync self-test: 55 checks, 0 failed`, run with the workflow's own command. It was red at `6f42fc12b066c93e91cf98764018725cb48623c0` on the stage string this batch corrects (`dev/programme/rosters/wave-r10-groups.json:8207`, the `done --at-sha ...` value), and it now reads `55 checks, 0 failed`.

`pr-contract / pr-contract` was red at that head on the step "Check the body against the contract", because that red was not named in this section; its other steps passed. This section is that naming.

`gate` was red at that head only in its "Judge this head" step, which prints `FAIL pr-contract / pr-contract: failure (this run)`: it is downstream of the required checks at the same head and has no failure of its own.

No other check at `6f42fc12b066c93e91cf98764018725cb48623c0` concluded red; `hassfest`, `kernel-points`, the `tests` matrix, `governance`, `codeql` and `validate` were skipped there behind the failures above.

## Forward-carry

- Triage batch 35 accepted three proposals whose carries could not be appended to this branch: `roster_edit.py`'s triage gate refuses text citing a ruling the edit's base cannot read, and the batch-35 record lives only on `handoff/triage-s6-batch35` (`c73d8984a`), not on origin/main or this branch. The three destinations, and the work each owns, are: P199's dead-train detection in `orchestrator_tick.py`'s `train()` -- a no-end-line train dir flagged with its last log line and its open queue entries, the s60 shape (3 of 27 dirs) -- Carry: R10-FLOW-WIP; P200's four unstated verdict relay checks in `fix-review.md` (the probe ref shape, the subject, the first line's two accepted forms, the `ev/` directory), which must pay the file's 140/140-line cap by deletion -- Carry: R10-ORCH-REVIEW-PACKET; P203's `roster_lib.gate_kind`, which separates a gate covered by the mandate in force from one awaiting the owner, 34 of 34 covered at the reading -- Carry: R10-ORCH-ROSTER-SCHEMA. Each lands as that group's roster carry once the triage record is on main; the orchestrator owes the merge, then one `append-carry` per line.

## Friction

- roster-stage-derivation: stale: two `roster_sync: derive stages from pull requests` commits (`d7c7f66fb`, `46ef8448f`) landed on this branch inside the batch and re-derived `resume.stage` for every group with an open pull request from `handoff` back to `in-progress`; the reconciler owns that field, so the four groups with an open PR read `in-progress` and the commit, branch and next step this batch wrote sit untouched beside it. Carry: R10-ORCH-ROSTER-SCHEMA
- stage-flag-stored: unenforced: `roster_edit.py` stores its stage argument whole, so `set-stage G "done --at-sha <sha>"` writes the flag into `resume.stage` -- the shape `governance / instrument-self-tests` refused at `6f42fc12b`; a one-line validator refusing a stage that holds whitespace, or that is outside the derivable and protected sets, with two self-test arms, is the countermeasure. Carry: R10-ORCH-ROSTER-SCHEMA

