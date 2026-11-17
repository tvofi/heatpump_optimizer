R11-START-EVALUATION-LAND (part 3): revision 6 of the round-11 start evaluation, written as the round's evaluator. It answers the gaps `check_scopes.py --round 11` printed at main c82f014a63 that are the evaluation's own: a keep/change/remove verdict for the two dimension briefs pull request 3672 added after revision 4 (D16.md, D17.md), and `merged` on the nine accepted cards that pull request built (E11-U1, U2, U4 to U10). The diff touches only `dev/audit/yardstick/round11/EVALUATION.json`.

- D16.md and D17.md: `keep` on a NO-READ yield, because no round has run either dimension. Each row names the record that would read it (round 11's finder reports, read by `dimension_read.py --round 11` at the close), its builder, and its cost: three seats per round, the brief's line count, and token cost NO-READ until R11-PRE-TOKEN-LEDGER lands. Each row also gives the measured universe and checks the owed cells against the U cards.
- E11-U1, U2, U4 to U10: `merged` b98c78e0f6144a5ea5b48a032e30bf2d085c2d61 (pull request 3672). Measured at c82f014a63: the merge is on main's first-parent line; `git merge-base --is-ancestor b98c78e0f6 83dc9488180379b859042b5f24b87d94a5a02c95` is rc 1; `git diff --name-only b98c78e0f6^1 b98c78e0f6` names D16.md and D17.md. The paths_note condition holds because both briefs landed under the planned file names.
- E11-N-P744-SCOPE: untouched. Pull request 3658 is not merged at c82f014a63.
- `revision_6` block (of, by, why, changes, review_owed). No existing verdict, card `decision`, `ruling` or `gates_finders` moves, and `review` is unchanged.

Review owed: the objects now differ from those at the review sha 83dc948818, so check_scopes.py keeps printing `at review sha 83dc9488180379b859042b5f24b87d94a5a02c95 is missing or graded other objects than this record`. Only the evaluation reviewer can clear that line. The reviewer is a second seat the orchestrator dispatches at this handoff head, and clears the line by approving at a commit that holds these rows. This seat does not clear it.

check_scopes.py gap lines, base c82f014a63:

```
FAIL start evaluation round=11: 13 gap(s), 12 card(s) beside the finders
   dev/audit/yardstick/round11/EVALUATION.json at review sha 83dc9488180379b859042b5f24b87d94a5a02c95 is missing or graded other objects than this record
   dev/audit/yardstick/round11/EVALUATION.json has no keep/change/remove verdict for dev/governance/dimensions/D16.md
   dev/audit/yardstick/round11/EVALUATION.json has no keep/change/remove verdict for dev/governance/dimensions/D17.md
   dev/audit/yardstick/round11/EVALUATION.json card E11-N-P744-SCOPE is accepted and not merged at this ref
   dev/audit/yardstick/round11/EVALUATION.json card E11-U1 is accepted and not merged at this ref
   dev/audit/yardstick/round11/EVALUATION.json card E11-U10 is accepted and not merged at this ref
   dev/audit/yardstick/round11/EVALUATION.json card E11-U2 is accepted and not merged at this ref
   dev/audit/yardstick/round11/EVALUATION.json card E11-U4 is accepted and not merged at this ref
   dev/audit/yardstick/round11/EVALUATION.json card E11-U5 is accepted and not merged at this ref
   dev/audit/yardstick/round11/EVALUATION.json card E11-U6 is accepted and not merged at this ref
   dev/audit/yardstick/round11/EVALUATION.json card E11-U7 is accepted and not merged at this ref
   dev/audit/yardstick/round11/EVALUATION.json card E11-U8 is accepted and not merged at this ref
   dev/audit/yardstick/round11/EVALUATION.json card E11-U9 is accepted and not merged at this ref
```

At head 1f4a5e2fe7:

```
FAIL start evaluation round=11: 2 gap(s), 12 card(s) beside the finders
   dev/audit/yardstick/round11/EVALUATION.json at review sha 83dc9488180379b859042b5f24b87d94a5a02c95 is missing or graded other objects than this record
   dev/audit/yardstick/round11/EVALUATION.json card E11-N-P744-SCOPE is accepted and not merged at this ref
```

Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`: the measured closures reach no script from this data file. The run-always scripts still ran: `4 TEST SCRIPT(S) PASSED; 31 SCOPED OUT AND NOT RUN`, exit 0. CI is the authority.

## Head

`d11b0cb1b2835280259314ad69c8dfbfb8cd8d93` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

1f4a5e2fe75d274557ce68fb5570506638395867

## Mutation proof

n/a: record only. The diff changes a data record and no code, so there is no fix to break. The record's own mutation is the gap list: remove either new object row, or the `merged` on any U card, and `check_scopes.py --round 11` prints that gap line again, as it did at base.

## Null control

At head 1f4a5e2fe7 these lines are byte-identical to base c82f014a63 (`diff` of `grep` over both outputs, empty):
- `at review sha 83dc9488180379b859042b5f24b87d94a5a02c95 is missing or graded other objects than this record` (1 line)
- `card E11-N-P744-SCOPE is accepted and not merged at this ref` (1 line)
- the 12 `PARALLEL` lines
- every `ok D<n>` scope line (D0 to D17)

## Figures

<!-- figure-block: scope-line mb=5854e4f69e361d841d7590ae0f868eea6758655f head=d11b0cb1b2835280259314ad69c8dfbfb8cd8d93 -->
~~~text
MODE: SCOPED -- 0 script(s) run, 33 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

none
