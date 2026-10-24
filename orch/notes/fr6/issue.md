_Requested by **tvofi**_

Part of #201.

## The defect

`tools/audit/seat/merge_train.py`'s recarry step fails on every pull request whose head needs an automatic origin/main absorb. Three proven instances on 2026-10-04 (#1893, #1894, #1896 — each stopped the train at recarry; the orchestrator absorbed each by hand).

Repro: queue a verdicted PR whose branch lacks origin/main. The train's recarry creates a **detached** worktree, merges origin/main there, then `remerge_main.sh`'s `app_push` refuses: `worktree HEAD (<auto-merge sha>) is not the committed tip of '<branch>'`.

## The fix

In the recarry path: check out the pull request's **branch** in the recarry worktree (not detached), or push the auto-merge sha directly to the branch ref — whichever keeps `remerge_main.sh`'s app_push identity flow intact. Add a self-test arm driving an absorbed-branch recarry end to end (fixture repo, verdict + queue entry, the merge lands). Document in the train's header comment that recarry requires the branch checkout, and that verdict comments must cite an absolute evidence path (app_approve's gate reads the comment).

## Sources

- Roster: `origin/handoff/audit-r9-fixplan` (group R9-FR-6, this issue).
- The three train stops: the orchestrator's train logs 2026-10-04 (train3/train5/train6, each `TRAIN STOPPED ... recarry`).
