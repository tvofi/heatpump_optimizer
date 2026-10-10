Fix review: merge 31f325e03f05609edf55bced84b1a9acee1671c6

bus-nonce: 7005ecbab55b429eb9dd9bb93d2f1c4c

Round 1 of this PR (no prior verdict on #2116). Everything below is measured at
**31f325e03f05609edf55bced84b1a9acee1671c6**, which was still
`refs/heads/fix/r9-bus-fetchhead` at publish time and is the sha the body's
`## Head` names; merge base 7cd5a588c. Contract read from `origin/main`
(`dev/governance/roles/fix-review.md`); `tools/audit/briefs/fix-review.md` does
not exist on `origin/main`, so the role contract plus the group brief on
`handoff/audit-r9-fixplan` (`.claude/workflows/wave-r9-groups.json`, group
R9-RC-BUS-FETCHHEAD) were the contract. All arms ran on COPIES with
`HPO_BUS_STATE` in scratch, against a throwaway bare origin; the live bus state
was not touched and no ref was pushed to the real origin.

## What the parent is now, exactly

`append_commit()` takes the parent from `$tip`, the sha `git ls-remote` answered
for `refs/heads/<fam>/<pr>`, captured into a shell local **before** the fetch:

    tip=$(git ls-remote "$REMOTE" "refs/heads/$fam/$pr" 2>/dev/null | awk 'NF { print $1; exit }')
    ...
    [[ $tip =~ ^[0-9a-f]{40}$ ]] || refuse
    git fetch -q "$REMOTE" "refs/heads/$fam/$pr" || refuse      # objects only
    parent="-p $tip"

`git ls-remote` writes no per-worktree state, and a shell local cannot be
rewritten by a concurrent fetch, so the parent no longer depends on `FETCH_HEAD`
at all. `git grep -n FETCH_HEAD 31f325e03 -- .` leaves only comments in the
instrument's production path; the one executable read is the new self-test's own
precondition assertion (`bus.sh:655`). The original `--exit-code` existence test
is also improved: a failed `ls-remote` now refuses instead of silently building a
parentless commit.

## RESULT lines

RESULT own-arm(base 7cd5a588c) appends=60 ok=39 refused=21 reparented=0 unreachable_built=6
parented_on_main_tip=6
RESULT own-arm(head) appends=60 ok=60 refused=0 reparented=0 unreachable_built=0
parented_on_main_tip=0
RESULT own-arm(base) refusal shapes: non-fast-forward push, and `fatal: ambiguous
argument 'FETCH_HEAD'` (the orchestrator's second shape)
RESULT race(base) push-verdict rc=1, built parent c723b3b10 = main's tip != review/21 tip 012eb79c7
RESULT race(head) push-verdict rc=0, built commit 9ae1b977c parent b8701f138 = review/21's tip
RESULT append(base) and append(head): 903ff5f3d / ec4bbbdc9 / tree c7d7c97b3, `diff` empty —
byte-identical (null control holds at both ends)
RESULT ootree(base) verdict/21 moved with 0 poster calls — HALF-APPLIED
RESULT ootree(head) nothing pushed, nothing posted
RESULT bodypush(base) parent 0c8080f83 (decoy) != A's tip 436b13d2f; bodypush(head) parent = A's tip
RESULT handoffpush(base) published "BODY MARKER B"; handoffpush(head) published "BODY MARKER A"
RESULT self-test(7cd5a588c) 45 checks, 0 failed
RESULT self-test(31f325e03) 48 checks, 0 failed
RESULT self-test(31f325e03 under /bin/bash 3.2.57) 48 checks, 0 failed
RESULT self-test(5bd9385fc, arms-first) 48 checks, 2 failed — exactly the two new arms (46 pass)
RESULT M1 (`parent="-p $tip"` -> `parent="-p $(git rev-parse FETCH_HEAD)"`) 48 checks, 1 failed,
the named arm and nothing else
RESULT M2 (poster-guard line deleted) 48 checks, 1 failed, its named arm
RESULT baseline export without `.git`: self-test 48/0 and the race arm green (the guard's null control)
RESULT check-runs at the head: 40 runs, no red (2 in_progress: Analyze (python), coverage)
RESULT class census `git grep -n FETCH_HEAD 7cd5a588c -- . | grep -v '^dev/audit/rounds/'`: 5 seams
(tests.yml:3117, body_push.sh:20, bus.sh:150, handoff_push.sh:40, handover_prompt.py:94) — each in the
diff or dispositioned
RESULT MODE: SCOPED -- 0 script(s) run, 33 scoped out; same 5 files as the body
RESULT STRUCTURE RATCHET PASSED; layout self-test ok; env_drift --all: no unclaimed drift, no stale
fixture; VERSION/manifest/notes untouched; merge-tree vs origin/main rc 0

## Answers to the adversarial questions

1. **FETCH_HEAD dependence removed?** Yes, for the parent — see above. The fetch
   that stays cannot reparent anything; if the ref moves after the answer the
   push is refused, which is a retry.
2. **Original failure reproduced?** Yes, twice, and the arm is mine, not the
   fixer's (the finding #2092 carried no committed harness — a narrative
   measurement — so I disclosed my own instrument and also ran the PR's). Mine
   injects nothing: a real concurrent fetch loop in the same checkout while the
   script appends 60 times. Baseline: 21 refusals, 6 commits parented on main's
   tip, both measured refusal shapes. Head: 0 of each, 60/60 landed. The race is
   timing-dependent, so I report counts over 60 appends rather than one
   deterministic run; the structural reason the head cannot lose is the captured
   `$tip` local.
3. **`--self-test` and a new arm?** 48/0 at the head, 45/0 at the merge base.
   Three new cases (the intervening fetch, the null control, the out-of-tree
   copy), red on the arms-first commit and killed by M1/M2; plus two sibling
   arms in `r9_rc_bus_fetchhead.sh`. Driven in CI by `governance.yml:332`.

## Disclosed, non-blocking

- `handover_prompt.py:94` is dispositioned "not this class" in the census, yet it
  instructs a seat to `git fetch origin <branch> && git worktree add --detach
  $SEAT/wt FETCH_HEAD` — the fetch-then-read shape, in one command by the same
  writer. Dispositioned, so not `class-open`; worth the follow-up lane's eye.
- `bus.sh` refuses when `ls-remote` fails; `body_push.sh` degrades to `|| tip=""`.
  A sibling inconsistency in strictness, disclosed here rather than blocking.
- The poster guard is a new fail-closed refusal at load in a live instrument:
  every subcommand now needs the derived (or `HPO_BUS_POSTER`) poster to be
  executable. I verified the checkout, the export without `.git`, and
  `HPO_BUS_POSTER`-set copies all pass, on bash 3.2 and in CI.
- Not re-derived by me: the body's local "12 of 109" harness-header figure
  (`tests/harness_headers.py` cannot import here — `tests/harness.py` needs
  `homeassistant`; it is not a CI check), its `ci_predict` figure for the un-taken
  `dev/audit/harnesses/` placement, and the run-specific shas in its arm tables
  (each run mints its own nonce, as the body says).

Forward-carry: the live instance is in R9-RO-10's brief on
`handoff/audit-r9-fixplan` ("A LIVE INSTANCE, 2026-10-10: the corpus itself names
a retired path..."), and the two cited policy lines do name the retired path
(`CLAUDE.md:150`, `fixer.md` step 18). Friction `none`.
