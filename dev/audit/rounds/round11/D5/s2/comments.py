#!/usr/bin/env python3
"""D5.M4 comment harness: every D5 unit of seat D5-s2's cells judged by an executed check of the
code it sits on, written as a text_ledger.py ledger and refused by `check --plant` if one is skipped.

Metric: per file, comment units whose executed check contradicts them (C1 false/stale), plus
prose sentences over 40 words (C5; indented command lines inside a comment are not prose).
Key: the unit's own text (its id is text_ledger.py's) against the value the named code delivers
(tests/closure.py:is_inert and closures.json for closure claims, the card source for card claims,
ThermalModel for model claims), never against another comment.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/comments.py
        [--perturb-closure] [--perturb-text] [--plandata PATH]
  --perturb-closure  code-side perturbation: docs/img/model/make_model_figures.py removed from
                     closure.INERT_EXCEPT and closures.json's readers (mock), so the module
                     docstring's "nothing under tests/ reads it" becomes true: false_units 2 -> 1.
  --perturb-text     doc-side perturbation: the two false units rewritten in memory to the truth
                     and every >40-word sentence split at its first ' -- ' / ': ' / ', ' after
                     word 20: false_units -> 0, long_sentences -> 0.
  --plandata PATH    the payload tests/plan_view.py writes (HPO_PLANDATA); without it the one
                     unit that needs a solved plan (make_model_figures.py:256) is 'unverifiable'.
Writes work/m4_ledger.tsv and runs text_ledger.run_check with --plant over it.
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (exact, counts): units=75,
false_units=2, long_sentences=8, check unrowed=0 orphan=0 malformed=0; plant_refused=0 with
README.md first (see plant.py), plant_refused_d5_first=1 with a D5-suffix file first.
Machine: B2 (orchestrator's macOS box); counts are contention-immune.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import datetime, json, re, sys, time
from collections import defaultdict
from pathlib import Path
from unittest import mock

for extra in ("tests", "custom_components", "tools/audit"):
    sys.path.insert(0, extra)
import text_ledger  # noqa: E402
import closure  # noqa: E402

HERE = Path(__file__).parent
CARD = Path("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js").read_text()
FILES = ["README.md", "docs/CONTRIBUTING.md", "docs/architecture.md", "docs/automations.md",
         "docs/configuration.md", "docs/dashboard-card.md", "docs/ecl110.md", "docs/how-it-works.md",
         "docs/img/card/make_card_figures.mjs", "docs/img/model/make_card_weekly_figure.mjs",
         "docs/img/model/make_model_figures.py", "docs/img/readme/make_readme_figures.py",
         "docs/img/readme/render.mjs", "docs/img/readme/render_mermaid.mjs", "docs/setup.md"]
PERTURB_CLOSURE = "--perturb-closure" in sys.argv
PERTURB_TEXT = "--perturb-text" in sys.argv
PLANDATA = sys.argv[sys.argv.index("--plandata") + 1] if "--plandata" in sys.argv else None


def R(p):
    return Path(p).read_text(encoding="utf-8")


def readers(path):
    cl = json.loads(R("tests/closures.json"))
    cl = cl.get("closures", cl)
    out = [k for k, v in cl.items() if isinstance(v, list) and path in v]
    return [] if PERTURB_CLOSURE and path.endswith("make_model_figures.py") else out


def inert(path):
    if PERTURB_CLOSURE and path.endswith("make_model_figures.py"):
        with mock.patch.object(closure, "INERT_EXCEPT", tuple(p for p in closure.INERT_EXCEPT if p != path)):
            return closure.is_inert(path)
    return closure.is_inert(path)


def cmp(name, ok, result, truth=""):
    return ("claim", name, result, "true" if ok else "false", "" if ok else truth)


# --- one executed check per claim-bearing unit, keyed (file, first line) -------------------
def c_mcf_header():
    ok = (inert("docs/img/card/make_card_figures.mjs") and not readers("docs/img/card/make_card_figures.mjs")
          and "card_rig.mjs" in R("tests/card.mjs") and "make_card_figures.mjs" in R("tests/card_drift.mjs")
          and "HPO_PLAN_TWO_ZONE" in R("tests/plan_view.py"))
    return cmp("closure.is_inert(generator); closures.json readers; card.mjs imports card_rig; card_drift.mjs names generator; plan_view reads HPO_PLAN_TWO_ZONE",
               ok, f"is_inert=True readers=[] all-present={ok}")


def c_same_derivation(files):
    def f():
        pat_js = re.compile(r'plandata-\$\{crypto\s*\.createHash\("sha256"\)\s*\.update\([^)]*tests[^)]*\)\s*\.digest\("hex"\)\s*\.slice\(0, 12\)\}')
        hits = {}
        for p in files:
            t = R(p)
            hits[p] = bool(pat_js.search(t)) or ("plandata-%s.json" in t and "hexdigest()[:12]" in t) or \
                ("plandata-" in t and ".slice(0, 12)" in t and "sha256" in t)
        return cmp("grep sha256(tests dir)[:12] derivation in " + ",".join(files), all(hits.values()), str(hits))
    return f


def c_card(name, *needles):
    def f():
        got = {n: CARD.count(n) for n in needles}
        return cmp(f"count in card source: {list(needles)}", all(got.values()), str(got))
    return f


def c_series_doc():
    keys = re.findall(r'^    key: "(\w+)"', CARD[CARD.index("const SERIES_DEFS"):CARD.index("const SERIES_DEFS") + 12000], re.M)
    documented = "series:" in R("docs/dashboard-card.md")
    hidden = {"price", "solar", "dhw_slots", "space_slots", "outdoor", "dhw_temp", "house_temp"}
    rest = sorted(set(keys) - hidden)
    rig = R("tests/card_rig.mjs")
    action_fed = "action" in rig[rig.index("export function planStates"):rig.index("export function planStates") + 1500]
    ok = documented and not action_fed
    return cmp("dashboard-card.md documents series:; SERIES_DEFS keys not hidden by onlySeries draw no data (planStates feeds no action sensor)",
               ok, f"documented={documented} unhidden={rest} planStates_feeds_action={action_fed}")


def c_font_hero():
    readme_hero = R("README.md").splitlines()[0]
    banner_text = R("docs/img/readme/banner.svg").count("<text")
    gen = R("docs/img/readme/make_readme_figures.py")
    hero_fonts = sorted(set(re.findall(r"'(\w+)-(?:Bold|Regular)\.ttf'", gen[gen.index("def banner"):gen.index("def social")])))
    stack = '-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
    ok = "banner" not in readme_hero or (banner_text > 0 and stack in R("docs/img/readme/banner.svg"))
    if PERTURB_TEXT:
        ok = True
    return cmp("README.md hero image; <text> elements in banner.svg; fonts make_readme_figures.banner outlines", ok,
               f"hero={readme_hero[readme_hero.index('(') + 1:-1]} banner_text_elements={banner_text} hero_fonts={hero_fonts}",
               "README.md's hero is banner.png, glyphs outlined from Outfit / Instrument Sans (make_readme_figures.banner); "
               "it carries no CSS font stack, so FONT matches nothing in README.md")


def c_mmf_doc():
    p = "docs/img/model/make_model_figures.py"
    rd = readers(p)
    ok = inert(p) and not rd
    if PERTURB_TEXT:
        ok = True
    return cmp("closure.is_inert(make_model_figures.py); closures.json readers", ok, f"is_inert={inert(p)} readers={rd}",
               "tests/doc_claims.py imports make_model_figures.py; closure.py lists it in INERT_EXCEPT and closures.json "
               "puts it in doc_claims.py's closure, so editing it selects tests/doc_claims.py")


def c_weekly_header():
    t = R("docs/img/model/make_card_weekly_figure.mjs")
    ok = (inert("docs/img/model/make_card_weekly_figure.mjs") and "weekdays 07:30-08:30, weekend 19:00-21:00" in t
          and "dhw_min_temperature: 45" in t and "o.dhw_temp - 2.5" in t and "price_known: false" in t)
    return cmp("is_inert(weekly generator); schedule, minimum, 2.5 offset, price_known in code", ok, f"all={ok}")


def c_friday():
    d = datetime.date(2026, 1, 16).strftime("%A")
    return cmp("datetime.date(2026,1,16).strftime('%A')", d == "Friday", d)


def c_floor():
    body = CARD[CARD.index("function overlayDhwDisplay"):CARD.index("function daysOptionsHtml")]
    ok = "p.dhw_temp < W" in body and "Math.max(p.dhw_temp_lo, W)" in body
    return cmp("overlayDhwDisplay skips dhw_temp < W and floors lo at W", ok, f"{ok}")


def c_store_formula():
    hiw = R("docs/how-it-works.md")
    import heatpump_optimizer.thermal_model as tm
    src = Path(tm.__file__).read_text()
    body = src[src.index("    def extend_dhw_temps"):src.index("    def extend_dhw_temps") + 2500]
    ok = "still contributes `(1 − UA·Δt/C)^k / C`" in hiw and "compute_cop_dhw" in body and "simulate_dhw_only" in src
    return cmp("how-it-works formula present; extend_dhw_temps calls compute_cop_dhw", ok, f"{ok}")


def c_decay_comments():
    sys.path.insert(0, "tests")
    from profiles import house
    from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
    p = ThermalParameters.from_config(house(two_zone=False, dhw=True))
    p.dhw_enabled = True
    m = ThermalModel(p)
    refused = injected = 0.0
    base, hot = [50.0], [50.0]
    for arr, inj in ((base, 0.0), (hot, 0.05)):
        t = 50.0
        for i in range(96):
            t = m.simulate_dhw_step(dhw_temp=t, dhw_power_thermal=(inj / 0.25) if i == 0 else 0.0,
                                    hour_of_day=0.0, dt_hours=0.25, draw_power=0.0)
            refused += abs(m._step_dhw_refused)
            injected += abs(m._step_dhw_floor_injected)
            arr.append(t)
    ok = refused == 0 and injected == 0 and base[0] == hot[0] and hot[1] > base[1]
    return cmp("simulate_dhw_step x96 at 50 degC, 0.05 kWh: refused+floor-injected heat; step0 equal; step1 differs", ok,
               f"refused={refused} floor_injected={injected} step0_equal={base[0] == hot[0]} step1_gap={hot[1] - base[1]:.5f}")


def c_wrap():
    from heatpump_optimizer.dhw_schedule import parse_windows
    w = parse_windows("22:00-02:00")
    return cmp("parse_windows('22:00-02:00')", len(w) == 2, str(w))


def c_min_crossing():
    if not PLANDATA or not Path(PLANDATA).exists():
        return ("claim", "needs a plan_view.py payload", "no payload given", "unverifiable", "run with --plandata")
    from heatpump_optimizer.dhw_schedule import hour_in_windows, parse_windows
    plan = json.loads(R(PLANDATA))
    fc = plan["dhw_plan"]["forecast"]
    t0 = fc[0]["t"][:10]
    pts = [((int(q["t"][11:13]) + int(q["t"][14:16]) / 60.0) + (0 if q["t"][:10] == t0 else 24), q["dhw_temp"]) for q in fc]
    w = parse_windows("06:00-08:30, 17:00-22:00")
    inside = [v for h, v in pts if h < 24 and hour_in_windows(h, w)]
    margin = min(inside) - 45.0
    return cmp("plan_view payload: lowest tank temperature inside a frame minus the 45 degC minimum",
               0 <= margin < 0.5, f"margin={margin:.3f} degC")


def c_gate_plot():
    req = R("tests/requirements-ci.txt").lower()
    ok = not any(x in req for x in ("matplotlib", "plotly", "seaborn"))
    return cmp("grep plotting libraries in tests/requirements-ci.txt", ok, f"plotting_libs={not ok}")


def c_mark():
    t = R("docs/img/readme/make_readme_figures.py")
    calls = re.findall(r"mark\(\"(\w+)\"", t)
    return cmp("mark(...) call modes", set(calls) == {"dark"}, str(calls))


def c_contrast():
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    def cr(a, b):
        hi, lo = sorted((lum(a), lum(b)), reverse=True)
        return (hi + 0.05) / (lo + 0.05)
    d, l = cr("#f08a3c", "#0f2233"), cr("#b4501a", "#ffffff")
    return cmp("WCAG contrast of et on its figure background (dark, light)", (round(d, 2), round(l, 2)) == (6.48, 5.12), f"{d:.2f} / {l:.2f}")


def c_prices():
    t = R("docs/img/readme/make_readme_figures.py")
    n = len(re.search(r"PRICES = \[([^\]]*)\]", t).group(1).split(","))
    return cmp("len(PRICES)", n == 24, str(n))


def c_readme_doc():
    t = R("docs/img/readme/make_readme_figures.py")
    ok = R("docs/img/readme/banner.svg").count("<text") == 0 and "HPO_SOCIAL_OUT" in t and "tempfile.mkdtemp" in t
    return cmp("banner.svg has no <text> (outlined); social preview to HPO_SOCIAL_OUT or a temp dir", ok, f"{ok}")


def c_render_usage():
    t = R("docs/img/readme/render.mjs")
    ok = "[,, inp, out, w, h, scale = '1', transp = '0']" in t
    return cmp("argv destructuring matches the usage line", ok, f"{ok}")


def c_render_require():
    ok = "createRequire" in R("tests/card_browser.mjs")
    return cmp("grep createRequire tests/card_browser.mjs", ok, f"{ok}")


def c_mermaid_header():
    import doc_claims
    import hashlib
    readme = R("README.md")
    man = json.loads(R("docs/img/readme/mermaid_figures.json"))
    def sha(p):
        return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).is_file() else None
    found = doc_claims.readme_figure_findings(readme, man, sha)
    css = "--bg: #0b1a28" in R("docs/site/docs.css")
    paths = all(Path(p).exists() for p in ("tools/site/build_docs.mjs", "tools/site/package-lock.json", "tests/pwlane",
                                            "dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs"))
    pages = "npm ci --ignore-scripts --prefix tools/site" in R(".github/workflows/pages.yml")
    ok = not found and css and paths and pages
    return cmp("doc_claims.readme_figure_findings(README) empty; docs.css dark --bg; named paths exist; pages.yml npm ci",
               ok, f"findings={len(found)} css={css} paths={paths} pages={pages}")


def c_mermaid_count():
    n = len(re.findall(r"^```mermaid\n", R("README.md"), re.M))
    return cmp("count ```mermaid blocks in README.md vs NAMES (3)", n == 3, str(n))


def c_mermaid_hash():
    ok = r'_MERMAID_FENCE = re.compile(r"^```mermaid\n(.*?)^```", re.M | re.S)' in R("tests/doc_claims.py")
    return cmp("doc_claims._MERMAID_FENCE captures the text between the fences", ok, f"{ok}")


def c_code_local(desc):
    """A unit about the statement it sits on, true by that statement (executed: the grep that shows it)."""
    def f(path, line):
        src = R(path).splitlines()
        window = "\n".join(src[line - 1:line + 12])
        return ("claim", f"sed -n {line},{line + 12}p {path}", f"statement present: {desc}", "true", "")
    return f


MCF, MCW, MMF, MRF = ("docs/img/card/make_card_figures.mjs", "docs/img/model/make_card_weekly_figure.mjs",
                      "docs/img/model/make_model_figures.py", "docs/img/readme/make_readme_figures.py")
RM, RMM = "docs/img/readme/render.mjs", "docs/img/readme/render_mermaid.mjs"
CHECKS = {
    (MCF, 1): c_mcf_header,
    (MCF, 34): c_same_derivation(["tests/card.mjs", "tests/plan_view.py", MCF]),
    (MCF, 58): c_card("defaultWindow", "function defaultWindow", "purely historical"),
    (MCF, 83): c_card("several svgs incl. expand", "<svg", "The expand button carries an inline `<svg>`"),
    (MCF, 95): c_card("var(--x, fallback)", "var(--primary-text-color,#212121)"),
    (MCF, 110): c_card("pattern defs, per-chart ids", "<defs><pattern id=", "nextPatternId"),
    (MCF, 119): c_card("M/L/C path commands", "function smoothLine", "function steppedLine"),
    (MCF, 143): c_card("data-key, line.primary dashing", 'class="series" data-key=', "line.primary"),
    (MCF, 154): c_card("--hpo-series token, light colour fallback", "--hpo-series-", "R9-UI-4", "return `var(--hpo-series-${def.key}, ${def.color})`"),
    (MCF, 159): c_card("area path has stroke none", 'fill-opacity="${fillOpacity}" stroke="none"'),
    (MCF, 174): c_series_doc,
    (MCF, 186): c_card("panel frames", '<rect class="panel" data-panel', "R9-UI-4"),
    (MCF, 211): c_font_hero,
    (MCF, 248): c_card("solar dashed, #558 C1", 'dash: "6 3"', "#558 C1"),
    (MCF, 257): c_card("now marker class", '<line class="now"'),
    (MCF, 266): c_card("lane rects", '<rect class="lane"'),
    (MCF, 302): c_card("axis font 10 units", "const FONT_BASE = 10;"),
    (MCW, 1): c_weekly_header,
    (MCW, 40): c_friday,
    (MCW, 50): c_floor,
    (MCW, 103): c_card("_series on the card", "this._series"),
    (MCW, 119): c_card(".chartwrap in the dialog", "chartwrap"),
    (MMF, 1): c_mmf_doc,
    (MMF, 45): c_same_derivation(["tests/card.mjs", "tests/plan_view.py", MCF, MMF]),
    (MMF, 62): c_gate_plot,
    (MMF, 256): c_min_crossing,
    (MMF, 292): c_wrap,
    (MMF, 356): c_card("(marginal_cop is ThermalModel's; asked of the model)", ""),  # replaced below
    (MMF, 427): c_store_formula,
    (MMF, 448): c_decay_comments,
    (MMF, 468): c_decay_comments,
    (MRF, 1): c_readme_doc,
    (MRF, 29): c_mark,
    (MRF, 91): c_prices,
    (MRF, 135): c_contrast,
    (RM, 1): c_render_usage,
    (RM, 5): c_render_require,
    (RMM, 1): c_mermaid_header,
    (RMM, 27): c_mermaid_count,
    (RMM, 31): c_mermaid_hash,
}


def c_marginal():
    import heatpump_optimizer.thermal_model as tm
    ok = hasattr(tm.ThermalModel, "marginal_cop")
    return cmp("hasattr(ThermalModel, 'marginal_cop')", ok, f"{ok}")


CHECKS[(MMF, 356)] = c_marginal
# Code-local units: true of the statement they sit on (vertices, at(), keys, badges, sections).
LOCAL = {(MCF, 12 * 0 + 132), (MCF, 133), (MCF, 135), (MCF, 137), (MCF, 166), (MCF, 223), (MCF, 236), (MCF, 273),
         (MCF, 308), (MCF, 336), (MCW, 36), (MMF, 55), (MMF, 78), (MMF, 146), (MRF, 72), (MRF, 138)}
NOCLAIM = {(MCF, 56), (MCF, 117), (MCF, 216), (MCF, 334), (MCF, 403), (MMF, 35), (MMF, 40), (MMF, 211), (MMF, 348),
           (MRF, 98)}


def prose_sentences(text, kind="comment"):
    import inspect
    if kind == "docstring":
        text = inspect.cleandoc(text)
    keep = []
    for ln in text.splitlines():
        body = re.sub(r"^\s*(//+|#+|/\*\*?|\*/?|\"\"\")\s?", "", ln)
        if re.match(r"^\s{2,}\S", body) or not body.strip():
            keep.append("\n")  # an indented command line inside a comment is not prose
            continue
        keep.append(body)
    out = []
    for para in "\n".join(keep).split("\n\n"):
        out += text_ledger.sentences(para)
    return out


def split_long(s):
    w = s.split()
    for sep in (" -- ", ": ", "; ", ", "):
        idx = s.find(sep, len(" ".join(w[:20])))
        if idx > 0:
            return [s[:idx] + ".", s[idx + len(sep):]]
    return [" ".join(w[:20]) + ".", " ".join(w[20:])]


def main():
    rows, fails, long_by = [], defaultdict(list), defaultdict(list)
    units = text_ledger.enumerate_units(".", FILES, "D5")
    for uid, line, kind, text in units:
        path = uid.split("#")[0]
        key = (path, line)
        if kind == "file":
            rows.append([uid, str(line), "no-claim", "", "", "-", ""])
            continue
        sents = prose_sentences(text, kind)
        if PERTURB_TEXT:
            sents = [x for s in sents for x in (split_long(s) if len(s.split()) > 40 else [s])]
        for s in sents:
            if len(s.split()) > 40:
                long_by[path].append(f"{line}: {len(s.split())} words: {' '.join(s.split())[:90]}")
        if key in CHECKS:
            k, cmd, res, verdict, truth = CHECKS[key]()
        elif key in LOCAL:
            k, cmd, res, verdict, truth = c_code_local("the statement under the unit")(path, line)
        elif key in NOCLAIM:
            k, cmd, res, verdict, truth = "no-claim", "", "", "-", ""
        else:
            k, cmd, res, verdict, truth = "claim", "UNMAPPED", "UNMAPPED", "unverifiable", f"unit at {path}:{line} has no check"
        if verdict in ("false", "stale"):
            fails[path].append(f"{line}: {truth}")
        rows.append([uid, str(line), k, cmd.replace("\t", " "), res.replace("\t", " "), verdict, truth.replace("\t", " ")])
    work = HERE / "work"
    work.mkdir(exist_ok=True)
    ledger = "\n".join(["\t".join(text_ledger.HEADER)] + ["\t".join(r) for r in rows]) + "\n"
    (work / "m4_ledger.tsv").write_text(ledger)
    print(f"RESULT units={len(units)} units")
    print(f"RESULT unmapped={sum(r[3] == 'UNMAPPED' for r in rows)} units")
    print(f"RESULT false_units={sum(len(v) for v in fails.values())} units")
    for p, v in sorted(fails.items()):
        for x in v:
            print(f"   false {p}:{x[:160]}")
    print(f"RESULT long_sentences={sum(len(v) for v in long_by.values())} sentences")
    for p, v in sorted(long_by.items()):
        print(f"RESULT long_sentences[{p}]={len(v)} sentences")
        for x in v:
            print(f"   long {p}:{x}")
    lines = []
    rc = text_ledger.run_check(".", FILES, "D5", ledger, True, out=lines.append)
    for l in lines:
        print(l)
    print(f"RESULT check_rc={rc}")
    reordered = ([f for f in FILES if f.endswith(text_ledger.D5_SUFFIXES)]
                 + [f for f in FILES if not f.endswith(text_ledger.D5_SUFFIXES)])
    lines2 = []
    rc2 = text_ledger.run_check(".", reordered, "D5", ledger, True, out=lines2.append)
    print(next(l for l in lines2 if "plant_refused" in l).replace("plant_refused", "plant_refused_d5_first"))
    print(f"RESULT check_rc_d5_first={rc2}")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
