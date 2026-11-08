# BLOCKED

CARRY-LANDED now passes (both carry ids are on handoff/audit-r10-roster). body_push.sh then refused on a different arm, with the body unchanged except that its Head already named b4446e5cb979:

    review_packet: REFUSE brief-carries: carry 1 is not named in the body (`Carry N`)
    review_packet: REFUSE brief-carries: carry 2 is not named in the body (`Carry N`)

The body needs the review packet to name `Carry 1` and `Carry 2`. The brief allows no body edit beyond the head, so this stops here; the refused body is kept on this ref.
