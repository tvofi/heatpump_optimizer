Adds `dev/programme/triage/s6-batch6.md`: one ruling, P64 (S6-V10, opener worktrees blocking `update_pr.sh`), under `dev/governance/roles/proposal-triage.md`. The file is under `dev/programme/`, which `tests/closure.py` lists as INERT.

Verdict: P64 is ACCEPT, narrowed to R10-FLY-OPENPR-ATOMIC. Each instrument that pushes a PR branch from a worktree it keeps detaches that worktree once, after its run's last push, and only when the worktree is clean and HEAD equals the pushed sha. The detach is never inside app_push.sh. handoff_push.sh's update arm re-attaches with `git checkout -q -f -B "$BR" "origin/$BR"` and keeps its `reset -q --hard`, so it never carries a dirty worktree. `update_pr.sh --free-holders` is rejected. The open points are four `Carry:` lines to R10-FLY-OPENPR-ATOMIC in the ruling.

## Head

`b2ab643173f7dc68713db1a56e748b23b9ef587a`, which merges origin/main `806aa2ce8` into `d1756ee44`.

## Mutation proof

n/a: the diff writes no code and no check. The file is a ruling record, and its consumer is the triage gate: `roster_edit.ruling_verdict(src, "P64")` returns `ACCEPT` at this head.

## Null control

At this head, `roster_edit.ruling_verdict` returns `None` for a pid the file lacks (`P99`).

## Figures

- Verdicts: `grep -c '^Verdict:' dev/programme/triage/s6-batch6.md` prints 1.
- Site census: `git grep -nE 'bash "?\$_push"?|push_app [0-9]' -- tools ':!tools/pr/app_push.sh' | wc -l` prints 8, and the ruling's Sites line names each of the 8.
- Re-attach: in a scratch repository, a detached worktree with a tracked edit was put through the update arm two ways. Today's arm, `reset -q --hard`, leaves `HEAD` detached and the tree clean. The prescribed `checkout -q -f -B br origin/br` followed by that reset leaves it on `refs/heads/br` and clean, with `status --porcelain` empty.
- Host paths: `python3 -I tools/audit/seat/ref_privacy.py --check` prints `0 refused` at this head.

## Red checks

- `governance / instrument-self-tests` at `c24be17f8`, job 120905519221. Its step "Refuse a push that names the host" refused `dev/programme/triage/s6-batch6.md:9`, where the Instances line named a host directory. That path is gone, and `ref_privacy.py --check` prints `0 refused` at this head. A cheaper detector exists: `ref_privacy.py --check` takes about 1 s locally, but no pre-push step runs it on added lines. Calling it from prepr.sh would catch this before the push for about 1 s per run. That is a proposal for triage, not part of this diff.
- `pr-contract / pr-contract` at `c24be17f8`, jobs 120911228627 and 120914579657. Both are the body-contract refusal for the unnamed red above, and naming it here answers them. At `d1756ee44`, job 120919828039 failed at the `codescan_wait.py` step while CodeQL was still running; the analysis concluded success afterwards. No cheaper detector exists for that one, because it is a wait on another workflow.
- `gate` at `c24be17f8` and `d1756ee44`. It repeats the reds above and the `still being judged` wait on runs that were in progress. It has no failure of its own, so no detector is owed.

## Forward-carry

n/a: the ACCEPT and its four `Carry:` lines route to R10-FLY-OPENPR-ATOMIC through `roster_edit.py`, citing this file once it is on main.

## Friction

none
