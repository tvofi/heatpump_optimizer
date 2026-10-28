Roster seat result for r10-roster-lint: no new roster edit was owed. `handoff/audit-r10-roster` already carried both the fix for the one lint error and the five `fixes` wires when this seat ran. This head is that branch's tip, unchanged.

## Head

`de410e4c923bdacfd4a06140a7453225f866e652` (`origin/handoff/audit-r10-roster` tip). Base `origin/main` is `e8cb7e68302b1d350bb8219fea99e911170af030`, which is also the merge-base. `git merge --no-edit origin/main` into the roster branch printed `Already up to date.` That disproves the brief's premise that main carries roster changes the branch lacks. This seat wrote no commit.

## Mutation proof

No production line was added, so there is nothing to mutate. The lint error's cause and its removal are shown under Null control.

## Null control

The lint error text, reproduced by `node tools/policy/brief_lint.mjs <roster>`. The run used a detached worktree at `origin/main` (`e8cb7e683`), not `--apply`. It linted the roster from `9aed78e0e`, the roster-branch commit before main was merged in:

    ERROR   [R10-IMMERSION-LATCH] path:line: const.py:1149: 'heatpump_optimizer' not found near custom_components/heatpump_optimizer/const.py:1149; found at line 10 instead
    TOTAL: 1 error(s) across 1 file(s)
    rc=1

Cause: v7.0.5 on main (`e8cb7e683`) moved `const.py`. That left R10-IMMERSION-LATCH's `const.py:1149` citation off its anchor. Every `roster_edit.py` op, and `roster_sync.py --apply`, then lints the whole roster from an `origin/main` checkout. So any edit was refused for this unrelated group's citation, not for its own change. That covers the five `wire-issue R10-RCA-FRICTION-RESIDUE --field fixes` ops.

Fix: commit `826c0f6ea` re-pinned the citation 1149 -> 1156. It is already on the roster branch (a merge of `origin/main` into it). The same lint, same `origin/main` worktree, over the roster at `826c0f6ea` and at `de410e4c9`:

    TOTAL: 0 error(s) across 1 file(s)
    rc=0

The 1149 roster is the control: it is the one input that differs, and it reads 1 error where the re-pinned one reads 0.

## Figures

- `git show <ref>:dev/programme/rosters/wave-r10-groups.json | jq -c '.. | objects | select(.group?=="R10-RCA-FRICTION-RESIDUE") | .fixes'`:
  - at `origin/handoff/audit-r10-roster` (`de410e4c9`): `[2410,2593,2597,2660,2784]`
  - at `origin/main` (`e8cb7e683`): `[]`, the control showing the field is the roster branch's own.
- Re-sending the first op, `roster_edit.py wire-issue R10-RCA-FRICTION-RESIDUE 2410 --field fixes`, without `--push`, with `--roster-ref origin/handoff/audit-r10-roster` and `--lint-cwd` at an `origin/main` worktree:
  `roster_edit: REFUSED: R10-RCA-FRICTION-RESIDUE already wires #2410 in fixes` (rc 2).
  - The wires landed earlier, in roster-branch commits `e331abfbf`, `d61e2834c`, `8a2310fc9`, `eb880dba1` and `9aed78e0e`.
  - The other four ops would hit the same duplicate refusal, since the field already holds all five issues. They were not sent.
- `roster_sync.py --roster-ref origin/handoff/audit-r10-roster` (dry run) printed `no derived change on handoff/audit-r10-roster; nothing written` (rc 0).
  - Input: `--pr-state` built from the REST pulls list (`gh api repos/tvofi/heatpump_optimizer/pulls?state=all`), cut to the tool's `DEFAULT_LIMIT` rows. This was needed because `gh pr list` (GraphQL) is refused from this session: `roster_sync: REFUSED: UNREADABLE gh pr list ... HTTP 403: GitHub GraphQL is not available`.
  - `--apply` was not run. It always pushes to `handoff/audit-r10-roster`, which is not this seat's return ref, and with no derived change it would have written nothing.

## Red checks

None. No check ran red on a commit of this seat's; it pushed no commit.

## Forward-carry

- A roster-wide lint gate refuses every op whenever main moves a cited line under any live group. That is how five unrelated wire ops were refused. `standing-roster.md` already names the remedy: merge `origin/main` and re-lint. Carry: dismissed: the contract already carries it, and `826c0f6ea` applied it.

## Friction

none
