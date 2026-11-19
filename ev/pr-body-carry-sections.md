## Forward-carry

- Carry 2, the first real DX0 scan with the owner's read credential and the choice of read identity (design "Decisions routed": a dedicated read-only App installation or the shared token under the 60 % floor), remains the owner's act. Carry: R11-PRE-SECURITY-PRIVACY | dismissed: duplicate of R11-PRE-SECURITY-PRIVACY carry 2 (0-based, item 75234782), which keeps it as the owner's act
- Carry 3, the seat account (an OS account owning the private root, unable to read the identity directory and the deploy key), remains the owner's act; without it `owner_only.py probe` refuses and DX0 does not run. Carry: R11-PRE-SECURITY-PRIVACY | dismissed: duplicate of R11-PRE-SECURITY-PRIVACY carry 3 (0-based, item 1cdaadd6), which keeps it as the owner's act
- Carry 4, the private-fork ruleset test, which needs a scratch security advisory (design note n4), remains the owner's act. Carry: R11-PRE-SECURITY-PRIVACY | dismissed: duplicate of R11-PRE-SECURITY-PRIVACY carry 4 (0-based, item 2a416932), which keeps it as the owner's act

## Friction

none
