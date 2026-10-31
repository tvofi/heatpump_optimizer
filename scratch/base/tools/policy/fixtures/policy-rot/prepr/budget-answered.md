## Head

`0000000000000000000000000000000000000000`

## Mutation proof

Reverting the guard turns the ratchet red.

## Null control

Clean.

## Figures

none

## Red checks

`budget-raise-gate`: this diff raises a structure budget, so the gate is red
until tvofi approves at the head. No cheaper detector separates it: the raise is
the change, and only the owner's review turns it.

## Forward-carry

none

## Friction

none
