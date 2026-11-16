R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3, part 2 of 2 (topic r11-outside-contributor-cycle-p3). Part 1 (#3619, merged 755b7f5) built the merge-path items, the interface reconciliation, the `selftest_closures.json` re-record and the four instrument guides; this part holds the two carries left.

Carry 1, decision 0017's half: **a policy change, drafted for the owner's approving review and not to merge on a seat's word.** Item 6 now says how a tool reads a fork head (`refs/pull/<pr>/head` fetched into a local ref only, the train's at `refs/remotes/pull/<pr>/head`), beside its existing sentence that no tool of ours pushes a fork head to a branch of origin. Item 7 names the merge mechanism, `remerge_main.sh --head-repo` (GitHub's `update-branch` as the hpo-author App at the expected head, read back as the automatic two-parent merge), and the train's `[OUTSIDE]` class with the stops that raise it. What a seat must do does not change: each sentence states what the tree at the merge base already does (Null control). The instrument guides' half was landed by part 1 (`remerge_main.sh.md`, `merge_train.py.md`), re-read at this base.

Carry 0, the three live checks on a test fork, is not run: Forward-carry.

## Head

357bc474396862a11a5c3a10ad79b0177a914a54, measured at origin/main 6aa7ddc71216c4bc357db0097839ce40ff94e263, 2026-11-16T02:26:24Z.

## Mutation proof

n/a: no production or test line changes; the diff is decision 0017's text alone, and each new sentence is checked against the code under Null control.

## Null control

Each claim the new text makes, read at the merge base, with the reading that would show it false:
- `update-branch` at the expected head as the App: `tools/audit/seat/remerge_main.sh` `--head-repo` arm, the `curl ... /pulls/$PR/update-branch --data '{"expected_head_sha":...}'` call; a push of a fork head would show as a `git push` in that arm, and there is none.
- `[OUTSIDE]` stops: `git grep -n "cls=OUTSIDE" -- tools/audit/seat/merge_train.py` returns 7 sites, each named in the new text: the unread head repository and branch (`the pulls API names no head repository and branch`), the stale copy (`is not origin/main's copy`), the contract's refusal (`the outside contract refuses #<n>`), a verdict-driven approval on a fork head (`no_fork_post`: `is never posted on a cross-repository head`), the fork head that could not be checked out (`could not make a detached worktree`), and the recarry's conflict and `REMERGE FAILED ... at push`. The stops with no `cls=OUTSIDE` (`could not say whether #<n>'s head is cross-repository`, an origin/main fetch failure, a fork's `REMERGE FAILED` at any other step) are plain stops and the text names none of them.
- Fetch only: `git grep -n "refs/pull/" -- tools .github .claude ':!*.md'` returns the readers `body_patch.sh`, `ci_probe.py`, `merge_train.py` (`+refs/pull/<pr>/head:refs/remotes/pull/<pr>/head`), `remerge_main.sh`, `app_approve.sh` (`refs/hpo-carry/head`) and `app_comment.sh` (`refs/hpo-comment-carry/head`), each a fetch; the only pushes to a `refs/pull/` ref are the self-test fixtures `bus.sh:2456` and `app_approve.sh` `setpr`/`forkpr`, to a local throwaway remote.

## Figures

<!-- figure-block: scope-line mb=6aa7ddc71216c4bc357db0097839ce40ff94e263 head=357bc474396862a11a5c3a10ad79b0177a914a54 -->
~~~text
MODE: SCOPED -- 0 script(s) run, 33 scoped out.
~~~
<!-- /figure-block -->
- Part 1's self-tests re-run at this base, unchanged by this diff: `python3 -I tools/audit/seat/merge_train.py --self-test` ends `merge_train self-test: 825 checks, 0 failed`; `bash tools/audit/seat/merge_pr.sh --self-test` ends `merge_pr self-test: 50 checks, 0 failed`; `python3 -I tools/pr/outside.py --self-test` ends `outside self-test: 266 checks, 0 failed`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

none

## Forward-carry

- Carry 0 (items 53108d53), the three live checks: (a) whether the hpo-author installation token may call `update-branch` on a maintainer-editable fork pull request and which identity the merge commit carries, (b) `app_approve.sh` approving an adopted verdict end to end after that merge, (c) which `commit_id` a class-O approval reports before and after it. Not run: this seat holds no `gh`, no App key (no `~/.zcode/hpo-author.pem`) and no fork pull request, as no fixer seat has across three dispatches of these checks. Decision 0017's `## Before the first allowlist entry` already records all three as owed, on the owner's credential and a fork, before any entry is added; control: if (a) is refused the train parks `[OUTSIDE] ... no personal token is tried without the owner`. Carry: dismissed: owner-held checks, recorded as owed in decision 0017 before the first allowlist entry

## Friction

none
