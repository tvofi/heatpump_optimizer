R10-HOTFIX-AUTHOR-EMAIL (triage s6-batch133 P408, owner hotfix tier, 2026-11-07). Commits reached main under placeholder or unnumbered author and committer emails (`seat@`, `hpo-fixer@`, `noreply@users.noreply.github.com`, `t@t`, `fixer@invalid`), which GitHub credits to unrelated accounts. History is not rewritten; this refuses the bad shapes on every commit a push newly publishes. `ref_privacy.py`'s guard now refuses `unnumbered-email` for any author or committer email outside this grammar: `<digits>+<login>@users.noreply.github.com` (the seat identity `70032254+tvofi@...` included), `[<digits>+]<name>[bot]@users.noreply.github.com`, `noreply@github.com` as committer only, and an adopted outside contributor's own address named per adoption by `--adopt-email ADDR` (author only). The refusal prints the exact pin (`-c user.name=tvofi -c user.email=70032254+tvofi@...`, `--author`, or the per-worktree `git config --worktree user.email` form) so a refused seat can self-correct. The fixture identity in `tests/throwaway_git.{py,sh}` moves from `t@t` to `1+t@users.noreply.github.com` so guarded self-tests keep passing. Writers of `seat@` and `hpo-fixer@`: none are in the tree (cloud-setup.sh, cloud_dispatch.py, update_pr.sh, open_pr.sh and delivery_row.sh already pin the numbered seat identity); they are local seats' own launch identities, which the orchestrator pins outside the tree.

## Head

Second repair round: `governance / instrument-self-tests` (job 128917294764) failed `plan_audit self-test: 27 checks, 1 failed`: `tools/audit/seat/plan_audit.py` asserted `git var GIT_AUTHOR_IDENT` starts with the literal `t <t@t>`, the fixture's old address. Code head: `84bd4fb40e87530ea6b27ba2ec0d97f4d235fb00`, on `45339147f9fbeffb50df4cbcf047ac248b94efb4`. Code from the first round is unchanged (`ref_privacy.py`, `tests/throwaway_git.*`).

## Mutation proof (plan_audit repair)

The assertion now builds its expected prefix from `throwaway_git.IDENTITY`, the fixture's one definition (alternatives: a second literal `1+t@users...` in plan_audit, which recurs at the next identity change; or dropping the assertion, which loses the check that the harness identity beats the box's). `delivery_row.sh`'s stale comment now names `IDENTITY` and no address. Null controls: with `IDENTITY` emails changed to `2+t@...`, `python3 tools/audit/seat/plan_audit.py --self-test` still ends `27 checks, 0 failed` (reads the definition); with the pre-fix `plan_audit.py` and the same change it ends `27 checks, 1 failed` (the hard-coded literal). Unchanged tree: `27 checks, 0 failed`; `bash tools/audit/seat/delivery_row.sh --self-test` `6 checks, 0 failed`.

## Mutation proof

Three mutants of `tools/audit/seat/ref_privacy.py`, each run through `python3 tools/audit/seat/ref_privacy.py --self-test` (baseline 124 checks, 0 failed):
- `email_shape` returns `[]` (admits everything): 7 arms fail, among them "every placeholder or unnumbered form is refused" and both guard-CLI arms.
- the digits requirement dropped from `_NUMBERED` (`(?:\d+\+)?`): 5 arms fail, including the `seat@users.noreply.github.com` arm.
- the committer-only restriction on `noreply@github.com` dropped: 1 arm fails, "noreply@github.com passes as a committer only".
- the `PIN_HINT` print removed: 2 arms fail (the author and committer guard-CLI arms).
Each was restored with `git checkout`.

## Repair of the instrument-self-tests red

Cause: `tools/pr/app_push.sh --self-test` stubs `git log` output for ref_privacy's guard with `t@t` author and committer (the stub at the `--not refs/remotes/origin/main` case, and a fast-import fixture's committer). The new `unnumbered-email` rule refuses `t@t`, so prepr's stub exited 2 before the mint and every arm after it failed. This is the branch's own doing (the guard it adds), not main's.
Fix: the `t@t` stub identities (the commit read's author and committer, and the fast-import fixture's committer) become `1+t@users.noreply.github.com`, as `tests/throwaway_git.*` already did.
Null control: `bash tools/pr/app_push.sh --self-test` at the red head ends `227 checks, 89 failed` in CI (job 128808974627) and `FAIL` lines locally; at origin/main it ends `227 checks, 0 failed`; at the repaired head it ends `227 checks, 0 failed`.
Mutation proof: reverting the three stub lines restores the red head's `89 failed`.

## Null control

On the unmodified tree the guard admits `seat@users.noreply.github.com` (self-test arms 0 failed at origin/main). At the head: the seat identity, `476059+Bankaifan@users.noreply.github.com`, `41898282+github-actions[bot]@...`, `hpo-author[bot]@users.noreply.github.com` and `331381602+hpo-author[bot]@...` pass; `noreply@github.com` passes as committer only; a `Co-authored-by:` trailer naming `476059+Bankaifan@users.noreply.github.com` and one naming `seat@users.noreply.github.com` is not judged (messages are not email-judged); the numbered fixture identity passes the guard CLI end to end.

## Figures

- Census (class: a consumer that hard-codes the fixture identity string), run at the code head: `git grep -nIE '(^|[^[:alnum:]_.+-])t@t([^[:alnum:]]|$)' -- . ':!dev/audit/rounds' ':!dev/programme'` prints 47 lines in 12 files; `git grep -nE 'GIT_AUTHOR_IDENT|GIT_COMMITTER_IDENT' -- tests tools .claude` prints the `plan_audit.py` read alone. Dispositions: `plan_audit.py` (the one reader of the fixture identity): closed in this diff; `delivery_row.sh` comment: closed in this diff; 3 lines in `ref_privacy.py` (docs and the refused-placeholder list): the guard's own subject, kept; the remaining 42 in `stop-selfcheck.sh`, `git_auto_maintenance_race.sh`, `entities.py`, `layout.py`, `bus.sh`, `cloud_relay.sh`, `open_driver_selftest.py`, `r9_rc_bus_fetchhead.sh`, `review_carry.py`, `brief_lint.mjs`, `prepr.sh`: each sets its own `-c user.email=t@t` (or `git config`) on a git call and reads no fixture identity: already guarded, none reaches `ref_privacy`'s guard (CI shows only app_push and plan_audit failing). Null control: the census's pattern is blind to `1+t@users` (the `+` is excluded before `t`), so it counts only the old spelling.

- `python3 tools/audit/seat/ref_privacy.py --self-test` prints 124 checks, 0 failed at the head (113 at origin/main).
- Writers: `git grep -nIE "(seat|hpo-fixer|noreply)@users\.noreply" -- tools .claude .github` finds none outside ref_privacy.py fixtures and the roster text.
- Other guarded self-tests at the head: `cloud_dispatch.py --self-test` 127 checks 0 failed; `ci_probe.py --self-test` 55 checks 0 failed; `prune_refs.py --self-test` 74 checks pass; `plan_public.py --self-test` pass; `delivery_row.sh --self-test` 6 checks 0 failed.
- `tools/pr/prepr.sh` at the head: every step ok except `self-test` (513 passed, 1 failed), the arm "a body naming only repository-relative paths and ~/ text passes (null control)". It sets `HOME` to a planted `/Users/exampleuser` and the pinned-python shim then exits 127 looking for `$HOME/.local/state/hpo/venv-ci`; the same `ref_privacy.py body-lines` call exits 127 on `git archive origin/main` as well as on the head, so it is a property of this macOS host, not of the diff.

## Red checks

- `governance / instrument-self-tests` (job 128917294764, `plan_audit self-test: 27 checks, 1 failed`): red at 45339147f, answered here. Cheaper detector: the census `git grep -nIE '(^|[^[:alnum:]_.+-])t@t([^[:alnum:]]|$)' -- . ':!dev/audit/rounds' ':!dev/programme'` plus `git grep -n 'GIT_AUTHOR_IDENT'`, run whenever `tests/throwaway_git.*`'s identity changes; standing cost about 1 s per such change, which happens rarely (this is its first move). No hook built: the consumer set is now one reader of the definition, so a further move cannot recur on this class.

- `governance / instrument-self-tests` (job 128808974627): red, answered above. Cheaper detector: `bash tools/pr/app_push.sh --self-test` runs in about a minute locally, and `tests/closures.json` does not select it from a `ref_privacy.py` diff; the closure that reaches `app_push.sh`'s stub is only the governance job. Standing cost: a guarded-stub census (`git grep -n "t@t" -- tools tests`) at each change to the guard's grammar, seconds; no hook built, since the guard is changed rarely. Other guarded stubs with `t@t` (`bus.sh`, `cloud_relay.sh`, `open_driver_selftest.py`, `review_carry.py`) pass `-c user.email` to git commits and never reach the guard; CI shows only app_push failing.
- `gate` (128814942428, 128809302557): aggregate of `pr-contract`, which this body fixes by naming the red; no code cause of its own.
- `pr-contract` (128814600834): red because this section did not name `governance / instrument-self-tests`; answered here.

Note for the orchestrator: live local seats must pin the numbered identity or the guard now refuses their push; that pin is outside the tree. Local: `heartbeat.sh --self-test` has 1 failing arm on a macOS host, identical at origin/main. Carry: dismissed: pre-existing at main.

## Forward-carry

none

## Friction

none
