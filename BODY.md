Adds `dev/programme/triage/s6-batch6.md`: one ruling, P64 (S6-V10, opener worktrees blocking `update_pr.sh`), under `dev/governance/roles/proposal-triage.md`. The file is under `dev/programme/`, which `tests/closure.py` lists as INERT, the route the earlier batches took.

Verdict: P64 ACCEPT narrowed to R10-FLY-OPENPR-ATOMIC. Each instrument that pushes a PR branch from a worktree it keeps detaches that worktree once, after its run's last push, never inside app_push.sh. A later run that pushes from the same worktree re-attaches it first; handoff_push.sh's update arm is the one that does. `update_pr.sh --free-holders` is rejected because of where it sits, not because it is unsafe.

Round 3 repairs the round-2 block (`origin/review/2738` VERDICT.md, ruling-unsound):
1. The site census now uses a rule that returns `push_app` calls. It covers handoff_push.sh's update arm (`mut:push-update`) and gives every returned line a disposition. The update arm re-attaches with `git -C "$WT" checkout -q -B "$BR" "origin/$BR"` in place of its `reset --hard` and then detaches after its own push. The ruling also states each site's next run: open_pr.sh adds a fresh worktree with `-b`, and update_pr.sh removes and re-adds its worktree with `-B`. A self-test arm for update-after-open and a re-attach mutant are added to the carry.
2. "Why not --free-holders" now engages merge_train.py's `freeable`/`free_holder` and says the earlier safety argument was overstated. The `freeable` predicate loses nothing, wherever the worktree is. The rejection now rests on placement: it would be a second consumer-side copy, where a detach at the source frees the branch for every consumer. The helper adopts `freeable`'s predicate.
3. The uncited clause "the holder detached by hand for #2735 and #2738" is dropped. The update_pr.sh site is justified instead by what the tree shows: after a run its worktree stays on `$BR`, where merge_train.py's recarry stops on it as `HOLDER`.

The Instances line no longer names a host directory. It cites the s6 orchestrator's out-of-tree record by file name. Citations are anchored to markers (`mut:push-open`, `mut:push-row`, `mut:push-update`, `$D/p1.log`, `$D/p2.log`, the `OWN=` sweep, `freeable`, the `is not the committed tip` gate) rather than bare line numbers.

## Head

`664f74dce8fefcbd554fcd5f759f75d6ef740ec3`, merging origin/main `73b69fe0a` (2026-10-24T15:36Z) into the reviewed head `c24be17f8`.

## Mutation proof

n/a: nothing here changes code or a check; the file is a ruling record. Its consumer is the triage gate, and `roster_edit.ruling_verdict(src, "P64")` reads the one entry as `ACCEPT` at this head.

## Null control

`roster_edit.ruling_verdict` on a pid the file lacks (`P99`) returns `None` at this head.

## Figures

- Entries and verdicts: `grep -c '^Verdict:' dev/programme/triage/s6-batch6.md` prints 1. `ruling_verdict(..., "P64")` returns `ACCEPT`.
- Site census: `git grep -nE 'bash "?\$_push"?|push_app [0-9]' -- tools ':!tools/pr/app_push.sh' | wc -l` prints 8, and the ruling gives each of the 8 lines a disposition. Null control: the round-2 rule, `git grep -n 'app_push.sh\|\$_push' -- tools | grep -c 'push_app [0-9]'`, prints 0, so it could not see the update arm.
- Update-after-detach refusal: `origin/review/2738:evidence/repro_update_after_detach.txt` ends `RESULT update-after-detach app_push-gate=REFUSE`. That is the reviewer's repro, cited here rather than re-run.
- P64 Instances: 2, each cited by a grep in the ruling (seat-ledger.md lines 99 and 102, proposals.md line 89). These files are out of tree and cannot be re-derived from it.

## Red checks

- `governance / instrument-self-tests`, red at the previous head `c24be17f8` (job 120905519221). Its only failing step is "Refuse a push that names the host, and an unregistered pusher". In that step `ref_privacy.py --check` refused `dev/programme/triage/s6-batch6.md:9`, the P64 Instances line, which named the s6 orchestrator's host directory: `host-path in an added line of a tracked file ... 1 refused`. This head removes the path. `python3 -I tools/audit/seat/ref_privacy.py --check` prints `0 refused` at `664f74dce`. Null control: the same command run in a worktree at `c24be17f8` prints `1 refused`. No other step in that job failed. The roster_sync arm passed (`roster_sync self-test: 53 checks, 0 failed`), so this red is not the inherited roster_sync carries-open red. Cheaper detector: `ref_privacy.py --check` itself takes about 1 s locally (`/usr/bin/time -p`: real 1.05). But no pre-push step runs it on file contents. prepr.sh never calls it, and the `guard --commits` that app_push.sh, handoff_push.sh and body_push.sh run judges commit metadata, not added lines. Putting `--check` in prepr.sh would catch this class before the push, at about 1 s per prepr. That is a proposal for triage, not part of this diff.

## Forward-carry

n/a: the ACCEPT, re-attach included, routes to R10-FLY-OPENPR-ATOMIC through `roster_edit.py` citing this file once it is on main.

## Friction

none
