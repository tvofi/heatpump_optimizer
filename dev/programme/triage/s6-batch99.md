# Proposal triage, session s9, batch 99 (P354)

The rolling batch after batch 98, which was pushed first and left at its head. Facts were read at
origin/main `c89de2f62`, at the round's roster branch `origin/handoff/audit-r10-roster`
(`c28fbf12d`), on the bus refs `verdict/*` (515 of them, `git ls-remote origin
'refs/heads/verdict/*'`), and in the bus state directory's `posted`, `posted-signed` and
`verdicts/3068/`.

## P354: the train refuses a posted verdict whose tip is a same-tree copy

Verdict: ACCEPT, as two carries:
- **(a)** on R10-FLY-TRAIN-DEFAULTS: the train keys a posted verdict on the bus's signed identity,
  `<pr> <tree>`;
- **(b)** on R10-FLY-RELAY-REVIEW-FF: `bus.sh confirm` stops appending same-tree copies. It is
  held until #3065 merges.

The interim answer for #3068 is a lossless rewind of `verdict/3068` to the posted commit. A by-id
waiver is not a legitimate interim.

Source: orchestrator s9, by message, 2026-11-01. The merge seat found it on #3068.

Instances:
- **#3068.** `git log origin/verdict/3068` shows two commits:
  - `3c0b62eaa`, the root, at 04:57:25 (+01:00);
  - `948d1ee60`, its child, at 04:57:34.

  Both have tree `03483ecd5`, the same message, and the same `bus-signature` line (equal md5).
  The App's only `Fix review:` comment, 6553126385 (03:57:35Z), says `bus: verdict/3068 at
  3c0b62eaa...`. The bus state's `posted` holds `3068 3c0b62eaa...`.
- **Which seat pushed the second commit.** A second `bus.sh confirm` of the same review commit,
  9 s after the first, in the same state directory.
  - The first confirm's body file `verdicts/3068/3c0b62eaa....md` was written at 04:57:32, and its
    post log at 04:57:36. Only after that post does `posted-signed` hold the tree.
  - The second confirm's pre-check (`bus.sh` `confirm`, "a replay is refused here, before any
    push") ran inside that window, so it passed and called `append_commit`. That is the
    04:57:34 commit; its directory `verdicts/3068/948d1ee60...` is dated 04:57:40.
  - Its `post_verdict` then refused the post as a replay.

  The orchestrator reports that the relay's `confirm_arm` and the dispatch seat's confirm raced;
  the times fit two callers. The bus ref is left at a tip that no comment names.
- **The class.** A same-tree parent/child scan over the 515 `verdict/*` refs (the objects are
  local) finds:
  - 170 pairs on 79 refs: 54 pairs 60 s apart or less, which are races, and 116 further apart,
    which are re-confirms;
  - 53 refs whose tip is such a copy;
  - 13 pairs since 2026-10-30, on #2980, #3009, #3010, #3022 (three), #3030, #3052 (four), #3062
    and #3068.
  - `verdict/3052` holds four commits of one tree, `2b14806a4`, from 00:04:56 to 01:00:47. That
    is a retried confirm, not a race. For it, `posted` and `posted-signed` hold no line in this
    state directory.
  - The three PRs with a copy at the tip are all open: #3052, #3062 (a blocked verdict, so the
    train does not read it) and #3068.
- **No instrument path clears #3068.**
  - `merge_train.py` `posted_verdict` returns "the newest posted verdict (comment ...) is not
    verdict/<n>'s tip" when the comment does not name the tip's sha (lines 2343-2345 at
    `c89de2f62`).
  - `bus.sh` `confirm` and `post_verdict` refuse a second post of the tree.
  - `merge_train.py` has no waiver: `grep -n -i waive` prints nothing.
- **The bus's own identity is the tree.** `post_verdict`'s comment reads: "What is signed is
  "<pr> <tree>", so each tree posts once per pull request whatever commit or encoding carries
  it; each round's nonce makes its tree distinct." The signature is over
  `hpo-bus verdict <pr> <tree>` (`confirm`). So two commits with one tree carry one signed
  verdict. A new round always has a new tree.

Cost:
- **(a)** About 8 lines in `posted_verdict`: one fetch of `verdict/<n>` and two tree reads with
  the existing `tree()` helper. Plus three queue self-test arms beside #18 and one mutant, for
  one S fixer on the group's sonnet/opus row.
  - `merge_train.py` is not a capped file: `grep -n merge_train tests/*_budgets.json` prints
    nothing.
  - #3063, R10-TRAIN-OVERLAP-GRADE's open part 2, edits `merge_train.py` (+300 lines). None of
    its hunks falls in `posted_verdict` (lines 2318-2350): its nearest hunks start at lines 2372
    and 2399. So (a) needs no hold, and whichever lands second merges main. #3010 is merged.
- **(b)** About 10 lines in `bus.sh` `confirm`: a `mkdir` lock as in #3065's `watch.lock`, and a
  tip-tree check. Plus four self-test arms beside the replay arms (lines 1002-1054), and one
  mutant.
  - It is held until #3065 merges, because both edit `bus.sh`. #3065's diff does not touch
    `confirm` or `append_commit`.
- Neither half adds a check, a file or an API call. (a) adds one `git fetch` per refused queue
  candidate.

Binding:
- **(a) is the fix that clears what wedges a merge.** The train keys a verdict on a commit sha,
  where the writer keys it on `<pr> <tree>`. Matching the writer's identity is the
  architecturally sound reading, and it releases #3068 without touching a ref. The ancestry
  condition keeps a same-tree commit from outside the ref's history from counting. The tree
  condition keeps #18's case waiting, because a newer round has a different tree.
- **(b) removes the copies at their source.** With (a) alone, the copies are harmless to the
  train, but each one is a push that wakes every bus watcher. The relay's `confirm_arm` already
  assumes confirm is idempotent (R10-FLY-RELAY-REVIEW-FF carry 6, "run bus.sh confirm <pr> <sha>
  (idempotent)"), and it is not: #3052 got four commits.
- **The groups.**
  - R10-FLY-TRAIN-DEFAULTS owns the train's verdict and approval reading (its P331 carry on
    `review_settle` and the approval-race SKIPs), has `merge_train.py` in `files`, and has no PR
    in flight.
  - R10-FLY-RELAY-REVIEW-FF owns the relay's confirm arm and `bus.sh` (`files`). Its single-
    instance lock carry (16) uses the same idiom.
- **The interim for #3068 is a rewind, not a by-id waiver.**
  - A waiver has no instrument. It would be a hand merge past `admit_add`'s check, and a hand
    merge leaves no record that the check's premise held.
  - What the check needs is true here, and the ref can be made to show it without losing
    anything. `948d1ee60` differs from `3c0b62eaa` only in its parent and dates: same tree,
    message and signature.
  - The rewind:
    `git push --force-with-lease=refs/heads/verdict/3068:948d1ee60fb13f73a6e944a61763ad5de35be22e origin 3c0b62eaae170958a07e5c85c452d9393172870c:refs/heads/verdict/3068`.
    Then read back `git ls-remote origin refs/heads/verdict/3068`.
  - No ruleset covers `verdict/*`. The two branch rulesets include only `~DEFAULT_BRANCH`.
  - The bus watcher then sees `verdict/3068` change to a commit that `posted` already holds, and
    skips it (`watch_once`: `grep -qx "<pr> <sha>" posted || post_verdict`).
  - `merge_train.py add` then passes unchanged.
  - The same applies to #3052 only if its newest App comment names a commit below its tip. Read
    that before rewinding it.

Carry (a), R10-FLY-TRAIN-DEFAULTS, `s7/carries/b99-P354a.txt`:

> From triage P354 (merge seat, #3068: `merge_train.py add` refused "the newest posted verdict
> (comment 6553126385) is not verdict/3068's tip 948d1ee60"). The bus signs and posts a verdict
> once per `<pr> <tree>` (tools/audit/seat/bus.sh `post_verdict`: "What is signed is "<pr>
> <tree>", so each tree posts once per pull request whatever commit or encoding carries it").
> `posted_verdict` in tools/audit/seat/merge_train.py instead keys on the commit sha, so a
> same-tree commit appended after the posting wedges the PR, and no instrument can clear it:
> bus.sh refuses the second post as a replay. Change `posted_verdict` only. When the newest App
> comment's `bus: verdict/<n> at <sha>,` names a sha that is not the tip, the comment stands for
> the tip iff <sha> is an ancestor of verdict/<n>'s tip and the two trees are equal; the objects
> come from a fetch of verdict/<n>. Otherwise it waits as today, with today's message. The
> returned verdict head and comment id are unchanged.
> Controls, in the queue self-test beside #18:
> - a tip one same-tree commit after the commented sha is queued;
> - null control: #18's case, a tip whose tree differs from the commented commit's, still waits (its fixture gains real trees);
> - a same-tree commit that does not descend from the commented sha still waits;
> - one mutant that drops the tree comparison leaves #18 red.
> triage: dev/programme/triage/s6-batch99.md#P354

Carry (b), R10-FLY-RELAY-REVIEW-FF, `s7/carries/b99-P354b.txt`:

> From triage P354 (#3068 and #3052). `bus.sh confirm` appends a new commit on verdict/<pr>
> before `post_verdict` refuses it as a replay. Its pre-check reads `$S/posted-signed`, which a
> concurrent confirm has not yet written, and which another state directory never writes. Two
> instances:
> - verdict/3068 got 3c0b62eaa at 04:57:25 and 948d1ee60 at 04:57:34 (+01:00), with tree
>   03483ecd5. The first post's record was written at 04:57:36, after the second confirm's
>   pre-check.
> - verdict/3052 holds four commits with one tree, 2b14806a4, from 00:04:56 to 01:00:47.
>
> Of 515 verdict refs, 79 hold a same-tree parent/child pair (170 pairs); 53 of them have such a
> commit at the tip.
> Fix, in tools/audit/seat/bus.sh `confirm` only:
> (1) hold a per-PR lock, `mkdir "$S/confirm.<pr>.lock"` holding the pid, with a dead holder's
> lock taken over (the watch.lock idiom), across the pre-check, append_commit and post_verdict;
> (2) when verdict/<pr>'s remote tip already has this tree, append nothing and post against
> that tip, so `post_verdict`'s own refusals (already posted, a replay) answer.
> Controls, in bus.sh's self-test beside the replay arms:
> - a second confirm of the same review commit leaves verdict/<pr>'s tip unchanged and posts
>   nothing;
> - null control: a later round (a new nonce, so a new tree) still appends and posts;
> - two concurrent confirms produce one commit and one post;
> - one mutant that drops the tip-tree check leaves the first arm red.
> Hold: lands after #3065 merges (both edit bus.sh).
> triage: dev/programme/triage/s6-batch99.md#P354

Roster ops, queued #held:
1. `append-carry R10-FLY-TRAIN-DEFAULTS @.../s7/carries/b99-P354a.txt`. It is released when this
   file is on origin/main.
2. `append-carry R10-FLY-RELAY-REVIEW-FF @.../s7/carries/b99-P354b.txt`. It is released when this
   file is on origin/main and #3065 has merged.

Rule run on each instance:
- **#3068.** Under (a), comment 6553126385 names `3c0b62eaa`, an ancestor of tip `948d1ee60`
  with the same tree, so the PR is queued. Under (b), the second confirm would have found the
  tip's tree equal and appended nothing.
- **#3052.** Under (b), three of its four commits would not have been made. Under (a), it is
  queued once its newest comment names any of the four.
- **#3062.** Its verdict is blocked, so the train leaves it either way (queue arm #14). Under
  (b), its 7 s copy would not have been made.
- **#18 (self-test, the null control).** Its fixture tip, `hx("7")` (line 4515), is a
  confirmed-not-posted round. Given trees, a different round has a different tree, so it waits
  under (a) as today.
