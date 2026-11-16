#!/usr/bin/env python3
"""D1-s3 M5: the seam rule for the persist-failure family -- every d1-excepts handler whose try body
saves a store (`async_save` / `async_delay_save` / a `_persist`/`persist` call) and the highest
log level its handler body uses.

Metric (one line): one line per handler: id, function, the max logging level the handler body
calls (debug/info/warning/error/exception or none), whether it re-raises.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s3/persist_seams.py
Static enumerator (the seam rule); the executed number is excepts_inject.py's.
"""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1s3hook as hook  # noqa: E402

LEVELS = ["debug", "info", "warning", "error", "exception", "critical"]


def main():
    rows = hook.handlers()
    trees = {}
    n = 0
    for r in rows:
        if r["file"] not in trees:
            trees[r["file"]] = ast.parse(open(r["file"]).read())
        for node in ast.walk(trees[r["file"]]):
            if not isinstance(node, ast.Try):
                continue
            hs = [h for h in node.handlers if h.lineno == r["line"]]
            if not hs:
                continue
            body = ast.unparse(ast.Module(body=node.body, type_ignores=[]))
            if not any(k in body for k in ("async_save(", "async_save_if_changed(", "async_delay_save(",
                                           "persist(", "_persist(")):
                continue
            h = hs[0]
            lv = "none"
            for c in ast.walk(h):
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr in LEVELS:
                    if lv == "none" or LEVELS.index(c.func.attr) > LEVELS.index(lv):
                        lv = c.func.attr
            n += 1
            print(f"{r['id']} {r['func']} level={lv} reraises={r['reraises']}")
    print(f"RESULT persist_handlers={n}")


if __name__ == "__main__":
    main()
