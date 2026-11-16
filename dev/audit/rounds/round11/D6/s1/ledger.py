#!/usr/bin/env python3
"""D6-s1 round 11: row every text unit of the seat's cells, with one executed check per checkable claim.

Metric: per file, the count of ledger rows whose executed check contradicts the tree (verdict false).
Key: the value the production seam delivers -- an option row's default/selector bounds from
config_flow._OPTION_FIELDS (via _page_schema-equivalent widget configs), a services.yaml key, a
strings.json entity translation key composed by entity.py's object-id rule, a tracked path, an
identifier present in production source, a link target resolved by tools/site/build_docs.mjs and
dev/audit/harnesses/d6_page_anchors.py, an external URL answered by HEAD.

RUN (export root, no cd):
    PYTHONUTF8=1 PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s1/ledger.py \
        [--tree TREE.txt] [--no-net] [--out dev/audit/rounds/round11/D6/s1/ledger.tsv]
  TREE.txt = the baseline's tracked paths (git ls-tree -r --name-only <sha>); without it the
  export's own files are used (the finder wall removed some registers, so a few dev/ paths read missing).
Expected: RESULT false_rows_total=<n> exact on the same tree; RESULT units equals
  `tools/audit/text_ledger.py units --dim D6 --seat D6-s1 ...` line count (3970 at baseline).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export /home/user/audit-r11-baseline, box B1).
Perturbation: `--perturb-default KEY=VALUE` swaps one _OPTION_FIELDS row's default in memory
  (e.g. comfort_weight=6): the configuration.md/README rows citing that default flip true->false,
  false_rows_total goes up.
Then: tools/audit/text_ledger.py check --dim D6 LEDGER --root . FILES... (step M3) reads the ledger.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, collections, json, re, subprocess, sys, tempfile, time, urllib.request, ssl
from pathlib import Path

ROOT = Path(".").resolve()
sys.path[:0] = [str(ROOT / "custom_components"), str(ROOT / "tests"), str(ROOT / "tests/hastub")]
FILES = ["DISCLAIMER.md", "README.md", "RELEASE_NOTES.md", "ROADMAP.md", "docs/architecture.md",
         "docs/automations.md", "docs/configuration.md", "docs/dashboard-card.md", "docs/ecl110.md",
         "docs/how-it-works.md", "docs/index.html", "docs/setup.md", "docs/site/docs.css",
         "tools/site/build_docs.mjs"]
HERE = Path(__file__).resolve().parent
NODE = os.environ.get("NODE", "/opt/node22/bin/node")

ap = argparse.ArgumentParser()
ap.add_argument("--tree")
ap.add_argument("--no-net", action="store_true")
ap.add_argument("--out", default=str(HERE / "ledger.tsv"))
ap.add_argument("--perturb-default", action="append", default=[])
ap.add_argument("--extra", default=str(HERE / "behaviour_rows.tsv"),
                help="rows produced by claims.py (unit id -> executed behavioural check)")
a = ap.parse_args()

t_cpu0, t_thr0 = time.process_time(), time.thread_time()

# ---------------------------------------------------------------- units
sys.path.insert(0, str(ROOT / "tools/audit"))
import text_ledger  # noqa: E402  the instrument's own enumeration, full text (its CLI truncates at 200)
units = [(uid, str(ln), kind, " ".join(t.split()) if kind != "code" else t)
         for uid, ln, kind, t in text_ledger.enumerate_units(".", FILES, "D6")]

# ---------------------------------------------------------------- facts from production
from heatpump_optimizer import config_flow as cf  # noqa: E402
from heatpump_optimizer import const  # noqa: E402

for spec in a.perturb_default:
    k, v = spec.split("=", 1)
    rows = list(cf._OPTION_FIELDS)
    for i, r in enumerate(rows):
        if r.key == k:
            rows[i] = r._replace(default=type(r.default)(float(v)) if isinstance(r.default, (int, float)) else v)
    cf._OPTION_FIELDS = tuple(rows)


def widget_cfg(w):
    c = getattr(w, "config", None)
    return dict(c) if isinstance(c, dict) else {}


OPT = collections.defaultdict(list)  # key -> [(default, min, max, step)]
for r in cf._OPTION_FIELDS:
    w = r.widget
    c = widget_cfg(w)
    OPT[r.key].append((r.default, c.get("min"), c.get("max"), c.get("step"), r.step))

STRINGS = json.loads((ROOT / "custom_components/heatpump_optimizer/strings.json").read_text())
LABEL2KEYS = collections.defaultdict(set)
for flow in ("config", "options"):
    for step, s in STRINGS[flow]["step"].items():
        blocks = [s.get("data", {})] + [sec.get("data", {}) for sec in s.get("sections", {}).values()]
        for b in blocks:
            for k, lab in b.items():
                LABEL2KEYS[lab.strip().lower()].add(k)
                LABEL2KEYS[re.sub(r"\s*\([^)]*\)\s*$", "", lab).strip().lower()].add(k)

# Wizard-side defaults: every module-level dict in config_flow keyed by setting keys with numeric values
WIZ = collections.defaultdict(set)
for _n, _v in vars(cf).items():
    if isinstance(_v, dict) and _n.isupper() or (isinstance(_v, dict) and _n.startswith("_") and _n.upper() == _n):
        for _k, _d in _v.items():
            if isinstance(_k, str) and isinstance(_d, (int, float)) and not isinstance(_d, bool):
                WIZ[_k].add(float(_d))
for _n, _v in vars(const).items():
    if _n.startswith("DEFAULT_") and isinstance(_v, (int, float)) and not isinstance(_v, bool):
        _ck = getattr(const, "CONF_" + _n[8:], None)
        if isinstance(_ck, str):
            WIZ[_ck].add(float(_v))
ENTITY_KEYS = {p: set(v) for p, v in STRINGS["entity"].items()}
SERVICES = set(re.findall(r"(?m)^([a-z_]+):", (ROOT / "custom_components/heatpump_optimizer/services.yaml").read_text()))

if a.tree:
    TREE = set(Path(a.tree).read_text().split())
else:
    TREE = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and "/._" not in "/" + str(p.relative_to(ROOT))}
TREE_DIRS = {"/".join(p.split("/")[:i]) for p in TREE for i in range(1, p.count("/") + 1)}
BASENAMES = collections.defaultdict(set)
for p in TREE:
    BASENAMES[p.rsplit("/", 1)[-1]].add(p)


def corpus(globs):
    parts = []
    for g in globs:
        for p in ROOT.glob(g):
            if p.is_file() and not p.name.startswith("._"):
                try:
                    parts.append(p.read_text(errors="replace"))
                except Exception:
                    pass
    return "\n".join(parts)


PROD = corpus(["custom_components/heatpump_optimizer/**/*.py", "custom_components/heatpump_optimizer/**/*.js",
               "custom_components/heatpump_optimizer/**/*.json", "custom_components/heatpump_optimizer/**/*.yaml",
               "blueprints/**/*.yaml", "hacs.json"])
DEV = corpus(["tests/*.py", "tests/*.mjs", "tools/**/*.py", "tools/**/*.mjs", "tools/**/*.sh", "tools/**/*.js",
              ".github/workflows/*.yml", ".claude/workflows/*.js", "dev/governance/**/*.md", "pyproject.toml"])


def ident_in(s, text):
    return re.search(r"(?<![A-Za-z0-9_])" + re.escape(s) + r"(?![A-Za-z0-9_])", text) is not None


# ---------------------------------------------------------------- atom checks
PATHLIKE = re.compile(r"^[\w.\-/*<>\[\]]+\.(py|md|mjs|js|json|yaml|yml|sh|toml|txt|zip|svg|png|html|css)$|^[\w.\-]+/[\w.\-/*]*$")
ENTITY = re.compile(r"^(sensor|binary_sensor|switch|button|climate|datetime)\.heat_pump_optimizer_([a-z0-9_]+)$")
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*(\(\))?$")


CTX = {}


def check_tick(span):
    """(verdict, result) for one backticked span, or None when it is an example/formula, not a claim atom."""
    s = span.strip()
    if not s or " " in s or not re.search(r"[A-Za-z]", s):
        return None
    m = ENTITY.match(s)
    if m:
        plat, key = m.groups()
        ok = key in ENTITY_KEYS.get(plat, set())
        return ("true" if ok else "false", f"entity {s}: translation key {key!r} {'in' if ok else 'NOT in'} strings.json entity.{plat}")
    if s.startswith(("sensor.", "switch.", "number.", "climate.", "binary_sensor.", "calendar.", "person.", "input_")) and "heat_pump_optimizer" not in s:
        return None  # a user's own entity, an example
    if s.startswith("heatpump_optimizer.") and s.split(".", 1)[1] in SERVICES:
        return ("true", f"service {s} in services.yaml")
    if s.startswith("/") and s.count("/") >= 2:
        seg, base = s.split("/")[1], s.rsplit("/", 1)[-1]
        ok = ident_in("/" + seg, PROD.replace('"/', '"/ ').replace(" ", "")) or ("/" + seg) in PROD
        okb = (not base) or base in BASENAMES
        return ("true" if ok and okb else "false", f"served path {s}: prefix /{seg} {'in' if ok else 'NOT in'} production, file {base} {'tracked' if okb else 'NOT tracked'}")
    if re.match(r"^[a-z0-9-]+(\.[a-z0-9-]+)+\.(com|io|org|net)(/|$)", s):
        host = s.split("/")[0]
        ok = host in PROD
        return ("true" if ok else "false", f"host {host} {'in' if ok else 'NOT in'} production source")
    if PATHLIKE.match(s) and ("/" in s or "." in s.rsplit("/", 1)[-1]):
        p = s.lstrip("/").rstrip("/")
        if "*" in p or "<" in p:
            return None
        if p in TREE or p in TREE_DIRS:
            return ("true", f"path {p} tracked")
        if p.rsplit("/", 1)[-1] in BASENAMES and "/" not in p:
            return ("true", f"basename {p} tracked at {sorted(BASENAMES[p])[0]}")
        suff = sorted(t for t in TREE if t.endswith("/" + p))
        if suff:
            return ("true", f"path {p} tracked as {suff[0]}")
        if "/" in p:
            if CTX.get("other_repo"):
                return ("true", f"path {p} not tracked here, as the sentence states (another repository; GitHub not read)")
            return ("false", f"path {p} not tracked at baseline")
    if s.startswith("_") and s.strip("_") and IDENT.match(s):
        frag = s.rstrip("()")
        ok = frag in PROD or ident_in(frag.strip("_"), PROD)
        return ("true" if ok else "false", f"name fragment {frag} {'in' if ok else 'NOT in'} production source (composed name)")
    if IDENT.match(s):
        name = s.rstrip("()")
        tail = name.rsplit(".", 1)[-1]
        if name in SERVICES:
            return ("true", f"service {name} in services.yaml")
        if ident_in(name, PROD) or ident_in(tail, PROD):
            return ("true", f"identifier {name} present in production source")
        if ident_in(name, DEV) or ident_in(tail, DEV):
            return ("true", f"identifier {name} present in tests/tools")
        if CTX.get("text") and re.search(r"\bnot\s+(\*\*)?`" + re.escape(s) + "`", CTX["text"]):
            return ("true", f"identifier {name} absent from production, as the sentence's negation states")
        if CTX.get("text") and re.search(r"the\s+`" + re.escape(s) + r"`\s+integration", CTX["text"]):
            return ("unverifiable", f"{name} names a third-party integration, not in this tree")
        return ("false", f"identifier {name} found nowhere in production, tests or tools")
    return None


NUM = re.compile(r"[−-]?\d+(?:[.,]\d+)?")


def num(x):
    x = re.sub(r"(?<=\d)[ \u00a0\u202f](?=\d{3}\b)", "", x.strip())
    if not re.match(r"^[~≈]?\s*[−-]?\d", x):
        return None
    m = NUM.search(x.replace("−", "-"))
    return float(m.group(0).replace(",", ".")) if m else None


def check_table_row(cells):
    """A settings-table row: label, default, range. (verdict, result) or None."""
    label = re.sub(r"[*`]", "", cells[0]).strip().lower()
    keys = LABEL2KEYS.get(label)
    if not keys or len(cells) < 3:
        return None
    dflt_doc = cells[1].strip()
    rng_doc = cells[2].strip() if len(cells) > 3 else ""
    notes = []
    verdicts = []
    for k in sorted(keys):
        for (d, mn, mx, st, step) in OPT.get(k, []):
            dn = num(dflt_doc)
            if dn is None or re.search(r"same|weekday|device|auto|empty|none|off|on\b|stored|derived|preset|from", dflt_doc.lower()):
                continue
            if isinstance(d, (int, float)) and not isinstance(d, bool):
                ok = abs(float(d) - dn) < 1e-9
                verdicts.append(ok)
                notes.append(f"{step}.{k} default={d} doc={dflt_doc!r}")
            elif WIZ.get(k):
                ok = any(abs(x - dn) < 1e-9 for x in WIZ[k])
                verdicts.append(ok)
                notes.append(f"{k} wizard/const default(s)={sorted(WIZ[k])} doc={dflt_doc!r}")
            m = re.match(r"\s*([−-]?\d+(?:\.\d+)?)\s*[–-]\s*([−-]?\d+(?:\.\d+)?)", rng_doc.replace("−", "-"))
            if m and mn is not None and mx is not None:
                lo, hi = float(m.group(1)), float(m.group(2))
                okr = abs(lo - float(mn)) < 1e-9 and abs(hi - float(mx)) < 1e-9
                verdicts.append(okr)
                notes.append(f"range {mn}-{mx} doc={rng_doc[:24]!r}")
    if not verdicts:
        return None
    return ("true" if all(verdicts) else "false", "; ".join(notes))


# ---------------------------------------------------------------- links
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)")
HREF = re.compile(r"(?i)(?:href|src)=[\"']([^\"']+)")
head_cache = {}


def head(url):
    if url in head_cache:
        return head_cache[url]
    if a.no_net:
        head_cache[url] = None
        return None
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "doc-link-check"})
        ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt") if Path("/root/.ccr/ca-bundle.crt").exists() else None
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            head_cache[url] = r.status
    except urllib.error.HTTPError as e:
        head_cache[url] = e.code
    except Exception as e:  # noqa: BLE001
        head_cache[url] = f"ERR {type(e).__name__}"
    return head_cache[url]


GH = re.compile(r"^https://(?:github\.com/tvofi/heatpump_optimizer/(?:blob|tree)/main/|raw\.githubusercontent\.com/tvofi/heatpump_optimizer/main/)(.+)$")


def check_link(src_file, target):
    target = target.replace("&amp;", "&")
    if target.startswith("mailto:"):
        return None
    if target.startswith("http"):
        m = GH.match(target)
        if m:
            p = m.group(1).split("#")[0].rstrip("/")
            ok = p in TREE or p in TREE_DIRS
            return ("true" if ok else "false", f"repo URL -> {p} {'tracked' if ok else 'NOT tracked'} (GitHub not read, COMMON.md)")
        if "github.com" in target:
            return ("unverifiable", "GitHub URL outside the tree: not read (COMMON.md bars reading GitHub)")
        st = head(target)
        if st is None:
            return ("unverifiable", "HEAD not run (--no-net)")
        return ("true" if st == 200 else "false", f"HEAD {target} -> {st}")
    if "${" in target:
        return None  # a JavaScript template, not a link
    if target.startswith("#"):
        return None  # anchors: build_docs / d6_page_anchors rows, file level
    p = target.split("#")[0]
    if not p:
        return None
    if src_file.endswith(".mjs"):
        return None  # build_docs.mjs builds hrefs for the OUT tree; the build run checks them
    base = Path(src_file).parent
    rp = os.path.normpath(str(base / p)) if not p.startswith("/") else p.lstrip("/")
    ok = rp in TREE or rp in TREE_DIRS
    return ("true" if ok else "false", f"relative link {target} -> {rp} {'tracked' if ok else 'NOT tracked'}")


# site build + anchors: one executed run, its FAIL lines keyed by file
tmp = Path(tempfile.mkdtemp(prefix="d6s1-"))
os.environ["HPO_PLANDATA"] = str(tmp / "plandata")
treefile = a.tree or str(tmp / "tree.txt")
if not a.tree:
    Path(treefile).write_text("\n".join(sorted(TREE)))
bd = subprocess.run([NODE, "tools/site/build_docs.mjs", "--root", ".", "--tree", treefile, "--out", str(tmp / "site"), "--mermaid", "none"],
                    capture_output=True, text=True)
BUILD_FAILS = [l for l in (bd.stdout + bd.stderr).splitlines() if "FAIL" in l]
pages = [str(p) for p in sorted((tmp / "site").glob("*.html"))]
an = subprocess.run([sys.executable, "dev/audit/harnesses/d6_page_anchors.py", "docs/index.html"] + pages, capture_output=True, text=True)
ANCHOR_OUT = an.stdout.strip().splitlines()

# ---------------------------------------------------------------- behaviour rows from claims.py
EXTRA = {}
if Path(a.extra).exists():
    for line in Path(a.extra).read_text().splitlines():
        if line and not line.startswith("#"):
            uid, cmd, res, ver = line.split("\t")[:4]
            EXTRA[uid] = (cmd, res, ver)

# ---------------------------------------------------------------- classify and row
IMPERATIVE = re.compile(r"^(\*\*)?(Keep|Do|Don't|Use|See|Open|Set|Turn|Choose|Read|Leave|Install|Add|Click|Pick|Enter|Go|Make|Restart|Copy|Download|Select|Paste|Point|Search|Treat|Check|Tap|Run|Give|Name|Remove|Edit|Try|Start|Fill|Press|Wait|Follow|Look|Report|Find|Note|Change|Clear|Answer|Drop|Put|Raise|Lower|Switch|Toggle|Configure|Create|Ignore|Expect|Think|Consider|Avoid|Never|Always|Thanks|Thank)\b")
HEADING = re.compile(r"^#{1,6}\s")
CMD_LEDGER = "PYTHONUTF8=1 PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D6/s1/ledger.py"

rows = []
for uid, ln, kind, text in units:
    f = uid.split("#")[0]
    checks = []
    if uid in EXTRA:
        cmd, res, ver = EXTRA[uid]
        checks.append((ver, res, cmd))
    CTX["text"] = text
    CTX["other_repo"] = bool(re.search(r"neither file lives|in the [\w-]+ repository|another repository", text))
    for span in re.findall(r"`([^`\n]+)`", text):
        r = check_tick(span)
        if r:
            checks.append((r[0], f"`{span}`: {r[1]}", CMD_LEDGER))
    for tgt in LINK.findall(text) + HREF.findall(text):
        r = check_link(f, tgt)
        if r:
            checks.append((r[0], r[1], CMD_LEDGER))
    if text.lstrip().startswith("|"):
        cells = [c.strip() for c in text.strip().strip("|").split("|")]
        r = check_table_row(cells) if f.endswith(".md") else None
        if r:
            checks.append((r[0], r[1], CMD_LEDGER))
    if checks:
        vs = [c[0] for c in checks]
        verdict = "false" if "false" in vs else ("stale" if "stale" in vs else ("true" if "true" in vs else "unverifiable"))
        res = " | ".join(c[1] for c in checks)[:600].replace("\t", " ")
        cmd = checks[0][2]
        truth = "" if verdict == "true" else "; ".join(c[1] for c in checks if c[0] != "true")[:400]
        rows.append((uid, ln, "claim", cmd, res, verdict, truth or "-"))
        continue
    t = text.strip()
    if kind == "file" or HEADING.match(t) or IMPERATIVE.match(t) or t.endswith("?") or re.fullmatch(r"[|\s:-]+", t) \
            or (kind == "code") or len(re.findall(r"[A-Za-z]{2,}", t)) < 4 or f == "DISCLAIMER.md":
        # DISCLAIMER.md: legal disclaimers assert no product fact beyond what other rows carry
        rows.append((uid, ln, "no-claim", "-", "-", "-", "-"))
    else:
        rows.append((uid, ln, "claim", "-", "NOT-REACHED: no executed check this round (behavioural or prose claim)",
                     "unverifiable", "not checked; carried to not_reached"))

with open(a.out, "w") as fh:
    fh.write("unit\tline\tkind\tcommand\tresult\tverdict\ttruth\n")
    for r in rows:
        fh.write("\t".join(str(x).replace("\t", " ").replace("\n", " ") for x in r) + "\n")

per = collections.defaultdict(collections.Counter)
for r in rows:
    f = r[0].split("#")[0]
    per[f][r[2] if r[2] == "no-claim" else ("notreached" if r[4].startswith("NOT-REACHED") else r[5])] += 1
for f in FILES:
    c = per[f]
    print(f"FILE {f} " + " ".join(f"{k}={c[k]}" for k in ("no-claim", "true", "false", "stale", "unverifiable", "notreached")))
for r in rows:
    if r[5] == "false":
        print(f"FALSE {r[0]} L{r[1]} :: {r[6][:300]}")
print("BUILD_DOCS", (bd.stdout.strip().splitlines() or ["?"])[-1], "fails", len(BUILD_FAILS))
for l in BUILD_FAILS:
    print("  ", l)
for l in ANCHOR_OUT:
    print("ANCHORS", l.replace(str(tmp), "$TMP"))
print(f"RESULT units={len(units)} count")
print(f"RESULT rows={len(rows)} count")
print(f"RESULT claims_checked={sum(1 for r in rows if r[2]=='claim' and not r[4].startswith('NOT-REACHED'))} count")
print(f"RESULT claims_not_reached={sum(1 for r in rows if r[4].startswith('NOT-REACHED'))} count")
print(f"RESULT no_claim={sum(1 for r in rows if r[2]=='no-claim')} count")
print(f"RESULT false_rows_total={sum(1 for r in rows if r[5]=='false')} count")
print(f"RESULT files_with_false={sum(1 for f in FILES if per[f]['false'])} count")
print(f"RESULT build_docs_fail_lines={len(BUILD_FAILS)} count")
cpu, thr = time.process_time() - t_cpu0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in Path("/proc/vmstat").read_text().splitlines() if l.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "0"
print(f"RESULT swapins={sw}")
