Approved under mandate 6329234399 (scope all) at head edc3158d23d19fa9270edaab06293c1ee5a92299.

Fix review: merge at this head (probe c3cb42b4, nonce 8ef89520). The round-3 timed-out mutant (RETURN_DEL at `return active, ret`) now dies in 1.7 s on the keystone. GUARD_OFF is red too. The unmutated head passes all 4335 feature checks. CI's mutation lane at this head re-verifies 3 of 3 pins and adds no unpinned site.

Rulings:
- Trailers on six round-1 commits: dismissed, as the reviewer recommended. They were published before the no-footers guard landed (a4b27986). Removing them would mean rewriting a reviewed, published branch, and we do not force-push. Round 4's own commits carry none.
- 9b5e6fd8: settled at this head.
- 325975e1: the HASTUB_TZ half predates this head (the same 4 checks fail at the base). It is carried to R10-FLY-SUITE-ENV-FLAKES. The after-edge half is already served by R10-LIVESTATE's `after` on R10-LOOP-CPU.
- The two extra R10-LIVESTATE controls are appended to that group's roster carries.
