ci(#3885): the pages release step's tag pipeline reads its listing to the end
Refs #3885

(abridged by the reviewer: the sections carry_audit reads, verbatim)

## Figures

none

## Red checks

`tests / fast (3.14)` at 455e9b09 (run 45719342344): `tests/entities.py` countermeasure B, "every `bash -c` / `sh -c` a check runs carries errexit", listed `tests/entities.py:_pages_tag_run`. Repaired at f8decf8b. Cheaper detector: none; that check is inside `tests/entities.py`, the script the PR's own test lives in,.

## Forward-carry

none

## Friction

none
