#!/usr/bin/env python
# D5 harness: reader-path notes -- doc-vs-code fact checks and link-graph
# reachability, grouped by the three reader paths of the D5 brief.
#
# Metric: each CHECK below states one claim a document makes that a reader on
# one of the three paths (P1 new user HACS->first plan, P2 configuring a
# feature: two-tank storage / ECL110 / capacity tariff, P3 developer running
# the tests) needs, and computes the fact from the tree (ast over the code,
# the closures record, the workflow file, the services catalogue).  A check
# FAILS when the document and the tree disagree, when a term the reader needs
# is defined nowhere, or when the document the path needs is unreachable from
# README.md by links.  dead_ends_<path> is the number of failed checks tagged
# with that path; doc_fact_checks_failed is the total.
#
# Command:
#   PYTHONPATH=tests/hastub .venv/bin/python tools/audit/round2/D5/reader_paths.py
#
# Expected (baseline c398fc84eec25fc44b60d74aae05b9a2da205884), all exact:
#   RESULT doc_fact_checks_total=36  doc_fact_checks_failed=15
#   RESULT failed_in[README.md]=2  failed_in[docs/]=1  failed_in[docs/configuration.md]=2
#          failed_in[docs/dashboard-card.md]=1  failed_in[docs/how-it-works.md]=2
#          failed_in[tests/README.md]=7
#   RESULT unreachable_docs_from_readme=3
#   RESULT tests_readme_drift=7  ecl110_guidance_contradiction=1  content_defects_user_docs=5
#   RESULT dead_ends_new_user=4  dead_ends_feature=4  dead_ends_developer=8
#
# Machine: Apple M1 (8 cores, 8 GB), macOS 26.6, Python 3.13.1.
# Instrumented symbols: tests/closure.py:INERT and NOT_A_TEST, tests/closures.json,
# tests/golden.py:SCENARIOS, tests/plan_view.py, tests/validate.py, tests/stress.py,
# custom_components/heatpump_optimizer/const.py (DEFAULT_ECL110_*,
# MANUAL_PLAN_WINDOW_HOURS), config_flow.py (peak window selector),
# topology.ASSIGNABLE_KEYS, services.yaml, sensor.py, the card's VIEW_W/VIEW_H,
# STRINGS and CARD_VERSION -- each read through ast/regex, never executed.
# Perturbation: in tests/README.md change "53 fixtures (47 plan scenarios" to
# "55 fixtures (49 plan scenarios" -> doc_fact_checks_failed goes DOWN by one
# and dead_ends_developer goes DOWN by one.
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

import ast
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PKG = ROOT / "custom_components" / "heatpump_optimizer"
TESTS = ROOT / "tests"
CARD = PKG / "www" / "heatpump-optimizer-card.js"

CHECKS = []


def check(cid, doc, paths, claim, ok, detail):
    CHECKS.append({"id": cid, "doc": doc, "paths": paths, "claim": claim, "ok": bool(ok), "detail": detail})


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def footer(t_proc0, t_thr0):
    proc = time.process_time() - t_proc0
    thr = time.thread_time() - t_thr0
    tf = proc / thr if thr > 0 else 1.0
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    swapins = -1
    try:
        vm = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=5).stdout
        m = re.search(r"Swapins:\s+(\d+)", vm)
        if m:
            swapins = int(m.group(1))
    except Exception:  # noqa: BLE001
        pass
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={load1:.2f}")
    print(f"RESULT swapins={swapins}")


def module_assign(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return node.value
    return None


def literal(node):
    try:
        return ast.literal_eval(node)
    except Exception:  # noqa: BLE001
        return None


def table_rows(text: str, start_heading: str, stop_prefix: str = "#"):
    """Count body rows of the first markdown table after a heading."""
    lines = text.split("\n")
    i = next((k for k, l in enumerate(lines) if l.strip() == start_heading), None)
    if i is None:
        return -1
    rows = 0
    seen_table = False
    for l in lines[i + 1 :]:
        if l.startswith(stop_prefix) and seen_table:
            break
        if l.startswith("#"):
            break
        if l.startswith("|"):
            if re.match(r"^\|\s*-", l) or (not seen_table and rows == 0 and "---" not in l and l.count("|") >= 2 and not seen_table):
                # header or separator
                if re.match(r"^\|\s*-", l):
                    seen_table = True
                continue
            if seen_table:
                rows += 1
    return rows


def main():
    t_proc0, t_thr0 = time.process_time(), time.thread_time()
    readme = read("README.md")
    tests_readme = read("tests/README.md")
    conf = read("docs/configuration.md")
    hiw = read("docs/how-it-works.md")
    ecl = read("docs/ecl110.md")
    arch = read("docs/architecture.md")
    card_doc = read("docs/dashboard-card.md")
    disclaimer = read("DISCLAIMER.md")
    version = read("VERSION").strip()
    card_src = CARD.read_text(encoding="utf-8")

    # ---------------------------------------------------------------- link graph
    docs = [ROOT / "README.md", ROOT / "DISCLAIMER.md", TESTS / "README.md"] + sorted((ROOT / "docs").glob("*.md"))
    rels = {str(p.relative_to(ROOT)) for p in docs}
    edges = {}
    for p in docs:
        src = p.read_text(encoding="utf-8")
        out = set()
        for m in re.finditer(r"\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)", src):
            tgt = (p.parent / m.group(1)).resolve()
            try:
                r = str(tgt.relative_to(ROOT))
            except ValueError:
                continue
            if r in rels:
                out.add(r)
        edges[str(p.relative_to(ROOT))] = out
    seen = {"README.md"}
    stack = ["README.md"]
    while stack:
        cur = stack.pop()
        for nxt in edges.get(cur, ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    unreachable = sorted(rels - seen)
    check("R1", "README.md", ["P3"], "every document is reachable from README.md by links",
          "tests/README.md" in seen, f"unreachable from README.md: {unreachable}")
    check("R2", "docs/", ["P1"], "no orphaned document under docs/",
          not [u for u in unreachable if u.startswith("docs/")],
          f"orphaned under docs/: {[u for u in unreachable if u.startswith('docs/')]}")

    # ---------------------------------------------------------------- P3: tests/README vs the gate
    inert = literal(module_assign(TESTS / "closure.py", "INERT")) or ()
    not_a_test = literal(module_assign(TESTS / "closure.py", "NOT_A_TEST")) or set()
    closures = json.load(open(TESTS / "closures.json"))["closures"]
    all_closure_files = set()
    for v in closures.values():
        all_closure_files.update(v if isinstance(v, list) else v.get("files", []))
    m = re.search(r"short, checked list of files no test can read \(([^)]*)\)", tests_readme, re.S)
    claimed = re.sub(r"\s+", " ", m.group(1)) if m else ""
    claimed_items = {
        "README.md": ["README.md"],
        "docs/": ["docs/"],
        "RELEASE_NOTES.md": ["RELEASE_NOTES.md"],
        "the licence files": ["LICENSE", "NOTICE"],
        "the brand images": ["custom_components/heatpump_optimizer/brand/icon.png",
                             "custom_components/heatpump_optimizer/brand/logo.png",
                             "custom_components/heatpump_optimizer/icon.png"],
    }
    wrong = []
    for label, paths in claimed_items.items():
        if label.strip("`") not in claimed and label not in claimed:
            continue
        for pth in paths:
            in_inert = any(pth == p or (p.endswith("/") and pth.startswith(p)) for p in inert)
            in_closure = pth in all_closure_files
            if in_closure or not in_inert:
                wrong.append(f"{label} -> {pth} (in INERT: {in_inert}, read by a test: {in_closure})")
    check("T1", "tests/README.md:129", ["P3"],
          "the files named as 'no test can read' are the ones tests/closure.py:INERT lists and no closure records",
          not wrong, "; ".join(wrong) or "all consistent")

    scen = module_assign(TESTS / "golden.py", "SCENARIOS")
    n_plan = len(scen.keys) if isinstance(scen, ast.Dict) else -1
    n_json = len(list((TESTS / "golden").glob("*.json")))
    n_coord = len(list((TESTS / "golden").glob("coord_*.json")))
    m = re.search(r"(\d+) fixtures \((\d+) plan scenarios, (\d+) coordinator captures", tests_readme)
    doc_total, doc_plan, doc_coord = (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (-1, -1, -1)
    check("T2", "tests/README.md:285", ["P3"],
          f"golden.py records {doc_total} fixtures ({doc_plan} plan scenarios, {doc_coord} coordinator captures)",
          (doc_total, doc_plan, doc_coord) == (n_json, n_plan, n_coord),
          f"tree: {n_json} fixture files, {n_plan} SCENARIOS keys, {n_coord} coordinator captures")
    m2 = re.findall(r"all (\d+) scenarios", tests_readme)
    check("T3", "tests/README.md:355", ["P3"], f"env_drift --all covers 'all {m2} scenarios'",
          all(int(x) == n_json for x in m2), f"tree: {n_json} fixtures")

    pv = read("tests/plan_view.py")
    hashed = "plandata-%s.json" in pv or "plandata-" in pv
    n_legacy = tests_readme.count("/tmp/plandata.json")
    check("T4", "tests/README.md:228,457", ["P3"],
          "plan_view.py writes /tmp/plandata.json",
          not (hashed and n_legacy), f"plan_view.py default is /tmp/plandata-<sha256(tests dir)[:12]>.json; README names /tmp/plandata.json {n_legacy} times")

    m = re.search(r"(\w+) files in `tests/` are not tests at all", tests_readme)
    words = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8}
    doc_n = words.get((m.group(1).lower() if m else ""), -1)
    runsh = read("tests/run.sh")
    m3 = re.search(r"^\s*([a-z_.|]+)\) continue ;;\s*#\s*shared plumbing", runsh, re.M)
    excl = set()
    for mm in re.finditer(r"^\s*((?:[a-z_]+\.(?:py|mjs)\|?)+)\) continue ;;", runsh, re.M):
        excl.update(mm.group(1).split("|"))
    check("T5", "tests/README.md:487", ["P3"],
          f"'{doc_n} files in tests/ are not tests at all'",
          doc_n == len(not_a_test), f"closure.py NOT_A_TEST has {len(not_a_test)}: {sorted(not_a_test)}; run.sh allow-lists {len(excl)}: {sorted(excl)}")

    wf = read(".github/workflows/tests.yml")
    check("T6", "tests/README.md:505", ["P3"],
          "the browser lane tests/card_browser.mjs (its own CI job) is documented; 'verify in a real browser as well' is the only guidance",
          "card_browser" in tests_readme, f"tests/README mentions card_browser.mjs {tests_readme.count('card_browser')} times; tests.yml runs it: {'card_browser.mjs' in wf}")

    val = read("tests/validate.py")
    n_run = len(re.findall(r"^run\(", val, re.M))
    m = re.search(r"validate\.py\s+#\s*(\d+) seasonal scenarios", tests_readme)
    check("T7", "tests/README.md:221", ["P3"], f"validate.py runs {m.group(1) if m else '?'} seasonal scenarios",
          m is not None and int(m.group(1)) == n_run, f"tree: {n_run} run(...) scenarios")

    seasons = module_assign(TESTS / "stress.py", "SEASONS")
    buildings = module_assign(TESTS / "stress.py", "BUILDINGS")
    edges_d = module_assign(TESTS / "stress.py", "edges")
    n_seasons = len(seasons.keys) if isinstance(seasons, ast.Dict) else -1
    n_build = len(buildings.keys) if isinstance(buildings, ast.Dict) else -1
    n_edges = len(edges_d.keys) if isinstance(edges_d, ast.Dict) else -1
    n_comb = n_seasons * 2 * 2 + 2 * 7 + n_build * 2  # the three product loops in stress.py
    m = re.search(r"stress\.py\s+#\s*(\d+) combinations, (\d+) edge cases", tests_readme)
    check("T8", "tests/README.md:224", ["P3"], "stress.py sweeps 48 combinations and 17 edge cases",
          m is not None and (int(m.group(1)), int(m.group(2))) == (n_comb, n_edges), f"tree: {n_comb} combinations, {n_edges} edge cases")
    m = re.search(r"1 of (\d+)", tests_readme)
    check("T9", "tests/README.md:102", ["P3"], "the closure record covers 16 scripts",
          m is not None and int(m.group(1)) == len(closures), f"tree: {len(closures)} closures")

    # ---------------------------------------------------------------- architecture.md
    n_mod = len(list(PKG.glob("*.py")))
    ha_mods = sorted(p.stem for p in PKG.glob("*.py") if re.search(r"^(from|import) homeassistant", p.read_text(), re.M))
    m = re.search(r"(\d+) modules, of which (\w+) touch", arch)
    check("A1", "docs/architecture.md:8", ["P3"], "45 modules, ten touch homeassistant",
          m is not None and int(m.group(1)) == n_mod and words.get(m.group(2), -1) == len(ha_mods) or (m and m.group(2) == "ten" and len(ha_mods) == 10 and int(m.group(1)) == n_mod),
          f"tree: {n_mod} modules, {len(ha_mods)} import homeassistant at module level: {ha_mods}")
    inputs_src = read("custom_components/heatpump_optimizer/inputs.py")
    fn_level = bool(re.search(r"^\s{4,}from homeassistant\.util import dt", inputs_src, re.M))
    others = [p.stem for p in PKG.glob("*.py") if p.stem not in ha_mods and p.stem != "inputs" and "homeassistant" in p.read_text() and re.search(r"(from|import) homeassistant", p.read_text())]
    check("A2", "docs/architecture.md:143", ["P3"], "only inputs.py touches homeassistant outside the ten, inside a function",
          fn_level and not others, f"inputs.py function-level import: {fn_level}; other modules importing homeassistant: {others}")
    services = re.findall(r"^([a-z_]+):", read("custom_components/heatpump_optimizer/services.yaml"), re.M)
    check("A3", "docs/architecture.md:61 README.md:389 docs/configuration.md:535", ["P1", "P3"],
          "eleven services", len(services) == 11 and "Eleven services" in readme and "11 services" in arch, f"services.yaml: {len(services)}")

    # ---------------------------------------------------------------- configuration.md vs services and const
    import yaml  # pyyaml is a test dependency (tests/README.md)
    sv = yaml.safe_load(open(PKG / "services.yaml"))
    n_stp = len(sv["set_thermal_parameters"]["fields"])
    n_sim = len(sv["simulate_plan"]["fields"])
    check("C1", "docs/configuration.md:547", ["P2"], "set_thermal_parameters has 28 optional fields",
          n_stp == 28 and "28 optional model fields" in conf, f"services.yaml: {n_stp}")
    check("C2", "docs/configuration.md:548", ["P2"], "simulate_plan has 11 optional fields",
          n_sim == 11 and "11 optional comfort fields" in conf, f"services.yaml: {n_sim}")
    import sys
    sys.path.insert(0, str(ROOT))
    from custom_components.heatpump_optimizer import topology  # PYTHONPATH=tests/hastub supplies homeassistant
    n_ak = len(topology.ASSIGNABLE_KEYS)
    listed = re.search(r"one of\s+the (\d+) assignable configuration keys \(([^)]*)\)", conf, re.S)
    n_listed = len(re.findall(r"`([a-z_]+)`", listed.group(2))) if listed else -1
    check("C3", "docs/configuration.md:608", ["P2"], "21 assignable keys, all listed",
          listed is not None and int(listed.group(1)) == n_ak == n_listed, f"topology.ASSIGNABLE_KEYS: {n_ak}; doc says {listed.group(1) if listed else '?'} and lists {n_listed}")

    d_set = literal(module_assign(PKG / "const.py", "DEFAULT_ECL110_DISPLACE_SET_TOPIC"))
    d_cmd = literal(module_assign(PKG / "const.py", "DEFAULT_ECL110_COMMAND_TOPIC"))
    coord = read("custom_components/heatpump_optimizer/coordinator.py")
    publishes_each_cycle = 'await self.async_publish_current_action(reason="scheduled_update")' in coord
    early_return = "if not self._ecl110_displace_set_topic and not self._ecl110_command_topic:" in coord
    conf_leave_blank = "Leave blank if you do not have" in conf
    conf_sensible = "default sensibly when absent" in conf
    ecl_clear = "clear the set topic and the legacy command topic" in ecl and "every cycle attempts a publish and logs the failure" in ecl
    check("E1", "docs/configuration.md:457,70 vs docs/ecl110.md:79", ["P1", "P2"],
          "a non-ECL110 install can 'leave blank'/'defaults sensibly when absent' the ECL110 topics",
          not (d_set and d_cmd and publishes_each_cycle and early_return and (conf_leave_blank or conf_sensible)),
          f"defaults are {d_set!r} and {d_cmd!r} (non-empty); coordinator publishes every cycle unless BOTH are empty; "
          f"configuration.md says leave blank ({conf_leave_blank}) / default sensibly ({conf_sensible}); ecl110.md says clear them or the failure is logged every cycle ({ecl_clear})")

    cf = read("custom_components/heatpump_optimizer/config_flow.py")
    m = re.search(r"_select\(\[([^\]]*)\],\s*\"peak_window\"\)", cf)
    opts = re.findall(r"\"(\d+)\"", m.group(1)) if m else []
    check("C4", "docs/configuration.md:287", ["P2"], "Measurement window offers 15 minutes / 1 hour",
          opts == ["15", "60"] and "15 minutes / 1 hour" in conf, f"config_flow selector options: {opts}")
    check("C5", "docs/how-it-works.md:746", ["P2"],
          "'90- and 120-minute tariffs meter correctly' -- a window the reader can configure",
          not ("90- and 120-minute" in hiw and set(opts) == {"15", "60"} and "peak_tariff_window" not in sv["set_thermal_parameters"]["fields"]),
          f"how-it-works names 90/120-minute windows; the UI offers {opts} and set_thermal_parameters has no window field")

    n_throttle_uses = len(re.findall(r"throttling", conf))
    # a definition names which valve modes count as throttling in the same sentence
    dm = re.search(r"[^.\n]*throttling[^.\n]*(?:Set by hand|Read from a sensor|Commanded by the optimizer|any (?:valve )?mode other than|every mode except|means a valve)[^.\n]*", conf + hiw + readme + card_doc, re.I)
    defined = bool(dm)
    check("C6", "docs/configuration.md:355,482-528", ["P1", "P2"],
          "'throttling valve' is defined for the reader somewhere in the docs",
          defined or n_throttle_uses == 0, f"'throttling' used {n_throttle_uses} times in configuration.md; definition sentence found: {dm.group(0).strip()[:120] if dm else None}; mixing_valve.py:THROTTLING_MODES defines it in code")

    # ---------------------------------------------------------------- README vs const/sensor
    mp = literal(module_assign(PKG / "const.py", "MANUAL_PLAN_WINDOW_HOURS"))
    check("M1", "README.md:120,400", ["P1"], "manual plan pins for up to 20 hours",
          mp == 20 and "up to 20 hours" in readme, f"MANUAL_PLAN_WINDOW_HOURS={mp}")
    n_disabled = read("custom_components/heatpump_optimizer/sensor.py").count("entity_registry_enabled_default = False")
    check("M2", "README.md:255", ["P1"], "six sensors disabled by default",
          n_disabled == 6 and "Six sensors are disabled by default" in readme, f"sensor.py: {n_disabled}")
    rows = table_rows(readme, "### Sensors (55 total)")
    check("M3", "README.md:262", ["P1"], "the sensor table has 55 rows", rows == 55, f"rows: {rows}")
    m = re.search(r"### Sensors \((\d+) total\)", readme)
    m_arch = re.search(r"(\d+) entities<br/>(\d+) sensors", arch)
    check("M4", "README.md:53,262 docs/architecture.md:35", ["P1"], "README and architecture agree on 65 entities / 55 sensors",
          m is not None and m_arch is not None and m.group(1) == m_arch.group(2) == "55" and "65 entities" in readme, "test-pinned by tests/entities.py (for D6)")

    # ---------------------------------------------------------------- dashboard-card.md vs the card
    vw = re.search(r"const VIEW_W = (\d+)", card_src)
    vh = re.search(r"const VIEW_H = (\d+)", card_src)
    check("D1", "docs/dashboard-card.md:153", ["P1"], "chart drawn in a fixed 900x380 coordinate system",
          vw and vh and f"{vw.group(1)}x{vh.group(1)}" in card_doc, f"card: {vw.group(1) if vw else '?'}x{vh.group(1) if vh else '?'}")
    check("D2", "docs/dashboard-card.md:461,510", ["P1"], "hours accepted 1..168",
          "hours > 168" in card_src and "168" in card_doc, "card validates hours > 168")
    i = card_src.index("const STRINGS = {")
    en_start = card_src.index("en: {", i)
    sv_start = card_src.index("sv: {", i)
    en_keys = re.findall(r"^\s{4}\"([^\"]+)\":", card_src[en_start:sv_start], re.M)
    sv_end = card_src.index("\n  },", sv_start)
    sv_keys = re.findall(r"^\s{4}\"([^\"]+)\":", card_src[sv_start:sv_end], re.M)
    missing_sv = sorted(set(en_keys) - set(sv_keys))
    check("D3", "docs/dashboard-card.md:109", ["P1"], "about 200 keys, no Swedish entry missing",
          150 <= len(en_keys) <= 260 and not missing_sv, f"en keys: {len(en_keys)}, sv keys: {len(sv_keys)}, missing in sv: {missing_sv[:5]}")
    cv = re.search(r"const CARD_VERSION = \"([^\"]+)\"", card_src)
    check("D4", "docs/dashboard-card.md:432", ["P1"], "the console example 'v4.3.0' is presented as an example, not the current card version (info)",
          True, f"CARD_VERSION={cv.group(1) if cv else '?'}, integration VERSION={version}; the paragraph says the card version is often lower and to compare with the release notes (release notes absent from the export)")

    # ---------------------------------------------------------------- editing artefacts and stale status
    long_lines = [k + 1 for k, l in enumerate(hiw.split("\n")) if len(l) > 100 and not l.startswith(("|", "```", "[", "-", " ", "http"))]
    check("H1", "docs/how-it-works.md:1189", ["P2"], "prose is wrapped like the rest of the document (an unwrapped 134-char line marks an unfinished edit)",
          not long_lines, f"unwrapped prose lines: {long_lines}")
    garbled = "may move within follow" in hiw
    check("H2", "docs/how-it-works.md:564", ["P2"], "the buffer-tank cooling paragraph parses ('the range learning may move within follow the tank's surface area')",
          not garbled, "sentence present" if garbled else "not present")
    status = readme[readme.index("## Project status"): readme.index("## Documentation")]
    cited = [tuple(int(x) for x in v.split(".")) for v in re.findall(r"v(\d+\.\d+\.\d+)", status)]
    cur = tuple(int(x) for x in version.split("."))
    check("S1", "README.md:608-617", ["P1"], "'Project status' describes the current release line",
          max(cited) >= (cur[0], 0, 0) if cited else False, f"newest release named: v{'.'.join(map(str, max(cited))) if cited else '?'}; VERSION={version}; also links docs/backlog.md (absent from the export)")

    # ---------------------------------------------------------------- doc-doc wording
    a = "simulated always-on thermostat" in disclaimer
    b = "simulated conventional thermostat following the same comfort schedule" in readme
    check("W1", "README.md:271 vs DISCLAIMER.md:72", ["P1"], "the savings baseline is described the same way in README and DISCLAIMER (info: wording only, not counted)",
          True, f"same wording: {not (a and b)}; README: conventional thermostat following the same comfort schedule (only the DHW half always-on); DISCLAIMER: simulated always-on thermostat (for D6)")

    # ---------------------------------------------------------------- ecl110.md vs code (met on the way, for D6)
    opt = read("custom_components/heatpump_optimizer/optimizer.py")
    check("E2", "docs/ecl110.md:17", ["P2"], "ON when a circuit clears half the modulation floor, at least 0.1 kW",
          "on_threshold = max(0.1, p.min_electrical_power * 0.5)" in opt, "optimizer._power_to_heat_pump_schedule")
    n_ecl_rows = table_rows(ecl, "## Options")
    n_conf_ecl_rows = table_rows(conf, "### Heat curve control (ECL110)")
    check("E3", "docs/ecl110.md:86", ["P2"], "all eight ECL110 settings, same set on both pages",
          n_ecl_rows == 8 == n_conf_ecl_rows, f"ecl110.md rows: {n_ecl_rows}; configuration.md rows: {n_conf_ecl_rows}")

    # ---------------------------------------------------------------- heading structure
    jumps = []
    for d in docs:
        depth = 0
        fence = False
        for k, line in enumerate(d.read_text(encoding="utf-8").split("\n"), 1):
            if line.strip().startswith("```"):
                fence = not fence
                continue
            if fence:
                continue
            m = re.match(r"^(#{1,6})\s", line)
            if m:
                n = len(m.group(1))
                if n > depth + 1:
                    jumps.append(f"{d.relative_to(ROOT)}:{k} h{depth}->h{n}")
                depth = n
    check("ST1", jumps[0].split(":")[0] + ":" + jumps[0].split(":")[1] if jumps else "all documents", [],
          "heading levels never skip (structure only, no path)",
          not jumps, f"skips: {jumps}" if jumps else "none")

    # ---------------------------------------------------------------- report
    print("CHECKS:")
    for c in CHECKS:
        print(f"  {'ok  ' if c['ok'] else 'FAIL'} {c['id']:3s} [{','.join(c['paths'])}] {c['doc']}\n         claim: {c['claim']}\n         tree:  {c['detail']}")
    failed = [c for c in CHECKS if not c["ok"]]
    per_path = {p: sum(1 for c in failed if p in c["paths"]) for p in ("P1", "P2", "P3")}
    per_doc = {}
    for c in failed:
        d = c["doc"].split(":")[0].split(" ")[0]
        per_doc[d] = per_doc.get(d, 0) + 1
    print()
    print(f"RESULT doc_fact_checks_total={len(CHECKS)} count")
    print(f"RESULT doc_fact_checks_failed={len(failed)} count")
    for d, n in sorted(per_doc.items()):
        print(f"RESULT failed_in[{d}]={n} count")
    print(f"RESULT unreachable_docs_from_readme={len(unreachable)} count")
    ids = {c["id"] for c in failed}
    print(f"RESULT tests_readme_drift={len(ids & {'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'})} count")
    print(f"RESULT ecl110_guidance_contradiction={len(ids & {'E1'})} count")
    print(f"RESULT content_defects_user_docs={len(ids & {'H1', 'H2', 'S1', 'C6', 'ST1'})} count")
    print(f"RESULT dead_ends_new_user={per_path['P1']} count")
    print(f"RESULT dead_ends_feature={per_path['P2']} count")
    print(f"RESULT dead_ends_developer={per_path['P3']} count")
    footer(t_proc0, t_thr0)


if __name__ == "__main__":
    main()
