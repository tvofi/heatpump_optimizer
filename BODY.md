Triage batch 83 rules the orchestrator s8's slip proposal of 2026-10-31. PR #3016's seat commits are authored `Claude <noreply@anthropic.com>` (cloud round 1) and `tvofi` (local round 2), and nothing refuses them. It is the next rolling batch under V182, after batch 82. It holds one ruling and one held roster op.

- **P320: ACCEPT as already carried, narrowed, with an amendment and a priority flag, on R10-FLY-NO-FOOTERS.**
  - The refusal is P253 (`s6-batch51.md`): an `anthropic-identity` class in `ref_privacy.email_leaks`, run at the opener. It is still unbuilt; `ref_privacy.py:717` still asserts `noreply@anthropic.com` passes. It is flagged to be dispatched first.
  - Amends P274 (`s6-batch59.md`): its `git config` identity pin landed at `066bbfabe` (2026-10-30T16:18Z), yet #3016's commits at 21:03Z and 21:17Z are still authored Claude, because the environment's author overrides config. `cloud-setup.sh` therefore exports the four `GIT_AUTHOR_*`/`GIT_COMMITTER_*` variables as the seat identity.
  - REJECTED: refusing every author other than hpo-fixer, which would refuse the owner's own, github-actions, ledger and App commits.
  - To the orchestrator, out of tree: the local seat launcher exports `GIT_AUTHOR_NAME=tvofi`. That is why this seat's own `1670b98d7` is authored tvofi; export the hpo-fixer identity instead. Rewriting history is not ruled; it is the owner's call.
  - Measured: 195 Claude-authored non-merge commits on main in 7 days and 38 in 2 days. Three of the 12 open PRs carry 12 more (#3016 8, #3009 2, #3004 2).

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`4314801747a19af1ecce6b3d16ef4a2075607755`; the file is the whole diff against `861f949ae`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P320 as `ACCEPT`. `triage_refusal` passes the carry text, which cites `triage: dev/programme/triage/s6-batch83.md#P320`: it returns None.
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same carry is refused: `dev/programme/triage/s6-batch83.md#P320 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main. The carry, appended to the live roster, gives `brief_lint.mjs` `TOTAL: 0 error(s)`.

## Figures

- `git log --no-merges --format='%an <%ae>' origin/main --since=7.days | sort | uniq -c` gives `195 Claude <noreply@anthropic.com>`. The same over `--since=2.days` gives 38.
- `git log --no-merges --format='%an' origin/main..origin/<branch>` over the 12 open PR branches gives Claude-authored commits on #3016 (8), #3009 (2) and #3004 (2).
- `git log -1 --format='%h %cI %s' -S'pin the seat identity' origin/main -- tools/audit/seat/cloud_dispatch.py` gives `066bbfabe 2026-10-30T16:18:33+00:00`.
- `git log -1 --format='%an <%ae>' 1670b98d7` gives `tvofi <70032254+tvofi@users.noreply.github.com>`.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
