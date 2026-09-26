#!/usr/bin/env bash
# D14 sweep, class "an entity family whose names do not lead with a shared token splits under
# the name sort". Finding: D8-s3-01 (weakened(low)). The finder's own harness
# (tools/audit/round9/D8/s3/m3_families.py) already enumerates every production-defined entity
# family (tariff, learning, accuracy, pv, card_headline, energy_meters, ecl110) across all three
# sort orders (entity_id, English name, Swedish name), so it IS the class enumerator; reused
# verbatim here rather than duplicated.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
PYTHONPATH=tests/hastub python3 tools/audit/round9/D8/s3/m3_families.py
