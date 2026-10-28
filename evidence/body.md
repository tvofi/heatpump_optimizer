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

Three rounds blocked on `carry-missing`; this cut replaces the body
(`fixer.md`, past three rounds).

- Round 1 (`aca91d7d1`, head `0f9a29e14`): A1/A2 were routed `Carry: #2733`,
  whose groups were done or absorbed. Answered: A1 and A2 sit on
  R10-FLOW-TOOLKIT-MODEL's carry (live, not-started), and the record's
  section 3 now names that group, not #2733.
- Round 2 (`94f8fa2b7`, head `0f9a29e14`): #2875's ownership and #2855's key
  were still `Carry: #2733`, and the record's sections 3 and 5 still said
  "#2733's". Answered: both items route to R10-ORCH-ROSTER-SCHEMA, which is
  live (carries-open) on handoff/audit-r10-roster and whose STRANDED-carry
  carry covers both. Both record sentences now name the live groups. Round 2
  also found the `## Red checks` answer wrong for `pr-contract`; it is
  corrected below.
- Round 3 (`d91a634f7`, head `73b1b4048`): `carry-2733.json` was a second
  destination for #2733. Answered: the file and its `tests/closures.json` entry
  are deleted (`633d4ec43`), and no item names it as a destination.

Dropped, and why:

- `dev/programme/carries/carry-2733.json` and its closures entry: contested in
  round 3, and not owed. The roster brief owes the record, not a carry file.
- The delivery row: it is the orchestrator's, not this seat's.
- Round history and every figure not re-taken in this pass. The record's
  figures are its own base's (`6eb552157`) and are labelled as such inside the
  record; they are not restated here.

Kept, and not contested: the record and its two evidence files, and the one
`bugclasses.json` `_rca` entry.

Non-blocking items taken in this cut: the record writes #2784's process state,
(c) per #2561 section 9 (round 1). The four open siblings #2429, #2436, #2437
and #2438 strand when this group goes done, as #2855 does; R10-ORCH-ROSTER-SCHEMA's
carry for #2855 names them too (round 3). For the orchestrator: that group's
STRANDED-carry carry names "carry-2733.json's two items" as first instances. That
file is deleted, so the instances are #2875 and #2855 themselves.
Carry: R10-ORCH-ROSTER-SCHEMA

## Head

`82a6ef4a1004d1c20fb0411bc4bee461a2015006` merges origin/main `beb570c81` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`2ee7cdc38e637ee435a8fbf154b768dece002c01` is the code head. It fast-forwards `633d4ec43` with a merge of
origin/main `beb570c81` (no conflict) and two commits to the record. The second
commit replaces the path `dev/governance/roles/root-cause.md` on the record's line 8
with the role's name. `ref_privacy` refused that path as a home directory on this seat,
whose home is `/root`. That is the substring false positive both earlier reviewers
reported, and dropping the path is the remedy the refusal itself prescribes. The merge base is `beb570c81`,
which is also origin/main at measurement (2026-10-28 18:29Z).

## Mutation proof

n/a: no check, test or production line changes. The diff is a record, two
evidence files and one register entry. The demonstrations A1 and A2 owe are
their fixers' (record section 3; R10-FLOW-TOOLKIT-MODEL's acceptance).

## Null control

- `rosterIssues()` with no argument indexes 1 issue. With
  `dev/programme/rosters` passed, it indexes 72 at `beb570c81`. The live-group
  arm is blind in production, which is A1's subject.
- The scoped gate on the unmodified closures: `MODE: SCOPED -- 0 script(s) run`.
  No changed file is in any measured closure.

## Figures

- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`:
  `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, four changed files.
- `node --input-type=module -e "import {rosterIssues} from './tools/policy/brief_lint.mjs'; console.log(rosterIssues().size, rosterIssues('dev/programme/rosters').size)"`:
  `1 72` at `beb570c81`.
- `python3 -I tests/structure.py`: `STRUCTURE RATCHET PASSED` at the head.
- `python3 -I tools/audit/carry_audit.py check --body <this body>`: the
  instrument's `CARRY-AUDIT` line, re-run by `prepr.sh`.
- `python3 -I tools/audit/fold_ledger.py check`: the instrument's summary and
  violation lines.

## Red checks

- `pr-contract` (and `gate` through it) at `1e917ac2`: the closes preflight
  refused all five `Closes` lines, because the group's `fixes` was empty at that
  run's base. It was not red only through `prelude`. A cheaper detector exists:
  `tools/pr/preflight.sh`'s closes check inside `prepr.sh`, which runs in seconds
  on the same roster arithmetic. It had already refused these lines locally. The
  red was the predicted result of the roster-write gap that record section 3
  names, and the orchestrator's roster edit repaired it.
- `prelude` at `1e917ac2`: GitHub API rate limit (`RATE-LIMITED`), transient.
  Cheaper detector: none. The repair is a re-run (HANDOVER trap 44).

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

