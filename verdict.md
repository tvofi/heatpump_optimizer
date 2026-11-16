Design review: revise dd3283712b7e924a66ccbead619019c7007f7404 architecture-unsound

Round 2. Reviewed from a detached worktree at dd3283712b (one file, design.md). The base judged is 030a4d377f, not the note's 824a016f75. Between them, R11-PRE-MACHINERY-LIMITER merged (#3627), so its after-edge is met. Of the note's files, only `dev/governance/rules/ratchet-budgets.md` changed (`git diff --stat 824a016f75 030a4d377f -- <the note's files>`). Cards were read as the note states them, at eval/r11 c6ce415b77.

## Round-1 points

- R1 (D, the vocabulary): answered. At handoff/r11-pre-round-metrics-p2, now 28c3ba15ee, `roster_lib.CAUSES` is `("external", "original")` plus `#<n>` or a group. D derives only `#<pr>` and `external`, and prints `unread` rather than writing a cause word. Derived rows carry no rca, are never written and never feed `injected`, which settles the rca rule. Product/machinery is taken from R11-PRE-TOOLCHAIN-PIN's gate.py split (design a37706d599, unmoved), not from paths.
- R3 (B, the rule date): answered. At 030a4d377f, all 10 files under `dev/governance/rules/` have a path add of bc0f17ddb6 (2026-10-06), later than their `--follow` add (2026-09-04 to 09-11). Enumerator: for each file in `git ls-tree --name-only 030a4d377f dev/governance/rules/`, take `git log --diff-filter=A` with and without `--follow`. The fixture at :54 plants the move.
- R2 (C, the refusal predicate): partly answered. Dropping the single exit code is right, but the replacement marker misses the repository's most common refusal format (point 1).

## Revise points

1. architecture-unsound, design.md:35 (part C, step 2) and :55 (the C evidence row). The marker `^\s*REFUSE[DS]?\b` / `^\s*refusing\b` is anchored at the start of the line. Most instruments prefix their refusals with their own name. Examples at 030a4d377f:
   - `tools/pr/app_push.sh:159` `die()` prints `app_push: REFUSE: %s`.
   - `tools/audit/seat/body_push.sh` prints `body_push: REFUSE head-stale ...` and `body_push: REFUSED <tok>`, and its own self-test greps `^body_push: REFUSED`.
   - `review_packet.py`, `ref_privacy.py`, `proof_watch.py`, `roster_edit.py`, `role_pack.py`, `state_docs.py` and `bus.sh` do the same.

   Enumerator: `git grep -l -E "(echo|print|printf)[ (]f?[\"'][a-z_.-]+: REFUS" 030a4d377f -- tools .claude/hooks`. The fixer re-derives the count at the part's merge base. All of these files are in the note's marker set (`git grep -l -E '\bREFUSE'`), so they never print `unmarked`/`unread`. Their prefixed refusals would count 0, and that is the "0, not unread" result round 1's R2 refused. The evidence row at :55 plants only an unprefixed `REFUSE pr-body` from prepr.sh, so the test passes while the miss is present.

   Fix wanted: admit an optional `<instrument>:` prefix, with `REFUSE`/`REFUSED`/`refusing` as the first word after it (for example `^\s*(?:[\w./-]+:\s*)?(?:REFUSE[DS]?|refusing)\b`). Add two planted refusals to part C's failing test, one prefixed (`app_push: REFUSE: ...`, exit 1) and one through `push.sh`'s `say REFUSE` column format (`tools/pr/push.sh:636`). Each must read as a refusal with its outcome.

## Routed

- decision: orchestrator. The routed edge from round 1 is answered (design.md:17): D builds after R11-PRE-ROUND-METRICS part 2 merges, and C after R11-PRE-TOKEN-LEDGER. The orchestrator adds those two `after` edges. Nothing is carried into part 2.

## Notes for the fixer

- Part D, design.md:15 and :42: the part-2 head is now 28c3ba15ee, not acf0b72578. Commits 02e54e0082 to 28c3ba15ee change `rca_lists`. Derived rows carry no rca, so D is not affected, but re-read `convergence_why` at part 2's merge commit. Carry: R11-PRE-NO-READ-BUILDERS (item d-p2-head)
- Part D, design.md:42: "fetched listings in". The note names no file or instrument that fetches the Actions listings (the prototype `gate_reds.py` is on eval/r11). Name the reader in the body and register its input. Carry: R11-PRE-NO-READ-BUILDERS (item d-fetcher)
- Hot files, design.md:60: design/R11-PRE-SECURITY-PRIVACY is now at 8f52783880, not ba8209b07f. Its section 7 and :201 still name the shared `fold_ledger.py` rebase order with this group, so the serial rule holds. Carry: R11-PRE-NO-READ-BUILDERS (item b-hotfile-head)
- Sibling designs in flight that touch this note's files: R11-PRE-PARALLEL-PIPELINE, R11-PRE-SHARED-FILES and R11-PRE-TOOLCHAIN-PIN name `gate.py`, which D leaves unchanged. R11-PRE-STANDING-SCRIPTS names `roster_lib.py` for `is_hotfix`/`is_outside`, not `convergence_why`. None of them claims D's seam. Carry: dismissed: no shared seam (item siblings)

Seat token count: not reported by this harness.
