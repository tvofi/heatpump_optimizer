#!/usr/bin/env bash
# D14 sweep, class "structure metric blind to a code shape".
# Finding: D7-s1-01 (verified, low -- tests/structure.py's ratchet cannot see coordinator state
# reached through a module-level `_helper(self, ...)`, the shape docs/HANDOVER.md records as
# refused, so it rewards that move (fewer coordinator_methods/coordinator_loc) and refuses its
# reversal (inlining a helper back into the class raises cross_seam_edges/cut_grid/cut_learning/
# internal_call_edges even when nothing about the code's behaviour changed).
# The finder's own --all leave-one-out grid across the 10 module-level coordinator helpers IS the
# class enumerator; reused verbatim.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
PYTHONPATH=tests/hastub python3 tools/audit/round9/D7/s1/helper_escape.py --all
