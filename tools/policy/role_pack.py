#!/usr/bin/env python3
"""One seat's policy, verbatim, in one read: its role contract, the rules that
contract's reads load, and the INSTRUMENTS.md entries the contract names.

    python3 tools/policy/role_pack.py render <role> [--out FILE]
    python3 tools/policy/role_pack.py check [<role> ...] [--pack FILE]
    python3 tools/policy/role_pack.py sizes
    python3 tools/policy/role_pack.py --self-test

WHY. A seat opens by reading its contract under dev/governance/roles/ and
tools/audit/seat/INSTRUMENTS.md with tool calls; each read lands the same text in
its context again, and INSTRUMENTS.md arrives whole although a contract names a
fraction of its entries. The pack is that reading done once, by a program, and
filtered only where the filter is mechanical. `.claude/hooks/session-start.sh`
writes it when HPO_SEAT_ROLE names a role, and prints one line naming it.

WHY A FILE, NOT THE HOOK'S STDOUT. Claude Code (2.1.318, read in its bundle)
keeps hook stdout of at most 10,000 characters in context; longer output is
saved to disk and the context gets a preview whose path it hides. Every pack
is longer than that (`check` prints each size), so a pack printed whole would
reach a seat as a preview it cannot follow. The pack goes under the git
directory (`git rev-parse --git-path`): in the checkout, untracked, and read
once by a path the seat can name.

VERBATIM, NEVER PARAPHRASED. Every byte between a BEGIN and an END frame is a
byte of the file the frame names: a whole file, or (INSTRUMENTS.md) whole entry
lines of it. A paraphrase once made a seat read real policy as something else,
so `check` refuses any line no source holds, and every source the role's plan
names must be present whole.

CLAUDE.md IS NOT IN THE PACK, deliberately. The harness injects it into every
Claude Code session before any hook output (a session transcript carries it as
a system-reminder), and this hook is Claude Code's, so a pack holding it would
put the same text in the same context twice.

WHICH RULES. Claude Code loads a rule under .claude/rules/ when a read matches
its `paths:` globs. A seat given the pack does not read its contract or
INSTRUMENTS.md, so the rules those reads would have loaded come in the pack:
every rule under dev/governance/rules/ (the canonical text; .claude/rules/ is
generated from it) with a glob matching one of the role's files. Derived at
each render, never listed: a rule whose globs change moves with them.

WHICH INSTRUMENTS. An INSTRUMENTS.md entry line is `- [`name ...`](instruments/
...) -- ...`; it is in the pack when the contract's text names `name` (the first
word in the backticks) as a whole token: not preceded by a word character, `.`
or `-`, so `push.sh` does not match inside `app_push.sh`.
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROLES_DIR = "dev/governance/roles"
RULES_DIR = "dev/governance/rules"
INSTRUMENTS = "tools/audit/seat/INSTRUMENTS.md"
ENV_VAR = "HPO_SEAT_ROLE"

# The roles a pack is rendered for, and the contract each opens. `finder` is
# every audit dimension's finder, whose contract is COMMON.md.
ROLE_CONTRACT = {
    "fixer": "fixer.md",
    "fix-review": "fix-review.md",
    "designer": "designer.md",
    "design-review": "design-review.md",
    "root-cause": "root-cause.md",
    "verifier": "verifier.md",
    "judge": "judge.md",
    "finder": "COMMON.md",
}

BEGIN = "===== BEGIN {} ====="
END = "===== END {} ====="
FRAME = re.compile(r"^===== (BEGIN|END) (\S+)(?: \((.*)\))? =====$")
ENTRY = re.compile(r"^- \[`([^`]+)`(?:[^\]]*)\]\(instruments/")


class Refusal(Exception):
    """A pack that cannot be rendered or does not check, in one line."""


def _read(root: Path, rel: str) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except OSError as e:
        raise Refusal(f"{rel}: {e.strerror}") from e


def rule_globs(text: str) -> list[str]:
    """The `paths:` list of a rule's YAML frontmatter; [] when it has none."""
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return []
    globs, inside = [], False
    for line in m.group(1).splitlines():
        if re.match(r"paths:\s*$", line):
            inside = True
        elif inside and re.match(r"\s+-\s+", line):
            globs.append(line.split("-", 1)[1].strip().strip("\"'"))
        elif inside and line.strip():
            inside = False
    return globs


def glob_match(pattern: str, path: str) -> bool:
    """Claude Code's rule-glob reading: `**` spans any number of segments
    (none included), every other segment is an fnmatch pattern that never
    crosses a `/`."""
    pat, segs = pattern.split("/"), path.split("/")

    def go(i: int, j: int) -> bool:
        if i == len(pat):
            return j == len(segs)
        if pat[i] == "**":
            return any(go(i + 1, k) for k in range(j, len(segs) + 1))
        return j < len(segs) and fnmatch.fnmatchcase(segs[j], pat[i]) and go(i + 1, j + 1)

    return go(0, 0)


def role_files(role: str) -> list[str]:
    """The files a seat in `role` opens by reading, which the pack replaces."""
    if role not in ROLE_CONTRACT:
        raise Refusal(f"role must be one of {', '.join(ROLE_CONTRACT)} (got {role!r})")
    return [f"{ROLES_DIR}/{ROLE_CONTRACT[role]}", INSTRUMENTS]


def named_entries(contract: str, instruments: str) -> list[str]:
    """INSTRUMENTS.md's entry lines whose instrument the contract names."""
    out = []
    for line in instruments.splitlines():
        m = ENTRY.match(line)
        if not m:
            continue
        name = m.group(1).split()[0]
        if re.search(r"(?<![\w.-])" + re.escape(name) + r"(?![\w-])", contract):
            out.append(line)
    return out


def plan(role: str, root: Path = ROOT) -> list[tuple[str, str, str]]:
    """(path, note, text) blocks, in pack order: contract, rules, instruments."""
    files = role_files(role)
    contract_rel = files[0]
    contract = _read(root, contract_rel)
    blocks = [(contract_rel, "", contract)]
    for rule in sorted((root / RULES_DIR).glob("*.md")):
        rel = f"{RULES_DIR}/{rule.name}"
        text = _read(root, rel)
        hits = [f for f in files if any(glob_match(g, f) for g in rule_globs(text))]
        if hits:
            blocks.append((rel, "loaded by a read of " + ", ".join(hits), text))
    if INSTRUMENTS in files:
        entries = named_entries(contract, _read(root, INSTRUMENTS))
        blocks.append((INSTRUMENTS, f"the {len(entries)} entries {contract_rel} names; "
                       "read the file for any other",
                       "".join(e + "\n" for e in entries)))
    return blocks


def render_blocks(role: str, blocks: list[tuple[str, str, str]]) -> str:
    head = (f"ROLE PACK for {role} (tools/policy/role_pack.py): each block is the verbatim text "
            "of the file its frame names, at this checkout, read in place of opening it; "
            "CLAUDE.md is not repeated, the harness loaded it above.\n")
    parts = [head]
    for rel, note, text in blocks:
        label = f"{rel} ({note})" if note else rel
        body = text if text.endswith("\n") or not text else text + "\n"
        parts.append(BEGIN.format(label) + "\n" + body + END.format(rel) + "\n")
    return "".join(parts)


def render(role: str, root: Path = ROOT) -> str:
    return render_blocks(role, plan(role, root))


def parse(pack: str) -> tuple[list[tuple[str, str]], list[str]]:
    """((path, text) per block, stray lines outside any block but the header)."""
    blocks, stray, cur, buf = [], [], None, []
    for i, line in enumerate(pack.splitlines(keepends=True)):
        m = FRAME.match(line.rstrip("\n"))
        if m and m.group(1) == "BEGIN" and cur is None:
            cur, buf = m.group(2), []
        elif m and m.group(1) == "END" and cur == m.group(2):
            blocks.append((cur, "".join(buf)))
            cur = None
        elif cur is not None:
            buf.append(line)
        elif not (i == 0 and line.startswith("ROLE PACK for ")):
            stray.append(line.rstrip("\n"))
    if cur is not None:
        stray.append(f"(unterminated block {cur})")
    return blocks, stray


def check(role: str, pack: str, root: Path = ROOT) -> list[str]:
    """Each way `pack` fails to be `role`'s pack, one line each; [] when it is."""
    errs = []
    want = plan(role, root)
    got, stray = parse(pack)
    got_paths = [p for p, _ in got]
    errs += [f"a line outside every frame: {s!r}" for s in stray]
    # Stated here, not read from role_files(): a file dropped from the role's
    # list drops it from plan() too, so only an independent statement sees it.
    for rel in (f"{ROLES_DIR}/{ROLE_CONTRACT[role]}", INSTRUMENTS):
        if rel not in got_paths:
            errs.append(f"{rel}: every {role} pack holds it, and this one does not")
    for rel, _, text in want:
        if rel not in got_paths:
            errs.append(f"{rel}: in the role's plan, absent from the pack")
    for rel, text in got:
        source = _read(root, rel) if (root / rel).is_file() else None
        if source is None:
            errs.append(f"{rel}: the pack frames a file the tree does not hold")
            continue
        if rel == INSTRUMENTS:
            lines = set(source.splitlines())
            extra = [l for l in text.splitlines() if l not in lines]
            errs += [f"{rel}: a line the file does not hold: {l!r}" for l in extra]
            expect = next((t for r, _, t in want if r == INSTRUMENTS), None)
            if expect is not None and text != expect:
                errs.append(f"{rel}: the entries differ from those the contract names")
        elif text != source:
            errs.append(f"{rel}: not byte-equal to the file")
        if rel not in [r for r, _, _ in want]:
            errs.append(f"{rel}: framed, but not in the role's plan")
    body = sum(len(t) for _, t in got)
    whole = sum(len(_read(root, r)) for r in dict.fromkeys(got_paths) if (root / r).is_file())
    if body > whole:
        errs.append(f"the framed text ({body} chars) exceeds the files it frames ({whole})")
    return errs


def sizes(root: Path = ROOT) -> list[str]:
    """Per role, in characters: the read set a pack replaces -- the contract,
    the rules a Read of it loads and the whole INSTRUMENTS.md -- beside the pack.
    A seat that reads its contract through Bash loads no rule, so its read set
    is the contract and INSTRUMENTS.md alone: the third column."""
    whole = len(_read(root, INSTRUMENTS))
    out = ["role read_set(Read) read_set(Bash) pack pack-read_set(Read) entries"]
    for role in ROLE_CONTRACT:
        blocks = plan(role, root)
        contract = len(blocks[0][2])
        rules = sum(len(t) for r, _, t in blocks if r.startswith(RULES_DIR))
        pack = len(render(role, root))
        out.append(f"{role} {contract + rules + whole} {contract + whole} {pack} "
                   f"{pack - contract - rules - whole} {len(blocks[-1][2].splitlines())}")
    return out


def self_test() -> int:
    """Every role's pack checks clean, and each rule refuses its own mutant."""
    passed = failed = 0

    def t(ok: bool, what: str) -> None:
        nonlocal passed, failed
        passed, failed = passed + ok, failed + (not ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {what}")

    for role in ROLE_CONTRACT:
        pack = render(role)
        t(check(role, pack) == [], f"{role}: the rendered pack checks clean (null control)")
        contract = _read(ROOT, role_files(role)[0])
        t(contract in pack, f"{role}: the pack holds its contract byte-equal")
    t(glob_match("dev/governance/**", "dev/governance/roles/fixer.md"), "`**` spans segments")
    t(glob_match("dev/governance/**", "dev/governance/x.md"), "`**` spans one segment")
    t(not glob_match("tests/**", "dev/governance/roles/fixer.md"), "a foreign prefix does not match")
    t(not glob_match("dev/*.md", "dev/governance/x.md"), "`*` does not cross a `/`")
    t(named_entries("run seat/bus.sh", "- [`push.sh`](instruments/p) -- x\n"
                    "- [`bus.sh`](instruments/b) -- y\n") == ["- [`bus.sh`](instruments/b) -- y"],
      "an entry is named by its whole token, and only then")
    t(named_entries("app_push.sh", "- [`push.sh`](instruments/p) -- x\n") == [],
      "`push.sh` is not named by `app_push.sh`")

    role = "fixer"
    blocks = plan(role)
    rules = [b for b in blocks if b[0].startswith(RULES_DIR)]
    t(len(rules) > 0, "the fixer's plan carries at least one rule, so the rule mutant has a target")
    entries = blocks[-1][2].splitlines()
    t(len(entries) > 0, "the fixer's plan carries at least one instrument entry")

    def refuses(mutant: list | str, what: str, rule: str) -> None:
        """The mutant is refused BY ITS OWN RULE: `rule` is a fragment of the one
        message that rule prints, so a mutant another rule happens to catch
        does not count as this rule's."""
        pack = mutant if isinstance(mutant, str) else render_blocks(role, mutant)
        errs = check(role, pack)
        t(any(rule in e for e in errs), f"mutant refused by its rule -- {what}"
          + (f": {errs[0]}" if errs else ": not refused"))

    absent, unequal, entries_rule = "absent from the pack", "not byte-equal", "the entries differ"
    refuses(blocks[1:], "the contract dropped from the role's list", absent)
    refuses([b for b in blocks if b is not rules[0]], f"a matched rule dropped ({rules[0][0]})", absent)
    rel, note, text = blocks[0]
    refuses([(rel, note, text.replace("Failing test first", "Write a test first", 1))] + blocks[1:],
            "one contract line paraphrased", unequal)
    other = next(l for l in _read(ROOT, INSTRUMENTS).splitlines()
                 if ENTRY.match(l) and l not in entries)
    refuses(blocks[:-1] + [(INSTRUMENTS, "", blocks[-1][2] + other + "\n")],
            "an entry the contract does not name added", entries_rule)
    refuses(blocks[:-1] + [(INSTRUMENTS, "", "".join(e + "\n" for e in entries[1:]))],
            "an entry the contract names dropped", entries_rule)
    refuses(blocks[:-1] + [(INSTRUMENTS, "", blocks[-1][2] + "- an instrument nobody wrote\n")],
            "a line no source holds, inside a frame", "a line the file does not hold")
    refuses(blocks + [("CLAUDE.md", "", _read(ROOT, "CLAUDE.md"))],
            "a file outside the role's plan framed", "not in the role's plan")
    module = sys.modules[__name__]
    kept = module.role_files
    module.role_files = lambda r: kept(r)[:1]  # INSTRUMENTS.md dropped from the list
    try:
        refuses(render(role), "INSTRUMENTS.md dropped from the role's list", "every fixer pack holds it")
    finally:
        module.role_files = kept
    refuses(render_blocks(role, blocks) + "a sentence of paraphrase\n",
            "a line outside every frame", "a line outside every frame")
    refuses(blocks[:1] + blocks, "the contract framed twice (each copy byte-equal)", "exceeds the files")
    try:
        role_files("planner")
        t(False, "an unknown role is refused")
    except Refusal:
        t(True, "an unknown role is refused")
    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser(prog="role_pack.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("role")
    r.add_argument("--out")
    sub.add_parser("sizes")
    c = sub.add_parser("check")
    c.add_argument("roles", nargs="*")
    c.add_argument("--pack", help="check this file as the pack of the one role named")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "render":
            pack = render(a.role)
            if a.out:
                Path(a.out).write_text(pack, encoding="utf-8")
            else:
                sys.stdout.write(pack)
            return 0
        if a.cmd == "sizes":
            print("\n".join(sizes()))
            return 0
        if a.pack and len(a.roles) != 1:
            raise Refusal("--pack checks one file, so name exactly one role")
        bad = 0
        for role in a.roles or list(ROLE_CONTRACT):
            pack = _read(Path.cwd(), a.pack) if a.pack else render(role)
            errs = check(role, pack)
            print(f"{'ok  ' if not errs else 'FAIL'} {role}: {len(pack)} chars, "
                  f"{len(parse(pack)[0])} blocks")
            for e in errs:
                print(f"     {e}")
            bad += bool(errs)
        return 1 if bad else 0
    except Refusal as e:
        print(f"role_pack: REFUSE {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
