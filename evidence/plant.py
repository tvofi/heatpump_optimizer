# step 14 plant: carve a file off INERT with NO new read. The closure movement
# must not reproduce (the table is recorded from reads), and the arm's own
# source-select check must refuse it.
import sys; sys.path.insert(0,"tests")
import closure as C
C.INERT = C.INERT  # no-op
_old = C._CITATION_POLICY
C._CITATION_POLICY = tuple(_old) + (r"RELEASE_NOTES\.md",)
print("planted RELEASE_NOTES.md into _CITATION_POLICY (no read added)")
print("  is_inert(RELEASE_NOTES.md):", C.is_inert("RELEASE_NOTES.md"))
print("  entities.py recorded closure holds it:",
      "RELEASE_NOTES.md" in json.loads(C.CLOSURES.read_text())["closures"]["tests/entities.py"])
print("  orphan_files():", len(C.orphan_files()))
sel = C.select(["RELEASE_NOTES.md"])
print("  select(RELEASE_NOTES.md) mode=%s run=%s" % (sel["mode"], sel["run"]))
C._CITATION_POLICY = _old
