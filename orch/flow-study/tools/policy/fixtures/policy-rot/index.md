# Rot fixture: index

This file stands in for CLAUDE.md when the acceptance runs the index check, so
that check is pinned on a fixture rather than only on a healthy corpus where a
deleted function and a clean run look the same.

It is rotten in both directions the check refuses.

Forward: it sends a seat to `tools/audit/briefs/D99-never-existed.md`, which is
in no tree. A seat sent to a file that does not exist cannot comply.

Backward: it names none of the policy files beside it, so every one of them
binds nobody, because the index is the only way a seat finds one.
