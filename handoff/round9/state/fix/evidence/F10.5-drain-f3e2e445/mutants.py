"""One mutant per new production predicate in tests/mutation_table.py (R9-F10.5)."""
MUTANTS = {
 "M1_split_anchor": ('        if not drivers or len(pool) + len(group) > cap:\n            continue\n        pool.extend(dict(s, drivers=drivers) for s in group)',
                     '        if not drivers or len(pool) + 1 > cap:\n            continue\n        pool.extend(dict(s, drivers=drivers) for s in group[:1])'),
 "M2_no_driver_kept": ('        if not drivers or len(pool) + len(group) > cap:', '        if len(pool) + len(group) > cap:'),
 "M3_seed_ignored": ('f"{seed}:{a}".encode()', 'f"{a}".encode()'),
 "M4_closure_ignored": ('        reads = [script, *closures.get(script, ())]', '        reads = [script]'),
 "M5_moved_head_unfiltered": ('    if measured_at != head:\n        if changed is None:', '    if False:\n        if changed is None:'),
 "M6_write_set_any_code": ('        if code != "??" or not path.startswith(DRAIN_ROWS):', '        if not path.startswith(DRAIN_ROWS):'),
 "M7_report_always_green": ('    ok = status in DRAIN_QUIET', '    ok = True'),
 "M8_status_before_pins": ('    if status != "measured":\n        return status or "skip-no-measurement"\n    try:\n        measured_at', '    try:\n        measured_at'),
}
