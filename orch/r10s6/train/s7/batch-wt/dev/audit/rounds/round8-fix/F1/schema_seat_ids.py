#!/usr/bin/env python3
"""R8 F1(c) -- a multi-seat round's finding ids must validate.

Round 8 ran more than one finder seat per dimension and numbered findings per
seat (`D1-s1-01`, `D2-s2-02`); `finding.schema.json`'s id pattern admitted
only `D<k>-<nn>`, so every seat-scoped report failed validation.

METRIC: ids the REGISTERED schema's finding id subschema admits, over a fixed
table of ids that must be admitted and ids that must be refused. Validated
with jsonschema's Draft7Validator against the subschema read from
tools/audit/finding.schema.json itself (never a copy of its pattern).

DESIGN CHOICE, stated: the seat token is `s<digits>` -- round 8's form. Round
5's seat-a/seat-b were directory names, never id tokens, so `D1-sa-01` is
refused on purpose; admitting letters is a one-character change if a round
wants them.

COMMAND (from a checkout or export root):
    python3 tools/audit/round8-fix/F1/schema_seat_ids.py
EXPECTED (tolerance: exact):
    RESULT must_admit_refused=0
    RESULT must_refuse_admitted=0
    RESULT seat_harness_path_admitted=1
Exit status 1 when either of the first two is not 0.

PERTURBATION: restore the pattern `^D(1[0-3]|[0-9])-[0-9]{2}$` ->
must_admit_refused=4 (the three seat-scoped ids and D14-01, admitted since
the rotation/D14 PR). Direction: up.
NULL CONTROL: the seven must-refuse ids are refused under both patterns, so
the widening admits the seat form and nothing else in the table.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

SCHEMA = Path("tools/audit/finding.schema.json")
MUST_ADMIT = ["D0-01", "D1-01", "D13-99", "D14-01", "D1-s1-01", "D2-s2-02", "D13-s12-03"]
MUST_REFUSE = ["D1-1", "D1-001", "D15-01", "D1-s-01", "D1-sa-01", "D1-s1-1", "D1-S1-01"]


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    ids = Draft7Validator(schema["definitions"]["finding"]["properties"]["id"])
    path = Draft7Validator(schema["definitions"]["evidence"]["properties"]["harness_path"])
    bad_admit = [i for i in MUST_ADMIT if not ids.is_valid(i)]
    bad_refuse = [i for i in MUST_REFUSE if ids.is_valid(i)]
    seat_path = path.is_valid("tools/audit/round8/D1/s1/probe.py")
    print(f"RESULT must_admit_refused={len(bad_admit)} {bad_admit}")
    print(f"RESULT must_refuse_admitted={len(bad_refuse)} {bad_refuse}")
    print(f"RESULT seat_harness_path_admitted={int(seat_path)}")
    return 1 if bad_admit or bad_refuse else 0


if __name__ == "__main__":
    sys.exit(main())
