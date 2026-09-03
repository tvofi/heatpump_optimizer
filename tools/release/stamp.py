#!/usr/bin/env python3
"""Stamp a release on main. This is the only way a version number is assigned.

    python tools/release/stamp.py --bump patch|minor --title "<what shipped>" [--push] [--dry-run]
    python tools/release/stamp.py --self-test

Versions are assigned at merge time, never in a branch: four branches each
picking "the next version" once cost real cycles, and a stamp that skipped a
claim file turned main red. So every rule below is a refusal, not a warning:

  1. The working tree is a checkout of origin/main (fetched), clean except for
     RELEASE_NOTES.md -- the stamper writes the notes section by hand first.
  2. The Tests workflow for HEAD has completed and succeeded (fast + closures),
     so a release never publishes ahead of the unscoped gate. --allow-red
     overrides, loudly, for a red main whose cause is already understood.
  3. The next version is greater than VERSION and than every existing tag, and
     its tag exists neither locally nor on origin.
  4. RELEASE_NOTES.md opens with a '## v<next>' section whose body mentions
     every PR merged since the last tag ('(#N)' in the merge subjects) -- a
     stamp covers everything unstamped, whoever merged it.
  5. manifest.json's version equals VERSION before the stamp (a botched
     earlier stamp is fixed by hand, not papered over here).

What it writes: VERSION, the manifest version, both claim files (the
`claims-for:` stamp moves to the new version, the reason block is rewritten,
and every bare claim line is deleted -- a stamp empties the list, the next
branch restates its own footprint), then one commit and one tag. Nothing is
pushed without --push.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION_FILE = ROOT / "VERSION"
MANIFEST = ROOT / "custom_components" / "heatpump_optimizer" / "manifest.json"
NOTES = ROOT / "RELEASE_NOTES.md"
CLAIM_FILES = (
    ROOT / "tests" / "golden" / "claimed_drift.txt",
    ROOT / "tests" / "golden" / "card_claimed_drift.txt",
)
TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
PR_RE = re.compile(r"\(#(\d+)\)")


class Refuse(SystemExit):
    def __init__(self, rule: int, why: str) -> None:
        super().__init__(f"stamp refused (rule {rule}): {why}")


def sh(*args: str, check: bool = True) -> str:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=check).stdout


# --- pure pieces (covered by --self-test) -----------------------------------

def bump(version: str, part: str) -> str:
    major, minor, patch = (int(x) for x in version.strip().split("."))
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    raise ValueError(part)


def version_tuple(v: str) -> tuple[int, int, int]:
    a, b, c = (int(x) for x in v.strip().lstrip("v").split("."))
    return a, b, c


def notes_section(text: str, version: str) -> str | None:
    """Body of the '## v<version>' section, which must be the first section."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("## "):
            if line.strip() != f"## v{version}":
                return None
            body: list[str] = []
            for rest in lines[i + 1:]:
                if rest.startswith("## v"):
                    break
                body.append(rest)
            return "\n".join(body).strip()
    return None


def merged_prs(subjects: list[str]) -> set[str]:
    return {m.group(1) for s in subjects for m in PR_RE.finditer(s)}


def rewrite_claims(text: str, new_version: str, title: str) -> tuple[str, str | None, int]:
    """Move the stamp, rewrite the reason block, delete every bare claim.

    Returns (new_text, old_stamp, deleted_claims). The reason block is the run
    of comment lines that follows `# claims-for:` up to the first blank line;
    `# may-drift:` lines sit after a blank line and are never touched.
    """
    lines = text.splitlines()
    out: list[str] = []
    old_stamp = None
    deleted = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^# claims-for:\s*(\S+)", line)
        if m:
            old_stamp = m.group(1)
            out.append(f"# claims-for: {new_version}")
            out.append("#")
            out.append(f"# v{new_version}: {title}. The stamp empties the list; the")
            out.append("# next branch restates its own footprint, claims included.")
            out.append("#")
            i += 1
            while i < len(lines) and lines[i].startswith("#") and not lines[i].startswith("# may-drift:"):
                i += 1
            continue
        if line.strip() and not line.startswith("#"):
            deleted += 1
            i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out) + "\n", old_stamp, deleted


def self_test() -> int:
    ok = True

    def check(name: str, cond: bool) -> None:
        nonlocal ok
        ok &= cond
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    check("bump patch", bump("6.2.12", "patch") == "6.2.13")
    check("bump minor", bump("6.2.12", "minor") == "6.3.0")
    check("tag order", version_tuple("v6.2.12") > version_tuple("v6.2.9"))
    notes = "# Notes\n\n## v6.2.13\n\n### T\n\nB (#170) and (#171).\n\n## v6.2.12\n\nold\n"
    check("notes: first section found", notes_section(notes, "6.2.13") == "### T\n\nB (#170) and (#171).")
    check("notes: wrong version is None", notes_section(notes, "6.2.14") is None)
    check("merged prs", merged_prs(["A (#170)", "B (#171)", "stamp"]) == {"170", "171"})
    claims = (
        "# header\n#\n# claims-for: 6.2.12\n#\n# The old reason.\n#\n\n"
        "# may-drift: wood_coil -- machine-sensitive\n"
        "capacity_tariff_15min  # moved\n"
    )
    new, old, deleted = rewrite_claims(claims, "6.2.13", "the test")
    check("claims: old stamp read", old == "6.2.12")
    check("claims: one bare claim deleted", deleted == 1)
    check("claims: new stamp present", "# claims-for: 6.2.13" in new)
    check("claims: may-drift kept", "# may-drift: wood_coil" in new)
    check("claims: old reason gone", "old reason" not in new)
    check("claims: no bare lines", all(not l.strip() or l.startswith("#") for l in new.splitlines()))
    tight = "# claims-for: 6.2.12\n# reason\n# may-drift: wood_coil -- x\nfoo  # claim\n"
    new2, _, deleted2 = rewrite_claims(tight, "6.2.13", "t")
    check("claims: may-drift survives without a blank line", "# may-drift: wood_coil" in new2 and deleted2 == 1)
    check("notes: #16 is not covered by #165", not re.search(r"#16(?!\d)", "fixed in #165"))
    check("tags: pre-release tags are ignored", not TAG_RE.match("v6.2.15-rc1") and bool(TAG_RE.match("v6.2.15")))

    # Rule 2's evidence, on both paths. gh is not installed everywhere a
    # release is taken from, and rule 2 used to call it before --allow-red
    # was read -- a missing binary raised FileNotFoundError instead of
    # refusing. These cover the pure pieces of the fallback: the URL, the
    # reduction of a runs payload to a verdict, and which path is taken.
    check("rule 2: the rest query", runs_url("abc123") ==
          "https://api.github.com/repos/tvofi/heatpump_optimizer/actions/runs?head_sha=abc123&event=push")
    check("rule 2: a token becomes a bearer header", rest_headers("t123")["Authorization"] == "Bearer t123")
    check("rule 2: no token, no header (the repository is public)", "Authorization" not in rest_headers(None))
    payload = {"total_count": 3, "workflow_runs": [
        {"id": 11, "name": "Tests", "path": ".github/workflows/tests.yml",
         "status": "completed", "conclusion": "success"},
        {"id": 12, "name": "Card", "path": ".github/workflows/card.yml",
         "status": "completed", "conclusion": "failure"},
        {"id": 13, "name": "Tests", "path": ".github/workflows/tests.yml",
         "status": "in_progress", "conclusion": None},
    ]}
    reduced = runs_from_payload(payload)
    check("rule 2: the payload reduces to gh's shape", reduced == [
        {"status": "completed", "conclusion": "success", "databaseId": 11},
        {"status": "in_progress", "conclusion": None, "databaseId": 13}])
    check("rule 2: another workflow's run is not the gate", all(r["databaseId"] != 12 for r in reduced))
    check("rule 2: a completed success is green", gate_verdict(reduced)[0])
    red = runs_from_payload({"workflow_runs": [
        {"id": 21, "name": "Tests", "status": "completed", "conclusion": "failure"}]})
    red_green, red_why = gate_verdict(red)
    check("rule 2: a red run refuses, naming the conclusion", not red_green and "failure" in red_why)
    queued = runs_from_payload({"workflow_runs": [
        {"id": 31, "name": "Tests", "status": "queued", "conclusion": None}]})
    check("rule 2: a run still going is counted, not awaited", gate_verdict(queued) ==
          (False, "no completed Tests run for HEAD yet; 1 run(s) still in progress"))
    check("rule 2: no run at all", gate_verdict([]) == (False, "no completed Tests run for HEAD yet"))
    check("rule 2: gh's shape and rest's reduce to one verdict",
          gate_verdict([{"status": "completed", "conclusion": "failure", "databaseId": 21}]) == gate_verdict(red))
    check("rule 2: the five newest Tests runs, as gh's --limit", len(runs_from_payload(
        {"workflow_runs": [{"id": i, "name": "Tests", "status": "completed", "conclusion": "success"}
                           for i in range(9)]})) == 5)
    check("rule 2: gh is used when it is installed", gate_source(lambda name: "/usr/bin/gh") == "gh")
    check("rule 2: rest is used when gh is absent", gate_source(lambda name: None) == "rest")

    def _no_gh(head: str) -> list[dict]:
        raise FileNotFoundError(2, "No such file or directory: 'gh'")

    unreadable = tests_gate("deadbee", which=lambda name: None, fetchers={"rest": _no_gh})
    check("rule 2: a source that cannot answer refuses, it does not raise",
          not unreadable[0] and "could not read the Tests gate" in unreadable[1])

    print(f"RESULT stamp_self_test={'pass' if ok else 'fail'}")
    return 0 if ok else 1


# --- the stamp ---------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bump", choices=("patch", "minor"))
    ap.add_argument("--title", help="what shipped, for the commit subject and the claim files")
    ap.add_argument("--push", action="store_true", help="push the commit and the tag to origin")
    ap.add_argument("--dry-run", action="store_true", help="run every check, write nothing")
    ap.add_argument("--allow-red", action="store_true", help="stamp even though HEAD's gate is not green")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.bump or not args.title:
        ap.error("--bump and --title are required (or --self-test)")

    # Rule 1: a fetched, clean checkout of origin/main.
    sh("git", "fetch", "origin", "--quiet", "--tags")
    head = sh("git", "rev-parse", "HEAD").strip()
    main = sh("git", "rev-parse", "origin/main").strip()
    if head != main:
        raise Refuse(1, f"HEAD {head[:7]} is not origin/main {main[:7]}; stamps go on main only")
    dirty = [l for l in sh("git", "status", "--porcelain").splitlines() if l.strip()]
    if any(not l.endswith("RELEASE_NOTES.md") for l in dirty):
        raise Refuse(1, f"working tree has changes beyond RELEASE_NOTES.md: {dirty}")

    # Rule 2: HEAD's unscoped gate is green.
    runs = json.loads(sh("gh", "run", "list", "--workflow", "Tests", "--commit", head, "--event", "push",
                         "--json", "status,conclusion,databaseId", "--limit", "5"))
    done = [r for r in runs if r["status"] == "completed"]
    green = any(r["conclusion"] == "success" for r in done)
    pending = [r for r in runs if r["status"] != "completed"]
    if not green:
        why = ("no completed Tests run for HEAD yet" if not done else
               f"Tests for HEAD concluded {[r['conclusion'] for r in done]}")
        if pending:
            why += f"; {len(pending)} run(s) still in progress"
        if not args.allow_red:
            raise Refuse(2, why + " (wait, or --allow-red with the cause understood)")
        print(f"WARNING: stamping a main whose gate is not green: {why}")

    # Rule 3: the next version is new, and above every tag.
    current = VERSION_FILE.read_text().strip()
    nxt = bump(current, args.bump)
    tags = [t for t in sh("git", "tag", "--list").split() if TAG_RE.match(t)]
    remote = [t for t in (l.split("refs/tags/")[1] for l in sh("git", "ls-remote", "--tags", "origin").splitlines()
                            if "refs/tags/v" in l and not l.endswith("^{}")) if TAG_RE.match(t)]
    if f"v{nxt}" in tags or f"v{nxt}" in remote:
        raise Refuse(3, f"tag v{nxt} already exists")
    top = max((version_tuple(t) for t in tags + remote), default=(0, 0, 0))
    if version_tuple(nxt) <= top:
        raise Refuse(3, f"next version {nxt} is not above the highest tag {'.'.join(map(str, top))}")
    last_tag = "v" + ".".join(map(str, top)) if top != (0, 0, 0) else None

    # Rule 4: the notes section exists and covers every merged PR.
    body = notes_section(NOTES.read_text(), nxt)
    if not body:
        raise Refuse(4, f"RELEASE_NOTES.md must open with a non-empty '## v{nxt}' section")
    subjects = sh("git", "log", f"{last_tag}..HEAD", "--format=%s").splitlines() if last_tag else []
    missing = sorted(pr for pr in merged_prs(subjects) if not re.search(rf"#{pr}(?!\d)", body))
    if missing:
        raise Refuse(4, f"merged since {last_tag} but not mentioned in the v{nxt} notes: #{', #'.join(missing)}")

    # Rule 5: the manifest agrees with VERSION before we move both.
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("version") != current:
        raise Refuse(5, f"manifest version {manifest.get('version')} != VERSION {current}; fix by hand first")

    plan = [f"VERSION {current} -> {nxt}", f"manifest version -> {nxt}"]
    claim_edits = []
    for path in CLAIM_FILES:
        new, old, deleted = rewrite_claims(path.read_text(), nxt, args.title)
        if old != current:
            print(f"WARNING: {path.name} was stamped {old}, not {current}; restamping anyway")
        claim_edits.append((path, new))
        plan.append(f"{path.relative_to(ROOT)}: claims-for {old} -> {nxt}, {deleted} claim(s) deleted")
    plan.append(f"commit 'v{nxt}: stamp {args.title}' and tag v{nxt}" + (" (pushed)" if args.push else " (not pushed)"))
    print("stamp plan:")
    for p in plan:
        print(f"  - {p}")
    if args.dry_run:
        print("dry run: nothing written")
        return 0

    VERSION_FILE.write_text(nxt + "\n")
    text = MANIFEST.read_text()
    text, n = re.subn(r'"version":\s*"[^"]+"', f'"version": "{nxt}"', text, count=1)
    if n != 1:
        raise Refuse(5, "could not rewrite the manifest version")
    MANIFEST.write_text(text)
    for path, new in claim_edits:
        path.write_text(new)
    sh("git", "add", str(VERSION_FILE), str(MANIFEST), str(NOTES), *map(str, CLAIM_FILES))
    sh("git", "commit", "-q", "-m",
       f"v{nxt}: stamp {args.title}\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>")
    sh("git", "tag", f"v{nxt}")
    if args.push:
        # main moves between fetch and push when another session is merging.
        # A rejected push must leave nothing behind: no local tag that would
        # make the retry refuse under rule 3, no stamp commit off main.
        try:
            sh("git", "push", "origin", "HEAD:main")
        except subprocess.CalledProcessError as exc:
            sh("git", "tag", "-d", f"v{nxt}")
            sh("git", "reset", "--hard", "origin/main")
            raise Refuse(1, "push to main was rejected (main moved); the stamp commit and tag were "
                            "discarded -- fetch, rewrite the notes for the new HEAD, run again: "
                            + exc.stderr.strip().splitlines()[-1]) from exc
        sh("git", "push", "origin", f"v{nxt}")
    print(f"RESULT stamped=v{nxt}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refuse as e:
        print(e, file=sys.stderr)
        sys.exit(2)
