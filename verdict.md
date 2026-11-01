Fix review: blocked 32d880b3dee4e525d16ec270af83d867f7006431 root-cause-unrecorded: governance / instrument-self-tests

bus-nonce: b377adaaa9b21df0d76b1e02c1e66651

Round 2 (round 1 blocked d843403626ee923fe1fbde4428f3a0b2eb734b06, probe/rev-3077-fb5f8cf6).

## Block

`governance / instrument-self-tests` (job 124821822711, run 41297624984) concluded `failure` at this head at 10:55:15Z. The body's `## Red checks` says "none" and does not name it. Every workflow at the head has concluded; `gate` finished at 11:09:03Z. The `pr-contract` run that started at 11:07:56Z, after the last red, refuses on exactly this (ev/ci-pr-contract.log line 1894): "check `governance / instrument-self-tests` is red and `## Red checks` does not name it."

The cause, as I read it: the failing step is `open_pr.sh --self-test`, whose `pr_args self-test: 158 checks, 2 failed` comes from tools/audit/seat/pr_args.sh:625. That line symlinks `/bin/sleep` as `unrelated-sleep`. The runner's multicall coreutils refuses to run under that name: "Security violation: Requested utility `unrelated-sleep` does not match executable name: /usr/lib/cargo/bin/coreutils/sleep" (ev/ci-instrument-self-tests.log). The two failures are "FAIL open_pr: the null control -- an unrelated sleeper survives" and "FAIL null control: a normal successful update_pr leaves nothing behind and stops nothing it did not start". This diff touches neither pr_args.sh nor open_pr.sh. The same job is also red on #3084 (run 41296915291), so the red looks like the runner image, not this change. I did not read #3084's log for its cause.

The check is still red at the head, and the body owes it its answer (defect-root-cause.md, second trigger). A seat's own run of this self-test uses the seat's coreutils, so it cannot reproduce the failure, and the check itself is the cheapest detector. Hence `root-cause-unrecorded`. Fix: add the check to `## Red checks` with that answer, or with a cheaper detector if the fixer finds one. That is a body edit only; the code below is otherwise ready.

## Findings

- The runner-image coreutils break `pr_args.sh`'s `unrelated-sleep` symlink null control on every head that runs `instrument-self-tests` (seen here and on #3084). That is a cross-PR CI defect, not this diff's. Carry: dismissed: not this PR's code; the orchestrator's root-cause seat owns a red shared across pull requests, and this PR answers it only by naming it in its body
- Brief item 4, the forged-bot-email residual: the dismissal holds. A forged author email does pass `bot_author`, since git author fields are free text. What it gains is limited to that subject's own `bot_paths`. Each of those files is graded at every head by a required check that does not read the carry: a raise in `tests/mutation_budgets.json` by `budget-raise-gate` (required-contexts.json:37; it owner-gates any `*_budgets.json` raise at the head); `tests/closures.json` by `tests / closures` (required, line 51); a claim-file subject can only drop lines (the `*claims*` numstat arm) and env_drift grades the rest. Round 2 narrowed the old reach, any driver file, to the subject's own paths (my plant `bot-outside-paths` refuses at the head and carries at d84340362). I did not trace a separate grader for fresh rows under `tests/mutation_ledger/`. Carry: dismissed: dismissal holds, each bot path has a required at-head check besides the carry
- Round-1 O1 (carry-over-wide) is answered: see the plants under Evidence. Carry: dismissed: fixed at this head
- Round-1 O3 (the `.md` context mask over instruction files, and the "or keep its patch (L6)" clause) is raised for the owner in the body's `## Approval`, which answers it. Carry: dismissed: owner decision, raised in the body
- Round-1 P123 row-binding residual: restated and dismissed in the body as round 1 dismissed it, and I agree. Carry: dismissed: data file, one path, owner identity only

## Evidence

- Head measured: 32d880b3dee4e525d16ec270af83d867f7006431 (ev/HEAD.txt). Live head re-read before the verdict: unchanged (ev/live-head.txt). Judged from a detached worktree at that SHA. `git diff <merge base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Brief item 1, the four seams. Read from carry(): (a) a merge's tree check `git diff --quiet "$t" "$c" -- . ${x[@]}`; (b) the bare `ci:` confinement; (c) the bot-subject confinement `y=(...)`; (d) the own-commit tree check `git diff --quiet "$t" "$h"`. The end-state loop now reads every `.gitattributes` `merge=` file at the head.
- My plants are on real history (ev/plants.sh), each run with four carry scripts: round-1 `app_approve.sh`, this head's, this head's with M1 (the end-state refusal replaced by `:`), and this head's with M8 (the bot path test removed). Results at both verdict heads, d84340362 (ev/plants-at-r1head.txt) and 32d880b3d (ev/plants-at-head.txt), identical at each:
  - (d) own `fix:` commit that bumps a structure_budgets.json value: r1 yes, head NO, M1 yes (killed).
  - (d) own `fix:` commit that appends a claimed_drift.txt line: r1 yes, head NO, M1 yes.
  - (d) null, an empty own commit: yes in all four.
  - (b) `ci: tidy` by t@t that bumps closures.json: r1 yes, head NO, M1 yes.
  - (b) null, an empty `ci:` commit: yes in all four.
  - (c) `ci: re-record closures` with the github-actions email that bumps structure_budgets.json (outside its paths): r1 yes, head NO, M1 yes, M8 yes (killed by both).
  - (c) null, the same subject bumping its own closures.json: yes in all four.
  - (a) a merge of a fake main (origin/main plus one README line) with structure_budgets.json hand-edited in the merge: r1 yes, head NO, M1 yes.
  - (a) null, the same merge automatic: yes in all four.
- Brief item 2: the eight body mutants. Each was a single-occurrence replacement (ev/mut.py asserts count==1), run in its own detached worktree at the head, then restored and checked with `git diff --quiet` (ev/mut-M*.log). All are killed: M1 14 failed, M2 2, M3 2, M4 1, M5 1, M6 27, M7 2, M8 2. The failing rows match the body's names. M1 and M6 also fail the rows 25c2038d0 added, which accounts for the body's 12 and 24 (the body says those ran before 25c2038d0).
- Brief item 3: my round-1 budget and claim plants refuse at this head and carry under the round-1 script. The empty-commit null carries (above).
- Self-tests at the head, Linux, `env -u BASH_ENV`: app_approve 316 checks, 0 failed; app_comment 67/0; app_push 204/0; bus 110/0; review_carry 29/0; merge_train 400/0. merge_train's 400 against the body's 381 comes from main's merge_train.py changes merged in at 32d880b3d. I could not re-derive the body's 314 for app_approve: the file is byte-identical between 25c2038d0 and this head and reads 316 here. The difference is likely the platform, but I did not establish that.
- Gate: `tools/pr/prepr.sh` at this head with no body: `PRE-PR: 32d880b3dee4e525d16ec270af83d867f7006431 ... rc=0` (ev/prepr.txt). The body's own line names 25c2038d0, the code head, not this merge head. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (structure.py has no `summary` argument). Scoped gate: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. Both claim files are byte-identical to origin/main. VERSION, the manifest and the notes heading are untouched in the three-dot diff. The delivery row dev/programme/delivery/3077.md is in the three-dot diff.
- `git merge-tree --write-tree origin/main 32d880b3d` against origin/main 6421fe135: exit 0, no conflict (ev/merge-tree.txt).
- CI: `merge_train.py classify` exited 1 (RED, "red: gate", ev/classify.txt). The red contexts are `governance / instrument-self-tests` (the block), then `pr-contract / pr-contract` and `gate` as consequences. Every other required context is success or skipped. `budget-raise-gate`, `tests / closures`, `tests / fast (3.14)`, `tests / mutation` and `arch-score` are green.
- Not re-run: the archscore figure (dS +0.0000), cited from CI's green `arch-score`, and the gate or mutation table (CI's heavy runs).
