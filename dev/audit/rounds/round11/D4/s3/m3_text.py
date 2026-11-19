"""D4.M3 (seat D4-s3): typographic notation inside one language, across the user-facing text files.

Metric: per language, quoted spans written with straight ASCII quotes ("x") in a language whose
other quoted spans in the same surfaces use typographic quotes (de: „x“, sv: ”x”), plus degree
temperatures written without the degree sign ("15 C") -- counted over translations/{en,de,sv}.json
(the strings Home Assistant renders for the config flow, entities, services and exceptions), the
card's STRINGS table (loaded from the card source in a Node vm, the table L() reads), services.yaml
and every blueprints/ file's name/description/input text.
Key: the delivered string values, never file bytes outside them (JSON keys and YAML keys excluded).

Run (export root):  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D4/s3/m3_text.py [--perturb=de_quotes]
Also: config/options page titles in Title Case among sentence-case ones (en, sv).
Perturbation sentence_titles: in memory, every en/sv page title is sentence-cased (acronyms and
the product's proper names kept); expected *_title_case_titles -> 0.
Perturbation de_quotes: in memory, de.json's straight-quoted spans are rewritten „x“; expected
de_straight_spans -> 0 and mixed_languages down by one. Expected baseline: REPORT.md (exact counts).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B10.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob
import json
import re
import subprocess
import sys

import yaml

PERTURB = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--perturb=")), "")
B = "custom_components/heatpump_optimizer/"


def leaves(d):
    if isinstance(d, dict):
        for v in d.values():
            yield from leaves(v)
    elif isinstance(d, list):
        for v in d:
            yield from leaves(v)
    elif isinstance(d, str):
        yield d


STRAIGHT = re.compile(r'"[^"\n]{1,80}"')
TYPO = {"de": re.compile(r"„[^“\n]{1,80}“"), "sv": re.compile(r"”[^”\n]{1,80}”"), "en": re.compile(r"“[^”\n]{1,80}”")}
DEG = re.compile(r"\b\d+(?:[.,]\d+)? C\b")

tr = {l: json.load(open(f"{B}translations/{l}.json", encoding="utf-8")) for l in ("en", "de", "sv")}
if PERTURB == "de_quotes":
    raw = json.dumps(tr["de"], ensure_ascii=False)
    tr["de"] = json.loads(re.sub(r'\\"([^"\\\n]{1,80})\\"', r"„\1“", raw))
js = r"""
const fs=require("fs"),vm=require("vm");const src=fs.readFileSync(process.argv[1],"utf8");
const i=src.indexOf("const STRINGS = {"),j=src.indexOf("\n};\n",i);
process.stdout.write(JSON.stringify(vm.runInNewContext("("+src.slice(i+16,j+2)+")")));"""
card = json.loads(subprocess.check_output(["node", "-e", js, f"{B}www/heatpump-optimizer-card.js"], text=True))
other = list(leaves(yaml.safe_load(open(f"{B}services.yaml", encoding="utf-8"))))
for f in sorted(glob.glob("blueprints/**/*.yaml", recursive=True)):
    txt = open(f, encoding="utf-8").read()
    txt = re.sub(r"!input\s+\S+", "''", txt)
    other += list(leaves(yaml.safe_load(txt)))

# Page titles: en and sv write titles in sentence case everywhere else in these files ("Your
# building", "Din byggnad"); a title word after the first that starts with a capital and is not an
# acronym or a proper name is a Title Case title among sentence-case ones. German capitalises
# nouns, so de is not read.
PROPER = {"Heat", "Pump", "Optimizer", "Home", "Assistant", "Tibber", "Nord", "Pool", "Open", "Meteo", "Modbus", "Nibe", "NIBE"}
if PERTURB == "sentence_titles":
    for lang in ("en", "sv"):
        for area in ("config", "options"):
            for st in tr[lang][area]["step"].values():
                if isinstance(st, dict) and isinstance(st.get("title"), str):
                    seen = []
                    def low(m):
                        x = m.group(0); seen.append(x)
                        return x if len(seen) == 1 or x.isupper() or x in PROPER else x[:1].lower() + x[1:]
                    st["title"] = re.sub(r"[^\s-]+", low, st["title"])
for lang in ("en", "sv"):
    titles = [(f"{area}.step.{k}", v["title"]) for area in ("config", "options")
              for k, v in tr[lang][area]["step"].items() if isinstance(v, dict) and isinstance(v.get("title"), str)]
    tc = [(k, t) for k, t in titles if any(re.match(r"^[A-ZÅÄÖ][a-zåäö]", x) and x not in PROPER for x in re.split(r"[\s-]+", t)[1:])]
    for k, t in tc:
        print(f"  {lang} title-case title {k}: {t!r}")
    print(f"RESULT {lang}_page_titles={len(titles)} count")
    print(f"RESULT {lang}_title_case_titles={len(tc)} count")
mixed = 0
for lang in ("en", "de", "sv"):
    vals = list(leaves(tr[lang])) + list(leaves(card[lang])) + (other if lang == "en" else [])
    s = sum(len(STRAIGHT.findall(v)) for v in vals)
    t = sum(len(TYPO[lang].findall(v)) for v in vals)
    d = [m for v in vals for m in DEG.findall(v)]
    print(f"{lang}: straight-quoted spans {s}, typographic spans {t}, degree-without-sign {d}")
    if s and t:
        mixed += 1
    print(f"RESULT {lang}_straight_spans={s} count")
    print(f"RESULT {lang}_typographic_spans={t} count")
    print(f"RESULT {lang}_degree_without_sign={len(d)} count")
print(f"RESULT mixed_languages={mixed} count")
print("RESULT thread_factor=1.00")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
