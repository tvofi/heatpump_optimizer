R10-HOTFIX-AUTHOR-EMAIL (triage s6-batch133 P408, owner hotfix tier, 2026-11-07). Commits reached main under placeholder or unnumbered author and committer emails (`seat@`, `hpo-fixer@`, `noreply@users.noreply.github.com`, `t@t`, `fixer@invalid`), which GitHub credits to unrelated accounts. History is not rewritten; this refuses the bad shapes on every commit a push newly publishes. `ref_privacy.py`'s guard now refuses `unnumbered-email` for any author or committer email outside this grammar: `<digits>+<login>@users.noreply.github.com` (the seat identity `70032254+tvofi@...` included), `[<digits>+]<name>[bot]@users.noreply.github.com`, `noreply@github.com` as committer only, and an adopted outside contributor's own address named per adoption by `--adopt-email ADDR` (author only). The refusal prints the exact pin (`-c user.name=tvofi -c user.email=70032254+tvofi@...`, `--author`, or the per-worktree `git config --worktree user.email` form) so a refused seat can self-correct. The fixture identity in `tests/throwaway_git.{py,sh}` moves from `t@t` to `1+t@users.noreply.github.com` so guarded self-tests keep passing. Writers of `seat@` and `hpo-fixer@`: none are in the tree (cloud-setup.sh, cloud_dispatch.py, update_pr.sh, open_pr.sh and delivery_row.sh already pin the numbered seat identity); they are local seats' own launch identities, which the orchestrator pins outside the tree.

## Head

Code head `b8e2901167d1fe2cb676f916ff3fa74c0e6e0bb4` on `handoff/r10-hotfix-author-email`, 4 commits over origin/main `8a4cf2618c53`; all figures measured at it.

## Mutation proof

Three mutants of `tools/audit/seat/ref_privacy.py`, each run through `python3 tools/audit/seat/ref_privacy.py --self-test` (baseline 124 checks, 0 failed):
- `email_shape` returns `[]` (admits everything): 7 arms fail, among them "every placeholder or unnumbered form is refused" and both guard-CLI arms.
- the digits requirement dropped from `_NUMBERED` (`(?:\d+\+)?`): 5 arms fail, including the `seat@users.noreply.github.com` arm.
- the committer-only restriction on `noreply@github.com` dropped: 1 arm fails, "noreply@github.com passes as a committer only".
- the `PIN_HINT` print removed: 2 arms fail (the author and committer guard-CLI arms).
Each was restored with `git checkout`.

## Null control

On the unmodified tree the guard admits `seat@users.noreply.github.com` (self-test arms 0 failed at origin/main). At the head: the seat identity, `476059+Bankaifan@users.noreply.github.com`, `41898282+github-actions[bot]@...`, `hpo-author[bot]@users.noreply.github.com` and `331381602+hpo-author[bot]@...` pass; `noreply@github.com` passes as committer only; a `Co-authored-by:` trailer naming `476059+Bankaifan@users.noreply.github.com` and one naming `seat@users.noreply.github.com` is not judged (messages are not email-judged); the numbered fixture identity passes the guard CLI end to end.

## Figures

- `python3 tools/audit/seat/ref_privacy.py --self-test` prints 124 checks, 0 failed at the head (113 at origin/main).
- Writers: `git grep -nIE "(seat|hpo-fixer|noreply)@users\.noreply" -- tools .claude .github` finds none outside ref_privacy.py fixtures and the roster text.
- Other guarded self-tests at the head: `cloud_dispatch.py --self-test` 127 checks 0 failed; `ci_probe.py --self-test` 55 checks 0 failed; `prune_refs.py --self-test` 74 checks pass; `plan_public.py --self-test` pass; `delivery_row.sh --self-test` 6 checks 0 failed.
- `tools/pr/prepr.sh` at the head: every step ok except `self-test` (513 passed, 1 failed), the arm "a body naming only repository-relative paths and ~/ text passes (null control)". It sets `HOME` to a planted `/Users/exampleuser` and the pinned-python shim then exits 127 looking for `$HOME/.local/state/hpo/venv-ci`; the same `ref_privacy.py body-lines` call exits 127 on `git archive origin/main` as well as on the head, so it is a property of this macOS host, not of the diff.

## Red checks

none by CI (no PR yet). Note for the orchestrator: live local seats must pin the numbered identity or the guard now refuses their push; that pin is outside the tree. Local: `heartbeat.sh --self-test` has 1 failing arm ("null control: the same host's message naming another path is pushed") on this host; it fails identically at origin/main (run from a detached worktree of origin/main), and heartbeat.sh calls the guard with `--message` only, so the new rule cannot reach it. Carry: dismissed: pre-existing at main. The prepr `self-test` arm above is the same host-shim class. Carry: dismissed: pre-existing at main.

## Forward-carry

none

## Friction

none
