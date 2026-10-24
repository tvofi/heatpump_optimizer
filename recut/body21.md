Roster for round 10, twenty-first landing (after #2646, batch 20). It records the roster seat's ops since batch 20, each at the roster SHA where it landed (the list under Figures). Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

`2bb638af88f6373fe208dd2e57676dfac723bec8` merges the authored code head `85ac3ec14187f3509a9a9bfbae99a11747b02778` and then merges origin/main `a243a79f4` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`539725d11287fbbf3c1b438e08c45c42dce9314a` merges origin/main `a243a79f4` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head, and then adds one commit containing only this PR's own row, `dev/programme/delivery/2651.md`.

`b15fd62a39a1e17638a615d469a7162c52acdd57` merges origin/main `a243a79f4` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head, and then adds one commit containing only this PR's own row, `dev/programme/delivery/2651.md`.

The authored code head is `85ac3ec14187f3509a9a9bfbae99a11747b02778`, the tip of `handoff/audit-r10-roster`. Its merge base with `origin/main` `a243a79f4b97776e25063bb18a4c4c3062aa61b8` is `8de7e22ac38cebf0badbaa204e392b306b368ccd`, the roster head batch 20 landed. The diff against `origin/main` is one file, `dev/programme/rosters/wave-r10-groups.json`, 55 insertions and 7 deletions (`git diff --stat origin/main...85ac3ec14` prints them) over 10 commits (`git rev-list --count origin/main..85ac3ec14` prints 10), each one `roster_edit.py` op pushed after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code 8de7e22ac38cebf0badbaa204e392b306b368ccd a243a79f4b97776e25063bb18a4c4c3062aa61b8 -- dev/programme/rosters/wave-r10-groups.json` has rc 0: the roster on main equals the merge base, so nothing main wrote since is overwritten. The `removed` list below is empty.

## Figures

The 10 ops, by roster SHA (`git log --format='%h %s' origin/main..85ac3ec14` prints them):

- `83997aaee` drop-carry R10-CI-LAYOUT-P2: the carry saying `ci_critpath.py --drop-edge` "refuses rather than mixing two graphs", which is false.
- `f65126e9d` append-carry R10-CI-LAYOUT-P2: the corrected carry: a window that straddles a job-graph change refuses only when both jobs of the dropped edge still run; if either is renamed or removed the drop is a silent no-op (gain 0, rc=0) and the median mixes two graphs.
- `c539935a3` append-carry R10-CURRENCY: the O19 carry from #2620's Forward-carry (structure.py counts cross-seam attribute-reference occurrences, so an alias games seam_cut_total). Replaced by the next two ops to mark its fix-shape clause as roster-seat wording.
- `59c2ebc02` append-carry R10-LEARNER-ETA, `524d335a0` append-carry R10-UX-HEALTH, `1f27f9daf` append-carry R10-ARCH-DOCS: the three #2647 Forward-carry items, each prefixed "(from R10-SCORES #2647, Forward-carry)".
- `5141c2b38` set-stage R10-FLY-NO-FOOTERS done at `7deeef1b6b083b0fb5a8379717f3facd61897c6a` (#2636), an ancestor of origin/main.
- `85ac3ec14` append-group R10-FLY-NO-FOOTERS-EMITTERS: a new group, a follow-up of R10-FLY-NO-FOOTERS (after it), stage in-progress on branch `fix/r10-trailer-emitters`. `delivery_row.sh:40` and `stamp.py:2114` hardcode Co-Authored-By trailers that ref_privacy and policy_lint refuse since #2636; the brief says to remove them, pin each producer with a self-test row reusing ref_privacy's pattern, and sweep the producer class.
- `46604890b` drop-carry R10-CURRENCY and `85ac3ec14` append-carry R10-CURRENCY: the O19 carry re-appended with "Roster-seat wording, not #2620's" before its fix shape. Its final landing SHA is `7f9ffa703`.

Measured with `B=origin/main`, `H=85ac3ec14`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{nb:($B|length),nh:($H|length),removed:[$B|keys[]|select($H[.]==null)],new:[$H|keys[]|select($B[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'` prints 167 and 168 groups, none removed, 1 new (R10-FLY-NO-FOOTERS-EMITTERS) and 6 changed (R10-ARCH-DOCS, R10-CI-LAYOUT-P2, R10-CURRENCY, R10-FLY-NO-FOOTERS, R10-LEARNER-ETA, R10-UX-HEALTH). Groups by `resume.stage`, main then this head: done 90 then 91, in-progress 10 then 10, not-started 60 then 60, queued 6 then 6, absorbed 1 then 1. `node tools/policy/brief_lint.mjs` on the roster at `H` prints `TOTAL: 0 error(s)`, and `python3 tools/audit/seat/ref_privacy.py --check` at `H` prints `0 refused`.

## Red checks

Read 2026-10-23 from `repos/tvofi/heatpump_optimizer/commits/a243a79f4b97776e25063bb18a4c4c3062aa61b8/check-runs` (main's tip, 59 runs), failures, cancellations and timeouts only: 14 `rerun-stale-contract` runs, a check about re-run pull requests that this roster file does not touch. Checks at this pull request's own head are read by CI.

## Forward-carry

none

## Friction

none
