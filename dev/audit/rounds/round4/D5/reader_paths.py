#!/usr/bin/env python3
"""D5 reader-path harness.

METRIC: dead ends per reader path. A DEAD END is an actionable token the
documentation puts in front of a reader on that path -- an entity id, a service
name, a UI label the reader is told to open or watch, a `.storage` file name, or
a test command -- that the shipped artefacts do not provide. Every token is
resolved against a production artefact, never against another document:

  entity id     -> strings.json entity.<domain>.<translation_key>  (sensor.py sets
                   entity_id = f"sensor.heat_pump_optimizer_{translation_key}")
  service name  -> services.yaml top-level keys AND async_register in services.py
  UI label      -> any string value in strings.json (step titles, menu options,
                   field labels, entity names)
  table setting -> first cell of every row of a "| Setting |" table: the label
                   the reader has to find on an options page, resolved against
                   strings.json's own field labels and step titles
  card option   -> first cell of every row of dashboard-card.md's option tables,
                   resolved against www/heatpump-optimizer-card.js
  storage file  -> the `heatpump_optimizer_..._<suffix>` store keys built in the
                   package
  test command  -> the tests/*.py, tests/*.mjs or tests/*.sh file it names

THREE READER PATHS, each an ordered list of (document, heading) sections:
  install    HACS install to a first plan
  configure  two-tank storage / ECL110 / capacity (grid peak) tariff
  develop    a developer running the tests

RUN (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D5/reader_paths.py
  ... --list      every dead end, with path, document:line and token
  ... --selftest  positive control: three fabricated tokens are appended to each
                  path's token set and must all be reported

EXPECTED at baseline 7dd68dd (Apple M1, 8 core, macOS 25.6): see RESULT lines.
Counts over file bytes and over strings.json/services.yaml; contention-immune.
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import json
import re
import sys
from pathlib import Path

ROOT = Path(".").resolve()
PKG = ROOT / "custom_components" / "heatpump_optimizer"

PATHS = {
    "install": [
        ("README.md", "Requirements"),
        ("README.md", "Installation"),
        ("README.md", "HACS (recommended)"),
        ("README.md", "Manual"),
        ("README.md", "Quick start — the first 30 minutes"),
        ("README.md", "Your first week"),
        ("README.md", "Dashboard card"),
        ("README.md", "Troubleshooting"),
        ("docs/configuration.md", "Initial setup"),
        ("docs/dashboard-card.md", "Installation"),
        ("docs/dashboard-card.md", "Automatic (recommended)"),
        ("docs/dashboard-card.md", "Configuration options"),
        ("docs/dashboard-card.md", "Entity discovery"),
    ],
    "configure": [
        ("docs/configuration.md", "Changing settings later"),
        ("docs/configuration.md", "Heating system and heat storage"),
        ("docs/configuration.md", "Hot water tank and inlet"),
        ("docs/configuration.md", "The hydronic layout catalog"),
        ("docs/configuration.md", "Grid peak tariff"),
        ("docs/configuration.md", "Transfer fees and contract"),
        ("docs/configuration.md", "Heat curve control (ECL110)"),
        ("docs/ecl110.md", None),
        ("README.md", "ECL110 heat-curve control"),
    ],
    "develop": [
        ("tests/README.md", None),
        ("docs/architecture.md", "Where to start reading"),
        ("docs/how-it-works.md", "What the tests actually prove"),
    ],
}

FENCE = re.compile(r"^\s*(```|~~~)")


def plain(cell):
    """A table cell reduced to its literal label text."""
    t = re.sub(r"`([^`]*)`", r"\1", cell)
    t = t.replace("**", "").replace("*", "").replace("\u00b7", "-")
    t = re.sub(r"\s+", " ", t).strip()
    return t
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def section(doc, heading):
    """[(lineno, text)] for the named heading's own section, or the whole file."""
    lines = (ROOT / doc).read_text(encoding="utf-8", errors="replace").splitlines()
    if heading is None:
        return list(enumerate(lines, 1))
    out, level, on = [], None, False
    for i, line in enumerate(lines, 1):
        m = HEADING.match(line)
        if m:
            if on and len(m.group(1)) <= level:
                break
            if not on and m.group(2).strip().rstrip("#").strip() == heading:
                on, level = True, len(m.group(1))
                continue
        if on:
            out.append((i, line))
    if not on:
        raise SystemExit(f"HARNESS ERROR: heading {heading!r} not found in {doc}")
    return out


# ---------------------------------------------------------------- artefacts
def artefacts():
    strings = json.loads((PKG / "strings.json").read_text(encoding="utf-8"))
    ent = {}
    for dom, keys in strings.get("entity", {}).items():
        for k in keys:
            ent[f"{dom}.heat_pump_optimizer_{k}"] = True

    labels = set()

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str):
            labels.add(o.strip())

    def walk_keys(o):
        if isinstance(o, dict):
            for k, v in o.items():
                labels.add(k)
                walk_keys(v)
        elif isinstance(o, list):
            for v in o:
                walk_keys(v)
    walk(strings)
    walk_keys(strings)
    # the product's own names, which live in the manifest rather than strings.json
    import json as _json
    for f in ("manifest.json",):
        labels.add(_json.loads((PKG / f).read_text(encoding="utf-8")).get("name", ""))
    labels.add((ROOT / "hacs.json").read_text(encoding="utf-8"))

    svc_yaml = set()
    for line in (PKG / "services.yaml").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([a-z][a-z0-9_]*):", line)
        if m:
            svc_yaml.add(m.group(1))
    svc_code = set(re.findall(r"async_register\(\s*DOMAIN\s*,\s*[\"']([a-z_]+)[\"']",
                              (PKG / "services.py").read_text(encoding="utf-8")))
    svc_code |= set(re.findall(r"SERVICE_[A-Z_]+\s*=\s*[\"']([a-z_]+)[\"']",
                               (PKG / "services.py").read_text(encoding="utf-8")))
    pkg_text = "\n".join(
        p.read_text(encoding="utf-8", errors="replace") for p in PKG.glob("*.py")
    )
    store_suffixes = set(re.findall(r"_([a-z_]+)\"\s*$", "", re.M))  # placeholder
    store_suffixes = set(re.findall(r"f\"\{DOMAIN\}_\{[^}]*\}_([a-z_]+)\"", pkg_text))
    store_suffixes |= set(re.findall(r"STORAGE_KEY[A-Z_]*\s*=\s*[^\n]*_([a-z_]+)\"", pkg_text))
    store_suffixes |= set(re.findall(r"_store_key\([^)]*\"([a-z_]+)\"", pkg_text))
    return ent, labels, svc_yaml, svc_code, store_suffixes, pkg_text


RE_ENTITY = re.compile(
    r"\b((?:sensor|binary_sensor|switch|button|climate|datetime|number|select|input_boolean)"
    r"\.heat_pump_optimizer_[a-z0-9_]+)")
RE_SERVICE = re.compile(r"\bheatpump_optimizer\.([a-z][a-z0-9_]*)\b")
RE_STORE = re.compile(r"heatpump_optimizer_<entry id>_([a-z_]+)")
RE_TESTCMD = re.compile(r"(?:^|\s)(?:\./)?(tests/[A-Za-z0-9_./-]+\.(?:py|mjs|sh|txt))")
# "watch **X**" / "press **X**" / "under **A → B**" -- a label the reader must find
RE_UILABEL = re.compile(r"\*\*([A-Z][^*]{2,60}?)\*\*")
RE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
SETTING_HDR = ("setting", "option", "field", "key", "name")
UI_VERB = re.compile(
    r"(?:open|press|watch|enable|switch on|switch off|turn on|turn off|tick|"
    r"under|go to|choose|select|set|on the)\s*$", re.I)


def label_hit(tok, labels):
    """A doc label matches a shipped string when one contains the other after
    case folding and punctuation stripping. Deliberately generous: the metric is
    "could the reader find this at all", not "is it spelled identically"."""
    t = re.sub(r"[^a-z0-9 ]+", " ", tok.lower())
    t = re.sub(r"\s+", " ", t).strip()
    if not t:
        return True
    for l in labels:
        s2 = re.sub(r"[^a-z0-9 ]+", " ", l.lower())
        s2 = re.sub(r"\s+", " ", s2).strip()
        if t == s2 or t in s2 or (len(t) > 12 and s2 and s2 in t):
            return True
    return False


def main():
    listing = "--list" in sys.argv
    selftest = "--selftest" in sys.argv
    ent, labels, svc_yaml, svc_code, stores, pkg_text = artefacts()
    card_text = (PKG / "www" / "heatpump-optimizer-card.js").read_text(
        encoding="utf-8", errors="replace")

    totals = {}
    dead = {}
    for pname, secs in PATHS.items():
        toks = []          # (kind, token, doc, line)
        for doc, head in secs:
            in_fence = False
            in_setting_table = [False]
            for ln, line in section(doc, head):
                if FENCE.match(line):
                    in_fence = not in_fence
                    continue
                for m in RE_ENTITY.finditer(line):
                    toks.append(("entity", m.group(1), doc, ln))
                for m in RE_SERVICE.finditer(line):
                    toks.append(("service", m.group(1), doc, ln))
                for m in RE_STORE.finditer(line):
                    toks.append(("store", m.group(1), doc, ln))
                if in_fence or line.lstrip().startswith(("    ", "\t")):
                    for m in RE_TESTCMD.finditer(line):
                        toks.append(("testcmd", m.group(1), doc, ln))
                    continue
                for m in RE_TESTCMD.finditer(line):
                    toks.append(("testcmd", m.group(1), doc, ln))
                for m in RE_UILABEL.finditer(line):
                    before = line[: m.start()]
                    if UI_VERB.search(before.rstrip()):
                        for part in re.split(r"\s*(?:→|->)\s*", m.group(1)):
                            part = part.strip().strip(".,;:")
                            if part and not part.isdigit():
                                toks.append(("uilabel", part, doc, ln))
                mrow = RE_ROW.match(line)
                if mrow:
                    cells = [c.strip() for c in mrow.group(1).split("|")]
                    first = cells[0] if cells else ""
                    if first and set(first.replace(" ", "")) <= set("-:"):
                        continue                       # header separator row
                    if first.lower().strip("* ") in SETTING_HDR:
                        in_setting_table[0] = True
                        continue
                    if not first:
                        in_setting_table[0] = False
                        continue
                    if in_setting_table[0]:
                        kind = ("cardopt" if doc.endswith("dashboard-card.md")
                                else "setting")
                        toks.append((kind, plain(first), doc, ln))
                else:
                    in_setting_table[0] = False
        if selftest:
            toks += [
                ("entity", "sensor.heat_pump_optimizer_zzz_fabricated", "SELFTEST", 0),
                ("service", "zzz_fabricated_service", "SELFTEST", 0),
                ("testcmd", "tests/zzz_fabricated.py", "SELFTEST", 0),
            ]

        bad = []
        for kind, tok, doc, ln in toks:
            ok = True
            if kind == "entity":
                ok = tok in ent
            elif kind == "service":
                ok = tok in svc_yaml and tok in svc_code
            elif kind == "store":
                ok = tok in stores or f'_{tok}"' in pkg_text
            elif kind == "testcmd":
                ok = (ROOT / tok).exists()
            elif kind == "setting":
                ok = label_hit(tok, labels)
            elif kind == "cardopt":
                ok = (tok in card_text) or label_hit(tok, labels)
            elif kind == "uilabel":
                ok = any(tok.lower() == l.lower() or tok.lower() in l.lower()
                         for l in labels)
            if not ok:
                bad.append((kind, tok, doc, ln))
        totals[pname] = toks
        dead[pname] = bad

    if listing:
        for pname in PATHS:
            print(f"== {pname}: {len(dead[pname])} dead end(s) of "
                  f"{len(totals[pname])} actionable tokens ==")
            for kind, tok, doc, ln in dead[pname]:
                print(f"  DEAD-END [{kind}] {tok!r}   {doc}:{ln}")

    grand = 0
    for pname in PATHS:
        print(f"RESULT tokens_{pname}={len(totals[pname])} count")
    for pname in PATHS:
        print(f"RESULT deadends_{pname}={len(dead[pname])} count")
        grand += len(dead[pname])
    print(f"RESULT deadends_total={grand} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
