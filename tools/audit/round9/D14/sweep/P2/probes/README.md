Each of P2's 27 findings reuses its own already-committed finder harness as its
sweep probe (see `../SWEEP.md`'s disposition table for the exact command per
finding, and `S1.json`'s `seams[].probe`). Those harnesses live at their
original paths under `tools/audit/round9/D<k>/...` on this branch (unchanged
from `handoff/audit-r9-evidence`) rather than being duplicated here, so that
re-running a probe also re-runs the exact committed script the finder/verifier
already reviewed. `enumerator.py` in the parent directory is the one fact
(two_zone_enabled / dhw_enabled / wood_furnace_on) that has a package-wide
mechanical detector (D14-s2-01's own `p2_facts.py`); the other 26 facts were
widened from their own `seam_rule`, not from a shared detector -- see
`../SWEEP.md` "Method" for why.
