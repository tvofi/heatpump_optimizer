## Head

`0000000000000000000000000000000000000000`

## Mutation proof

Reverting the guard turns the ratchet red.

## Null control

Clean.

## Figures

none

## Red checks

`mutation`: the diff adds a guard no pin kills, so the mutation lane is red
until mutation-autofix pins it after the push. The cheaper detector is step 6d,
which lists the site before the push; its standing cost is one static read.

## Forward-carry

none

## Friction

none
