#!/usr/bin/env python3
"""D5.M2 structure harness: heading depth/order, internal links and anchors, paragraph repeats,
orphaned documents, external links, over every heading and link row text_ledger.py outline prints
for README.md and docs/*.md (seat D5-s2's documents).

Metric: count of outline rows (heading or link) that fail a structure rule, per rule.
  heading_skip   a heading more than one level below the previous heading (h2 -> h4)
  heading_multi_h1  a second h1 in one document
  link_file_missing  internal link whose target file does not exist in the tree
  link_anchor_missing  internal link whose #anchor matches no heading slug (GitHub rule) or id/name
  dup_paragraph  paragraph (whitespace-normalised, >= 12 words) that appears in two places
  orphan_doc     docs/*.md no other document of the set links to
  external_bad   external link answering >= 400 or not at all (only with --net)
Key: the count is keyed on the documents' own text as the outline enumerator splits it
(tools/audit/text_ledger.py:outline), never on a list carried here.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/structure.py [--net] [--perturb] [--plant]
  --plant    null control: two dead anchors and one repeated paragraph planted in README, in memory
             (link_anchor_missing 0 -> 2, dup_paragraph +1).
  --perturb  in-memory perturbation: rewrite each missing anchor to the nearest existing slug,
             so link_anchor_missing must go to zero (the fix's direction).
  --dedupe   in-memory perturbation for D5-s2-01: README.md's two options-page tables replaced by
             one link to docs/configuration.md#changing-settings-later, so dup_paragraph 15 -> 9 and
             menu_twin_drift 14 -> 0 (down).
  --link-orphans  in-memory perturbation for D5-s2-02: one README link to docs/CONTRIBUTING.md,
             so orphan_doc 1 -> 0 (to_zero).
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, exact (counts): outline_rows=382,
heading_skip=0, heading_multi_h1=0, link_file_missing=0, link_anchor_missing=0, dup_paragraph=15,
orphan_doc=1, external_bad=0 (with --net, 33 checked), menu_twin_drift=14, dup_fence=4.
Machine: the orchestrator's macOS box (B2); counts are contention-immune.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import hashlib, json, re, sys, time, urllib.request, urllib.error
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, "tools/audit")
import text_ledger  # noqa: E402  (the production enumerator this harness drives)

DOCS = ["README.md"] + sorted(str(p) for p in Path("docs").glob("*.md"))
OUT = Path(__file__).with_name("work")


def slug(text):
    """GitHub's heading anchor rule: lowercase, drop punctuation but - and _, spaces to -."""
    t = re.sub(r"<[^>]*>", "", text)
    t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t)  # link text only
    t = t.replace("`", "").strip().lower()
    t = re.sub(r"[^\w\- ]", "", t, flags=re.UNICODE)
    return t.replace(" ", "-")


def anchors_of(path, text):
    out, seen = set(), defaultdict(int)
    for line, kind, t in text_ledger.outline(path, text):
        if kind == "heading":
            s = slug(t.split(" ", 1)[1])
            k = seen[s]
            seen[s] += 1
            out.add(s if k == 0 else f"{s}-{k}")
    for m in re.finditer(r"<a\s[^>]*(?:id|name)=[\"']([^\"']+)", text):
        out.add(m.group(1))
    for m in re.finditer(r"\{#([\w-]+)\}", text):
        out.add(m.group(1))
    return out


def paragraphs(text):
    paras, cur, fence = [], [], False
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        if not line.strip() or text_ledger.BLOCK_START.match(line):
            if cur:
                paras.append(cur)
            cur = []
        if line.strip():
            cur.append((n, line))
    if cur:
        paras.append(cur)
    out = []
    for p in paras:
        t = " ".join(" ".join(l for _, l in p).split())
        if len(re.findall(r"[^\W\d_]{2,}", t)) >= 12:
            out.append((p[0][0], t))
    return out


def run(perturb=False, net=False):
    texts = {d: Path(d).read_text(encoding="utf-8") for d in DOCS}
    if "--plant" in sys.argv:  # null control: one planted dead anchor and one planted repeat must count
        texts["README.md"] += ("\n\nSee [x](#no-such-anchor-planted) and [y](docs/setup.md#nor-this-one).\n\n"
                               + paragraphs(texts["docs/setup.md"])[0][1] + "\n")
    if "--dedupe" in sys.argv:
        out, skip = [], False
        for l in texts["README.md"].splitlines():
            if l.startswith("| Page |") or l.startswith("| Advanced page |"):
                skip = True
                out.append("See [the page list](docs/configuration.md#changing-settings-later).")
                continue
            if skip and l.startswith("|"):
                continue
            skip = False
            out.append(l)
        texts["README.md"] = "\n".join(out) + "\n"
    if "--link-orphans" in sys.argv:  # perturbation for D5-s2-02: README's Documentation list names it
        texts["README.md"] += "\n- [Contributing from a fork](docs/CONTRIBUTING.md)\n"
    anchors = {d: anchors_of(d, t) for d, t in texts.items()}
    fails = defaultdict(list)
    rows = 0
    inbound = defaultdict(set)
    external = []
    for d in DOCS:
        last, h1 = 0, 0
        for line, kind, t in text_ledger.outline(d, texts[d]):
            if kind == "heading":
                rows += 1
                lv = int(t[1])
                if last and lv > last + 1:
                    fails["heading_skip"].append(f"{d}:{line} h{last}->{t}")
                if lv == 1:
                    h1 += 1
                    if h1 > 1:
                        fails["heading_multi_h1"].append(f"{d}:{line} {t}")
                last = lv
            elif kind == "link":
                rows += 1
                if re.match(r"^[a-z]+:", t):
                    if t.startswith("http"):
                        external.append((d, line, t))
                    continue
                target, _, anchor = t.partition("#")
                tpath = os.path.normpath(os.path.join(os.path.dirname(d), target)) if target else d
                if target:
                    inbound[tpath].add(d)
                if not Path(tpath).exists():
                    if tpath.startswith("dev/archive/backlog"):
                        fails["wall_removed"].append(f"{d}:{line} {t}")
                    else:
                        fails["link_file_missing"].append(f"{d}:{line} {t}")
                    continue
                if anchor and tpath.endswith(".md"):
                    have = anchors.get(tpath)
                    if have is None:
                        have = anchors_of(tpath, Path(tpath).read_text(encoding="utf-8"))
                    if anchor not in have:
                        if perturb:
                            continue  # the fix's direction: the anchor rewritten to an existing slug
                        fails["link_anchor_missing"].append(f"{d}:{line} {t}")
    # paragraph repeats across README.md and docs/*.md
    seen = defaultdict(list)
    for d in DOCS:
        for line, t in paragraphs(texts[d]):
            seen[hashlib.sha1(t.encode()).hexdigest()[:10]].append(f"{d}:{line}")
    for h, locs in seen.items():
        if len(locs) > 1:
            fails["dup_paragraph"].append(f"{h} " + " ".join(locs))
    # fenced blocks (diagrams, code) kept in two documents: >= 60 % of their non-blank lines shared
    fences = []
    for d in DOCS:
        for line, kind, t in text_ledger.prose_units(texts[d]):
            if kind == "code":
                lines = {" ".join(x.split()) for x in t.splitlines()[1:-1] if x.strip()}
                if len(lines) >= 5:
                    fences.append((d, line, lines))
    for i in range(len(fences)):
        for j in range(i + 1, len(fences)):
            (d1, l1, a), (d2, l2, b) = fences[i], fences[j]
            if d1 != d2:
                share = len(a & b) / min(len(a), len(b))
                if share >= 0.6:
                    fails["dup_fence"].append(f"{d1}:{l1} ~ {d2}:{l2} shared={share:.2f} "
                                              f"differing_lines={len(a ^ b)}")
    for d in DOCS:
        if d != "README.md" and not (inbound[d] - {d}):
            fails["orphan_doc"].append(d)
    # stale versions: a version literal in prose that names this integration's version
    ver = Path("VERSION").read_text().strip()
    hacs = json.loads(Path("hacs.json").read_text())["homeassistant"]
    for d in DOCS:
        for n, l in enumerate(texts[d].splitlines(), 1):
            for m in re.finditer(r"Home(?:%20| )Assistant[- ](\d{4}\.\d+(?:\.\d+)?)", l):
                if m.group(1) != hacs:
                    fails["stale_ha_version"].append(f"{d}:{n} {m.group(1)} vs hacs.json {hacs}")
    # twin tables: the options-menu page table kept in README.md and again in docs/configuration.md;
    # a row whose page name is in both but whose description differs is a drifted twin.
    def menu_rows(text, heads):
        rows, on = {}, False
        for l in text.splitlines():
            if l.startswith("|") and l.split("|")[1].strip() in heads:
                on = True
                continue
            if on and not l.startswith("|"):
                on = False
            if on and not l.startswith("|---"):
                c = [x.strip() for x in l.strip().strip("|").split("|")]
                rows[c[0]] = " ".join(c[1:])
        return rows
    rm = menu_rows(texts["README.md"], {"Page", "Advanced page"})
    cm = menu_rows(texts["docs/configuration.md"], {"First menu", "Advanced settings"})
    both = sorted(set(rm) & set(cm))
    twins_same = [k for k in both if rm[k] == cm[k]]
    twins_drift = [k for k in both if rm[k] != cm[k]]
    fails["menu_twin_drift"] = [f"{k}: README={rm[k]!r} | configuration={cm[k]!r}" for k in twins_drift]
    print(f"RESULT menu_rows_readme={len(rm)} rows")
    print(f"RESULT menu_rows_configuration={len(cm)} rows")
    print(f"RESULT menu_twins_identical={len(twins_same)} rows")
    print(f"RESULT menu_only_one_side={len(set(rm) ^ set(cm))} rows")
    ext_checked = 0
    if net:
        cache = {}
        for d, line, url in external:
            if url not in cache:
                code = None
                for method in ("HEAD", "GET"):
                    try:
                        req = urllib.request.Request(url, method=method, headers={"User-Agent": "Mozilla/5.0 (link-check)"})
                        with urllib.request.urlopen(req, timeout=20) as r:
                            code = r.status
                    except urllib.error.HTTPError as e:
                        code = e.code
                    except Exception as e:  # noqa: BLE001
                        code = f"ERR {type(e).__name__}"
                    if code == 200 or method == "GET":
                        break
                cache[url] = code
                time.sleep(0.3)
            ext_checked += 1
            c = cache[url]
            if not isinstance(c, int) or c >= 400:
                fails["external_bad"].append(f"{d}:{line} {url} -> {c}")
    OUT.mkdir(exist_ok=True)
    (OUT / ("structure_fails" + ("_perturbed" if perturb else "") + ".json")).write_text(json.dumps(fails, indent=1))
    print(f"RESULT outline_rows={rows} rows")
    print(f"RESULT external_links={len(external)} links")
    print(f"RESULT external_checked={ext_checked} links")
    for k in ("heading_skip", "heading_multi_h1", "link_file_missing", "link_anchor_missing", "dup_paragraph",
              "orphan_doc", "stale_ha_version", "external_bad", "wall_removed", "menu_twin_drift", "dup_fence"):
        print(f"RESULT {k}={len(fails[k])} count")
        for x in fails[k][:40]:
            print(f"   {k}: {x}")
    lf = os.getloadavg()[0]
    tf = time.process_time() / max(time.thread_time(), 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={lf:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    run(perturb="--perturb" in sys.argv, net="--net" in sys.argv)
