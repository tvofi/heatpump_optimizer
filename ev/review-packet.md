# Review packet #3865
head: f93e28bb6267d66f3cec852f9502843ea52b7fca
base: baa9a467ac518bc3f8733d2603ea8ae406b235af

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=137273142510 success
arch-score / arch-score id=137282708550 success
arm id=137272879964 skipped
budget-raise-gate / budget-raise-gate id=137282673823 success
cancel-superseded id=137282673058 success
codeql id=137282699738 skipped
codeql / Analyze (actions) id=137273077733 success
codeql / Analyze (javascript-typescript) id=137273077692 success
codeql / Analyze (python) id=137273077690 success
gate id=137282672884 success
governance id=137282673517 skipped
governance / env-matrix id=137273077861 success
governance / instrument-self-tests id=137273077820 success
governance / policy-docs id=137273077779 success
governance / record id=137273078915 skipped
governance / wave-script id=137273077746 success
hassfest id=137282674128 skipped
hassfest / hassfest id=137273077742 success
kernel-points id=137282673253 skipped
pr-contract id=137282673893 skipped
pr-contract / pr-contract id=137280543305 success
prelude id=137282716569 success
refresh id=137282710619 success
sweep-self id=137282967352 skipped
tests id=137282673872 skipped
tests / arch-instrument id=137273453149 success
tests / briefs id=137273077831 success
tests / browser id=137273453148 success
tests / ci-ratchet id=137280007280 skipped
tests / claims-autofix id=137274703822 skipped
tests / closure-scope id=137273077772 success
tests / closures id=137273453200 success
tests / closures-autofix id=137278056432 skipped
tests / coverage id=137273453197 success
tests / coverage-ratchet id=137280006474 success
tests / fast (3.14) id=137273453166 success
tests / graders-head-copy id=137280006387 success
tests / lane-proofs id=137280006400 success
tests / mutation id=137273077799 success
tests / mutation-autofix id=137273507382 skipped
tests / mutation-pins id=137273507476 skipped
tests / nightly-ha id=137273454385 skipped
tests / nightly-status id=137273077762 success
tests / replay id=137273454828 skipped
tests / typing id=137273453189 success
validate id=137282709705 skipped
validate / validate-hacs id=137273077704 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified python3 -c 'import runpy,sys,zipfile; zipfile.ZipInfo.is_dir=lambda s: s.filename[-1]=="/"; sys.argv=["tools/audit/seat/corpus_mirror.py","--self-test","--no-mutants"]; runpy.run_path(sys.argv[0], run_name="__main__")'
             python3 runs an inline script rather than a file
  ok         python3 tools/audit/seat/corpus_mirror.py --self-test --no-mutants
             `tools/audit/seat/corpus_mirror.py` is in the tree at this head
  unverified python3
             python3 with no script argument
  ok         python3 tools/audit/seat/corpus_mirror.py --self-test
             `tools/audit/seat/corpus_mirror.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 4 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3865.md b/dev/programme/delivery/3865.md
new file mode 100644
index 0000000000..1970140601
--- /dev/null
+++ b/dev/programme/delivery/3865.md
@@ -0,0 +1 @@
+- [#3865](https://github.com/tvofi/heatpump_optimizer/pull/3865) — **open**, corpus_mirror: read a zip member's dir-ness from its name, not ZipInfo.is_dir (R11-HOTFIX-CORPUS-MIRROR-PY311)
diff --git a/tools/audit/seat/corpus_mirror.py b/tools/audit/seat/corpus_mirror.py
index 540693099d..13f379873e 100755
--- a/tools/audit/seat/corpus_mirror.py
+++ b/tools/audit/seat/corpus_mirror.py
@@ -138,6 +138,16 @@ def unmapped(ls_remote: str) -> list[str]:
     return sorted(out)
 
 
+def names_directory(name: str) -> bool:
+    """Whether a member's name marks a directory: read from the name alone, never `ZipInfo.is_dir`.
+
+    CPython 3.11.5's `is_dir` is `filename[-1] == '/'` and raises IndexError on an empty name (3.12 guards it),
+    so the interpreter's zipfile would decide whether an archive's shape raises. An empty name is no directory
+    here, and so meets the rule "a member's path is the archive's directory".
+    """
+    return name.endswith("/")
+
+
 def archive_refusal(zf: zipfile.ZipFile, dest: Path) -> str:
     """The rule an archive breaks, or "": judged whole, before any member is written."""
     base, total, files, parents = os.path.realpath(dest), 0, set(), set()
@@ -148,11 +158,11 @@ def archive_refusal(zf: zipfile.ZipFile, dest: Path) -> str:
         target = os.path.realpath(os.path.join(base, name))
         if name.startswith(("/", "\\")) or re.match(r"[A-Za-z]:", name) or not (target == base or target.startswith(base + os.sep)):
             return "a member's path leaves the archive's directory"
-        if target == base and not info.is_dir():
+        if target == base and not names_directory(name):
             return "a member's path is the archive's directory"
         if any(len(part.encode("utf-8", "replace")) > MAX_NAME for part in name.split("/")):
             return "a member's name is past the length cap"
-        (parents if info.is_dir() else files).add(target)
+        (parents if names_directory(name) else files).add(target)
         parent = os.path.dirname(target)
         while len(parent) > len(base):  # every directory between the member and the archive's own
             parents.add(parent)
@@ -207,7 +217,7 @@ def safe_extract(data: bytes, dest: Path) -> str:
         try:
             os.makedirs(dest, mode=0o700, exist_ok=True)  # an archive of no file is whole too, and has its directory
             for info in zf.infolist():
-                if info.is_dir():
+                if names_directory(info.filename):
                     continue
                 body, bad = read_archive(lambda: member(info))
                 if bad:
@@ -984,6 +994,19 @@ def cases(m) -> dict[str, bool]:
             got == {**{label: ("a member's path is both a file and a directory", False) for label in shapes},
                     "a member named for the directory itself": ("a member's path is the archive's directory", False),
                     "the same through a parent": ("a member's path is the archive's directory", False)}
+        buf_ = io.BytesIO()
+        with zipfile.ZipFile(buf_, "w") as z_:
+            z_.writestr(zipfile.ZipInfo(""), "x")  # built before the patch below: writestr reads the name too
+        real_is_dir = m.zipfile.ZipInfo.is_dir
+        m.zipfile.ZipInfo.is_dir = lambda self: self.filename[-1] == "/"  # CPython 3.11.5's body: IndexError on ""
+        try:
+            empty = m.safe_extract(buf_.getvalue(), Path(td) / "shape" / "empty"), (Path(td) / "shape" / "empty").exists()
+        except Exception as e_:  # the defect: the interpreter's zipfile decides, and raises
+            empty = "RAISED " + type(e_).__name__, None
+        finally:
+            m.zipfile.ZipInfo.is_dir = real_is_dir
+        r["archives: a member with an empty name is refused whole as the directory itself, read from the name under any interpreter's ZipInfo.is_dir"
+          + ("" if empty[1] is False else f"; got {empty}")] = empty == ("a member's path is the archive's directory", False)
         try:
             long_name = m.safe_extract(zip_of([("ok.txt", "x"), ("n" * 300, "x")]), Path(td) / "shape" / "long"), (Path(td) / "shape" / "long").exists()
         except Exception as e_:
@@ -998,10 +1021,13 @@ def cases(m) -> dict[str, bool]:
                 partial = e_
         r["archives: a write this host fails is raised, never returned as the archive's rule, and what was written before it is removed"] = \
             isinstance(partial, OSError) and partial.errno == errno.EIO and not (Path(td) / "shape" / "partial").exists()
-        r["archives null: nested files, a directory entry and a repeated ancestor extract whole"] = \
-            m.safe_extract(zip_of([("./", ""), ("a", "x"), ("b/", ""), ("b/c", "y"), ("b/d/e", "z")]), Path(td) / "shape" / "ok") == "" \
-            and sorted(str(f.relative_to(Path(td) / "shape" / "ok")) for f in (Path(td) / "shape" / "ok").rglob("*") if f.is_file()) == ["a", "b/c", "b/d/e"] \
-            and m.safe_extract(zip_of([("only/", "")]), Path(td) / "shape" / "nofile") == "" and (Path(td) / "shape" / "nofile").is_dir()
+        try:  # a directory entry written as a file raises here: a FAIL line, never a traceback that names no case
+            nested = m.safe_extract(zip_of([("./", ""), ("a", "x"), ("b/", ""), ("b/c", "y"), ("b/d/e", "z")]), Path(td) / "shape" / "ok") == "" \
+                and sorted(str(f.relative_to(Path(td) / "shape" / "ok")) for f in (Path(td) / "shape" / "ok").rglob("*") if f.is_file()) == ["a", "b/c", "b/d/e"] \
+                and m.safe_extract(zip_of([("only/", "")]), Path(td) / "shape" / "nofile") == "" and (Path(td) / "shape" / "nofile").is_dir()
+        except Exception:  # noqa: BLE001 -- any raise is this case's failure
+            nested = False
+        r["archives null: nested files, a directory entry and a repeated ancestor extract whole"] = nested
         s_ = Stub(hostile={"repos/o/r/actions/runs/901/logs": zip_of([("a", "x"), ("a/b", "y")])})
         try:
             ms, rc = mirror(Path(td) / "s5shape", s_, only=("S5",))
@@ -1176,7 +1202,10 @@ MUTANTS = {
     "traversal": ("not (target == base or target.startswith(base + os.sep)):", "False:", "a traversing member"),
     "link": ("        if stat.S_ISLNK(info.external_attr >> 16):\n", "        if False:\n", "a link and a ratio bomb"),
     "ratio": ("        if info.file_size > MAX_RATIO * max(info.compress_size, 1):\n", "        if False:\n", "a ratio bomb"),
-    "directory itself": ("        if target == base and not info.is_dir():\n", "        if False:\n", "a member that is the directory itself"),
+    "directory itself": ("        if target == base and not names_directory(name):\n", "        if False:\n", "a member that is the directory itself"),
+    "dir-ness from the name": ('    return name.endswith("/")\n', "    return zipfile.ZipInfo(name).is_dir()\n", "a member with an empty name"),
+    "dir entry is a parent": ("        (parents if names_directory(name) else files)", "        (parents if False else files)", "a member that is the directory itself"),
+    "dir entry not written": ("                if names_directory(info.filename):\n                    continue\n", "                if False:\n                    continue\n", "archives null: nested files"),
     "file and directory": ("    if files & parents:\n", "    if False:\n", "a member that is the directory itself"),
     "ancestors": ("        while len(parent) > len(base):  #", "        while False:  #", "a member that is the directory itself"),
     "archive boundary": ("    except Exception as e:  # noqa: BLE001 -- the boundary is the rule", "    except (OSError, ValueError, zipfile.BadZipFile) as e:  #", "a member that cannot be read"),

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
