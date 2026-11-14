Fix review: merge 32c768ae03ddbed07c5f4975f458930a1054e35e

bus-nonce: 8c42767da2e8f916067887cdf1feac19

## Evidence

- Round: a later, body-only round at the same reviewed head 32c768ae03ddbed07c5f4975f458930a1054e35e. The packet's `## Review scope` reads `delta`, and the delta diff is empty. The code review in the previous verdict stands, and the code was not re-reviewed.
- Previous block resolved. The live body's `## Figures` block `<!-- figure-block: scope-line mb=9fdba3b8547f9762438dc19b98b310a63d34dcb1 head=32c768ae… -->` now reads `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`. `python3 -I tools/pr/figure_block.py verify <live body> --base 9fdba3b8547f9762438dc19b98b310a63d34dcb1 --head 32c768ae…` printed `1 block(s), 0 refused`, rc=0 (ev/figure-block-verify.txt). 9fdba3b8 is the PR's recorded base sha from the REST pull read, and the head sha there is 32c768ae…. The live body is in ev/pr-body.md.
- figure_lint at the head (packet): `FIGURES: 10 resolved, 1 not verified, 0 refused`. The one unverified segment is the MODE line itself, which figure_lint cannot run but figure_block verify confirms above.
- `## Red checks` answers the two reds of the previous round. One bullet covers `pr-contract / pr-contract` and `gate` (jobs 132550761259 and 132553014911), naming the cause (the body-only script rendered against current main, not the PR's base), the repair (`figure_block.py refresh … --base 9fdba3b8…`) and the cheaper detector (`figure_block.py verify`, about 1 s). It also answers `tests / fast (3.14)` and `tests / mutation` as before.
- Live checks at this head: `pr-contract / pr-contract` id=132558684111 success, and `gate` id=132558683183 success at 19:20:06Z (ev/checks-prcontract-gate.txt, ev/review-packet.md). `merge_train.py classify 32c768ae… --pr 3532` at 19:23:50Z read `GREEN 32c768ae03ddbed07c5f4975f458930a1054e35e pending: none red: none`, rc=0 (ev/classify.log). `tests / nightly-status` is red, but it is not in the `owed-reds` set (ev/owed-reds.txt), so it is neither answered nor a block.
- Merge with main: `git merge-tree --write-tree origin/main 32c768ae…` returned rc=0 at origin/main 5b8f05ba4e30d248b9b4a1f4c44fd8e62148c5db (ev/merge-tree.txt). REST mergeable_state is `clean`.
- carry_audit at the head (packet): `0 finding item(s)`. The previous verdict's body-text finding (the repeated `## Head` paragraph) was dismissed there as body text with no code effect, and it gates nothing here.

## Findings

none
