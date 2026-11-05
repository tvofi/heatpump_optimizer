## Head

Dismissed review finding (no destination file): rounded drivers do not always sum to the rounded grade (up to 0.1). Carry: dismissed: per-item rounding of an exact sum is the house grade's existing convention (`envelope_drivers` since #2816), invisible at the card's whole-point display.

## Forward-carry

- P9's clip check `unreachable()` (`tests/card_browser.mjs`) starts its ancestor walk at `parentOf(run.el)`, so a clip set on the text run's own element is outside its reach and a driver line clipped by its own box passes the grid. Pre-existing, not this PR's change. Carry: R10-WHY-NOW-WIDGET
- In sv at 375 px the evidence line can break between a number and its unit ("0⏎till 3 °C"). Carry: dismissed: cosmetic; P9 overlap, clip and contrast pass, and a no-break space between number and unit is a card-wide copy convention, not this PR's
