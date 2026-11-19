"""Function-entry sentinel for D7-s3 (round 11): which production functions a process enters.

Loaded through PYTHONPATH by fn_trace.sh and m5_train.py; inert unless HPO_FN_TRACE names
an output directory or HPO_FN_MUTATE names a function (`<file>:<first line>`), which then
raises RuntimeError on every entry: the in-memory deletion mutant. Uses sys.monitoring PY_START and disables each code object after its first
entry, so the cost is one callback per function, not per call. One JSON file per process
(children of a test script included), written at exit and every 30 s.
"""
import os
import sys

_OUT = os.environ.get("HPO_FN_TRACE")
if _OUT:
    import atexit
    import json
    import threading

    _MARK = os.sep + os.path.join("custom_components", "heatpump_optimizer") + os.sep
    _seen = set()
    _mon = sys.monitoring
    _TOOL = 4

    def _start(code, _offset):
        fn = code.co_filename
        i = fn.rfind(_MARK)
        if i >= 0:
            _seen.add((fn[i + len(_MARK):], code.co_qualname, code.co_firstlineno))
        return _mon.DISABLE

    def _dump():
        tag = os.environ.get("HPO_FN_TRACE_TAG", "untagged")
        path = os.path.join(_OUT, "%s.%d.json" % (tag, os.getpid()))
        tmp = path + ".tmp"
        try:
            with open(tmp, "w") as fh:
                json.dump(sorted(_seen), fh)
            os.replace(tmp, path)
        except OSError:
            pass

    def _tick():
        _dump()
        t = threading.Timer(30.0, _tick)
        t.daemon = True
        t.start()

    try:
        _mon.use_tool_id(_TOOL, "d7s3_fn_trace")
        _mon.register_callback(_TOOL, _mon.events.PY_START, _start)
        _mon.set_events(_TOOL, _mon.events.PY_START)
        atexit.register(_dump)
        _t = threading.Timer(30.0, _tick)
        _t.daemon = True
        _t.start()
    except ValueError:
        pass

_MUT = os.environ.get("HPO_FN_MUTATE")
if _MUT and not _OUT:
    _mfile, _mline = _MUT.rsplit(":", 1)
    _mline = int(_mline)
    _MARK2 = os.sep + os.path.join("custom_components", "heatpump_optimizer") + os.sep + _mfile
    _mon2 = sys.monitoring

    def _start2(code, _offset):
        if code.co_firstlineno == _mline and code.co_filename.endswith(_MARK2):
            raise RuntimeError("d7s3-deleted %s:%d" % (_mfile, _mline))
        return _mon2.DISABLE

    try:
        _mon2.use_tool_id(4, "d7s3_fn_mutate")
        _mon2.register_callback(4, _mon2.events.PY_START, _start2)
        _mon2.set_events(4, _mon2.events.PY_START)
    except ValueError:
        pass
