#!/usr/bin/env python3
"""Reviewer's own harness (not the fixer's): drive roster_edit's op layer at a
given checkout and print RESULT lines.

    python3 -I both_ends.py <checkout> <label>

Key: whether a stage word outside the registry is WRITTEN (baseline defect) or
refused with a message naming the roster, group and value (head), and whether a
size outside tools/plan/durations.json is written or refused. The legal op
beside each is the null control: a writer that refuses everything is not the
claim.
"""
import inspect
import json
import os
import sys
import tempfile

root = os.path.abspath(sys.argv[1])
label = sys.argv[2]
sys.path.insert(0, os.path.join(root, "tools/audit/seat"))
sys.path.insert(0, os.path.join(root, "tests/hastub"))
import roster_edit  # noqa: E402
import roster_lib  # noqa: E402


def call(fn, *args, **kw):
    """Call an op with only the parameters this checkout's signature has."""
    have = inspect.signature(fn).parameters
    return fn(*args, **{k: v for k, v in kw.items() if k in have})


def roster():
    return {"repo": "fixture/roster", "groups": [
        {"group": "R9-A", "lane": "L1", "issues": [10], "fixes": [],
         "after": [], "brief": "fixture A",
         "resume": {"stage": "not-started", "branch": "handoff/a"}},
        {"group": "R9-B", "lane": "L1", "issues": [11], "fixes": [],
         "after": [], "brief": "fixture B",
         "resume": {"stage": "not-started", "branch": "handoff/b"}},
    ]}


def stage_op(word, group="R9-A"):
    r = roster()
    try:
        call(roster_edit.op_set_stage, r, group, word, None, rel="the/roster.json")
    except roster_edit.Refuse as e:
        return False, str(e)
    except BaseException as e:  # noqa: BLE001 - a crash is a different result
        return "CRASH", f"{type(e).__name__}: {e}"
    return True, r["groups"][0]["resume"].get("stage")


def resume_op(word):
    r = roster()
    try:
        call(roster_edit.op_set_resume, r, "R9-B", "stage", word, rel="the/roster.json")
    except roster_edit.Refuse as e:
        return False, str(e)
    except BaseException as e:  # noqa: BLE001
        return "CRASH", f"{type(e).__name__}: {e}"
    return True, r["groups"][1]["resume"].get("stage")


def append_op(entry):
    r = roster()
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(entry, f)
    try:
        sizes = ()
        try:
            sizes = roster_lib.sizes(roster_lib.read_durations(root))
        except BaseException:  # noqa: BLE001 - baseline has no such helper
            pass
        call(roster_edit.op_append_group, r, path, rel="the/roster.json", sizes=sizes)
    except roster_edit.Refuse as e:
        return False, str(e)
    except BaseException as e:  # noqa: BLE001
        return "CRASH", f"{type(e).__name__}: {e}"
    finally:
        os.unlink(path)
    g = [x for x in r["groups"] if x["group"] == entry["group"]][0]
    return True, ((g.get("resume") or {}).get("stage"), g.get("size"))


R = []
def res(name, ok, detail):
    line = f"RESULT {label} {name}: ok={ok} detail={detail!r}"
    print(line, flush=True)
    R.append(line)

# 1. an unclassified stage word -- the class (writer accepted what no read closed)
write, d = stage_op("shipped")
res("set-stage-shipped-written", write is True, d)
# 2. the null control beside it: a classified word still lands at head
write, d = stage_op("review")
res("set-stage-review-written", write is True, d)
# 3. the same barrier at the second write path
write, d = resume_op("shipped")
res("set-resume-stage-shipped-written", write is True, d)
write, d = resume_op("fixing")
res("set-resume-stage-fixing-written", write is True, d)
# 4. the size half + its null control
write, d = append_op({"group": "R9-H", "lane": "L2", "after": [], "brief": "H",
                      "size": "XS"})
res("append-group-XS-written", write is True, d)
write, d = append_op({"group": "R9-I", "lane": "L2", "after": [], "brief": "I",
                      "size": "S"})
res("append-group-S-written", write is True, d)
# 5. the stage half at append-group
write, d = append_op({"group": "R9-G", "lane": "L2", "after": [], "brief": "G",
                      "resume": {"stage": "shipped"}})
res("append-group-shipped-written", write is True, d)

print("\n".join(R))
