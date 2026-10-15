Fix review: blocked 92f549f9cf7339627c3d8acda08c6d4eec0061b1 class-open: C14 seed misses Union[X, None], Union[None, X] and Annotated[X, ...] -- each reopens rt_16 (IMPROVES at head)

bus-nonce: 02a6aa4c98a477e5c3c91a31790e55e3

Round 1. Head measured: 92f549f9cf7339627c3d8acda08c6d4eec0061b1 (authored code head 4c6f984e2, plus the delivery row). Merge base 586455741.
Roles diff vs origin/main: empty.

## Finder's harnesses (ARCH-s3, handoff/audit-r10-arch-s3 @ e0a2e91bd, sha1s match the body), merge base -> head
RESULT blind_keys=10 -> 0; census_keys=166 -> 176
RESULT perturb_away_keys_census_sees=0 -> 10; perturb_headline_untyped=0 -> 10
RESULT untyped_with_Any_or_None / _Optional_Any / _string_Any / _alias_Any = 0 -> 6 each
RESULT untyped_with_float=0 both ends; ablated_C1_untyped_with_Any=0 both ends
RESULT game_family_orphan_overrides=0 -> 2; honest_family_orphan_overrides=0 both ends
All agree with the body's Figures.

## Mutation proof (re-run by me)
M1 (Flow.env seeds through eng.seed_env): tests/arch_score_head.py 1 of 16 FAILED, 10 away keys unseen; restored, 16/16 pass. M2 and M3 were not re-run; they re-execute after the repair.

## The block (step 6: attacking other configurations the harness accepts)
C14 is stated as "a parameter annotated with a package class holds an instance of it". I re-spelled the parameter of rt_16, changing only its annotation:
RESULT rt_90 Union[X, None] = IMPROVES (open)
RESULT rt_95 Union[None, X] = IMPROVES (open)
RESULT rt_91 Annotated[X, "x"] = IMPROVES (open)
RESULT rt_92 "X | None" = NULL; rt_93 None | X = NULL; rt_94 Optional["X"] = NULL; rt_16 X = NULL
Optional[X] is Union[X, None], so the counter closes one spelling of a type and leaves its equivalent open. The same diff's is_any (C1b) unwraps Union and Annotated, so its two new predicates disagree on what a spelling is. The body's seam rule lists sites, not spellings, so the rule itself returned no seam. These are spellings at the one site the rule names (Flow.seed).
Repair: share one unwrapper between Flow.seed and is_any, covering Optional, Union with None, Annotated and strings, and add a planted case or attempt for Union and Annotated.

## Other steps
Step 4/5: no fixture, claim file, VERSION, manifest or notes heading in the diff. Step 7: body names 92f549f9c, the head measured. Step 11: no failure check-run on 35b754807, 2f69def8e, 4c6f984e2 or the head (4c6f984e2's cancelled runs are superseded); closures still in progress at the head when posted. Step 13: not reached.
Evidence: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-archscore/ev
