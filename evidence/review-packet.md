# Review packet #3143
head: 7786d6e6b40b5694000c8f6222a9be56b4a3a075
base: f04b25a005f51b9df48154a6544c03e6873ed9de

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124982674855 neutral
arch-score / arch-score id=124982473760 success
arm id=124982357783 skipped
budget-raise-gate / budget-raise-gate id=124982474025 success
cancel-superseded id=124982331608 success
codeql / Analyze (actions) id=124982473766 success
codeql / Analyze (javascript-typescript) id=124982473893 success
codeql / Analyze (python) id=124982473770 in_progress
governance / delivery-status id=124982473887 success
governance / delivery-status-publish id=124982475481 skipped
governance / env-matrix id=124982473920 success
governance / instrument-self-tests id=124982474000 in_progress
governance / policy-docs id=124982473861 success
governance / record id=124982475726 skipped
governance / wave-script id=124982473858 success
hassfest / hassfest id=124982473784 success
kernel-points id=124982474770 skipped
prelude id=124982331536 success
refresh id=124982331404 success
tests / arch-instrument id=124982645564 success
tests / briefs id=124982473735 success
tests / browser id=124982645661 success
tests / claims-autofix id=124986012340 skipped
tests / closure-scope id=124982473941 success
tests / closures id=124982645589 in_progress
tests / coverage id=124982645619 in_progress
tests / fast (3.14) id=124982645540 success
tests / mutation id=124982473802 success
tests / mutation-autofix id=124982704603 skipped
tests / mutation-pins id=124982704950 skipped
tests / nightly-ha id=124982646838 skipped
tests / nightly-status id=124982473694 success
tests / replay id=124982646671 skipped
tests / typing id=124982645615 success
validate / validate-hacs id=124982473773 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 2f7ab1ba: R10-ROSTER-OPS-2
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/roster_edit.py --self-test
             `tools/audit/seat/roster_edit.py` is in the tree at this head
  ok         python3 tools/audit/seat/r10_roster_ops_mutants.py --self-test
             `tools/audit/seat/r10_roster_ops_mutants.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git merge-tree --write-tree HEAD refs/pull/3054/head
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 3 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3143.md b/dev/programme/delivery/3143.md
new file mode 100644
index 000000000..4fb6b2257
--- /dev/null
+++ b/dev/programme/delivery/3143.md
@@ -0,0 +1 @@
+- [#3143](https://github.com/tvofi/heatpump_optimizer/pull/3143) — **open**, R10-ROSTER-OPS-2 (part 1): set-size and set-files roster ops (R10-ROSTER-OPS-2)
diff --git a/tools/audit/seat/instruments/roster_edit.py.md b/tools/audit/seat/instruments/roster_edit.py.md
index bc6ac41e1..d191c3f42 100644
--- a/tools/audit/seat/instruments/roster_edit.py.md
+++ b/tools/audit/seat/instruments/roster_edit.py.md
@@ -6,7 +6,12 @@
   fixes|issues]` (refuses an absent N), `append-group`, `edit-brief`,
   `append-carry`, `drop-carry <group> <index|--match TEXT>` (0-based index,
   or the one entry containing TEXT; the last drop leaves `"carry": []`, the
-  key kept),
+  key kept), `set-size <group> <size> [--cite <ref>@<sha>]` (size must be in
+  the durations model; old size and cite go to `resume.note`),
+  `set-files <group> [--add <path>...] [--set-files <p,p|->] [--set-hot <p,p|->]
+  [--cite <ref>@<sha>]` (a new path must be in the tree at origin/main or at the
+  cited sha; a hot token a basename of the group's files or a known hot token;
+  a value already held writes nothing),
   `set-after <group> <G1,G2,...|->` (replaces the after-edges whole, `-` for
   none), and `set-resume <group> --field
   <stage|commit|branch|last_step|next_step|note>` for the resume free-text
diff --git a/tools/audit/seat/r10_roster_ops_mutants.py b/tools/audit/seat/r10_roster_ops_mutants.py
index fa13963e1..0c5e08318 100644
--- a/tools/audit/seat/r10_roster_ops_mutants.py
+++ b/tools/audit/seat/r10_roster_ops_mutants.py
@@ -119,6 +119,51 @@ PLANTS = {
 }
 
 
+# --- R10-ROSTER-OPS-2 part 1: set-size and set-files. A SEPARATE block, merged
+# into PLANTS here so it neither edits the table above nor the docstring.
+#   Z1-Z4   set-size: the _size_why check skipped, the cite check skipped, the
+#           size write dropped, and the no-op case writing a note (null control).
+#   Z5-Z9   set-files: the path-in-tree refusal skipped, the files write
+#           dropped, the hot_files write dropped, the hot-token refusal
+#           skipped, the cite check skipped.
+#   Z10     set-files' unknown group (a silent write to a detached dict).
+#   Z11     the dispatch dropping the cite, so set-size never checks it.
+#   Z12     set-files writing hot_files on a call that never named it.
+#   R11     cite_why's merge-base --is-ancestor clause dropped, so a ref holds
+#           any commit that exists (the fix review's survivor of #3143).
+CITE_GUARD = ("    if cite is not None and cite_check:\n"
+              "        why = cite_check(cite)\n        if why:\n"
+              "            raise Refuse(f\"{op}: {why}\")\n")
+PLANTS.update({
+    "Z1": ('    why = _size_why(size, sizes, rel, group)\n    if why:\n'
+           '        raise Refuse(f"set-size: {why}")\n',
+           '    why = None  # Z1\n    if why:\n'
+           '        raise Refuse(f"set-size: {why}")\n'),
+    "Z2": (CITE_GUARD.replace("{op}", "set-size"),
+           CITE_GUARD.replace("{op}", "set-size").replace(
+               "if cite is not None and cite_check:", "if False:  # Z2")),
+    "Z3": ('    g["size"] = size\n', ""),
+    "Z4": ("    if old == size:\n        return\n", ""),
+    "Z5": ("        if p not in old_files and in_tree and not in_tree(p, cite):\n",
+           "        if False:  # Z5\n"),
+    "Z6": ('        g["files"] = files\n', ""),
+    "Z7": ('        g["hot_files"] = hot\n', ""),
+    "Z8": ("        if bad:\n            raise Refuse(f\"set-files: hot_files token",
+           "        if False:  # Z8\n            raise Refuse(f\"set-files: hot_files token"),
+    "Z9": (CITE_GUARD.replace("{op}", "set-files"),
+           CITE_GUARD.replace("{op}", "set-files").replace(
+               "if cite is not None and cite_check:", "if False:  # Z9")),
+    "Z10": ("    g = _need(roster, group)\n    if not add and set_files",
+            f"    {DETACHED}\n    if not add and set_files"),
+    "Z11": ("op_set_size(roster, a.group, value, sizes, rel, a.cite, cite_check)",
+            "op_set_size(roster, a.group, value, sizes, rel, None, cite_check)"),
+    "Z12": ("    if hot != old_hot:\n", "    if True:  # Z12\n"),
+    "R11": ('                    and _git_ok(checkout, "merge-base", "--is-ancestor",\n'
+            '                                sha, cand):\n',
+            '                    and True:  # R11\n'),
+})
+
+
 def target_self_test():
     r = subprocess.run([sys.executable, TARGET, "--self-test"], cwd=ROOT,
                        capture_output=True, text=True)
diff --git a/tools/audit/seat/roster_edit.py b/tools/audit/seat/roster_edit.py
index 270dd0700..8c7bf8422 100644
--- a/tools/audit/seat/roster_edit.py
+++ b/tools/audit/seat/roster_edit.py
@@ -10,6 +10,9 @@
     python3 tools/audit/seat/roster_edit.py set-resume  <group> --field <stage|commit|branch|last_step|next_step|note> <text | @file>
     python3 tools/audit/seat/roster_edit.py set-after   <group> <G1,G2,... | ->
     python3 tools/audit/seat/roster_edit.py drop-carry  <group> <index | --match TEXT>
+    python3 tools/audit/seat/roster_edit.py set-size    <group> <size> [--cite <ref>@<sha>]
+    python3 tools/audit/seat/roster_edit.py set-files   <group> [--add <path>...] [--set-files <p,p | ->]
+        [--set-hot <p,p | ->] [--cite <ref>@<sha>]
         [--at-sha SHA] [--checkout DIR] [--roster-ref BR] [--branch OUT]
         [--roster-path PATH] [--worktree DIR] [--lint-cwd DIR] [--push]
         [--message MSG]
@@ -103,6 +106,19 @@ resolve is refused whether or not the text names a proposal.
                last entry leaves the `carry` list empty, never removing the
                key (27 of the 91 live groups carry `"carry": []`, and none
                omits it, so the key's presence is the file's own shape).
+  set-size     writes the group's own `size`, refusing a size the duration
+               model (tools/plan/durations.json) does not key -- the
+               `_size_why` check append-group runs -- and, with --cite, a
+               cite whose ref does not hold the sha. The old size and the
+               cite go to resume.note; the current size writes nothing.
+  set-files    writes `files` (--add appends, --set-files replaces whole, `-`
+               for none) and `hot_files` (--set-hot, `-` for none) for one
+               existing group. A path new to `files` must be in the tree at
+               origin/main or at the cited sha; a hot token must be a
+               basename of the resulting files or one some group already
+               holds. Old values and the cite go to resume.note; a value
+               already held writes nothing, and every other field stays
+               byte-identical.
 """
 
 from __future__ import annotations
@@ -463,6 +479,139 @@ def _text(arg):
     return arg
 
 
+# --------------------------------------------- set-size / set-files
+# R10-ROSTER-OPS-2 part 1. One op pair for the fields a group owns outright --
+# `size` and `files`/`hot_files` -- each in its own functions so the write path
+# above is untouched. A change records what it replaced, and the cite it
+# rests on, in resume.note; a change to the value already held writes nothing.
+CITE_RE = re.compile(r"\A([A-Za-z0-9._/-]+)@([0-9a-f]{7,40})\Z")
+
+
+def _git_ok(checkout, *args) -> bool:
+    return subprocess.run(["git", "-C", str(checkout), *args],
+                          capture_output=True).returncode == 0
+
+
+def cite_why(cite, checkout):
+    """Why `cite` (`<ref>@<sha>`) is not a ref that holds that sha, or None."""
+    m = CITE_RE.match(cite)
+    if not m:
+        return f"cite {cite!r} is not <ref>@<sha>"
+    ref, sha = m.groups()
+    if _git_ok(checkout, "cat-file", "-e", f"{sha}^{{commit}}"):
+        for cand in (f"origin/{ref}", ref):
+            if _git_ok(checkout, "rev-parse", "--verify", "--quiet",
+                       f"{cand}^{{commit}}") \
+                    and _git_ok(checkout, "merge-base", "--is-ancestor",
+                                sha, cand):
+                return None
+    return f"cite ref {ref!r} does not hold {sha}"
+
+
+def path_in_tree(checkout, path, cite=None) -> bool:
+    """Whether `path` is in the tree at origin/main or at the cited sha."""
+    revs = ["origin/main"] + ([CITE_RE.match(cite).group(2)] if cite else [])
+    return any(_git_ok(checkout, "cat-file", "-e", f"{r}:{path}")
+               for r in revs)
+
+
+def _note_append(g, text):
+    resume = g.setdefault("resume", {})
+    resume["note"] = f"{resume['note']} | {text}" if resume.get("note") else text
+
+
+def _cited(text, cite):
+    return f"{text} (cite {cite})" if cite else text
+
+
+def op_set_size(roster, group, size, sizes, rel="", cite=None, cite_check=None):
+    """Write a group's own `size`, vocabulary-checked against the duration
+    model by `_size_why`; the old size and the cite go to resume.note."""
+    g = _need(roster, group)
+    if not size:
+        raise Refuse(f"set-size: {group} needs a size")
+    why = _size_why(size, sizes, rel, group)
+    if why:
+        raise Refuse(f"set-size: {why}")
+    if cite is not None and cite_check:
+        why = cite_check(cite)
+        if why:
+            raise Refuse(f"set-size: {why}")
+    old = g.get("size")
+    if old == size:
+        return
+    g["size"] = size
+    _note_append(g, _cited(f"set-size {old or 'unset'} -> {size}", cite))
+
+
+def _paths(spec, what):
+    if spec == "-":
+        return []
+    out = [p.strip() for p in spec.split(",") if p.strip()]
+    repeated = sorted({p for p in out if out.count(p) > 1})
+    if repeated:
+        raise Refuse(f"set-files: duplicate {what}: {repeated}")
+    return out
+
+
+def op_set_files(roster, group, add=(), set_files=None, set_hot=None,
+                 cite=None, cite_check=None, in_tree=None):
+    """Write a group's `files` (`--add` appends, `--set-files` replaces whole,
+    `-` for none) and `hot_files` (`--set-hot`, `-` for none). A path new to
+    `files` must be in the tree (`in_tree`); a hot token must be a basename of
+    the group's resulting files or one some group already holds."""
+    g = _need(roster, group)
+    if not add and set_files is None and set_hot is None:
+        raise Refuse("set-files needs --add, --set-files or --set-hot")
+    if cite is not None and cite_check:
+        why = cite_check(cite)
+        if why:
+            raise Refuse(f"set-files: {why}")
+    old_files, old_hot = list(g.get("files") or []), list(g.get("hot_files") or [])
+    files = list(old_files)
+    if set_files is not None:
+        files = _paths(set_files, "path")
+    files += [p for p in dict.fromkeys(add) if p not in files]
+    for p in files:
+        if p not in old_files and in_tree and not in_tree(p, cite):
+            raise Refuse(f"set-files: {p!r} is not in the tree at origin/main"
+                         + (f" or at {cite}" if cite else ""))
+    hot = old_hot
+    if set_hot is not None:
+        hot = _paths(set_hot, "hot token")
+        known = {t for x in roster.get("groups", [])
+                 for t in x.get("hot_files") or []}
+        base = {f.rstrip("/").rsplit("/", 1)[-1] for f in files} | set(files)
+        bad = [t for t in hot if t not in base and t not in known]
+        if bad:
+            raise Refuse(f"set-files: hot_files token {bad} is neither a files "
+                         f"basename of {group} nor a known hot-file token")
+    notes = []
+    if files != old_files:
+        g["files"] = files
+        notes.append(f"files {old_files} -> {files}")
+    if hot != old_hot:
+        g["hot_files"] = hot
+        notes.append(f"hot_files {old_hot} -> {hot}")
+    if notes:
+        _note_append(g, _cited("set-files " + "; ".join(notes), cite))
+
+
+def apply_files_op(roster, a, value, rel, checkout, worktree):
+    """The set-size / set-files dispatch `main` calls beside `apply_op`."""
+    cite_check = lambda c: cite_why(c, checkout)
+    if a.op == "set-size":
+        try:
+            sizes = roster_lib.sizes(roster_lib.read_durations(worktree))
+        except roster_lib.SchemaError as e:
+            raise Refuse(str(e))
+        op_set_size(roster, a.group, value, sizes, rel, a.cite, cite_check)
+    else:
+        op_set_files(roster, a.group, a.add or (), a.set_files, a.set_hot,
+                     a.cite, cite_check,
+                     lambda p, c: path_in_tree(checkout, p, c))
+
+
 def added_texts(before, after):
     """The roster text `after` adds over `before`: a new group's brief and
     carries, a changed brief, and carry entries `before` did not hold."""
@@ -770,7 +919,8 @@ def main(argv=None) -> int:
     p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
     p.add_argument("op", choices=("set-stage", "wire-issue", "unwire-issue", "append-group",
                                   "edit-brief", "append-carry", "set-resume",
-                                  "set-after", "drop-carry"))
+                                  "set-after", "drop-carry", "set-size",
+                                  "set-files"))
     p.add_argument("group")
     p.add_argument("value", nargs="?")
     p.add_argument("--at-sha")
@@ -781,6 +931,13 @@ def main(argv=None) -> int:
                    help="the value, for when a positional value does not fit")
     p.add_argument("--match",
                    help="drop-carry: drop the one carry entry containing it")
+    p.add_argument("--cite", help="set-size / set-files: <ref>@<sha>, a ref "
+                   "that must hold the sha; recorded in resume.note")
+    p.add_argument("--add", nargs="+", help="set-files: paths appended to files")
+    p.add_argument("--set-files", help="set-files: replace files whole "
+                   "(comma list, - for none)")
+    p.add_argument("--set-hot", help="set-files: replace hot_files whole "
+                   "(comma list, - for none)")
     p.add_argument("--checkout", default=".")
     p.add_argument("--roster-ref", default=None,
                    help="the base ref (default main)")
@@ -807,8 +964,16 @@ def main(argv=None) -> int:
         p.error("drop-carry takes an index or --match, not both")
     if a.op == "drop-carry" and value is None and a.match is None:
         p.error("drop-carry needs an index or --match")
-    if a.match is None and (value is None
-                            or (value == "" and a.op != "set-resume")):
+    if a.op == "set-files" and value is not None:
+        p.error("set-files takes --add, --set-files or --set-hot, no value")
+    if a.op not in ("set-size", "set-files") and a.cite:
+        p.error("--cite is a set-size / set-files flag")
+    if a.op != "set-files" and (a.add or a.set_files is not None
+                                or a.set_hot is not None):
+        p.error("--add, --set-files and --set-hot are set-files flags")
+    if a.op != "set-files" and a.match is None and (
+            value is None or (value == "" and a.op not in ("set-resume",
+                                                           "set-size"))):
         p.error(f"{a.op} needs a value argument")
     if a.op == "set-resume" and not a.field:
         p.error("set-resume needs --field")
@@ -838,6 +1003,9 @@ def main(argv=None) -> int:
                         roster_lib.read_durations(a.worktree))
                 except roster_lib.SchemaError as e:
                     raise Refuse(str(e))
+            if a.op in ("set-size", "set-files"):
+                apply_files_op(roster, a, value, rel, a.checkout, a.worktree)
+                return True
             apply_op(roster, a.op, a.group, value, a.field, a.at_sha, a.match,
                      rel, sizes)
             if a.op == "set-stage" or (a.op == "set-resume" and a.field == "stage"):
@@ -1320,6 +1488,180 @@ def _self_test() -> int:
           refuses("--match is a drop-carry flag", "set-after", "R9-B",
                   "R9-A", match="x"))
 
+    # set-size / set-files (R10-ROSTER-OPS-2 part 1): one op pair for the
+    # carries that asked for set-size (with and without a cite), set-files
+    # --add, --set-hot and a whole-field replace. Every refusal leaves the
+    # remote branch where it was; every null control is byte-identical.
+    sf_main = run(["git", "-C", str(drv), "rev-parse", "origin/main"]).strip()
+    run(["git", "-C", str(drv), "checkout", "-q", "-b", "cited", "origin/main"])
+    (drv / "NEW.md").write_text("added by the cited ref\n", encoding="utf-8")
+    (drv / "__bad__.md").write_text("lint plant\n", encoding="utf-8")
+    run(["git", "-C", str(drv), "add", "-A"])
+    run(["git", "-C", str(drv), "commit", "-q", "-m", "cited ref adds files"])
+    sf_cited = run(["git", "-C", str(drv), "rev-parse", "HEAD"]).strip()
+    run(["git", "-C", str(drv), "push", "-q", "origin", "cited"])
+    run(["git", "-C", str(drv), "checkout", "-q", "--detach", "origin/main"])
+
+    def more(op, group, *extra, value=None, wt="wt"):
+        args = [op, group] + ([value] if value is not None else []) + list(extra)
+        try:
+            return main(args + ["--checkout", str(drv), "--roster-ref", "main",
+                                "--branch", "edit-1", "--worktree",
+                                str(Path(tmp, wt)), "--lint-cwd", str(seed),
+                                "--issue-state", str(ISSUES["closed"]),
+                                "--push"])
+        except SystemExit as e:
+            return e.code
+
+    def more_refusal(*args, **kw):
+        err = io.StringIO()
+        with contextlib.redirect_stderr(err):
+            rc = sysrc(lambda: more(*args, **kw))
+        return rc, err.getvalue()
+
+    def grp(group):
+        return next(g for g in branch_roster()["groups"] if g["group"] == group)
+
+    def sans(g, *keys):
+        """A group minus some top-level keys and resume.note: what an op that
+        owns those must leave of everything else."""
+        out = json.loads(json.dumps(g))
+        for k in keys:
+            out.pop(k, None)
+        out.get("resume", {}).pop("note", None)
+        return out
+
+    t_sf = tip()
+    rc, said = more_refusal("set-size", "R9-A", "--cite", f"main@{sf_main}",
+                            value="XL")
+    check("set-size refuses a size the durations model lacks, naming it",
+          rc == 2 and "not in the durations model" in said and "'XL'" in said
+          and tip() == t_sf, (rc, said[-200:]))
+    check("set-size refuses an empty size",
+          more_refusal("set-size", "R9-A", value="")[0] == 2 and tip() == t_sf)
+    check("set-size refuses an unknown group",
+          more_refusal("set-size", "R9-ZZ", value="L")[0] == 2
+          and "no roster group" in more_refusal("set-size", "R9-ZZ", value="L")[1])
+    rc, said = more_refusal("set-size", "R9-A", "--cite", f"main@{'f' * 40}",
+                            value="L")
+    check("set-size refuses a cite whose ref lacks the sha",
+          rc == 2 and "does not hold" in said and tip() == t_sf, (rc, said[-200:]))
+    rc, said = more_refusal("set-size", "R9-A", "--cite", f"main@{sf_cited}",
+                            value="L")
+    check("set-size refuses a cite whose sha exists but main does not hold it",
+          rc == 2 and "does not hold" in said and tip() == t_sf, (rc, said[-200:]))
+    rc, said = more_refusal("set-size", "R9-A", "--cite", "no-such-ref@" + sf_main,
+                            value="L")
+    check("set-size refuses a cite whose ref does not exist",
+          rc == 2 and "does not hold" in said and tip() == t_sf, (rc, said[-200:]))
+    rc, said = more_refusal("set-size", "R9-A", "--cite", "mainish", value="L")
+    check("set-size refuses a cite that is not <ref>@<sha>",
+          rc == 2 and "<ref>@<sha>" in said and tip() == t_sf, (rc, said[-200:]))
+    before_a = grp("R9-A")
+    check("set-size with a valid cite lands",
+          more("set-size", "R9-A", "--cite", f"main@{sf_main}", value="L") == 0
+          and grp("R9-A").get("size") == "L")
+    note = (grp("R9-A").get("resume") or {}).get("note") or ""
+    check("... recording the old size and the cite in resume.note",
+          "set-size" in note and "unset" in note and "L" in note
+          and f"main@{sf_main}" in note, note)
+    check("... and touching no other field",
+          sans(grp("R9-A"), "size") == sans(before_a, "size"))
+    t_sf = tip()
+    check("set-size to the current size is byte-identical (null control)",
+          more("set-size", "R9-A", "--cite", f"main@{sf_main}", value="L") == 0
+          and tip() == t_sf)
+    check("set-size without a cite lands (the cite is optional)",
+          more("set-size", "R9-B", value="M") == 0
+          and grp("R9-B").get("size") == "M")
+    check("set-size from a recorded size names the old one",
+          more("set-size", "R9-B", value="S") == 0
+          and "M -> S" in grp("R9-B")["resume"]["note"])
+
+    t_sf = tip()
+    rc, said = more_refusal("set-files", "R9-A", "--add", "no/such/path.py")
+    check("set-files --add refuses a path not in the tree at origin/main",
+          rc == 2 and "not in the tree" in said and "no/such/path.py" in said
+          and tip() == t_sf, (rc, said[-200:]))
+    rc, said = more_refusal("set-files", "R9-A", "--add", "NEW.md")
+    check("... even one a branch outside origin/main adds, when uncited",
+          rc == 2 and "not in the tree" in said and tip() == t_sf)
+    check("set-files unknown group refused",
+          more_refusal("set-files", "R9-ZZ", "--add", "README.md")[0] == 2
+          and "no roster group" in more_refusal("set-files", "R9-ZZ",
+                                                "--add", "README.md")[1])
+    rc, said = more_refusal("set-files", "R9-A")
+    check("set-files with nothing to write refused",
+          rc == 2 and "needs --add" in said and tip() == t_sf, (rc, said[-200:]))
+    rc, said = more_refusal("set-files", "R9-A", "--add", "README.md",
+                            "--cite", f"main@{'f' * 40}")
+    check("set-files refuses a cite whose ref lacks the sha",
+          rc == 2 and "does not hold" in said and tip() == t_sf)
+    rc, said = more_refusal("set-files", "R9-A", "--add", "README.md",
+                            "--cite", f"main@{sf_cited}")
+    check("set-files refuses a cite whose sha exists but main does not hold it",
+          rc == 2 and "does not hold" in said and tip() == t_sf, (rc, said[-200:]))
+    before_a = grp("R9-A")
+    check("set-files --add lands a path in the tree",
+          more("set-files", "R9-A", "--add", "README.md") == 0
+          and grp("R9-A").get("files") == ["README.md"])
+    check("... and touches no other field",
+          sans(grp("R9-A"), "files") == sans(before_a, "files"))
+    t_sf = tip()
+    check("set-files --add of a path already held is byte-identical (null control)",
+          more("set-files", "R9-A", "--add", "README.md") == 0 and tip() == t_sf)
+    check("set-files --add accepts a path the cited ref adds",
+          more("set-files", "R9-A", "--add", "NEW.md",
+               "--cite", f"cited@{sf_cited}") == 0
+          and grp("R9-A").get("files") == ["README.md", "NEW.md"]
+          and f"cited@{sf_cited}" in grp("R9-A")["resume"]["note"])
+    t_sf = tip()
+    rc, said = more_refusal("set-files", "R9-B", "--add", "__bad__.md",
+                            "--cite", f"cited@{sf_cited}", wt="wt-sflint")
+    check("set-files lints like every other op (the planted text is refused rc 3)",
+          rc == 3 and tip() == t_sf, (rc, said[-200:]))
+
+    rc, said = more_refusal("set-files", "R9-A", "--set-hot", "nowhere.py")
+    check("set-files --set-hot refuses a path that is neither a files basename "
+          "nor a known token",
+          rc == 2 and "nowhere.py" in said and "hot" in said and tip() == t_sf,
+          (rc, said[-200:]))
+    before_a = grp("R9-A")
+    check("set-files --set-hot lands a files basename",
+          more("set-files", "R9-A", "--set-hot", "NEW.md,README.md",
+               "--cite", f"cited@{sf_cited}") == 0
+          and grp("R9-A").get("hot_files") == ["NEW.md", "README.md"])
+    check("... recording the old value in resume.note, other fields untouched",
+          "hot_files" in grp("R9-A")["resume"]["note"]
+          and sans(grp("R9-A"), "hot_files") == sans(before_a, "hot_files"))
+    t_sf = tip()
+    check("set-files --set-hot with the current value is byte-identical (null control)",
+          more("set-files", "R9-A", "--set-hot", "NEW.md,README.md") == 0
+          and tip() == t_sf)
+    check("set-files --set-hot accepts a token another group already holds",
+          more("set-files", "R9-B", "--set-hot", "README.md") == 0
+          and grp("R9-B").get("hot_files") == ["README.md"])
+    check("set-files --set-hot - clears the field, keeping the key",
+          more("set-files", "R9-A", "--set-hot", "-") == 0
+          and grp("R9-A").get("hot_files") == []
+          and "[]" in grp("R9-A")["resume"]["note"])
+    t_sf = tip()
+    check("set-files --set-hot - on an already-empty field is byte-identical (null control)",
+          more("set-files", "R9-A", "--set-hot", "-") == 0 and tip() == t_sf)
+    before_a = grp("R9-A")
+    check("set-files --set-files replaces files whole, `-` for none",
+          more("set-files", "R9-A", "--set-files", "-") == 0
+          and grp("R9-A").get("files") == []
+          and sans(grp("R9-A"), "files") == sans(before_a, "files"))
+    check("... and takes a comma list, refusing a path not in the tree",
+          more("set-files", "R9-A", "--set-files", "README.md") == 0
+          and grp("R9-A").get("files") == ["README.md"]
+          and more_refusal("set-files", "R9-A", "--set-files",
+                           "README.md,no/such.py")[0] == 2)
+    check("set-files names no op flag on another op",
+          more_refusal("set-after", "R9-B", "--add", "README.md",
+                       value="R9-A")[0] == 2)
+
     # drop-carry: the inverse of append-carry, by index or by a unique match.
     # R9-B carries `"carry": []`, the live roster's empty shape (27 of 91
     # groups; none omits the key), so the round-trip below is pinned on the

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
