A second null control, for the sections whose accepted value is a WORD rather
than content. `good.md` carries a well-formed `## Friction` line; this one
carries `none`, and both must pass. Splitting them is the point: one fixture
covering only `none` left the parser's accept path unexercised, which is how a
body written in this repository's own backticked style came to be refused by
the check that was supposed to accept it.

## Head

`0000000000000000000000000000000000000000`

## Mutation proof

n/a: no production symbol changes.

## Null control

n/a: nothing quantified.

## Red checks

none

## Forward-carry

none

## Friction

none
