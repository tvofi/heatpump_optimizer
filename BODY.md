The plan narrative now prices money in the price feed's currency (`coordinator.currency`), like every other money surface. Before this change, `_narrative_view` resolved the currency itself with `resolve_currency(hass)`, which returns the instance's label currency. A EUR feed on a SEK instance therefore published EUR sensors next to a narrative written in SEK. The local precedence is deleted, and the view reads the one value that `currency.py`'s `declared_currency` decides and the coordinator adopts on each cycle. The `narrative.render` docstring justified that local precedence ("A narrative line is recorded nowhere, so it can simply follow the instance"), and it is rewritten to state the new contract (fixer.md step 9).

The price-units comment in `_audit_price_units` named a nonexistent ``money_currency``. It now names what the sensors actually carry: `unit_of_measurement` and the `currency` attribute.

Fixes #2243
Fixes #2222

#2243 is D14-s3-01, with D14-s2-01 merged into it. #2222 is D5-s3-01.

### Orchestrator decision and the after-edge (mandate 6329234399, session s4)

The architect note's shape ("read the currency from one owner; delete the local precedence") costs one cross-seam attribute reference. `_narrative_view` is in the `views` seam, and `currency` is stored only by `core` units, so round 1 stopped at `seam_cut_total` 709 > 708. The orchestrator chose **route 1** under mandate 6329234399 (session s4) and granted an after-edge for this group only, into `_raise_cop_issue` in the `learning` seam of `coordinator.py`. No budget was raised and no `--record` was run.

The hunk does two things:
- It binds `self.currency` to one local, `currency`, which both the log line and the issue placeholder read. This lowers `learning`'s cut by 1, and `seam_cut_total` nets to 708 <= 708.
- It corrects the stale comment "In the instance currency: the prices are" to the price feed's currency. This is the same claim class as D5-s3-01: the method prices `self._prices`, which are the feed's, and publishes `self.currency`, which is the feed's code. The comment is now one line, `# The price feed's currency: its prices are (audit D4-04, #168).`. The added local would otherwise cost `class_excess_loc` and `max_class_loc` +1 each, since both count source lines. The clause it drops ("the placeholder used to be named after SEK") is history that #168 and git already hold.

A features check now pins the corrected claim (below). The D4-04 test's comment, which said "instance's currency", now says the coordinator's currency (with no feed, the instance's).

Architecture score: dS +0.0000 NULL.


Carries settled in this diff, so none is forwarded:

- R10-FEEDS carry (callers of `_get_current_price` / `_current_spot_price` must handle `None`): this diff touches no such call site. Nothing to carry.
- The stale "In the instance currency" comment in `_raise_cop_issue`, which round 1 carried to this decision, is closed in this diff. Nothing left to carry.

## Head

`23392d5d697ce7e26fab677a12d0d58921793d07`. It is round 1's head `701448f90` with origin/main `50808a755ce300fac4b19b7cfe7f89c795b8387b` merged in, plus the route-1 commit. Merge base `50808a755`, measured 2026-10-22.

## Mutation proof

- **Round 1's fix (narrative).** The production line was mutated back to `narrative.render(items, chosen, resolve_currency(hass))`, and `PYTHONPATH=tests/hastub python3 tests/features.py` printed `1 of 4302 FEATURE CHECKS FAILED`: `FAIL D14-s3-01: the narrative prices a EUR feed on a SEK instance in EUR, and a SEK feed in SEK  [{'EUR/kWh': ['SEK'], 'SEK/kWh': ['SEK']}]`. This was measured at round 1's head. This round's merge with main does not touch `_narrative_view`, `narrative.py` or that check.
- **Route 1 (COP notice).** At this head, in a separate worktree, `currency = self.currency` in `_raise_cop_issue` was mutated to `currency = resolve_currency(self.hass)` (that line only), and `PYTHONPATH=tests/hastub python3 tests/features.py` printed `1 of 4303 FEATURE CHECKS FAILED`: `FAIL R10-CURRENCY: the COP notice prices a EUR feed on a SEK instance in EUR, and a SEK feed in SEK  [{'EUR/kWh': ['SEK'], 'SEK/kWh': ['SEK']}]`. Restored. At the head, `ALL 4303 FEATURE CHECKS PASSED`.
- **Failing test first.** For D14-s3-01, the check fails alone on round 1's base (shown in round 1). The new R10-CURRENCY check **cannot fail on any shipped tree**: `_raise_cop_issue` already read `self.currency` at the base, so only the comment was wrong, not the behaviour. The check pins the corrected claim against the mutant above, which is the regression the stale comment invited. The existing D4-04 check could not catch that mutant, because it uses an instance with no feed, where both expressions give the instance code.

## Null control

- The finder's harness `clean` arm (a EUR feed on a EUR instance) reads 0 mismatched seams at the base and at the head. Its `reintroduce` arm (`declared_currency -> None`) reads 14 of 14 at the base and at the head, as the brief required.
- In both new checks, a SEK feed on the same SEK instance gives `['SEK']` at the base, under each mutant and at the head. Only the EUR-feed arm moves.
- D5-s3-01: `comment_symbols.py` at round 1's base lists `MISSING coordinator.py:2078 \`money_currency\``, and the head's list differs from the base's by exactly that line.

## Figures

- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/s3/p8_replay_currency.py` (sha1 `1acaac172452ff43387e83cbff0f02cfcd8a5a2d`, the same bytes as the finder's at d23205d13), run from each tree:
  - base `50808a755`: `base_money_seams=14`, `base_mismatched_seams=1`, `clean_mismatched_seams=0`, `narrative_fixed_mismatched_seams=0`, `reintroduce_mismatched_seams=14`
  - head `23392d5d6`: `base_money_seams=14`, `base_mismatched_seams=0`, `clean_mismatched_seams=0`, `narrative_fixed_mismatched_seams=0`, `reintroduce_mismatched_seams=14`
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D5/s3/comment_symbols.py`: `comment_symbols_untriaged_missing` reads 7 at base `50808a755` and 6 at the head.
- `PYTHONPATH=tests/hastub python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`, `ok   seam_cut_total 708 <= 708`.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD` prints `Architecture score: dS +0.0000 NULL`. `--diff 701448f9 HEAD` (route 1 alone, over the merge) prints the same.
- Gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=50808a755ce300fac4b19b7cfe7f89c795b8387b ./tests/run.sh` with `PREPR_SKIP_CLOSURES=1`, under a `tests/gate_lock.py` lease. The mode line is `MODE: SCOPED -- 21 script(s) run, 12 scoped out.`, the tail is `23 TEST SCRIPT(S) PASSED; 11 SCOPED OUT AND NOT RUN`, and it exited 0. `tests/stress.py` was scoped out (`did NOT run -- no changed file is in its measured closure`).
- Class enumeration (step 8): `grep -rn "resolve_currency(" custom_components/` gives the same dispositions as round 1 (`_narrative_view` closed; the `__init__` fallback, `_audit_price_units` ×2 and `config_flow.py` ×6 instance-labelled by design). `_raise_cop_issue` never called it; it is now pinned against doing so.

## Red checks

`tests/structure.py` (`seam_cut_total` +1) was red in round 1, locally, before any push. The cheaper detector is the one that caught it (a 17-second local run), so no countermeasure is owed. The orchestrator's route 1 resolved it. Locally, this round's first route-1 cut went red on `class_excess_loc` and `max_class_loc` +1 (the added local line), and condensing the comment paid for it before any push.

## Forward-carry

none

## Friction

- fixer.md-step17: contradiction: the architect note's mandated shape (read the one owner from the `views` seam) cost `seam_cut_total` +1 at zero headroom, and the note forbade the out-of-seam hunk that paid for it. A second dispatch round was needed. Carry: orchestrator.md section 5 (an architect note should price its shape against `seam_cut_total` before dispatch).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_011aqzm4YL9jLhU4jLvbkLYE
