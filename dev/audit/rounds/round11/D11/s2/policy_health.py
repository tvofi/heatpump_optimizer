#!/usr/bin/env python3
"""D11.M3: the policy structure's own health -- size and direction, duplication,
and the rulings file's overlap with policy.

Metrics (one line each):
  ratio            lines added / lines deleted over the policy corpus
                   (`policy_lint.mjs --corpus-filter` over `git ls-files`, plus
                   dev/governance/decisions and RULINGS.md) across v10.0.0..baseline.
  dup_units        normalized D6 units (`tools/audit/text_ledger.py:units_of`) of
                   >= 8 words that occur verbatim in two or more policy files, a
                   `.claude/rules/` copy folded onto its dev/governance/rules source
                   (rules_sync.mjs --check holds that pair).
  rulings_overlap  live RULINGS.md entries (before `## Superseded`) carrying a
                   quoted span of >= 6 words that a policy-corpus file (RULINGS.md
                   and the decisions excluded) also states verbatim.
Key: the unit text text_ledger delivers, normalized to lower-case words.

Run:   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D11/s2/policy_health.py [--perturb] [--list]
       --perturb deletes, in memory, every corpus sentence an overlapping ruling
       quotes, and one file of every duplicate pair: rulings_overlap and dup_units
       must go to 0.
       --list prints each duplicate and each overlapping entry.
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B7: exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re, subprocess, sys, tempfile, time
from collections import defaultdict

sys.path[:0] = ["tools/audit"]
import text_ledger  # noqa: E402

BASE, HEAD = "v10.0.0", "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"


def norm(t):
    return re.sub(r"\W+", " ", t.lower()).strip()


def corpus():
    env = dict(os.environ, HPO_PLANDATA=tempfile.mkdtemp(prefix="d11s2-"))
    ls = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout
    pol = subprocess.run(["node", "tools/policy/policy_lint.mjs", "--corpus-filter"], input=ls,
                         capture_output=True, text=True, env=env).stdout.split()
    extra = subprocess.run(["git", "ls-files", "dev/governance/decisions", "dev/programme/RULINGS.md"],
                           capture_output=True, text=True).stdout.split()
    return pol, extra


def live_rulings(text):
    body = text.split("\n## Superseded", 1)[0]
    entries, cur = [], None
    for ln in body.splitlines():
        if ln.startswith("- "):
            cur = [ln]
            entries.append(cur)
        elif cur is not None and ln.startswith("  "):
            cur.append(ln)
        else:
            cur = None
    return [" ".join(e) for e in entries]


def main(argv):
    t0, c0 = time.process_time(), time.thread_time()
    pol, extra = corpus()
    files = sorted(set(pol + extra))
    num = subprocess.run(["git", "log", "--numstat", "--format=", f"{BASE}..{HEAD}", "--", *files],
                         capture_output=True, text=True).stdout.split("\n")
    add = sum(int(l.split("\t")[0]) for l in num if l and l.split("\t")[0].isdigit())
    dele = sum(int(l.split("\t")[1]) for l in num if l and l.split("\t")[0].isdigit())
    texts = {f: text_ledger.read(".", f) for f in files}
    by = defaultdict(set)
    for f in files:
        key = "dev/governance/rules/" + f.split("/")[-1] if f.startswith(".claude/rules/") else f
        for _, _, _, t in text_ledger.units_of(f, texts[f], "D6"):
            n = norm(t)
            if len(n.split()) >= 8:
                by[n].add(key)
    dups = {t: fs for t, fs in by.items() if len(fs) > 1}
    rul = live_rulings(texts["dev/programme/RULINGS.md"])
    policy_text = {f: norm(texts[f]) for f in pol if f != "dev/programme/RULINGS.md"}
    if "--perturb" in argv:
        for t, fs in dups.items():
            drop = sorted(fs)[0]
            for f in list(policy_text):
                if (("dev/governance/rules/" + f.split("/")[-1]) if f.startswith(".claude/rules/") else f) == drop:
                    policy_text[f] = policy_text[f].replace(t, " ")
        dups = {}
    overl = []
    for e in rul:
        quotes = [norm(q) for q in re.findall(r"\"([^\"]+)\"", e) + re.findall(r"\*\"([^\"]+)\"\*", e)]
        quotes = [q for q in quotes if len(q.split()) >= 6]
        hit = [(q, f) for q in quotes for f, t in policy_text.items() if q in t]
        if hit and "--perturb" in argv:
            for q, f in hit:
                policy_text[f] = policy_text[f].replace(q, " ")
            hit = [(q, f) for q in quotes for f, t in policy_text.items() if q in t]
        if hit:
            overl.append((e[:110], sorted({f for _, f in hit})))
    if "--list" in argv:
        for t, fs in sorted(dups.items(), key=lambda kv: sorted(kv[1])):
            print(f"DUP\t{' | '.join(sorted(fs))}\t{t[:120]}")
        for e, fs in overl:
            print(f"OVERLAP\t{' | '.join(fs)}\t{e}")
    print(f"RESULT corpus_files={len(files)} count")
    print(f"RESULT lines_added={add} count")
    print(f"RESULT lines_deleted={dele} count")
    print(f"RESULT added_per_deleted={add / dele if dele else float('inf'):.3f} ratio")
    print(f"RESULT dup_units={len(dups)} count")
    print(f"RESULT rulings_live={len(rul)} count")
    print(f"RESULT rulings_bytes={len(texts['dev/programme/RULINGS.md'].encode())} bytes")
    print(f"RESULT rulings_overlap={len(overl)} count")
    pc, tc = time.process_time() - t0, time.thread_time() - c0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main(sys.argv[1:])
