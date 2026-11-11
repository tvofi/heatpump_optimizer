# Proposal triage, session s14, batch 152 (P563)

This batch rules `s7/triage-queue-s7.txt` line 246, which arrived after batch 151. The bar and the
denominators are batch 141's.

Sources: origin/main `63bcdcaad8` (line numbers); the round roster branch; PR 3424's body, read
with `gh api repos/tvofi/heatpump_optimizer/pulls/3424 --jq .body` (head `fix/r10-train-residue`
at `175556657a`).

## P563: S14-LANDED-PR-NEEDS-ROSTER-PR

Verdict: ACCEPT. It repairs an observed wrong behaviour: a fresh fixer PR whose body holds a status
line on its own group's carries refuses its first reviewer dispatch. One of the proposal's two
remedies is right; its stated cause, and the remedy that follows from it, are wrong.

Source: queue line 246 (2026-11-11T01:43:33Z, the orchestrator; PR 3424 at 01:40Z).

Instances:
- **Measured.** `carry_audit.py landed --body <3424 body>` was run in six forms: three argument
  forms, each at `--roster-ref origin/main` and at `origin/handoff/audit-r10-roster`.

  | roster ref | arguments | rc | result |
  |---|---|---|---|
  | origin/main | `--pr '#3424'` | 1 | 3 missing |
  | origin/main | `--pr '#3424' --topic r10-train-residue` | 1 | 3 missing |
  | origin/main | `--topic r10-train-residue` | 1 | 3 missing |
  | round branch | `--pr '#3424'` | 1 | 3 missing |
  | round branch | `--pr '#3424' --topic r10-train-residue` | 0 | 0 missing, 3 `CARRY-STATUS` |
  | round branch | `--topic r10-train-residue` | 0 | 0 missing, 3 `CARRY-STATUS` |

  With `--topic fix/r10-train-residue`, the PR's own head ref, it is rc 0 and 0 missing.
- **The cause, corrected.** The source says `--pr` maps the PR to its group through the roster's
  `resume.pr`, which only `roster_sync` writes. `carry_audit.py` never reads `resume.pr`. It reads
  `resume` for `stage` and `absorbed_into`, and as text searched for item ids (line 914). Command:
  `grep -n resume tools/audit/carry_audit.py`.
  - The real cause: `own_group` (line 587) skips every `#`-prefixed source (line 593: `if not
    x.startswith("#")`).
  - `bus.sh` `carry_landed` (line 229) passes only `--pr "#$1"` (line 237).
  - So a dispatch never resolves the PR's own group, and running `roster_sync` would change
    nothing. A false premise would have looked like `--pr` alone passing at the round ref. It
    refused, 3 missing.
- **The second factor is already ruled.** At `origin/main` even the topic form refuses. That is
  `bus.sh`'s hard-coded `--roster-ref origin/main`, which P557 (`s6-batch148.md`) already carried to
  R10-PREPR-RESIDUE.
- **The cost.** PR 3424's first reviewer dispatch was refused. A seat then queued the status line as
  a roster carry, and it had to be voided (the source's account).

Cost: `carry_landed` already makes `gh api repos/$REPO/pulls/$1`.
- It reads `.head.ref` in that same call and passes it as `--topic` to both `landed` and `land-ops`.
- `own_group` then resolves the group by `pr_group_of` (line 441: `group_for_branch`, then without
  a trailing `-pr`), as `audit --branch` already does (line 980).
- No new API call and no new file. The `roster_sync`-after-open remedy is rejected: it writes a
  field `landed` does not read.
- Self-test:
  - the 3424 shape (`--pr` plus the head ref, with an own-group status line) passes at the round
    ref;
  - the null control: a body routing a finding to another group that does not hold it is still
    CARRY-MISSING;
  - a mutant dropping the `--topic` argument fails the first case.
- Neither `bus.sh` nor `carry_audit.py` has a row in `tests/structure_budgets.json`.

Binding: one carry to R10-PREPR-RESIDUE. It holds `bus.sh` and `carry_audit.py` and already carries
P557, which changes the same `carry_landed` call, so one part rewrites that call once. Its fixer was
dispatched at 00:41Z and has not handed off, so the carry takes the PART 2 ITEM prefix. Carry file:
`b152-P563.txt`.
