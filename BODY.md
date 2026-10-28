The root-cause record for the friction residue #2561 left unmeasured. It lands
no production code and no policy file. It measures the group's keys at its
merge base and gives each closed issue a named cause, a process state, a cost
test and a countermeasure or a recorded refusal; the open keys' countermeasures
are drafted and routed below.

Closes #2410
Closes #2593
Closes #2597
Closes #2660
Closes #2784

#2429, #2436, #2437, #2438 and #2855 stay open: their countermeasures are
drafted and routed, not landed.

## Re-cut

Round 4 (`17dc8769b`, head `82a6ef4a1`) blocked on one item: a conflict on
`dev/audit/config/bugclasses.json` with origin/main `b6f6ceca4`. It disputed
nothing else. A conflict with main is resolved by merge, never a re-cut
(`fixer.md`, step 6), so this pass is a merge plus this body; the diff's
content is unchanged apart from the resolved file.

- **Answered: the conflict.** `7cda20df8` merges origin/main `b0b2d7697` into
  `82a6ef4a1`. Both sides appended one `_rca` entry after
  `R10-N-vocabulary-drift`; the resolution keeps both, `R10-RCA-CLOSURE-ARGV`
  (main) and `R10-RCA-FRICTION-RESIDUE` (this branch), with main's bytes
  otherwise identical. It also restores the file's trailing newline. Without
  it `ledger_merge._format` reads no side as the writer's format and refuses
  every concurrent edit of this ledger, which is what turned this race into a
  hand conflict (the verdict's instrument finding). With it, the file
  round-trips as `{'indent': 2}` under `_format`.

Kept, and not contested in round 4: the record and its two evidence files, and
the one `bugclasses.json` `_rca` entry. Dropped earlier and still dropped:
`carry-2733.json` and its closures entry. The delivery row in the diff is the
orchestrator's, not this seat's.

For the orchestrator (round 4, non-blocking): R10-ORCH-ROSTER-SCHEMA carry[24]
still names "carry-2733.json's two items" as the STRANDED report's first
instances. That file is deleted; the instances are #2875 and #2855 themselves.
Carry: R10-ORCH-ROSTER-SCHEMA

## Head

`7cda20df866c0d2e94395ea030ce1f2587993ecc` is the code head: a merge of
origin/main `b0b2d7697` into the previous head `82a6ef4a1`, resolving
`dev/audit/config/bugclasses.json` as described in `## Re-cut`. The merge base
is `b0b2d7697`, which is also origin/main at measurement (2026-10-28).

## Mutation proof

n/a: no check, test or production line changes. The diff is a record, two
evidence files, one register entry and the orchestrator's delivery row. The
demonstrations A1 and A2 owe are their fixers' (record section 3;
R10-FLOW-TOOLKIT-MODEL's acceptance).

## Null control

- `rosterIssues()` with no argument indexes 1 issue. With
  `dev/programme/rosters` passed, it indexes 72 at `7cda20df8`. The live-group
  arm is blind in production, which is A1's subject.
- The scoped gate on the unmodified closures: `MODE: SCOPED -- 0 script(s) run`.
  No changed file is in any measured closure.

## Figures

All re-taken at `7cda20df8` in this pass.

- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`:
  `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, five changed files (the
  three-dot diff's `--name-only` count).
- `node --input-type=module -e "import {rosterIssues} from './tools/policy/brief_lint.mjs'; console.log(rosterIssues().size, rosterIssues('dev/programme/rosters').size)"`:
  `1 72`.
- `python3 -I tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 -I tools/audit/fold_ledger.py check`: `127 rca entries`,
  `0 violation(s)` (126 before main's `R10-RCA-CLOSURE-ARGV` came in).
- `python3 -I tools/audit/carry_audit.py check --body <this body>`: the
  instrument's `CARRY-AUDIT` line, re-run by `prepr.sh`.

## Red checks

- None at `82a6ef4a1` but `gate` 123069364626 in `CI code`, whose only verdict
  line is a deferral (`FAIL run(s) [...] at this head are still being judged;
  their gate decides`); the edit run's `gate` printed `PASS` and
  `pr-contract` was green after it (round 4's evidence). No cause to answer;
  cheaper detector: none needed.
- `prelude` at `1e917ac2` (an earlier head of this PR): GitHub API rate limit
  (`RATE-LIMITED`), transient. Cheaper detector: none exists; the repair is a
  re-run (HANDOVER trap 44), and `prelude` is green at `82a6ef4a1`.

## Forward-carry

- **A1, the roster index.** `rosterIssues()`'s no-argument path reads
  `roster_lib.ROSTERS_DIR` as well, so the live-group refusal fires in CI; the group's carry is in
  `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-FLOW-TOOLKIT-MODEL
- **A2, the merge-time fold.** The orchestrator writes each `Carry: <GROUP>`
  body item's id into the destination group's brief before merging, with the
  post-fold id assertion. Carry: R10-FLOW-TOOLKIT-MODEL
- **The derived `other (untaught)` friction family** in `statsFamilies` (`tools/policy/policy_lint.mjs`).
  Carry: #2436
- **The `root-cause` family** (`root-cause-unanswered`, `root-cause-detectable`,
  `root-cause-unrecorded`) in the same map. Carry: #2437
- **#2479's cross-run count** comes from the record's section 5. Its policy
  sentence is the owner's. Carry: #2437
- **#2875 is unowned**: an open friction issue that no roster group lists. That
  is the subject of the STRANDED-carry report. Carry: R10-ORCH-ROSTER-SCHEMA
- **The ci-autofix wait bound and the measured-pin rule**, after the owner's
  approval, in `.claude/rules/ci-autofix.md`. Carry: #2429
- **The carry-control enumerator lint** in `brief_lint`, and the sentence that a
  ruling's destination is a `Carry:` marker, in `tools/policy/brief_lint.mjs`
  and `dev/governance/roles/`. Carry: #2438
- **#2612's row** is dispositioned by the record's section 8 as section 3's
  cause. Carry: #2438
- **#2855's key** is dispositioned in the record. The mechanism that keeps a
  disposed key from stranding is the routing audit's, and the same carry names
  #2429, #2436, #2437 and #2438. Carry: R10-ORCH-ROSTER-SCHEMA
- **#2452's census cost** is a recorded refusal. Carry: dismissed: cheaper census is the spelling list that failed

## Friction

- `rounds.py`: unenforced: the group's brief names `rounds.py --stats`, which is not a mode; the invocation exits 0 with zero bytes and would read as a measurement (record section 1). Carry: R10-ROUND-PLAYBOOK
- `brief_lint`: unenforced: rosterIssues() with no argument never reads dev/programme/rosters (1 of 72 indexed at beb570c81), so a carry file at a covered issue is accepted. Carry: R10-FLOW-TOOLKIT-MODEL
- `policy_lint.mjs`: unclear: the threshold's unit is the class spelling, so many untaught words over many PRs aggregate to no filing (record section 4). Carry: #2436
- `ci-autofix.md`: unclear: "wait for the bot" has no terminating condition when the bot's own job stalls (record section 7). Carry: #2429
- `finding-propagation.md`: unenforced: the producing seat cannot write the destination brief (record section 8). Carry: #2438

