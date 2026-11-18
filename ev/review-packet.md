# Review packet #3729
head: 5fe137027a72cdd44483f1b2ad8c4345bb554857
base: ae0ed64af898d8923ac35afe6e9c031ac1e6b111

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=134917831474 skipped
cancel-superseded id=134917939214 queued
prelude id=134917938589 queued
refresh id=134917939362 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item a17d4699: dismissed:corrected by that ruling before this run, pending owner confirmation as the ruling states
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 8 script(s) run, 25 scoped out.
             no segment of this names a program this check knows
  unverified git archive 819aa2e354b4e5baaf824b8568fd72bea8168a75 dev/audit/rounds/round11
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/structure.py --record
             `tests/structure.py` is in the tree at this head
  unverified git diff origin/main...HEAD -- tests/structure_budgets.json
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tools/audit/archscore/score.py --diff bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/arch_score.py
             `tests/arch_score.py` is in the tree at this head
  ok         tests/arch_score_head.py
             `tests/arch_score_head.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 12 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (no verdict on verdict/<pr> names the reviewed head fc2daf48862599bb19f70ff563db63e347bdf2e7, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/dev/programme/delivery/3729.md b/dev/programme/delivery/3729.md
new file mode 100644
index 0000000000..d95d02f4e1
--- /dev/null
+++ b/dev/programme/delivery/3729.md
@@ -0,0 +1 @@
+- [#3729](https://github.com/tvofi/heatpump_optimizer/pull/3729) — **open**, R11-SEAM-ratchets: ratchets (R11-SEAM-ratchets)
diff --git a/tests/entities.py b/tests/entities.py
index 7782c6a294..7f4d5d151b 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -42370,10 +42370,28 @@ _R10_LATCH_WORD = re.compile(r"(warn|logged|report|latch|announc|_failed|notifie
 
 
 def _r10_unlatched_logs(sources):
-    """N-log-flood seams: each ``_LOGGER.warning``/``.error`` with no latch in
-    an enclosing ``if`` (a latch-named test, or a ``not in`` against a set the
-    function ``.add``s to; the R10 sweep's static rule), per (module, function)."""
+    """N-log-flood seams: each ``_LOGGER`` call at WARNING or above (``.warning``
+    and its ``.warn`` alias, ``.error``, ``.exception``, ``.critical`` and its
+    ``.fatal`` alias, ``.log`` at such a level: R11 D14-s2-03, the barrier read
+    two of the seven) with no latch in an enclosing
+    ``if`` (a latch-named test, or a ``not in`` against a set the function
+    ``.add``s to; the R10 sweep's static rule), per (module, function). A logger
+    under another name is refused by ``_r11_logger_aliases``."""
     found = Counter()
+
+    def flood_level(call):
+        # WARNING or above; ``.log`` at a level below it is quiet, any other
+        # level, a computed one included, is counted. Kept inside this
+        # function: logflood_shape.py execs it alone.
+        if call.func.attr in ("warning", "warn", "error", "exception", "critical", "fatal"):
+            return True
+        if call.func.attr != "log" or not call.args:
+            return False
+        level = call.args[0]
+        if isinstance(level, ast.Constant) and isinstance(level.value, int):
+            return level.value >= 30
+        return ast.unparse(level) not in ("logging.DEBUG", "logging.INFO", "logging.NOTSET")
+
     for name, source in sources.items():
         tree = ast.parse(source)
 
@@ -42381,8 +42399,8 @@ def _r10_unlatched_logs(sources):
             for child in ast.iter_child_nodes(node):
                 inner = child if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn
                 if (isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute)
-                        and child.func.attr in ("warning", "error")
-                        and ast.unparse(child.func.value) == "_LOGGER"):
+                        and ast.unparse(child.func.value) == "_LOGGER"
+                        and flood_level(child)):
                     latched = False
                     for test in chain:
                         text = ast.unparse(test.test)
@@ -42399,6 +42417,97 @@ def _r10_unlatched_logs(sources):
     return found
 
 
+def _r11_logger_aliases(sources):
+    """``(module, line, binding)`` per way a package line can log through
+    something the barrier does not read. The barrier keys on the text
+    ``_LOGGER``, so the one logger it sees is a module-level
+    ``_LOGGER = logging.getLogger(...)`` used only as ``_LOGGER.<method>(...)``.
+    Refused: a name bound to ``_LOGGER``, to a ``getLogger``/``getChild``
+    result or to a ``logging`` alias; any other ``getLogger``/``getChild``
+    call, bound or inline, ``logging.getLogger`` or a bare ``getLogger``; an
+    import of ``_LOGGER`` or of ``logging``'s loggers and level functions;
+    ``logging.<level>(...)`` on the root logger; and ``_LOGGER`` itself
+    escaping, as an argument, a return value, an element or a bound method,
+    which is how a logger reaches a parameter the barrier cannot name."""
+    levels = {"debug", "info", "warning", "warn", "error", "exception",
+              "critical", "fatal", "log"}
+    root_names = levels | {"root", "getLogger", "Logger", "LoggerAdapter"}
+    binders = (ast.Assign, ast.AnnAssign, ast.NamedExpr)
+
+    def logger_call(node):
+        return isinstance(node, ast.Call) and (
+            (isinstance(node.func, ast.Attribute) and node.func.attr in ("getLogger", "getChild"))
+            or (isinstance(node.func, ast.Name) and node.func.id == "getLogger"))
+
+    out = []
+    for name, source in sources.items():
+        tree = ast.parse(source)
+        top = set(map(id, tree.body))
+        parent = {id(c): n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
+        canonical_values = set()
+        for node in tree.body:
+            if (isinstance(node, ast.Assign) and len(node.targets) == 1
+                    and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "_LOGGER"
+                    and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute)
+                    and node.value.func.attr == "getLogger"
+                    and ast.unparse(node.value.func.value) == "logging"):
+                canonical_values.add(id(node.value))
+        for node in ast.walk(tree):
+            up = parent.get(id(node))
+            if isinstance(node, ast.Import):
+                for a in node.names:
+                    if a.name == "logging" and a.asname:
+                        out.append((name, node.lineno, a.asname))
+            elif isinstance(node, ast.ImportFrom):
+                for a in node.names:
+                    if a.name == "_LOGGER" or (node.module == "logging" and a.name in root_names):
+                        out.append((name, node.lineno, a.asname or a.name))
+            elif isinstance(node, binders):
+                value = node.value
+                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
+                is_logger = (isinstance(value, ast.Name) and value.id == "_LOGGER") or logger_call(value)
+                canonical = id(node) in top and id(value) in canonical_values
+                if is_logger and targets and not canonical:
+                    out.append((name, node.lineno, ", ".join(ast.unparse(t) for t in targets)))
+            elif logger_call(node) and id(node) not in canonical_values and not (
+                    isinstance(up, binders) and up.value is node):
+                out.append((name, node.lineno, ast.unparse(node.func)))
+            elif (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
+                    and node.value.id == "logging" and node.attr in levels | {"root", "Logger", "LoggerAdapter"}):
+                out.append((name, node.lineno, ast.unparse(node)))
+            elif isinstance(node, ast.Name) and node.id == "_LOGGER" and isinstance(node.ctx, ast.Load):
+                via = up
+                if isinstance(via, ast.Attribute) and via.value is node:
+                    if isinstance(parent.get(id(via)), ast.Call) and parent[id(via)].func is via:
+                        continue
+                    out.append((name, node.lineno, f"_LOGGER -> {ast.unparse(via)}"))
+                    continue
+                if isinstance(via, binders) and via.value is node:
+                    continue
+                if isinstance(via, (ast.keyword, ast.Starred)):
+                    via = parent.get(id(via))
+                where = ast.unparse(via.func) if isinstance(via, ast.Call) else type(via).__name__
+                out.append((name, node.lineno, f"_LOGGER -> {where}"))
+    return out
+
+
+#: Each place ``_LOGGER`` leaves the package's own call sites, and why the
+#: barrier need not follow it there.
+_R11_LOGGER_HANDOVERS = {
+    # Home Assistant's DataUpdateCoordinator logs a failed refresh at ERROR
+    # only on the success -> failure transition (its last_update_success
+    # latch) and at INFO on recovery, so it cannot flood.
+    ("coordinator.py", "_LOGGER -> super().__init__"): 1,
+}
+
+
+def _r11_alias_verdict(found):
+    seen = Counter((m, b) for m, _l, b in found)
+    return {k: (seen.get(k, 0), _R11_LOGGER_HANDOVERS.get(k, 0))
+            for k in set(seen) | set(_R11_LOGGER_HANDOVERS)
+            if seen.get(k, 0) != _R11_LOGGER_HANDOVERS.get(k, 0)}
+
+
 #: Unlatched WARNING/ERROR sites by why each may stay so. The sweep's 85-site
 #: disposition (dev/audit/rounds/round10/sweep-N-log-flood.md) less the
 #: instances routed through ``log_latch.log_held``.
@@ -42426,6 +42535,9 @@ _R10_LOG_ALLOWED_BY_REASON = {
         # R10-GENERIC-HEAT-CURVE-PERSISTENT: a baseline with no writer left is
         # named once and disarmed in the same call, so it cannot repeat.
         ("off_restore.py", "_restore_baseline"): 1,
+        # R11 D14-s2-03: a fit that raises ends the experiment in the same
+        # call (phase done, a refusal published), so it logs once per night armed.
+        ("sysid.py", "_finish"): 1,
     },
     "not reached per cycle: load, restore, migration, setup, frontend "
     "registration, a service call or shutdown": {
@@ -42476,7 +42588,33 @@ _r10_log_planted = _r10_unlatched_logs({
                   "def latched(self):\n    if not self._warned:\n        _LOGGER.warning('once')\n",
     "inputs.py": _r10_sources["inputs.py"]
     + "\ndef _age_gate(x):\n    _LOGGER.warning('a')\n    _LOGGER.warning('b')\n",
+    # R11 D14-s2-03: each level a flood can log at is a site, a quiet one is not
+    "levels.py": "def exc(self):\n    _LOGGER.exception('x')\n"
+                 "def crit(self):\n    _LOGGER.critical('x')\n"
+                 "def at_warning(self):\n    _LOGGER.log(logging.WARNING, 'x')\n"
+                 "def at_forty(self):\n    _LOGGER.log(40, 'x')\n"
+                 "def at_debug(self):\n    _LOGGER.log(logging.DEBUG, 'x')\n"
+                 "def at_info(self):\n    _LOGGER.info('x')\n"
+                 "def warn_alias(self):\n    _LOGGER.warn('x')\n"
+                 "def fatal_alias(self):\n    _LOGGER.fatal('x')\n",
 })
+_r11_aliases_found = _r11_logger_aliases(_r10_sources)
+_r11_aliases_planted = {(m, b) for m, _l, b in _r11_logger_aliases({
+    "ok.py": "import logging\n_LOGGER = logging.getLogger(__name__)\n"
+             "def f():\n    _LOGGER.warning('x')\n    _LOGGER.isEnabledFor(logging.DEBUG)\n",
+    "alias.py": "_LOGGER = logging.getLogger(__name__)\ndef f():\n    log = _LOGGER\n    log.warning('x')\n",
+    "child.py": "_LOG = logging.getLogger(__name__)\nCHILD = _LOGGER.getChild('c')\n",
+    "mod.py": "import logging as lg\n",
+    "field.py": "class C:\n    when: int\n    _LOGGER: object = None\n",
+    # R11 D14-s2-03 review: the shapes a logger reached the barrier's blind side by
+    "bare.py": "from logging import getLogger\nLOG = getLogger(__name__)\n",
+    "inline.py": "import logging\ndef f():\n    logging.getLogger(__name__).warning('x')\n",
+    "root.py": "import logging\ndef f():\n    logging.warning('x')\n    logging.root.error('y')\n",
+    "fromimp.py": "from .x import _LOGGER as log\n",
+    "param.py": "_LOGGER = logging.getLogger(__name__)\ndef f(log):\n    log.warning('x')\n"
+                "def g():\n    f(_LOGGER)\n    return _LOGGER\n",
+    "method.py": "_LOGGER = logging.getLogger(__name__)\ndef g():\n    return _LOGGER.error\n",
+})}
 R.check(
     "R10 N-log-flood barrier: every unlatched WARNING/ERROR is on the reasoned list "
     "with its exact count -- a persisting condition goes through log_held",
@@ -42489,9 +42627,31 @@ R.check(
     # one, and a second site inside a listed function, are each refused
     and ("planted.py", "poll") in _r10_log_verdict(_r10_log_planted)
     and ("planted.py", "latched") not in _r10_log_verdict(_r10_log_planted)
-    and ("inputs.py", "_age_gate") in _r10_log_verdict(_r10_log_planted),
+    and ("inputs.py", "_age_gate") in _r10_log_verdict(_r10_log_planted)
+    and all(("levels.py", f) in _r10_log_verdict(_r10_log_planted)
+            for f in ("exc", "crit", "at_warning", "at_forty", "warn_alias", "fatal_alias"))
+    and not {("levels.py", "at_debug"), ("levels.py", "at_info")} & set(_r10_log_verdict(_r10_log_planted)),
     f"mismatch {_r10_log_verdict(_r10_log_found)}; read {sum(_r10_log_found.values())} sites",
 )
+R.check(
+    "R11 N-log-flood barrier reach: every package logger is a module-level "
+    "``_LOGGER = logging.getLogger(...)``, the one name the barrier reads",
+    not _r11_alias_verdict(_r11_aliases_found)
+    # null control: the canonical binding and its method calls are not
+    # refused; perturbation: an alias, another getLogger name, a getChild, a
+    # logging alias, a bare-callee getLogger, an inline getLogger, a root
+    # logging call, a from-import of _LOGGER, a logger handed to a parameter
+    # or returned, and a bound method each are
+    and _r11_aliases_planted == {("alias.py", "log"), ("child.py", "_LOG"),
+                                 ("child.py", "CHILD"), ("mod.py", "lg"),
+                                 ("bare.py", "getLogger"), ("bare.py", "LOG"),
+                                 ("inline.py", "logging.getLogger"),
+                                 ("root.py", "logging.warning"), ("root.py", "logging.root"),
+                                 ("fromimp.py", "log"), ("param.py", "_LOGGER -> f"),
+                                 ("param.py", "_LOGGER -> Return"),
+                                 ("method.py", "_LOGGER -> _LOGGER.error")},
+    f"refused {_r11_alias_verdict(_r11_aliases_found)}; planted read {sorted(_r11_aliases_planted)}",
+)
 
 # THE RECORD JOB'S WINDOW CACHE WIRING (R10-RECORD-API-BUDGET, M1). The cache is
 # unit-pinned in `policy_lint.mjs`'s acceptance, but the saving only exists if
diff --git a/tests/structure.py b/tests/structure.py
index 87a5d72cd4..be96cf9822 100644
--- a/tests/structure.py
+++ b/tests/structure.py
@@ -92,6 +92,12 @@ Metrics (definitions, one line each; the code is the authority):
                               and compared PACKAGE-wide; each class counts its
                               members past the first -- the copies that would
                               go if the logic were shared (#1738 arm a)
+  in_function_copies          the same window written at two or more
+                              non-overlapping places of ONE function and in no
+                              other (R11 D7-s1-02): duplication_copies joins
+                              functions, so a copy inside one function moved
+                              no row. Keyed by place; each window counts its
+                              places past the first
   functions_cc_over_25 /      cyclomatic complexity 1 + decision points
   functions_cc_over_15        (if/elif, for, while, ternary, except, assert,
                               boolean operator terms beyond the first, each
@@ -103,6 +109,12 @@ Metrics (definitions, one line each; the code is the authority):
   import_cycle_modules        modules in a cycle of the package's import
                               graph, function-scope imports in and imports
                               under ``if TYPE_CHECKING:`` out (#1738)
+  unused_package_imports      ``from .<module> import N`` bindings the
+                              importing module never loads, that no other
+                              module re-imports from it and that no string in
+                              it names (R11 D7-s1-03): dead_top_level_symbols
+                              counts definitions, and a binding nothing reads
+                              keeps its definition live by name alone
   dead_top_level_symbols      top-level defs/classes/assignments no load in
                               the integration resolves to (dunder, HA entry
                               points, HA convention constants and
@@ -584,6 +596,35 @@ def bound_references(trees: list[tuple[Path, ast.Module]]) -> set[tuple[str, str
     return {(str(mods[m][0].relative_to(REPO_ROOT)), n) for m, n in found if m in mods}
 
 
+def unused_package_imports(trees: list[tuple[Path, ast.Module]]) -> list[tuple[str, int, str]]:
+    """``(rel, line, bound name)`` per package from-import nothing reads (R11 D7-s1-03).
+
+    A binding ``from .<module> import N [as A]`` is unused when the importing
+    module never loads ``A``, no module imports ``A`` from it (a re-export,
+    read off ``import_bindings``' own symbol bindings) and no string in it
+    names ``A`` (``__all__``, a ``getattr`` name, a patch target). A star
+    import binds no one name, so it is never a row.
+    """
+    mods = {p.relative_to(PACKAGE_DIR).as_posix()[:-3].replace("/", "."): (p, t)
+            for p, t in trees}
+    sym_bind, _mod_bind = import_bindings({m: (str(p), t) for m, (p, t) in mods.items()})
+    reexported = set(sym_bind.values())
+    out = []
+    for mod, (path, tree) in mods.items():
+        loads = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Store)}
+        words = {w for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)
+                 for w in n.value.replace(".", " ").split()}
+        for node in ast.walk(tree):
+            if not isinstance(node, ast.ImportFrom) or node.level == 0:
+                continue
+            for alias in node.names:
+                bound = alias.asname or alias.name
+                if alias.name == "*" or bound in loads or bound in words or (mod, bound) in reexported:
+                    continue
+                out.append((str(path.relative_to(REPO_ROOT)), node.lineno, bound))
+    return sorted(out)
+
+
 def is_dead_symbol(key: tuple[str, str], bound: set[tuple[str, str]],
                    exempt: set[tuple[str, str]]) -> bool:
     """No load resolves to ``(rel, name)``, and no convention or proof exempts it."""
@@ -766,21 +807,16 @@ def normalized_window(stmts: list[ast.stmt], local: set[str], modalias: set[str]
         ast.dump(Normalize().visit(ast.parse(ast.unparse(s)).body[0])) for s in stmts)
 
 
-def duplicate_clones(trees: list[tuple[Path, ast.Module]],
+def function_windows(trees: list[tuple[Path, ast.Module]],
                      window: int = DUP_WINDOW_STATEMENTS,
-                     min_nodes: int = DUP_MIN_NODES) -> list[list[tuple[str, str, int]]]:
-    """Clone classes: functions sharing a normalized statement window, package-wide.
+                     min_nodes: int = DUP_MIN_NODES):
+    """Yield ``(owner, digest, (first line, last line))`` per statement window.
 
-    A window is ``window`` consecutive statements of one block (a body, an
-    ``else``, a handler) carrying at least ``min_nodes`` AST nodes, nested
-    defs excluded. Two functions sharing any window are joined, IN ANY MODULE
-    (#1738 arm a: a copy placed in another module used to move nothing, the
-    same copy in its own module moved it). Each connected group of functions
-    is one clone class; ``duplication_copies`` counts every member past the
-    first, the copies that would go if the logic were shared -- a count of
-    copies, not of pairs, so a third copy costs one more, not two.
+    The one window rule both clone rows read: ``window`` consecutive
+    statements of one block (a body, an ``else``, a handler) carrying at least
+    ``min_nodes`` AST nodes, nested defs excluded, digested in
+    ``normalized_window``'s form. ``owner`` is ``(rel, function, line)``.
     """
-    windows: dict[str, set[tuple[str, str, int]]] = defaultdict(set)
     for path, tree in trees:
         rel = str(path.relative_to(REPO_ROOT))
         modalias = _module_aliases(tree)
@@ -809,7 +845,55 @@ def duplicate_clones(trees: list[tuple[Path, ast.Module]],
                             continue
                         digest = hashlib.sha1(
                             normalized_window(stmts, local, modalias).encode()).hexdigest()
-                        windows[digest].add(owner)
+                        yield owner, digest, (stmts[0].lineno, stmts[-1].end_lineno)
+
+
+def in_function_copies(trees: list[tuple[Path, ast.Module]],
+                       window: int = DUP_WINDOW_STATEMENTS,
+                       min_nodes: int = DUP_MIN_NODES,
+                       ) -> list[tuple[str, str, int, list[tuple[int, int]]]]:
+    """``(rel, function, line, places)`` per window one function writes twice.
+
+    ``duplicate_clones`` joins FUNCTIONS, so a rule written at two places of
+    one function is one member and moved no row (R11 D7-s1-02). This keys the
+    window by PLACE: the spans one function holds it at, overlapping spans
+    merged (a statement repeated three times in a row is one place, not two),
+    and only a window no second function holds -- that one is a clone class
+    already, priced by ``duplication_copies``.
+    """
+    owners: dict[str, set[tuple[str, str, int]]] = defaultdict(set)
+    spans: dict[tuple[tuple[str, str, int], str], list[tuple[int, int]]] = defaultdict(list)
+    for owner, digest, span in function_windows(trees, window, min_nodes):
+        owners[digest].add(owner)
+        spans[(owner, digest)].append(span)
+    out = []
+    for (owner, digest), found in spans.items():
+        places: list[tuple[int, int]] = []
+        for span in sorted(found):
+            if not places or span[0] > places[-1][1]:
+                places.append(span)
+        if len(places) > 1 and len(owners[digest]) == 1:
+            out.append((*owner, places))
+    return sorted(out)
+
+
+def duplicate_clones(trees: list[tuple[Path, ast.Module]],
+                     window: int = DUP_WINDOW_STATEMENTS,
+                     min_nodes: int = DUP_MIN_NODES) -> list[list[tuple[str, str, int]]]:
+    """Clone classes: functions sharing a normalized statement window, package-wide.
+
+    A window is ``window`` consecutive statements of one block (a body, an
+    ``else``, a handler) carrying at least ``min_nodes`` AST nodes, nested
+    defs excluded. Two functions sharing any window are joined, IN ANY MODULE
+    (#1738 arm a: a copy placed in another module used to move nothing, the
+    same copy in its own module moved it). Each connected group of functions
+    is one clone class; ``duplication_copies`` counts every member past the
+    first, the copies that would go if the logic were shared -- a count of
+    copies, not of pairs, so a third copy costs one more, not two.
+    """
+    windows: dict[str, set[tuple[str, str, int]]] = defaultdict(set)
+    for owner, digest, _span in function_windows(trees, window, min_nodes):
+        windows[digest].add(owner)
     parent: dict[tuple[str, str, int], tuple[str, str, int]] = {}
 
     def find(x):
@@ -3009,6 +3093,8 @@ def measure() -> dict:
     writers = coordinator_writers(roles)
 
     clones = duplicate_clones(trees)
+    in_fn_copies = in_function_copies(trees)
+    unused_imports = unused_package_imports(trees)
     cycles = import_cycle_modules(trees)
     excess, helper_loc = class_excess(trees, helpers)
     max_method_loc, max_cc = table_maxima(monsters, cc_scores)
@@ -3033,6 +3119,8 @@ def measure() -> dict:
         "max_method_loc": max_method_loc,
         "max_cc": max_cc,
         "duplication_copies": sum(len(g) - 1 for g in clones),
+        "in_function_copies": sum(len(places) - 1 for *_owner, places in in_fn_copies),
+        "unused_package_imports": len(unused_imports),
         "functions_cc_over_25": sum(1 for cc, *_ in cc_scores if cc > CC_LIMITS[0]),
         "functions_cc_over_15": len(cc_scores),
         "const_modules_over_50": sum(1 for n in const_fanout.values() if n > CONST_FANOUT_LIMIT),
@@ -3063,6 +3151,8 @@ def measure() -> dict:
         "dynamic_exempt": sorted(dynamic_exempt),
         "dynamic_problems": dynamic_problems,
         "clones": clones,
+        "in_function_copies": in_fn_copies,
+        "unused_imports": unused_imports,
         "seam_rows": seam["seam_rows"],
         "helpers": sorted(helpers),
         "private_reach": reach,
@@ -3158,6 +3248,16 @@ def print_report(result: dict) -> None:
     for group in tables["clones"]:
         print("  " + "  ==  ".join(f"{rel}:{line} {name}" for rel, name, line in group))
 
+    print()
+    print("########## duplication inside one function (the same window at two places) ##########")
+    for rel, name, line, places in tables["in_function_copies"]:
+        print(f"  {rel}:{line} {name}  " + "  ==  ".join(f"{a}-{b}" for a, b in places))
+
+    print()
+    print("########## package from-imports nothing reads ##########")
+    for rel, line, bound in tables["unused_imports"]:
+        print(f"  {rel}:{line}  {bound}")
+
     print()
     print("########## coordinator private reach (outside its methods and helpers) ##########")
     for rel, line, member, kind, fn in tables["private_reach"]:
@@ -4058,6 +4158,50 @@ ROLE_SELF_CHECK_SOURCES = {
         "        return 4\n",
 }
 
+# One window written twice in one function is an in-function copy; the same
+# window in a second function is a clone class, and three consecutive copies
+# of one statement are a run, so neither of those is.
+IN_FUNCTION_SELF_CHECK_SOURCES = {
+    "twice": (
+        "def twice(xs, k):\n"
+        "    t = sum(v * k for v in xs if v > 0)\n"
+        "    r = max(t, len(xs) * k - 1)\n"
+        "    print(r)\n"
+        "    t = sum(v * k for v in xs if v > 0)\n"
+        "    r = max(t, len(xs) * k - 1)\n"
+        "    return r\n"),
+    "two_functions": (
+        "def one(xs, k):\n"
+        "    t = sum(v * k for v in xs if v > 0)\n"
+        "    r = max(t, len(xs) * k - 1)\n"
+        "    print(r)\n"
+        "    t = sum(v * k for v in xs if v > 0)\n"
+        "    r = max(t, len(xs) * k - 1)\n"
+        "    return r\n"
+        "def other(xs, k):\n"
+        "    t = sum(v * k for v in xs if v > 0)\n"
+        "    r = max(t, len(xs) * k - 1)\n"
+        "    return r\n"),
+    "run": (
+        "def run(xs, k):\n"
+        "    t = max(sum(v * k for v in xs if v > 0), len(xs) * k - 1)\n"
+        "    t = max(sum(v * k for v in xs if v > 0), len(xs) * k - 1)\n"
+        "    t = max(sum(v * k for v in xs if v > 0), len(xs) * k - 1)\n"
+        "    return t\n"),
+}
+
+#: ``reader.py`` binds five names: one loaded, one only named in a string, one
+#: re-imported from it by ``user.py``, and two read nowhere (one through ``as``).
+UNUSED_IMPORT_SELF_CHECK_SOURCES = {
+    "const.py": "READ = 1\nNAMED = 2\nPASSED = 3\nUNREAD = 4\nORIGINAL = 5\n",
+    "reader.py": ("from .const import READ, NAMED, PASSED, UNREAD\n"
+                  "from .const import ORIGINAL as renamed\n"
+                  "from .const import *\n"
+                  "__all__ = ['NAMED']\n"
+                  "def f():\n    return READ\n"),
+    "user.py": "from .reader import PASSED\nprint(PASSED)\n",
+}
+
 # One window, three spellings of it: a second copy in another module is a
 # copy, and a third costs one more, not two more.
 DUP_SELF_CHECK_BODY = (
@@ -4280,6 +4424,13 @@ def role_self_check() -> tuple[tuple[str, bool], ...]:
         return sum(len(g) - 1 for g in duplicate_clones(
             [(PACKAGE_DIR / f"m{i}.py", ast.parse(s)) for i, s in enumerate(srcs)]))
 
+    def in_function(source: str) -> list[int]:
+        return [len(places) for *_owner, places in in_function_copies(
+            [(PACKAGE_DIR / "twice.py", ast.parse(source))])]
+
+    unused = {(rel.rsplit("/", 1)[-1], bound) for rel, _line, bound in unused_package_imports([
+        (PACKAGE_DIR / m, ast.parse(src)) for m, src in UNUSED_IMPORT_SELF_CHECK_SOURCES.items()])}
+
     field_dead, field_kept = dead_members(
         Package([(PACKAGE_DIR / "fields.py", ast.parse(FIELD_SELF_CHECK_SOURCE))]))
 
@@ -4320,6 +4471,15 @@ def role_self_check() -> tuple[tuple[str, bool], ...]:
         ("a copy in another module is one copy, renamed or not",
          copies(("xs", "k", "t"), ("values", "scale", "total")) == 1),
         ("a third copy costs one more", copies(("a", "b", "c"), ("d", "e", "f"), ("g", "h", "i")) == 2),
+        ("a window written twice in one function is an in-function copy",
+         in_function(IN_FUNCTION_SELF_CHECK_SOURCES["twice"]) == [2]),
+        ("a window one function writes twice and another once is a clone class, not an in-function copy",
+         in_function(IN_FUNCTION_SELF_CHECK_SOURCES["two_functions"]) == []
+         and copies(("xs", "k", "t"), ("xs", "k", "t")) == 1),
+        ("a statement repeated in a row is one place, not two",
+         in_function(IN_FUNCTION_SELF_CHECK_SOURCES["run"]) == []),
+        ("a package from-import nothing loads is unused",
+         unused == {("reader.py", "UNREAD"), ("reader.py", "renamed")}),
         ("a function-scope import closes a cycle", cycles(CYCLE_SELF_CHECK_SOURCES["b.py"]) == [["a", "b"]]),
         ("a TYPE_CHECKING import is not an edge", cycles(CYCLE_SELF_CHECK_GUARDED) == []),
     )
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 8f925f20e3..6a4af61604 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -10,12 +10,14 @@
  "functions_cc_over_15": 26,
  "functions_cc_over_25": 7,
  "import_cycle_modules": 0,
+ "in_function_copies": 11,
  "max_cc": 44,
  "max_class_loc": 7875,
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
  "name_kept_members": 38,
- "recorded_at": "e352724335c136b65562cd3e71f728549ad04a82",
- "seam_cut_total": 415
+ "recorded_at": "bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f",
+ "seam_cut_total": 415,
+ "unused_package_imports": 14
 }
diff --git a/tools/policy/field_coverage.mjs b/tools/policy/field_coverage.mjs
index 20f6f83d74..d31e029881 100644
--- a/tools/policy/field_coverage.mjs
+++ b/tools/policy/field_coverage.mjs
@@ -488,6 +488,15 @@ const CENSUSES = [
     plant: { file: 'custom_components/heatpump_optimizer/const.py', add: '\n\nclass _CensusKept:\n    def as_dict(self):\n        return {}\n\n\n(lambda x: (x.as_dict(), _CensusKept))\n' },
     read: (out) => /^RESULT name_kept_members=(\d+)\b/m.exec(out)?.[1],
   },
+  {
+    // A package from-import the importing module never loads (R11 D7-s1-03).
+    // Planted in a module that already imports from .const, so no new edge.
+    name: 'structure.py unused_package_imports',
+    gate: 'unused_package_imports',
+    instrument: STRUCTURE_PY,
+    plant: { file: 'custom_components/heatpump_optimizer/away.py', add: '\n\nfrom .const import DOMAIN as _census_unused_package_import\n' },
+    read: (out) => /^RESULT unused_package_imports=(\d+)\b/m.exec(out)?.[1],
+  },
   {
     // One unused top-level card function: no other token names it.
     name: 'archscore card_dead_definitions',

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
