R10-FLY-NO-FOOTERS-PUSH-PATHS (lane FLY, size S, instrument). Two holes let a
commit carrying `Co-Authored-By` and `Claude-Session` trailers (767a06f7f, and
its re-commit cc51e6626) reach a pull-request head after the R10-FLY-NO-FOOTERS
guard (a4b27986) landed. Both are closed here by sharing ref_privacy's one
attribution check (`refusal()` over `attribution()`), never a copy of it.

1. **Every push path that publishes commits now judges each commit message.**
   - `tools/audit/seat/ref_privacy.py`: `published(rev, cwd, over=None)` and
     `guard --commits REV --over BASE` judge every commit under REV that BASE
     does not hold. Without `--over` the scope is unchanged: what the push
     publishes first (`--not --remotes`). It is one reader with one record
     shape, so every caller below shares it.
   - `tools/audit/seat/handoff_push.sh`: right after it resolves the code head,
     it fetches main and runs `guard --ref fix/<topic> --commits CODE --over
     refs/remotes/origin/main`. That happens before any worktree, PR or push
     exists. It is the first reader of a `handoff/<topic>` head the cloud
     harness pushed unguarded.
   - `tools/audit/seat/ci_probe.py` `push`: judges `ref_privacy.published(sha)`,
     the messages and the identities, through `ref_privacy.refusal`. A
     refusal comes before the rate check and before any API write, dry run
     included.
   - `tools/audit/seat/body_push.sh`: reads the body commit back with `guard
     --commits "$C"`, where it used to pass the message it composed
     (`--message "body: $TOPIC"`). It now judges the commit as written: its
     message, its identity, and any parent origin does not hold.
   - **What covers the cloud harness's own `git push`.** The tree cannot hook
     it, and this diff does not claim to. A cloud seat's `handoff/<topic>`
     push still publishes unjudged. Three later readers cover it before the
     commit can reach a pull request: `handoff_push.sh`'s new guard, and
     `app_push.sh` (item 2) under both `open_pr.sh` and `update_pr.sh`, since
     every PR push goes through it (decision 0011). The `.claude/settings.json`
     `attribution` off-switch (#2636) stops the harness writing the trailers in
     the first place, on any base that carries it. A trailer on a
     `handoff/*`/`ci-probe/*` ref that never becomes a PR is not judged. That
     ref is transport, not a PR head.
2. **`app_push.sh` judges every commit the PR adds over main.** The guard call
   is now the function `judge_commits` (worktree, branch, head). It fetches
   `origin main` first, so a stale `origin/main` cannot charge the PR with
   main's own history. That matters: main holds thousands of trailer commits
   (Figures). Then it runs `guard --commits HEAD --over
   refs/remotes/origin/main`, which is `git rev-list origin/main..HEAD`'s set.
   A failed fetch refuses. A commit first published on `ci-probe/*` or
   `handoff/*` is no longer exempt.

**Author identity is out of scope.** The owner's rule names footers, trailers
and session links, not authors. The orchestrator's ruling under mandate
6329234399 puts author identity OUT of scope for this group. The check is
not widened. A commit authored `Claude <noreply@anthropic.com>` passes, as
before; the existing `host-email` class judges only a machine-naming domain,
and a public noreply domain passes it.

**Existing open PRs that item 2 would refuse at their next push.** I measured
all eight open PRs (Figures). Five carry an attribution commit in
`origin/main..<head>`:

| PR | refusing commit(s) | authored (UTC) | against the a4b27986 cutoff (2026-10-22T23:07Z) |
|---|---|---|---|
| #2662, #2657, #2656 | `cc51e6626c91` | 2026-10-23T03:51:16Z | **after**: not dismissed. This is the hole commit itself, so the refusal is correct |
| #2632 | `86b3fe71d656` | 2026-10-22T23:16:10Z | **after**, by nine minutes, but before the guard reached main (7deeef1b6, 06:08Z). Not dismissed by the ruling's letter; the orchestrator's call |
| #2632 | `add0c10232dc`, `a1e2138ce50e`, `2854b13844f5`, `3d87e5910357`, `1b4fbc55bd90` | 21:07Z to 21:45Z, 2026-10-22 | before: dismissed |
| #2620 | `701448f9062f`, `23392d5d697c`, `08ba3d9d7b11` | 17:28Z to 19:09Z, 2026-10-22 | before: dismissed |

#2663, #2654 and #2653 (`record/autofix`) pass.

**Proposal: an allow-list, NOT added in this diff.** It changes how no later stage works, so there is no Forward-carry; the orchestrator rules on it and on `86b3fe71d656` from this body. The brief forbids adding
it silently. It would be a set of full commit SHAs in `ref_privacy.py`, keyed
on the SHA alone, each entry citing the orchestrator's ruling that commits
authored before a4b27986 are dismissed because a published branch is not
rewritten. It would hold the eight pre-cutoff SHAs above, nothing else. The
key separates (fixer.md step 14): a SHA matches one commit object only, so
an entry cannot blind the guard to any later commit, a re-commit included
(cc51e6626 is 767a06f7f re-committed and would need its own entry, which the
cutoff refuses). `86b3fe71d656` is the one borderline entry. Until the
orchestrator rules, #2632 and #2620 are refused at their next `app_push.sh`
push. A merge of main does not clear them, because the commits stay in
`origin/main..HEAD` until the PR merges.

**Orchestrator ruling (mandate 6329234399), 2026-10-23T13:40Z, on the allow-list proposal above.** No allow-list is added. The impact table is settled by merge order and by retiring the affected PRs:
- **#2632** merged at 7108101d7 before this PR. Its commits, including the borderline `86b3fe71d656`, are now ancestors of origin/main and leave `origin/main..HEAD` for every later PR. Nothing is owed.
- **#2620** (three pre-cutoff, dismissed commits) is ordered to merge before this PR. Its approval is live at 87f6c34e, and the train holds this PR behind it. If #2620 cannot merge first, this PR waits; the guard is not weakened for it.
- **`cc51e6626c91`** on #2662, #2657 and #2656 is the hole commit, and refusing it is correct. #2662 is replaced by the P2b re-cut (trailer-free 619ff2d55 in place of cc51e6626), and #2657/#2656 are cut-over probe PRs that close when Arm B ends. None of them is pushed through app_push.sh again after this lands.

## Head

`22bb373a318c1c8d4aa3c593db44a7b65da12a08` merges origin/main `12032c43c` into the authored code head `8aefaa95bc7186fba6f8fa5fe8f662449f945586` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`8aefaa95bc7186fba6f8fa5fe8f662449f945586`. Merge base and origin/main tip are both
`4c31eb16e5756579e1c951ff560bd3d7a8e39c4c`, measured at 2026-10-23T13:15Z.

## Mutation proof

Each mutant was applied in the worktree at the head, then the command was run
and the file restored. The driver applies the edit, asserts the target text
appears exactly once, and restores it in a `finally`.

| # | mutant | command | what went red |
|---|---|---|---|
| M1 | handoff_push: the `guard ... --over` line becomes `true` | `bash tools/audit/seat/handoff_push.sh --self-test` | `a code head carrying a co-author trailer is refused, and nothing is pushed` |
| M2 | body_push: back to `--message "body: $TOPIC"` | `python3 -I tools/audit/seat/ref_privacy.py --self-test` | `body_push refuses a topic that puts a session link in the message` (the reason is no longer the commit's), `body_push refuses a body commit whose author email names a machine` (pushed) |
| M3 | body_push: guard line becomes `true` | same | `body_push refuses a topic naming a host path`, plus both rows of M2 |
| M4 | ci_probe: `refusal(short, messages, emails=emails)` becomes `refusal(short)` | `python3 -I tools/audit/seat/ci_probe.py --self-test` | `push refuses a commit carrying a co-author trailer, before any API write`, `the remote holds main and the two probe refs only` |
| M5 | app_push: `judge_commits` drops `--over refs/remotes/origin/main` (back to first-published) | `bash tools/pr/app_push.sh --self-test` | `real git: a trailer commit first published on ci-probe/* is refused when the PR carries it (got '00', want '13')`, plus the stubbed-git happy path: the stub answers only the `--not refs/remotes/origin/main` read |
| M6 | ref_privacy: `fence` ignores `over` | `python3 -I tools/audit/seat/ref_privacy.py --self-test` | `--over origin/main refuses it, exit 3` |

**Failing fixture first.** M1, M3, M4, M5 and M6 each put a path's judgement
back to its origin/main form, and the new fixture goes red on each. So every
fixture fails on the base's predicate and passes at the head.

## Null control

On every path, a clean commit passes and main's own trailers are not charged:
- ref_privacy: `and passes the clean commit below it, over main's own trailer (the null control)`;
  `a trailer commit origin holds on ci-probe/x passes the first-publish scope (the hole)`
  shows the hole at the base scope.
- app_push, real git: `a clean commit first published on ci-probe/*, over a trailer main holds, passes (null control: main is not charged)`.
- handoff_push: `null control: the open path pushes the pull request, then its row`
  and `null control: the update path pushes its head once`, both over the new guard.
- ci_probe: `null: a clean commit above the same base lands`.
- body_push: `and pushes a clean topic (the null control)`.
- **An old dismissed commit is refused**, as stated above: no allow-list
  exists. Measured on the five open PRs in the table; the guard prints the
  class and the 12-character SHA.

## Figures

- `python3 -I tools/audit/seat/ref_privacy.py --self-test`: `ref_privacy self-test: 90 checks, 0 failed`.
- `python3 -I tools/audit/seat/ci_probe.py --self-test`: `ci_probe self-test: 42 checks, 0 failed`.
- `bash tools/pr/app_push.sh --self-test`: `app_push self-test: 199 checks, 0 failed`.
- `bash tools/audit/seat/handoff_push.sh --self-test`: `handoff_push self-test: 3 checks, 0 failed`, after `delivery_row self-test: 6 checks, 0 failed`.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: `25 file(s) with a push site, 12 guarded, ... 0 refused`.
- Open PRs: the list is the `state=open` pull-request listing at 2026-10-23T13:15Z (8 PRs). Each head was fetched as
  `git fetch origin refs/pull/<N>/head:refs/pr/<N>`, then judged by the shipped guard:
  `python3 -I tools/audit/seat/ref_privacy.py guard --ref fix/x --commits refs/pr/<N> --over origin/main`
  gives rc=3 for #2662, #2657, #2656, #2632, #2620 and rc=0 for #2663, #2654, #2653.
  The per-commit table lists `git log refs/pr/<N> --not origin/main --format=%H%x1f%aI%x1f%B` with each message judged by
  `ref_privacy.attribution`. Its null control is the three PRs that pass.
- Main's own trailers, the reason `judge_commits` fetches main first: `git log origin/main --format=%H%x1f%B%x1e`,
  each message judged by `ref_privacy.attribution`, counting non-empty class lists, at `4c31eb16e575`:
  4160 commits. Its null control is `attribution('plain message') == []`. A stale `origin/main`
  would put such commits in `origin/main..HEAD`.
- This branch's own messages: `python3 -I tools/audit/seat/ref_privacy.py guard --ref handoff/r10-fly-no-footers-push-paths --commits HEAD --over origin/main` gives rc=0.
- Seam enumeration (fixer.md step 8): the rule is `ref_privacy.py --check`'s `PUSHERS` registry. It
  enumerates every tracked file holding a push site. The seams that publish commits a seat
  composed are disposed of as follows:
  - `app_push.sh`, `body_push.sh`, `ci_probe.py`: closed here.
  - `handoff_push.sh`: holds no push site of its own and pushes through `app_push.sh`; closed here by its own guard.
  - `wt_sync.sh`, `push.sh`, `stamp.py`, `bus.sh`, `heartbeat.sh`, `state_docs.py`, `roster_edit.py`,
    `cloud_dispatch.py`: already guarded on their messages (`guard --commits` or `refusal`), unchanged.
  - `merge_main_bot.py`, `merge_train.py`, `tests.yml`, `nightly.yml`: `republishes` under constant messages.
  - The `fixture` and `prompt` entries publish nothing.
  - The cloud harness's push is outside the tree; see item 1.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 -I tools/audit/archscore/gate.py --base 4c31eb16e575 --head HEAD --body <this body>`: `PASS: dS +0.0000 NULL, no gate metric rose`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints
  `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. The one script is `tests/entities.py` (`PYTHONPATH=tests/hastub python3 tests/entities.py`), which prints its `ENTITY CHECKS PASSED` line at this head.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>`: the instrument's PRE-PR line at this head, agreement lane `AGREEMENT ok` among its steps.

## Unpinned sites

none: prepr step 6d prints `the diff adds no unpinned mutation site`.

## Red checks

none

## Forward-carry

none

## Friction

none

