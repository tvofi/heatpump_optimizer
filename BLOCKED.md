Question: the review packet's brief-carries check refuses this split part's handoff unless the body names all 24 carries on R10-REVIEW-DISPATCH-RESIDUE's roster entry, numbered 1-based, while the brief says part 1 owns Carries 14 and 22 by their 0-based index out of 23. Which numbering is binding, and how should a split part's body answer the other parts' carries without claiming them? Or should the orchestrator run the packet with this part's carry subset?

Code head (clean prepr.sh, PRE-PR rc=0): 185699076fb42c0082be4e5eaae31ab1abf2c1ad on handoff/r10-review-dispatch-residue-p1. Self-test 433/0. Seven spec mutants KILLED, NULL SURVIVED. The refused body is kept at handoff-wip/r10-review-dispatch-residue-p1-body 819f39ac5be3630ff6c7fd236177e305f80fb29c.

Under the packet's 1-based numbering, the brief's 0-based 14 and 22 would be packet carries 15 and 23. The packet accepted 14, 17 and 22 only because the body mentions those numbers: 17 is named as part 6's.

body_push.sh output (refusal lines):
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
review_packet: REFUSE brief-carries: carry 11 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 12 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 13 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 15 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 16 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 18 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 19 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 20 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 21 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 23 is not named in the body (`Carry N`)
review_packet: REFUSE brief-carries: carry 24 is not named in the body (`Carry N`)
review-packet handoff: R10-REVIEW-DISPATCH-RESIDUE at 185699076fb4, 24 carries, 21 refused
body_push: the review packet refuses this head at the handoff (above); answer each, push the code, then the body
body_push: REFUSED REVIEW-PACKET
body_push: refused body kept at handoff-wip/r10-review-dispatch-residue-p1-body 819f39ac5be3630ff6c7fd236177e305f80fb29c
