Fix review: merge 9c8ca4f7acfae4366671942a34afa978e722643e

bus-nonce: ecf6e731d44169c53cd209ababef94a2

## Summary

Round 1, first-round adversarial fix review of #3256 (R10-POLICY-ROLE-PACK, partial delivery of #2717), from a detached worktree at 9c8ca4f7acfae4366671942a34afa978e722643e, merge base 30638cf0c8a7114019682f87051a4a282d2981ff. No role contract changed on main since the merge base (`git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty).

**This is a POLICY pull request.** It changes `dev/governance/roles/nudge.md` (POLICY_GLOBS) and the code-owned paths `.claude/hooks/session-start.sh` and `dev/governance/roles/` (`.github/CODEOWNERS` `@tvofi`). It merges ONLY on the owner's (tvofi) approving GitHub review at this head, or under the mandate the roster's `owner_gate` names (6329234399). This verdict is not that approval.

### Every changed policy sentence, for the owner (from ev/nudge-diff.txt)

1. `nudge.md` step 3, removed: "Leave out of the queue: a change to a `*_budgets.json` file, a policy path as `policy_lint.mjs --corpus-filter` defines it, and a `record:` pull request, which `--bot-prs` merges. Never pass `--allow-red`."
   Added: "Leave out a `record:` pull request, which `--bot-prs` merges. A `*_budgets.json` or policy-path head stays in: the train routes it serial, and `--pre-flight` parks one the owner has not approved at that head (`Train.raise_hold`, `Train.policy_gate`) for step 7. Never pass `--allow-red`."
2. `nudge.md` step 3 command: `merge_train.py run <queue.json> --mandate ...` becomes `merge_train.py run <queue.json> --bot-prs --pre-flight --mandate ...` (the `--ignore-red` arguments are unchanged).
3. `nudge.md` step 7, removed: "Direct-merge only what step 3 leaves out of the queue, other than a `record:` pull request: a budgets-file or policy-path pull request whose mandate review is already on that head."
   Added: "Direct-merge only what `--pre-flight` parked: a budgets-file or policy-path pull request whose mandate review is already on that head." The rest of step 7 is unchanged.
4. `.claude/hooks/session-start.sh` (code-owned): when `HPO_SEAT_ROLE` names a role, the hook writes the role pack to `git rev-parse --git-path role-pack-<role>.md` and prints one `role pack:` line. When the variable is unset, the output is unchanged.

## Evidence

- RESULT ci: `merge_train.py classify 9c8ca4f7acfae4366671942a34afa978e722643e --pr 3256` printed `GREEN 9c8ca4f7acfae4366671942a34afa978e722643e pending: none red: none` (rc 0) at 17:58:28Z (ev/classify.log). Earlier runs of the classifier printed RED and then WAIT on `gate`.
  - Gate job 128053723956 (run 42255236501) failed with "FAIL run(s) [42264496323] at this head are still being judged; their gate decides". That is a deferral, not a cause.
  - The gate of run 42264496323 (128056441642) concluded success, and so did the gate of run 42255235770 (128053721808).
- Check runs: I read all 68 check runs of the head in one page (total_count 68). The only non-success, non-skipped results:
  - `governance / instrument-self-tests` 128053713196 was cancelled at its 30-minute limit (16:54:40 to 17:24:42). That is the owner's standing line (cure R10-PROCESS-SLIM, #3245), not a finding.
  - The deferring gate above.
  - Every other required context succeeded. That includes `governance / policy-docs`, which runs the hook's `--self-test`, and so `role_pack.py --self-test`, in CI.
- Red checks of the earlier head 9478bca5: the body names and answers each one (instrument-self-tests census, codeql python, pr-contract, gate aggregate), each with its cheaper detector or the finding that none exists. The pr-contract run 128054392050, started after the last red, concluded success. Step 11 is answered.
- RESULT role_pack self-test: `35 passed, 0 failed`. `role_pack.py check`: all 8 roles `ok`. The `sizes` table matches the body exactly: fixer 55676/36004/42744 and judge 36737/17065/22824 (ev/checks.txt).
- RESULT hook self-test: `24 passed, 0 failed`. `pr_args.sh --self-test`: `174 checks, 0 failed`. `pr_pushers`: rc 0, no OPEN line. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Attack (1), planted packs checked with `role_pack.py check fixer --pack` (ev/plants.txt). The null control, the clean render, gives rc 0. Each plant is refused by its own rule, rc 1:
  - paraphrase: "not byte-equal to the file"
  - missing rule block: "in the role's plan, absent from the pack"
  - CLAUDE.md framed: "framed, but not in the role's plan"
  - stray line: "a line outside every frame"
  - contract framed twice: "the framed text (62384 chars) exceeds the files it frames (55676)"
- Rule derivation (attack 1), checked independently. I listed every rule's `paths:` globs. `dev/governance/**` matches the contracts in brief-citations, defect-root-cause, finding-propagation and writing-for-agents, and no rule's glob matches `tools/audit/seat/INSTRUMENTS.md`. That is exactly the fixer pack's 4 rule blocks.
  - In a scratch worktree I planted a rule with `paths: dev/governance/roles/fix*.md`. It entered the fixer pack (1) and not the judge pack (0).
  - With its glob changed to a non-match, it left the fixer pack (0). The rules are derived at render, never listed.
- Attack (2), the hook against the base hook (ev/hook.txt):
  - Unset, the base hook's output (from `git show <merge-base>:.claude/hooks/session-start.sh`) and the head hook's output are byte-equal: `cmp` is silent, 327 bytes.
  - `HPO_SEAT_ROLE=` (set but empty) is also byte-equal to unset.
  - Set to fixer, the output gains exactly one `role pack:` line.
  - `planner` prints a REFUSE line, and the session still starts.
- My mutants (ev/my-mutants.txt), both killed:
  - M1: the hook's `[ -n "${HPO_SEAT_ROLE:-}" ] && role_pack` line replaced with `:` gives `19 passed, 5 failed`.
  - M2: `elif text != source` changed to `elif False` gives `34 passed, 1 failed` ("one contract line paraphrased: not refused"), and the paraphrase plant then checks rc 0.
- Attack (3), the census repair (ev/census-plants.txt, ev/census-grep.txt):
  - `grep -nE 'subprocess|os\.system|Popen|exec' tools/policy/role_pack.py` exits 1, and its imports are only argparse, fnmatch, re, sys and pathlib. The positive control, the same grep on `merge_train.py`, counts 27, as the body says.
  - `PR_PUSHER_RULE` is unchanged against origin/main.
  - A planted new `tools/policy/new_pusher.py` that runs `app_push.sh` is refused: `OPEN ... undispositioned`, rc 1. The null control at the head is rc 0. With the repair line deleted, role_pack.py is OPEN again, rc 1.
  - The stated departure (no narrower rule) is sound: an over-inclusive census with dispositions by hand is the safe direction, and the `mention:` entry is the census's existing disposition, beside its siblings.
- Figure slip in the body, not blocking: it says the rule matches role_pack.py lines 46, 272 and 275. It also matches 276 (`"`push.sh` is not named by `app_push.sh`")`). The disposition does not depend on the count.
- Attack (4), partial delivery: the body states it does not close #2717. Its text has no GitHub closing keyword (close/closes/closed, fix/fixes/fixed, resolve/resolves/resolved) followed by an issue reference. "closed in this diff (nudge.md ...)" names no issue.
- Attack (5), claim files and versions: the three-dot diff of `tests/golden/claimed_drift.txt`, `card_claimed_drift.txt`, `VERSION`, `RELEASE_NOTES.md`, the manifest and `*budgets.json` is empty. There is no budget raise.
- Merge with main: `git merge-tree --write-tree origin/main 9c8ca4f7` exits 0, tree b57ca06c03e7116425a45e1d493629970cd33bd1. No claim-driver line appears, because no claim file conflicts.
- Finder's harness: this group has none (a policy and instrument feature). The packet says "none named". The instruments I used are the PR's own `check`/`--self-test`, `pr_pushers` and my plants, each disclosed above. My plants live only in this ev/ directory and change no reusable instrument.
- Architecture score: the body says `dS +0.0000 NULL`. I did not re-run it. CI's `arch-score` check succeeded at this head.
- Forward-carry (step 10): the two residuals (no pack for cloud seats; local Agent-tool seat briefs must name `render`) and the Friction contradiction are carried to #2717, which stays open. carry_audit at the head: 4 items routed, 0 unrouted.
- Head check: the PR head was 9c8ca4f7acfae4366671942a34afa978e722643e when I read the PR. I re-checked it immediately before pushing this verdict.

## Findings

- `role_pack.py check --pack` accepts a pack with a whole rule block framed twice. Appending `brief-citations.md` (3,492 chars) a second time to the clean fixer pack still checks `ok fixer: 46236 chars, 7 blocks`, rc 0 (ev/plants.txt `dup_rule`, ev/dup_rule.md). The size rule counts the whole of INSTRUMENTS.md (about 19.6k chars) although the pack frames only the named entries, which leaves about 13k chars of slack for duplicated blocks. The body's literal claim ("a pack larger than the files it frames") holds, and the hook always writes `render` output, so no seat is misled today. But the verbatim, one-read intent is not enforced on `--pack` input. Cure: refuse a repeated BEGIN path, or compare `--pack` with `render(role)` byte for byte. Carry: #2717
