# BLOCKED: r10-review-dispatch-residue-p5 handoff body refused by the review packet

Question: body_push.sh's review packet scopes this part-5 handoff to the whole R10-REVIEW-DISPATCH-RESIDUE group (33 live carries) and refuses every carry this part was not given (brief: carries 17, 20, 11, 28 only), and it refuses 'carry 17 is cited as landed at 676d726d..., which is not on the roster ref'. prepr.sh also reported 'carry targets: no roster group answers for branch'. Both refusals sit on the roster or packet scoping, which this seat may not write. Should the relay re-scope the roster group to part 5 (or fold the carry-17 landing) and then re-run body_push.sh?

State: the code is pushed to handoff/r10-review-dispatch-residue-p5 at f779168acc9cb030a44743a4c8a9fb177ff5c0c6, fast-forward from f71c5e6933. prepr.sh at that head had no code refusals: its three refusals (pr-body Friction parse, carry UNROUTED, ci predict pr-contract) were all body items, and `prepr.sh --body-check` is clean on the final body. The final body is kept at handoff-wip/r10-review-dispatch-residue-p5-body 50255d18205ab8b0343129a2f32689bab1772f1d. Every listed mutant is KILLED, the NULL mutants survive, the three self-tests print 0 failed, and policy_lint is TOTAL 0.

## body_push.sh output

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review_packet: REFUSE brief-carries: carry 0 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 1 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 2 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 3 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 4 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 5 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 6 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 7 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 8 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 9 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 10 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 12 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 13 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 14 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 15 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 16 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 18 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 19 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 21 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 22 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 23 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 24 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 25 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 26 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 27 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 29 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 30 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 31 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 32 is not named in the body (`Carry N`)
review_packet: REFUSE carry-landed: carry 17 is cited as landed at 676d726d27c4a5400d86c331bba87190bd34534c, which is not on the roster ref
review-packet handoff: R10-REVIEW-DISPATCH-RESIDUE at f779168acc9c, 33 live, 33 dispatched carries, 30 refused
body_push: the review packet refuses this head at the handoff (above); answer each, push the code, then the body
body_push: REFUSED REVIEW-PACKET
body_push: refused body kept at handoff-wip/r10-review-dispatch-residue-p5-body 50255d18205ab8b0343129a2f32689bab1772f1d
```
