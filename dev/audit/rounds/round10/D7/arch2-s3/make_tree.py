"""Materialise a bench tree: ``custom_components/`` and ``tests/`` at a git ref, plus patches in order.

    python3 dev/audit/rounds/round10/D7/arch2-s3/make_tree.py REF DEST [PATCH ...]

Read from the tree objects (``git ls-tree`` / ``cat-file``), as ``archscore.score.tree_of`` does, so a
dirty working tree never leaks into a bench arm. DEST must not exist.
"""
import subprocess
import sys
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = repo_root(__file__)


def extract(ref: str, prefix: str, into: Path) -> None:
    git = ["git", "-C", str(REPO)]
    listing = subprocess.run([*git, "ls-tree", "-r", "-z", ref, prefix], capture_output=True, check=True).stdout
    entries = []
    for entry in filter(None, listing.split(b"\0")):
        meta, path = entry.split(b"\t", 1)
        mode, kind, sha = meta.decode().split()
        if kind == "blob" and mode != "120000":
            entries.append((mode, sha, path.decode()))
    # One cat-file --batch for every blob: a process per file took minutes on tests/.
    blob = subprocess.run([*git, "cat-file", "--batch"], input="".join(f"{s}\n" for _, s, _ in entries).encode(),
                          capture_output=True, check=True).stdout
    pos = 0
    for mode, sha, path in entries:
        nl = blob.index(b"\n", pos)
        size = int(blob[pos:nl].split()[2])
        data = blob[nl + 1: nl + 1 + size]
        pos = nl + 1 + size + 1
        dest = into / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        if mode == "100755":
            dest.chmod(0o755)


def main() -> int:
    ref, dest, *patches = sys.argv[1:]
    dest = Path(dest)
    if dest.exists():
        sys.exit(f"{dest} exists")
    for prefix in ("custom_components", "tests"):
        extract(ref, prefix, dest)
    for p in patches:
        subprocess.run(["patch", "-p1", "-s", "-f", "--no-backup-if-mismatch", "-d", str(dest),
                        "-i", str(Path(p).resolve())], check=True)
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
