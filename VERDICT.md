Fix review: merge da2b6345011354ef7ec5b30b1cd57da2d95dbb83

bus-nonce: 421f65606994645397aadad0a0b1d252

Measured head: `da2b6345011354ef7ec5b30b1cd57da2d95dbb83`
(`refs/heads/fix/bus-row-dispatch` == `refs/pull/2107/head`; the PR body names
it; `8961643da111cc7612e1f2c097321171075fdc43` is the authored code head). I
reviewed from a detached worktree at that SHA. `fix-review.md` was current at
the merge base (roles diff vs main empty).

## RESULT lines

    RESULT arm-refusal      dispatch <rowless head> -> rc 1 "carries no dev/programme/delivery/2107.md", no state written   PASS
    RESULT arm-control      dispatch <row-with-row> -> rc 0, bus-nonce printed, record appended                            PASS
    RESULT arm-early        dispatch is the sole writer of $S/dispatched; confirm needs dispatched_to -> rowless cannot post PASS
    RESULT mutation-A       row predicate forced true -> "47 checks, 1 failed" on the named arm; restored -> 47/0            PASS
    RESULT self-test-head   bash tools/audit/seat/bus.sh --self-test -> 47 checks, 0 failed                                PASS
    RESULT self-test-base   same at merge base 1301d7e45 -> 45 checks, 0 failed                                            PASS
    RESULT arm-set-delta    45 -> 47; 0 arms removed, exactly the 2 new arms added                                          PASS
    RESULT null-control     #2075 addd6f45758ff90ab862bcbe62357c1373ed7786: base rc 0 (nonce), head rc 1                   PASS
    RESULT live-bus-intact  ~/.zcode/bus/dispatched 361 lines before and after every arm                                    PASS
    RESULT conflict         git merge-tree --write-tree origin/main HEAD -> rc 0 (no conflict)                              PASS
    RESULT red-checks       no check-runs conclusion "failure" at any head in the range                                     PASS
    RESULT census-rerun     row_position.py --limit 60 -> 39/20/0/1 (body: 41/17/1/1; live state moved)                     NOTE
    RESULT version-untouched VERSION, manifest version, notes heading untouched (diff is 3 files)                           PASS

## What I re-ran (the finder's / the body's arms), and what I built

*Failing-first and control*, against a **copy** of `bus.sh` with
`HPO_BUS_STATE` in a temp dir I own (the caution in my brief), never the live
bus: `dispatch 2107 1301d7e45…` refuses (rc 1, "carries no
dev/programme/delivery/2107.md", and writes nothing to `$S`); `dispatch 2107
da2b63450…` records (rc 0, `bus-nonce: <32 hex>`, one line appended). Refusal
is at DISPATCH: `dispatch` is the only writer of `$S/dispatched` (one append
site, line 281) and `confirm`/`review_status` call `dispatched_to`, so a
rowless head cannot reach a posted verdict.

*Mutation proof* (contract step 1): forcing the named predicate
`git cat-file -e "$h:$row"` true turns the new self-test arm red —
`47 checks, 1 failed`, the same line the body quotes; restoring it is green.
The arm pins the gate.

*Null control, both ends*: on the real head #2075 (`addd6f457…`) the unmodified
`bus.sh` at the merge base accepts it (rc 0, nonce) and the head's gate refuses
it (rc 1). Live `~/.zcode/bus/dispatched` is 361 lines before and after — no
pollution.

*Self-test, arm sets*: base 45/0, head 47/0; `comm` shows **0 arms removed** and
exactly the two new arms added — no existing arm broken.

## Class (contract step 6)

The cited class, R9-RCA-1990 **class E**, has two entries — #1977 and #1988 —
and both are the **same seam**: a row commit landing after the measured head.
#1977's row commit moved the head 7 min late; #1988's title is "record:
delivery rows for #1984 (autofix)" and its blocked verdict reads `measured
b30d6450…, head is 54c050c2…`. So class E is one seam, not two, and the diff
addresses it. The body names its instrument (`row_position.py`, which
enumerates the row-position classes) and its rule. No open seam.

## Notes (non-blocking)

1. `tools/audit/seat/row_position.py`'s docstring (line 4) prints the usage
   `python3 dev/audit/harnesses/row_position.py …` — a path that does not exist.
   `8961643da` moved the file from `dev/audit/harnesses/` (to keep
   `tests/harness_headers.py`'s recorded reads fresh) and left the docstring
   naming the old path; running it as documented fails. The body's Figures uses
   the right path, so the operator can run it. `moved_paths.py` does not flag it
   because `dev/audit/harnesses/` is an active, not moved, prefix.
2. The body's "dispatch is the single chokepoint" holds **within the bus** only:
   a `Fix review: merge` comment posted directly through `app_comment.sh`
   (bypassing `push-verdict`/`confirm`) never touches `dispatch`. The bus is the
   adopted path, so the practical impact is low, but the claim is stronger than
   the mechanism.
3. The census figures no longer re-derive as quoted: `row_position.py --limit 60`
   now prints 39 `row-before-verdict` / 20 `no-merge-verdict` / 1
   `no-row-in-head` / 0 `row-AFTER-verdict` (the body: 41/17/1/1). The movement
   is live state, and I re-derived it: #2075's row (`9d62d06`) was not an
   ancestor of the body's newest verdict `addd6f457…` (11:51Z) but is an ancestor
   of the re-review verdict `dcf0340d…` (13:42Z), so #2075 moved out of
   `row-AFTER-verdict`. A census, as the docstring says.

## Orchestration note, not this PR's defect

#2107's live bus dispatch record carries a head that **does not exist**:
`2107 da2b634509bf9f62c1a5ff8f7b0f9db0e1e6cd05 rev-2107
421f65606994645397aadad0a0b1d252`. `git cat-file -t
da2b634509bf9f62c1a5ff8f7b0f9db0e1e6cd05` fails; no object, ref or reflog in
the repo carries it. The dispatch gave that phantom to my brief too. The real
head is `da2b6345011354ef7ec5b30b1cd57da2d95dbb83`. `push-verdict` does not read
the record, so this verdict pushes; `confirm`'s `dispatched_to` matches on
`pr hsha nonce` and will **not** match unless the orchestrator re-dispatches
#2107 at the real head. Naming the phantom here would be naming a commit that
does not exist; naming the measured head is what `fix-review.md` step 12 asks.
