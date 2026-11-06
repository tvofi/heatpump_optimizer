import sys, pathlib
root, name = sys.argv[1], sys.argv[2]
C = pathlib.Path(root, "custom_components/heatpump_optimizer/coordinator.py")
S = pathlib.Path(root, "custom_components/heatpump_optimizer/services.py")
def sub(p, old, new):
    t = p.read_text()
    n = t.count(old)
    if n != 1:
        sys.exit(f"MUTATE-FAIL {name}: {n} matches")
    p.write_text(t.replace(old, new))
M = {
 "null_comment": (C, '_REPLY_FRAME_MAX_BYTES = 256 * 1024 * 1024\n', '_REPLY_FRAME_MAX_BYTES = 256 * 1024 * 1024\n# null-control comment\n'),
 "measure": (C, '    return pickle.load(_frame_reader(fd, _REPLY_FRAME_TIMEOUT_S))\n',
   '    _r = _frame_reader(fd, _REPLY_FRAME_TIMEOUT_S)\n    _n = [0]\n    def _rd(k):\n        b = _r.read(k)\n        _n[0] += len(b)\n        return b\n    _o = pickle.load(SimpleNamespace(read=_rd, readline=_r.readline))\n    with open("/tmp/mut/sizes.log", "a") as _f:\n        _f.write(f"{_n[0]}\\n")\n    return _o\n'),
 "none": (C, "PROCESS_REPLY_TIMEOUT_S = 1800.0\n", "PROCESS_REPLY_TIMEOUT_S = 1800.0\n"),
 "m4": (C, '        log_held(hass, key, True, "%s; %s skipped this cycle", err, name)\n', ''),
 "m6": (C, '    log_held(hass, key, False)\n    return result\n', '    return result\n'),
 "guard_off": (C, '        if size > left_bytes:\n', '        if False:\n'),
 "frame_time_off": (C, '            if left_s <= 0 or not _reply_ready(fd, left_s):\n', '            if False:\n'),
 "frame_bypass": (C, '    return pickle.load(_frame_reader(fd, _REPLY_FRAME_TIMEOUT_S))\n', '    return pickle.load(stdout)\n'),
 "transl_off": (S, '    if failed:\n        entry_ids', '    if False:\n        entry_ids'),
 "transl_key_off": (S, '            translation_key="diagnose_interval_failed",\n', ''),
 "deadline_none": (C, '    if not _reply_ready(stdout, timeout):\n', '    if not _reply_ready(stdout, None):\n'),
 "check_after_read": (C,
   '        if size > left_bytes:\n            raise ValueError(\n                f"reply frame exceeds {_REPLY_FRAME_MAX_BYTES} bytes"\n            )\n        left_bytes -= size\n        chunks: list[bytes] = []\n',
   '        _asked = size\n        chunks: list[bytes] = []\n'),
}
p, old, new = M[name]
sub(p, old, new)
if name == "check_after_read":
    t = C.read_text()
    old = '            size -= len(chunk)\n        return b"".join(chunks)\n'
    new = ('            size -= len(chunk)\n        if _asked > left_bytes:\n            raise ValueError(\n'
           '                f"reply frame exceeds {_REPLY_FRAME_MAX_BYTES} bytes"\n            )\n'
           '        left_bytes -= _asked\n        return b"".join(chunks)\n')
    assert t.count(old) == 1
    C.write_text(t.replace(old, new))
print("MUTATED", name)
