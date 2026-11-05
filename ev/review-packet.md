# Review packet #3167
head: 4e4bb291b503be5abac829a6a068358ffdea1091
base: 086a59da409fc634bfbf7882c97367cf2ad8bc5f

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=126904701640 skipped
cancel-superseded id=126904715261 queued
prelude id=126904715331 queued
refresh id=126904714964 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/debug_collect.py
             `tests/debug_collect.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/replay.py
             `tests/replay.py` is in the tree at this head
  unverified git diff --quiet origin/main -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION RELEASE_NOTES.md && echo claims-identical
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 7 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3167.md b/dev/programme/delivery/3167.md
new file mode 100644
index 000000000..c984d1bcf
--- /dev/null
+++ b/dev/programme/delivery/3167.md
@@ -0,0 +1 @@
+- [#3167](https://github.com/tvofi/heatpump_optimizer/pull/3167) — **open**, R10-REPLAY-OPEN-LOG: replay open log (R10-REPLAY-OPEN-LOG)
diff --git a/tests/replay.py b/tests/replay.py
index e675cdb77..3cdb86868 100644
--- a/tests/replay.py
+++ b/tests/replay.py
@@ -1274,6 +1274,49 @@ def _in_window(doc: dict) -> dict[str, int]:
             for eid in doc["inputs"]}
 
 
+def _open_line_branches(tmp: Path, fake: "_FakeMySQL", marked: Path) -> list[tuple[str, bool, str]]:
+    """``export.open_recorder`` on each of its three branches, the stderr line
+    each prints: the kind by a constant, the path only on ``--db``, never a
+    value from the URL (code-scanning alert 47). The default branch has no
+    other pin: its line deleted, made constant or called MySQL stays green."""
+    import export
+
+    saved = {m: sys.modules.get(m) for m in ("MySQLdb", "pymysql")}
+    sys.modules["MySQLdb"] = fake  # type: ignore[assignment]
+    sys.modules["pymysql"] = None  # type: ignore[assignment]
+    canaries = (_CANARY_KEY, _CANARY_USER, "core-mariadb", "hadb")
+    got: dict[str, list[str]] = {}
+    try:
+        install = tmp / "default-install"
+        install.mkdir()
+        shutil.copy(tmp / "mariadb-backing.db", install / "home-assistant_v2.db")
+        for name, cfg, db, url in (
+                ("default", install, None, None),
+                ("db_path", install, marked, None),
+                ("mysql_url", install, None, _DB_URL),
+                ("sqlite_url", install, None, "sqlite:///home-assistant_v2.db")):
+            err = io.StringIO()
+            with contextlib.redirect_stderr(err):
+                export.open_recorder(cfg, db, url).close()
+            got[name] = err.getvalue().splitlines()
+    finally:
+        for name, module in saved.items():
+            if module is None:
+                sys.modules.pop(name, None)
+            else:
+                sys.modules[name] = module
+    want = {"default": ["reading the recorder: SQLite database"],
+            "db_path": [f"reading the recorder: SQLite database {marked}"],
+            "mysql_url": ["reading the recorder: MySQL/MariaDB database"],
+            "sqlite_url": ["reading the recorder: SQLite database"]}
+    res = [(f"recorder:open_recorder_line:{name}", got.get(name) == line, str(got.get(name)))
+           for name, line in want.items()]
+    leaked = [c for c in canaries if any(c in l for ls in got.values() for l in ls)]
+    res.append(("recorder:open_recorder_lines_carry_no_url_value",
+                not leaked and len(_CANARY_KEY) > 3, f"leaked {leaked}"))
+    return res
+
+
 def recorder_checks() -> list[tuple[str, bool, str]]:
     import export
 
@@ -1324,6 +1367,7 @@ def recorder_checks() -> list[tuple[str, bool, str]]:
                     and "core-mariadb" not in said_url and marked.name not in said_url
                     and len(_CANARY_KEY) > 3 and len(_CANARY_USER) > 3,
                     "the URL branch's stderr searched for the user, password and host"))
+        res.extend(_open_line_branches(tmp, fake, marked))
         # The unsupported-scheme refusal names neither the URL nor any part of
         # it; a URL without credentials reads the same text (the null).
         _, bad = _export_mariadb(None, tmp, db_url=f"ftp://{_CANARY_USER}:{_CANARY_KEY}@core-mariadb/x")

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
