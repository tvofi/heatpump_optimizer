Fix review: merge 54cb8531b6cbe7576381d0acf68f733e496a115b

bus-nonce: c10030fbf2bb4c9b928407042a7c42fb

Round 2 (round 1 blocked class-open at 92f549f9c, comment 6200522380). Head measured: 54cb8531b6cbe7576381d0acf68f733e496a115b, which is authored head 87d54712c plus a main merge. Merge base 74cf47b9c. Roles diff vs origin/main: empty.

## Round-1 block, re-taken with my own probes (disclosed as mine: rt_16 with only the parameter annotation re-spelled)
RESULT rt_90 Union[X, None] = NULL (was IMPROVES)
RESULT rt_95 Union[None, X] = NULL (was IMPROVES)
RESULT rt_91 Annotated[X, "x"] = NULL (was IMPROVES)
RESULT rt_92..94 ("X | None", None | X, Optional["X"]) = NULL
RESULT rt_96 Optional[Annotated[X, "x"]] = NULL; rt_97 "Union[X, None]" = NULL; rt_98 typing.Union[X, None] = NULL
rt_16, rt_16b and rt_16c match their recorded verdicts (not in MOVED).

## Finder's harnesses (ARCH-s3 @ e0a2e91bd), merge base -> head
RESULT blind_keys=10 -> 0; census_keys=166 -> 176; perturb_away_keys_census_sees=0 -> 10; perturb_headline_untyped=0 -> 10
RESULT untyped_with_Any_or_None / _Optional_Any / _string_Any / _alias_Any = 0 -> 6 each; untyped_with_float=0 both ends; ablated_C1_untyped_with_Any=0 both ends
RESULT game_family_orphan_overrides=0 -> 2; honest_family_orphan_overrides=0 both ends

## Mutation proof (my own targeted mutants on the repair)
RESULT M1 (Flow.env seeds through eng.seed_env): arch_score_head 1 of 16 FAILED; restored 16/16
RESULT MU (annotation_members' Union branch deleted): rt_16b NULL -> IMPROVES; a3_payload_annotated_param_spelling_control WORSENS -> IMPROVES
RESULT MA (Annotated dropped from _WRAPPERS): rt_16c NULL -> IMPROVES; a3_payload_annotated_param_spelling_control_write WORSENS -> IMPROVES
RESULT M0: the same case set gives no MOVED line except rt_16, which is outside --only. All mutants restored; the probe worktree is clean.

## Other steps
Step 6: the body's round-2 rule (grep annotation_members|is_any|.annotation) returns typed_dicts (x2, through resolve_aliases), Flow.seed and Flow.contract. Flow.contract is dispositioned in the body: it resolves a TypedDict, so an unresolved spelling there can only overcount untyped keys and gives a gaming move nothing. Residual spellings (generic X[T], TypeVar bound, Protocol) are named in the body.
Step 4/5: VERSION, manifest, RELEASE_NOTES and both claim files are untouched (three-dot).
Step 7: the body names 54cb8531b6cbe7576381d0acf68f733e496a115b.
Step 11: no failed check-run on the PR's own commits (448ac5a75..54cb8531b). The pr-contract failures on 288d6009f and e43c2ca82 are main's record commits, brought in by the merge. Every check at the head is complete with no failure; pr-contract, arch-score and mutation are success.
Step 13: git merge-tree origin/main 54cb8531b6cbe7576381d0acf68f733e496a115b exits 0.
Step 14: expected.json gains only the round-1 and round-2 cases; no recorded verdict moved; the mutants show each new case is earned by its mechanism.
Evidence: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-archscore/ev2
