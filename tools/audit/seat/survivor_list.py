#!/usr/bin/env python3
"""A `mutation-vacuous` block names every survivor its evidence reports.

    python3 -I tools/audit/seat/survivor_list.py check VERDICT.md EVIDENCE_DIR
    python3 -I tools/audit/seat/survivor_list.py --self-test

Owner ruling (tvofi, 2026-11-07, waste-study card 2, NARROW): a reviewer that
blocks `mutation-vacuous` lists every survivor it found at that head in the one
verdict, so the repair answers them in one round rather than one per round
(#3262: four blocks, each a new survivor in the same files). `fix-review.md`
step 1 binds the reviewer; `bus.sh push-verdict` runs `check`, so a local seat
and a cloud relay (which calls push-verdict) are refused alike.

WHAT IS READ. Every file under EVIDENCE_DIR, for the survivor lines the three
drivers print:
  mutant_run.py --diff     `SURVIVED <file>:<line> <OPERATOR>  <mutated line>`
  mutant_run.py --spec     `SURVIVED <name>` (its automatic NULL is not one)
  mutation_table.py        `  LIVES <file>:<line> <kind>`, less a site its own
                           survivor list marks `[triaged equivalent]`
  mutation_table.py --pin-killed  `  UNPINNED <file>:<line> <kind> -- lives`
A survivor is LISTED when the verdict holds its key -- `<file>:<line>`, or the
spec name -- as a whole token. Only the review's own driver output is counted:
the rule asks for what the review found, never a hunt past it, and a verdict
whose evidence holds no driver output has nothing to count (rc 0).

WHAT IS CHECKED. Only a first line `Fix review: blocked <40 hex> mutation-vacuous:`.
Any other class, and `merge`, pass unread. rc 0 listed (or not this class);
rc 1 one `UNLISTED <key>` line per survivor the verdict omits, then a summary;
rc 2 unreadable input.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
import mutation_table  # noqa: E402  the --pin-killed survivor grammar's owner

CLASS = re.compile(r"^Fix review: blocked [0-9a-f]{40} mutation-vacuous:")
SITE = r"(\S+:\d+)"
DRIVER_LINES = (
    re.compile(rf"^SURVIVED {SITE} [A-Z_]+\b", re.M),          # mutant_run --diff
    re.compile(r"^SURVIVED (?!NULL$)([^\s:]+)$", re.M),       # mutant_run --spec
    re.compile(rf"^  LIVES {SITE} \S+", re.M),                # mutation_table
)  # --pin-killed's `UNPINNED ... -- lives` is read by its owner, mutation_table.survivor_sites
TRIAGED = re.compile(rf"^    {SITE} \S+: .*\[triaged equivalent\]$", re.M)
PRODUCERS = {
    "tools/audit/seat/mutant_run.py": (
        'print(f"SURVIVED {rel}:{n} {op}  {new}"',
        '("SURVIVED " if rc == 0 else "KILLED ") + m["name"]'),
    "tests/mutation_table.py": (
        'mark = "LIVES" if verdict == "LIVES"',
        "print(f\"  {mark} {mut['file']}:{mut['line']} {mut['kind']}{note}\")",
        '"  [triaged equivalent]"',
        "def survivor_sites(run: str | None) -> list[str]:"),
}


def survivors(texts: list[str]) -> list[str]:
    """Every survivor key the driver outputs report, less triaged-equivalent sites."""
    found, triaged = set(), set()
    for t in texts:
        for rx in DRIVER_LINES:
            found.update(rx.findall(t))
        found.update(k.split(" ", 1)[0] for k in mutation_table.survivor_sites(t))
        triaged.update(TRIAGED.findall(t))
    return sorted(found - triaged)


def unlisted(verdict: str, texts: list[str]) -> list[str]:
    """The survivors a `mutation-vacuous` verdict does not name; [] for any other verdict."""
    if not CLASS.match(verdict):
        return []
    return [k for k in survivors(texts)
            if not re.search(rf"(?<![\w./-]){re.escape(k)}(?![\w])", verdict)]


def evidence_texts(ev: Path) -> list[str]:
    return [p.read_text(encoding="utf-8", errors="replace")
            for p in sorted(ev.rglob("*")) if p.is_file()]


def check(verdict_path: str, ev_dir: str) -> int:
    try:
        verdict = Path(verdict_path).read_text(encoding="utf-8")
        ev = Path(ev_dir)
        if not ev.is_dir():
            raise OSError(f"no evidence directory {ev_dir}")
        texts = evidence_texts(ev)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"survivor_list: unreadable: {exc}")
        return 2
    missing = unlisted(verdict, texts)
    for k in missing:
        print(f"UNLISTED {k}")
    if missing:
        n = len(survivors(texts))
        print(f"a mutation-vacuous verdict names {n - len(missing)} of the {n} survivor(s) "
              f"its evidence reports; list every one (fix-review.md step 1)")
        return 1
    return 0


def _self_test() -> int:
    fails, ran = [], []

    def t(name, cond):
        ran.append(name)
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    h = "a" * 40
    mv = f"Fix review: blocked {h} mutation-vacuous: "
    diff_two = ("SURVIVED custom_components/x/a.py:12 GUARD_OFF  if False:\n"
                "SURVIVED custom_components/x/a.py:40 RETURN_DEL  pass\n")
    t("two diff-mode survivors are both read",
      survivors([diff_two]) == ["custom_components/x/a.py:12", "custom_components/x/a.py:40"])
    t("a verdict naming one of two is refused, naming the other",
      unlisted(mv + "custom_components/x/a.py:12 lives", [diff_two]) == ["custom_components/x/a.py:40"])
    t("a verdict naming both passes",
      unlisted(mv + "custom_components/x/a.py:12 and custom_components/x/a.py:40", [diff_two]) == [])
    t("null control: another blocked class with the same evidence passes",
      unlisted(f"Fix review: blocked {h} class-open: seam", [diff_two]) == [])
    t("null control: a merge verdict passes",
      unlisted(f"Fix review: merge {h}", [diff_two]) == [])
    t("a key is a whole token: :12 does not list :120",
      unlisted(mv + "custom_components/x/a.py:120", ["SURVIVED custom_components/x/a.py:12 CALL_DEL  pass\n"])
      == ["custom_components/x/a.py:12"])
    t("a key is a whole token: tools/setup.py:3 does not list setup.py:3",
      unlisted(mv + "tools/setup.py:3", ["SURVIVED setup.py:3 CALL_DEL  pass\n"]) == ["setup.py:3"])
    t("spec mode: a named survivor is read, NULL is not",
      survivors(["SURVIVED NULL\nSURVIVED guard_off\nKILLED other\n"]) == ["guard_off"])
    table = ("  LIVES custom_components/x/b.py:7 cmp\n"
             "  ok    custom_components/x/b.py:9 cmp  -- killed\n"
             "  LIVES custom_components/x/b.py:11 const\n\n"
             "  2 survivor(s) of 3 evaluated = 33.3%, cap 50.0%\n"
             "    custom_components/x/b.py:7 cmp: x < y\n"
             "    custom_components/x/b.py:11 const: n = 3  [triaged equivalent]\n")
    t("mutation_table: LIVES read, a triaged-equivalent site and a kill are not",
      survivors([table]) == ["custom_components/x/b.py:7"])
    t("--pin-killed: an UNPINNED ... -- lives line is read",
      survivors(["  UNPINNED custom_components/x/c.py:3 guard -- lives\n"]) == ["custom_components/x/c.py:3"])
    t("evidence with no driver output counts nothing",
      unlisted(mv + "x", ["RESULT mutant=a rc=1 fails=2\n"]) == [])
    with tempfile.TemporaryDirectory() as d:
        ev = Path(d, "ev")
        (ev / "sub").mkdir(parents=True)
        (ev / "head.txt").write_text(h + "\n")
        (ev / "sub" / "mutants.log").write_text(diff_two)
        v = Path(d, "V.md")
        v.write_text(mv + "custom_components/x/a.py:12\n\nbus-nonce: " + "0" * 32 + "\n")
        t("check reads nested evidence and returns rc 1", check(str(v), str(ev)) == 1)
        v.write_text(mv + "custom_components/x/a.py:12, custom_components/x/a.py:40\n")
        t("check returns rc 0 once every survivor is listed", check(str(v), str(ev)) == 0)
        t("check returns rc 2 for a missing evidence directory", check(str(v), d + "/none") == 2)
    # The formats above are the producers' own print statements: one that changes shape turns
    # this red, rather than every survivor silently reading as none (fixer.md step 11).
    root = Path(__file__).resolve().parents[3]
    for rel, anchors in PRODUCERS.items():
        src = (root / rel).read_text(encoding="utf-8")
        for a in anchors:
            t(f"{rel} still prints {a!r}", a in src)
    print(f"survivor_list self-test: {len(ran)} checks, {len(fails)} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return _self_test()
    if len(argv) == 3 and argv[0] == "check":
        return check(argv[1], argv[2])
    print(__doc__.split("\n\n")[1])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
