Record PR: rewrites `dev/programme/HANDOVER.md` in place against main `a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0` (merge of #3016); `updated-for:` names that merge. The file was last written on main at `b161681af` (2026-10-23). It now states what a resuming session cannot derive in one command:
- the standing seats and their contracts;
- the instruments in daily use, as a pointer to `tools/audit/seat/INSTRUMENTS.md`, not a restatement;
- the mandate's operating rules: read from the API at use; the kill stem voids it beside an id, and an identifier such as a group name counts; scope `all` means the orchestrator approves code-owned, policy and budget-raise merges;
- the critical path to closure, as `roster_lib.critical_path` derives it;
- the merge, train and stamp sequence, including decision 0016's `--round-close 10`.

Removed because false or answered by the tree:
- the 2026-10-14 mandate and its dates (superseded; the id and dates live on #201);
- the owed item that the soft-cap instrument refuses an owed handoff (`pr_cap.py dispatch-gate` now exists and states the exemption);
- the per-merge chronology.

Volatile state (open PRs, the cap in force, the mandate id) is left to #201 by pointer. Not policy: the file sits outside `POLICY_GLOBS`, so no `## Approval` is owed. It surfaces one divergence under Owed: `standing-merge.md` still names `merge_pr.sh` for budget and policy heads, which the owner's 2026-10-26 ruling supersedes. That policy edit is not made here.

## Round-1 block, answered

**rule-lost: the owner's 2026-09-09 model-routing ruling was deleted.** Restored under "Decisions taken", whole: Opus, Sonnet and Fable each with its scope, and the model-trailer clause. A pointer ties it to the seats section's effort line, which it does not contradict.

The class is a rule the rewrite cut, not this one rule. The verification is therefore over every base item, per `orchestrator.md` section 6: both parents rebuilt, and the merged artifact read back against them. main's side is empty: `git diff --stat 8fec54ee2 origin/main -- dev/programme/HANDOVER.md` prints nothing, so the base file at the merge base is the other parent. The rule that enumerates the seams covers every `**...**` span in the base file (123 spans) that is neither found verbatim in the head nor has at least 80% of its words of four or more characters in the head. After the round-2 edits, 22 spans are below that threshold. Each was read in both files, with this disposition:

- Restored in this round (they had been cut):
  - the model-routing ruling;
  - the traps preamble's "promotion, not cutting";
  - the graduated traps as one-line pointers, each detector checked present in the tree: `tools/policy/policy_lint_envmatrix.mjs` (#387), `tools/policy/check-wave-script.mjs` with `policy_lint --hooks`, the depth-1 driver refusal in `tests/entities.py` (#901), `.claude/hooks/session-start.sh`, `policy-docs`'s `[budgets]` (#608), `policy_lint`'s `citations`, `policy_lint --record`'s `table` check, and the sectioned config-flow schema assertion;
  - the trap "six of this project's own instruments reported rather than measured";
  - the closing keyword in a branch's commit message (#503);
  - re-pointing a branch chain by position;
  - `_ABSENT_FALLBACKS` (#1107), restored as a pointer because its detector is now proven (Mutation proof).
- Present in rewritten form in the head: the cloud-seat dispatch (Seat placement), the body as one live object, the `hpo-ledger` bypass, the instance-not-property trap with its record-artifact point, the leftover sweep (#715, #690), #1116 and #1121, the repair empty by construction, `CANCELLED`, the post-hoc reviews and the `fixer.md` finding (Owed), only-arm inputs, and the count trap ("Derive it").
- Kept in another file: "every sentence earns its place" (`writing-for-agents.md`) and the read-back trap (`comment-readback.md`, "Byte-identity against the file you sent").
- History, ruled so by the round-1 review: #510 and the `f605da4` measurement.
- Removed as false or answered, per the description above: mandate 6175172275 and the soft-cap owed item.

The round-1 review also found the `_ABSENT_FALLBACKS` bullet removed with no detector confirmed. It is restored as a graduated pointer, and its detector is now proven by mutation.

## Head

`7d180484d4b7a04c0d6dba593806c40b630a38a5` (round 2). Two commits on the round-1 head 6502ddfcfd985f97998bbc369fc8807ae81cd9ca: afeba7de3 and 7d180484d. Merge base 8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f. main was not merged: `git merge-tree --write-tree origin/main HEAD` exits 0 against origin/main 92588d581fde4ce287af3db5e8bb61461dc28015 at 2026-11-01T08:55Z, which has not touched `dev/programme/HANDOVER.md` since the merge base.

## Figures

- The rule enumeration above: an inline Python pass over `git show 8fec54ee2:dev/programme/HANDOVER.md` and the head file. It reports 123 bold spans and, below threshold, 29 at the round-1 head and 22 at this head. Each of the 22 is dispositioned above.
- Detectors named by the restored pointers: `git ls-files --error-unmatch` on `tools/policy/policy_lint_envmatrix.mjs`, `tools/policy/check-wave-script.mjs` and `.claude/hooks/session-start.sh`, each present. The two `policy_lint` modes and the `entities.py` refusals were each found by `grep` in their files.
- Handover checks: `tests/entities.py` stops on this Mac at `_hb_stdlib_reads` (task-port `PermissionError`) and waits on the shared heavy slot. Its handover block was therefore run alone: the slice from "# One living handover (#518)" to "# --- the real-Home-Assistant lane's own reporting", exec'd with `tests/closure.py` imported and a recording `R` stub, printed `handover block: 4 checks, 0 failed` at this head.
- The scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. It names `tests/entities.py`, which is CI's `tests / fast` in full.
- Structure ratchet at this head: `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED.
- Layout guard: `python3 -I tests/layout.py --guard --base $(git merge-base origin/main HEAD)` printed GUARD: 0 refusal(s).
- Policy lint: `node tools/policy/policy_lint.mjs` printed TOTAL: 0 error(s) across 50 policy file(s).
- prepr: `tools/pr/prepr.sh <body>` printed `PRE-PR: 7d180484d4b7a04c0d6dba593806c40b630a38a5 0000000000000000000000 rc=0` (2026-11-01, on a committed tree).
- The critical path named in the file: load `wave-r10-groups.json` from `origin/handoff/audit-r10-roster` and call `critical_path` in `tools/audit/seat/roster_lib.py`. It is a snapshot dated 2026-10-31, and the file says to re-derive it.

## Mutation proof

The diff touches no production, test or check code. The one restored claim that names a detector which nothing had proven, `_ABSENT_FALLBACKS`, was proven in a detached scratch worktree at this head:
- `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` printed `ALL 534 checks PASSED` (rc 0) on the unmutated tree.
- The mutant drops one key, `away_temperature`, from `config_flow._ABSENT_FALLBACKS`'s derivation: `and key != "away_temperature"` was appended to its filter. With it, the same run printed `4 of 534 checks FAILED` (rc 1). The first was `FAIL _ABSENT_FALLBACKS is exactly the proven set [unproven but listed: []; proven but missing: ['away_temperature']]`; the three others were reload checks.
- The tree was restored (`git diff --quiet`) and the worktree removed.

## Null control

- The handover block with the `updated-for:` line deleted printed `handover block: 4 checks, 3 failed`. The file was then restored by `git checkout` and confirmed by `git diff --quiet`.
- The enumeration's own null: spans the head carries verbatim, such as "A gate cannot be its own witness", score at or above the threshold and are not listed.

## Red checks

none

## Forward-carry

none

## Friction

none
