`tools/audit/seat/bus.sh` built the parent of every commit it appends on
`FETCH_HEAD`. `git fetch` rewrites `FETCH_HEAD` as per-worktree state of the
checkout it runs in, so anything else fetching in that checkout between the
script's own fetch of the bus ref and its read of the tip -- a sibling seat, the
orchestrator, a watcher -- substitutes an unrelated ref's sha, and the push is
refused non-fast-forward (or lands a verdict on main's lineage when the two are
related). Measured twice on 2026-10-09: #2071's round-4 reviewer's first
`push-verdict` built its verdict commit parented on main's tip `23d354970` (its
push guard held, and it disclosed the refusal), and an orchestrator fetch of a
handoff ref followed by `git -C <another worktree> reset --hard FETCH_HEAD`
answered `fatal: ambiguous argument 'FETCH_HEAD'` -- the same state read from the
worktree that did not write it.

The ref tip now comes from `git ls-remote`, which the existence test already
asked, resolved in the worktree that uses it and read into a local. The fetch
stays, for the objects only: `commit-tree` cannot write a commit whose parent it
cannot read (measured: rc 128, "is not a valid object"). A ref that moves after
the answer is a refused push -- a retry, never a commit on the wrong lineage.

`bus.sh` had a second shape, hit while confirming #2074: `ROOT` is three levels
above the script, so a copy parked outside a checkout derived its default poster
from a path that cannot exist, and `confirm` found that out only AFTER signing
and pushing `verdict/<pr>` -- verdict commit `7c64dd213` landed, the comment did
not, and the record was left saying "already posted" for the older tip. It now
refuses at load, before any remote write, keyed on the poster it will actually
call: the one dependency that broke, and one that an export of the tree without
`.git` also satisfies, so a harness run from a baseline export (`fixer.md` step
3) is not refused by it.

The class census (`git grep -n FETCH_HEAD -- .`) found the same predicate in two
sibling instruments, and one of them is worse than `bus.sh`'s:

- `body_push.sh` parented its body commit on `FETCH_HEAD` after fetching
  `handoff-body/<topic>` -- the same two-line shape, refused non-fast-forward
  when another fetch lands in the window. It takes the parent from `ls-remote`
  now, the fetch kept for the objects only.
- `handoff_push.sh` read the pull request's `BODY.md` with
  `git show FETCH_HEAD:BODY.md`, from the MAIN checkout where fetches are
  constant. An intervening fetch of another seat's `handoff-body` ref published
  ANOTHER TOPIC'S body as this pull request's -- a wrong artifact, not a refusal
  (measured below: the arm published "BODY MARKER B" for topic A). It reads the
  sha origin answered for the ref now, resolved in the worktree that uses it.

The `push-verdict` refusals are untouched -- grammar, `bus-nonce:`, evidence
naming the 40-hex head -- and `confirm`/`post` keep recorded-before-post and
withdrawn-on-refusal exactly as they were. The three `bus.sh` arms are
case-level in `--self-test`, which `governance.yml` runs in CI; all five are
drivable without a worktree per round through
`tools/audit/seat/r9_rc_bus_fetchhead.sh`.

## Head

`de34038eb071333c6e3be4caab634b1f1bb233a5`

Every figure below is measured at that sha, except the baseline runs, which name
`7cd5a588c`'s scripts -- byte-identical to this branch's merge base for `bus.sh`
(`cmp` of `git show 7cd5a588c:tools/audit/seat/bus.sh` against
`git show 23d354970:tools/audit/seat/bus.sh` is empty; main moved only
elsewhere), and the siblings' own merge-base copies.

## Mutation proof

Four predicate mutations in a detached worktree at the head, each the fix's own
predicate restored or deleted and nothing else -- not a line appended past a
return.

- M1 -- `bus.sh`: `parent="-p $tip"` reverted to
  `parent="-p $(git rev-parse FETCH_HEAD)"` (the defect itself):
  `bash tools/audit/seat/bus.sh --self-test` -> `48 checks, 1 failed`, and the
  one is `FAIL an intervening fetch of an unrelated ref does not reparent the
  appended commit`. The null control and the out-of-tree arm stay green, so the
  mutant is attributed to that line and not to the arms around it.
- M2 -- `bus.sh`: the poster-guard line deleted -> `48 checks, 1 failed`:
  `FAIL a copy outside a checkout refuses before it pushes the verdict ref`.
- M3 -- `body_push.sh`: `P="-p $tip"` reverted to
  `P="-p $(git rev-parse FETCH_HEAD)"` -> the `bodypush` arm reports
  `its parent 0c8080f8...` (the decoy's tip) and
  `parent == handoff-body/A's tip? no`, rc 1.
- M4 -- `handoff_push.sh`: `git show "$tip:BODY.md"` reverted to
  `git show FETCH_HEAD:BODY.md` -> the `handoffpush` arm reports
  `published body BODY MARKER B`, `the published body is NOT topic A's`, rc 1.

## Null control

Five arms; the second is the null control and must not move.

**Arm 1, the intervening fetch** (`r9_rc_bus_fetchhead.sh <bus.sh> race`).
It appends a second verdict onto an existing `review/<pr>` while a fetch of an
UNRELATED ref (`main`) lands in the window between the script's own fetch of the
ref and its read of the tip, injected by a git wrapper on PATH. The plant must go
INSIDE the window: measured first, because `git fetch` rewrites `FETCH_HEAD` even
when the ref is unchanged, so a plant placed before the script's own fetch is
overwritten by it and the arm would be green on the bug it pins. The assertion is
the PARENT SHA of the built commit, never the push -- a refused push is already
the bug's behaviour, so an arm that passes on refusal proves nothing.

    baseline   main tip c723b3b10  review/21 before 21aa2c395
               FETCH_HEAD the script could read c723b3b10  push-verdict rc 1
               built commit's parent c723b3b10  != the ref tip -> rc 1
    fixed      main tip c723b3b10  review/21 before 47efaa53
               FETCH_HEAD the script could read c723b3b10  push-verdict rc 0
               built commit f544799e  its parent 47efaa53 == the ref tip -> rc 0

(Each run mints its own nonce, so the two runs' shas are not comparable to each
other; what is asserted is the parent against the ref tip within a run.)

**Arm 2, the null control** (`<bus.sh> append`): the ordinary two-round append
with no plant at all, timestamps pinned, so the shas are a function of the tree
and nothing else. Baseline and head outputs diff empty -- byte-identical, at both
ends and at `ea69cee35`:

    round-1 commit 903ff5f3d
    round-2 commit ec4bbbdc9   parent 903ff5f3d
    review/30 tree c7d7c97b3
    round-2 message "verdict: #30 Fix review: merge 1111..."

and in the tree's own instrument, every case that existed before the fix still
passes: `45 checks, 0 failed` at `7cd5a588c` and `48 checks, 0 failed` at the head
-- 46 of the 48 pass on the arms-first commit, where the two new defect arms are
the two that fail.

**Arm 3, the out-of-tree copy** (`<bus.sh> ootree`): `confirm` from a copy three
levels under a throwaway directory, with no `HPO_BUS_POSTER`.

    baseline   confirm rc 1, poster calls 0, verdict/21 AFTER confirm: exists
               -> HALF-APPLIED: the verdict commit landed, the post never ran
    fixed      confirm rc 1, poster calls 0, verdict/21 after confirm: absent
               -> nothing pushed, nothing posted

The refusal lands before the push, which is the point: the baseline's
half-applied operation is exactly #2074's, where the ref moved and the comment
did not. The arm uses a PR whose dispatch matches the proposal, or an unfixed
script would stop at `dispatched_to` and the case would be green on the defect.

**Arm 4, `body_push.sh`** (`<body_push.sh> bodypush`): two throwaway topic refs,
A pushed and B the decoy, both built without the instrument, and the plant opens
the window on the fetch of A.

    baseline   handoff-body/A before 436b13d2  decoy B 0c8080f8
               FETCH_HEAD the script could read 0c8080f8  rc 1
               built commit 6e8d135  its parent 0c8080f8 != A's tip -> rc 1
    fixed      handoff-body/A before 436b13d2  decoy B 0c8080f8
               FETCH_HEAD the script could read 0c8080f8  rc 0
               built commit 409e20e  its parent 436b13d2 == A's tip -> rc 0

**Arm 5, `handoff_push.sh`** (`<handoff_push.sh> handoffpush`): same fixtures,
plus a `handoff/<topic>` ref carrying the code head (the script refuses
otherwise). The instrument runs from a copy inside the throwaway checkout, so
its own main checkout, worktree, branch and push all stay in the throwaway
repository. The assertion is the body it published.

    baseline   handoff-body/A BODY.md "BODY MARKER A"; decoy B "BODY MARKER B"
               published body "BODY MARKER B" -> NOT topic A's -> rc 1
    fixed      published body "BODY MARKER A" -> topic A's -> rc 0

## Figures

- `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, changed files
  `tools/audit/seat/r9_rc_bus_fetchhead.sh`,
  `tools/audit/seat/body_push.sh`, `tools/audit/seat/bus.sh`,
  `tools/audit/seat/handoff_push.sh` -- `python3 tests/closure.py select --diff
  $(git merge-base origin/main HEAD) --workdir "$D"`. Keyed on the mode line:
  this diff is inert.
- `STRUCTURE RATCHET PASSED` (rc 0) -- `python3 tests/structure.py`.
- `CI PREDICT: no closures or fast red predicted against 7cd5a588cbbb` (rc 0) --
  `python3 tools/pr/ci_predict.py --base origin/main`. At
  `dev/audit/harnesses/` the same command printed `PREDICT closures INERT READS
  tests/harness_headers.py: .../r9_rc_bus_fetchhead.sh (a new file beside 4 it
  lists)` at rc 1: `harness_headers.py` rglobs that directory, so a fifth file
  there is an INERT read the recording does not list, and the recording is
  re-derived only on Linux. The route changed rather than the table
  (`fixer.md` step 14): the harness sits beside the three instruments it
  exercises, which is where `CLAUDE.md`'s Instruments paragraph sends a new
  reusable instrument.
- `layout self-test: ok`, rc 0 -- `python3 tests/layout.py`; it refuses a file
  re-added under `tools/audit/harnesses/`, a retired path, so the harness is at
  `tools/audit/seat/r9_rc_bus_fetchhead.sh`.
- `bus self-test: 48 checks, 0 failed` -- `bash tools/audit/seat/bus.sh
  --self-test`; the same at `7cd5a588c` is `45 checks, 0 failed`, and
  `bash tools/audit/seat/handoff_push.sh --self-test` is `1 checks, 0 failed`.
- Arms 1-5 outputs -- `bash tools/audit/seat/r9_rc_bus_fetchhead.sh <script>
  race|append|ootree|bodypush|handoffpush`, against this head's scripts and
  against `git show 7cd5a588c:<path>`.
- THE CLASS CENSUS (fixer.md step 8),
  `git grep -n FETCH_HEAD -- . | grep -v '^dev/audit/rounds/'` (the round trees
  are measurement records, not code paths), every seam and its disposition:
  - `tools/audit/seat/bus.sh`, the `parent="-p $tip"` line in `append_commit()`
    -- CLOSED here; arms: the self-test case and `race`.
  - `tools/audit/seat/bus.sh`, the `[ -x "$POSTER" ] || die` line after the
    poster default -- CLOSED here; arms: the self-test case and `ootree`.
  - `tools/audit/seat/body_push.sh`, the `P="-p $tip"` line -- CLOSED here; arm:
    `bodypush`.
  - `tools/audit/seat/handoff_push.sh`, the `git show "$tip:BODY.md"` line --
    CLOSED here; arm: `handoffpush`.
  - `.github/workflows/tests.yml:3117` -- a comment recording that the step uses
    an explicit refspec precisely because a bare fetch lands on `FETCH_HEAD`:
    ALREADY GUARDED.
  - `tools/audit/seat/handover_prompt.py:94` -- prose in a seat prompt naming a
    `FETCH_HEAD` read; a prompt, not a ref-parent resolution. Not this class.
  - `tools/audit/seat/r9_rc_bus_fetchhead.sh` -- this PR's own arm, reading
    `FETCH_HEAD` to show the poison WAS in place (it asserts `FETCH_HEAD` is not
    the ref tip), i.e. the arm's precondition.

## Red checks

- `harness header EXPECTED vs RESULT (#817)` is red in my environment
  (`12 of 109 HARNESS HEADER CHECKS FAILED`). Not this diff's:
  `python3 -c 'import sys;sys.path.insert(0,"tests");import harness_headers as h;
  print(h._discover())'` executes 9 harnesses, all under `dev/audit/rounds/`, none
  of which this diff touches, and `dirty_registers()` returns `(True, 'clean')`.
  Its inputs are byte-identical to main's, so its result is main's; the scoped
  gate runs no script for this diff and CI is the authority.

## Forward-carry

`tests/layout.py` refuses a file re-added under `tools/audit/harnesses/` ("it
lives at dev/audit/harnesses/"), while the policy corpus still instructs seats to
write there: `CLAUDE.md:150` ("per-group harnesses in `tools/audit/harnesses/`
and `tools/audit/round9/`") and `dev/governance/roles/fixer.md:257` (step 18, "a
harness in `tools/audit/harnesses/`"). Following those two lines leads into a
retired path AND, measured above, into a predicted CI `closures` red -- a policy
corpus sending seats where a guard refuses them. That is the stale-retired-path
class of group `R9-RO-10`, and it belongs in that lane's brief;
`tests/README.md:272` carries the same stale citation. This PR lands the harness
where the checks allow and changes no policy.

## Friction

`none`
