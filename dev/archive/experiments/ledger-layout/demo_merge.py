#!/usr/bin/env python3
"""Replay a real concurrent mutation-ledger edit under GitHub's default merge.

    python3 tools/audit/ledger-layout/demo_merge.py            the pinned event
    python3 tools/audit/ledger-layout/demo_merge.py --ours A --theirs B

design/ledger-layout, the prototype's evidence. GitHub never runs a custom
merge driver, so whether an open pull request goes DIRTY when main moves is
decided by git's own text merge. This script takes two real commits, their
merge base, and the mutation ledger at each, and merges them twice in
throwaway repositories, with no merge driver configured anywhere:

  TODAY   tests/mutation_budgets.json byte-for-byte, one file
  SPLIT   the same three ledgers converted by this tree's writer
          (`mutation_table.write_budgets`): the caps file plus one file per
          disposition under tests/mutation_ledger/

The .gitattributes of this tree is committed into both repositories, so the
`merge=ledgermerge` it names is present and UNDEFINED, which is exactly the
state GitHub is in: git falls back to its text merge. (Equivalently
`git -c merge.ledgermerge.driver=false merge` would make the driver refuse;
an undefined driver is the closer model of a server that never had one.)

Then it checks the SPLIT result is not merely conflict-free but RIGHT: the
merged rows must equal a key-wise three-way merge of the three ledgers --
every row either side added or changed, every row either side deleted gone.

The pinned default is the replay's event `#1562->#1581` (DESIGN.md): #1562
merged into main at 2026-09-25 02:41 while #1581 was open at 5003d56f; both
had recorded new `killed_by` rows, no row in common, and GitHub's merge of the
two conflicted in this file. Four safety arms follow on synthetic edits of the
same base, each of which must CONFLICT (or, for the last, keep the deletion):

  same row, two verdicts              both sides rewrote one disposition
  row deleted on one side, edited     modify/delete: git refuses, the row is
    on the other                      not resurrected
  row deleted beside another's        the deletion stands (a `merge=union`
    addition                          JSONL resurrects it -- shown)
  a branch cut before the split       conflicts once; `--carry-rows` applies
                                      exactly its own row delta onto main's

Exit 0 when every expectation holds, 1 otherwise. Nothing in the checkout is
written; the scratch repositories live under a temporary directory.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402

LEDGER = "tests/mutation_budgets.json"
# `#1562->#1581` from the replay: main after #1562's merge, against #1581's
# head at that moment.
PINNED = ("ae3bb36adcaf82727a9cce65abe861ecead41d03", "5003d56f9d9f7617d5e4dc1372e49dbdbacd39bd")


def git(*a, cwd=ROOT, check=True):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(a)}: {r.stderr.strip()}")
    return r


def show(ref: str, path: str) -> str:
    return git("show", f"{ref}:{path}").stdout


# ---------------------------------------------------------------- layouts
def split_files(ledger_text: str) -> dict[str, str]:
    """The SPLIT layout of one monolithic ledger, via this tree's writer."""
    with tempfile.TemporaryDirectory() as tmp:
        saved = mt.BUDGETS
        mt.BUDGETS = Path(tmp) / "tests" / "mutation_budgets.json"
        mt.BUDGETS.parent.mkdir(parents=True)
        try:
            mt.write_budgets(json.loads(ledger_text))
            return {str(p.relative_to(tmp)): p.read_text()
                    for p in sorted(Path(tmp).rglob("*")) if p.is_file()}
        finally:
            mt.BUDGETS = saved


def load_split(files: dict[str, str]) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        for rel, text in files.items():
            p = Path(tmp) / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        saved = mt.BUDGETS
        mt.BUDGETS = Path(tmp) / "tests" / "mutation_budgets.json"
        try:
            return mt.load_budgets()
        finally:
            mt.BUDGETS = saved


def jsonl_files(ledger_text: str) -> dict[str, str]:
    """The rejected candidate, for the union arm: one sorted row per line."""
    d = json.loads(ledger_text)
    rows = [json.dumps([m, k, v], sort_keys=True)
            for m in mt.LEDGER_MAPS for k, v in sorted(d.get(m, {}).items())]
    return {"tests/mutation_ledger.jsonl": "\n".join(rows) + "\n"}


# ------------------------------------------------------------ scratch repo
class Repo:
    def __init__(self, path: Path, attributes: str, union: bool = False):
        self.path = path
        path.mkdir(parents=True)
        git("init", "-q", "-b", "main", str(path), cwd=path)
        git("config", "user.email", "demo@example.invalid", cwd=path)
        git("config", "user.name", "demo", cwd=path)
        self.attributes = attributes
        if union:
            (path / ".git" / "info" / "attributes").write_text("* merge=union\n")

    def commit_on(self, branch: str, start: str | None, files: dict[str, str],
                  msg: str) -> None:
        if start:
            git("checkout", "-q", "-B", branch, start, cwd=self.path)
        else:
            git("checkout", "-q", "--orphan", branch, cwd=self.path)
        for p in self.path.iterdir():
            if p.name != ".git":
                shutil.rmtree(p) if p.is_dir() else p.unlink()
        for rel, text in {**files, ".gitattributes": self.attributes}.items():
            p = self.path / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        git("add", "-A", cwd=self.path)
        git("commit", "-q", "--allow-empty", "-m", msg, cwd=self.path)

    def merge(self, ours: str, theirs: str) -> tuple[bool, list[str], dict[str, str]]:
        """(clean, conflicted paths, merged files) of `git merge theirs` into ours."""
        git("checkout", "-q", ours, cwd=self.path)
        r = git("merge", "--no-edit", "-q", theirs, cwd=self.path, check=False)
        conflicted = git("diff", "--name-only", "--diff-filter=U",
                         cwd=self.path).stdout.split()
        files = {}
        for p in sorted(self.path.rglob("*")):
            rel = p.relative_to(self.path).as_posix()
            if p.is_file() and not rel.startswith(".git/") and rel != ".gitattributes":
                files[rel] = p.read_text()
        if r.returncode != 0:
            git("merge", "--abort", cwd=self.path, check=False)
        return r.returncode == 0 and not conflicted, conflicted, files


def three_way(o: dict, a: dict, b: dict) -> tuple[dict, list[str]]:
    """Key-wise three-way merge of the two disposition maps."""
    out: dict = {}
    both: list[str] = []
    for m in mt.LEDGER_MAPS:
        om, am, bm = o.get(m, {}), a.get(m, {}), b.get(m, {})
        res = {}
        for k in sorted(set(om) | set(am) | set(bm)):
            vo, va, vb = om.get(k), am.get(k), bm.get(k)
            if va == vb:
                v = va
            elif va == vo:
                v = vb
            elif vb == vo:
                v = va
            else:
                both.append(f"{m}/{k}")
                continue
            if v is not None:
                res[k] = v
        out[m] = res
    return out, both


def run_pair(tmp: Path, name: str, o: str, a: str, b: str, attributes: str,
             layout) -> tuple[bool, list[str], dict[str, str]]:
    repo = Repo(tmp / name, attributes, union=(layout is jsonl_files))
    repo.commit_on("base", None, layout(o), "base")
    repo.commit_on("ours", "base", layout(a), "ours")
    repo.commit_on("theirs", "base", layout(b), "theirs")
    return repo.merge("ours", "theirs")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ours", default=PINNED[0], help="e.g. main after one PR merged")
    ap.add_argument("--theirs", default=PINNED[1], help="another PR's head at that moment")
    args = ap.parse_args()
    ours = git("rev-parse", "--verify", args.ours + "^{commit}").stdout.strip()
    theirs = git("rev-parse", "--verify", args.theirs + "^{commit}").stdout.strip()
    base = git("merge-base", ours, theirs).stdout.strip()
    o, a, b = show(base, LEDGER), show(ours, LEDGER), show(theirs, LEDGER)
    attributes = (ROOT / ".gitattributes").read_text()
    ok = True

    def expect(label: str, cond: bool, detail: str) -> None:
        nonlocal ok
        ok &= cond
        print(f"  {'ok  ' if cond else 'FAIL'} {label}: {detail}")

    jo, ja, jb = json.loads(o), json.loads(a), json.loads(b)
    want, both = three_way(jo, ja, jb)
    changed = lambda x: {f"{m}/{k}" for m in mt.LEDGER_MAPS  # noqa: E731
                         for k in set(x.get(m, {})) | set(jo.get(m, {}))
                         if x.get(m, {}).get(k) != jo.get(m, {}).get(k)}
    print(f"event: ours {ours[:9]}  theirs {theirs[:9]}  base {base[:9]}")
    print(f"  rows changed: ours {len(changed(ja))}, theirs {len(changed(jb))}, "
          f"both {len(changed(ja) & changed(jb))}")

    tmp = Path(tempfile.mkdtemp(prefix="ledger-demo-"))
    try:
        print("\nTODAY -- one file, no merge driver (GitHub)")
        clean, conf, _ = run_pair(tmp, "today", o, a, b, attributes,
                                  lambda t: {LEDGER: t})
        expect("GitHub's merge of the real event", not clean,
               f"conflicted {conf}" if conf else "clean")

        print("\nSPLIT -- caps file + one file per row, no merge driver")
        clean, conf, files = run_pair(tmp, "split", o, a, b, attributes, split_files)
        expect("GitHub's merge of the same event", clean,
               "clean" if clean else f"conflicted {conf}")
        got = load_split(files) if clean else {}
        rows_ok = clean and not both and all(
            got.get(m, {}) == want[m] for m in mt.LEDGER_MAPS)
        expect("the merged rows equal a key-wise three-way merge", rows_ok,
               f"{sum(len(want[m]) for m in mt.LEDGER_MAPS)} row(s)"
               + (f"; both sides changed {both}" if both else ""))
        caps_ok = clean and {k: v for k, v in got.items() if k not in mt.LEDGER_MAPS} \
            == {k: v for k, v in ja.items() if k not in mt.LEDGER_MAPS}
        expect("the caps are ours' (theirs did not change them)",
               caps_ok or jb.get("max_survivor_fraction") != jo.get("max_survivor_fraction"),
               "max_survivor_fraction and last_measured unchanged")

        print("\nSAFETY ARMS -- synthetic edits of the same base, SPLIT layout")
        row = sorted(jo["killed_by"])[0]
        nb = sorted(jo["killed_by"])[1]

        def edited(d: dict, **rows) -> str:
            d = json.loads(json.dumps(d))
            for k, v in rows.items():
                if v is None:
                    d["killed_by"].pop(k, None)
                else:
                    d["killed_by"][k] = v
            return json.dumps(d, indent=2) + "\n"

        v1 = dict(jo["killed_by"][row], reason="verdict one")
        v2 = dict(jo["killed_by"][row], reason="verdict two")
        c, conf, _ = run_pair(tmp, "same-row", o, edited(jo, **{row: v1}),
                              edited(jo, **{row: v2}), attributes, split_files)
        expect("same row, two different verdicts", not c, f"conflicted {conf}")

        c, conf, _ = run_pair(tmp, "del-edit", o, edited(jo, **{row: None}),
                              edited(jo, **{row: v1}), attributes, split_files)
        expect("row deleted on one side, edited on the other", not c,
               f"conflicted {conf} (modify/delete)")

        # A new row that SORTS right after the deleted one, so the two edits
        # touch adjacent lines of a one-row-per-line file.
        new = dict(jo["killed_by"][nb], reason="a neighbour's new row")
        new_key = row + "#9"
        ours_del = edited(jo, **{row: None})
        theirs_add = edited(jo, **{new_key: new})
        c, conf, files = run_pair(tmp, "del-add", o, ours_del, theirs_add,
                                  attributes, split_files)
        merged = load_split(files) if c else {}
        expect("row deleted beside another side's addition", c
               and row not in merged.get("killed_by", {})
               and new_key in merged.get("killed_by", {}),
               "deletion stands, addition lands" if c else f"conflicted {conf}")
        c, conf, files = run_pair(tmp, "del-add-union", o, ours_del, theirs_add,
                                  attributes, jsonl_files)
        text = files.get("tests/mutation_ledger.jsonl", "")
        resurrected = any(json.loads(line)[1] == row for line in text.splitlines() if line)
        print(f"  note the same arm under JSONL + merge=union: "
              f"{'the deleted row is RESURRECTED' if resurrected else 'deletion kept'}"
              f"{' (clean merge)' if c else f' (conflicted {conf})'}")

        print("\nMIGRATION -- a branch cut before the split")
        repo = Repo(tmp / "migrate", attributes)
        repo.commit_on("base", None, {LEDGER: o}, "base: today's layout")
        repo.commit_on("main", "base", split_files(a), "main: ours, after the split")
        repo.commit_on("pr", "base", {LEDGER: b}, "pr: theirs, never split")
        c, conf, _ = repo.merge("pr", "main")
        expect("an unsplit branch merging the split main", not c,
               f"conflicted {conf} -- once, where the carry below resolves it")
        # The tempting shortcut: split the branch, then merge. Its base has no
        # row directory, so every row the branch holds reads as its addition.
        repo.commit_on("pr2", "pr", split_files(b), "pr: split before merging")
        c, conf, files = repo.merge("pr2", "main")
        got = load_split(files) if c else {}
        back = sorted(f"{m}/{k}" for m in mt.LEDGER_MAPS
                      for k in set(got.get(m, {})) - set(want[m]))
        print(f"  note split-then-merge: {'clean' if c else f'conflicted {conf}'}, "
              f"and {len(back)} row(s) one side deleted since the base came "
              f"back as the other side's addition: {back[:2]}")
        # The procedure: merge main, take main's ledger, carry the branch's
        # own rows onto it (`mutation_table.py --carry-rows BASE HEAD`).
        carried, clash = mt.carry(jo, jb, load_split(split_files(a)))
        expect("the carry procedure (merge main, take its ledger, --carry-rows)",
               not clash and all(carried.get(m, {}) == want[m] for m in mt.LEDGER_MAPS),
               "rows equal the three-way merge" if not clash else f"refused {clash}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nDEMO {'PASSED' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
