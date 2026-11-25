#!/usr/bin/env python3
"""D5-s8 step M4: row every D5 comment unit of the seat's cells by an executed resolvability check.

Metric: per unit, the references it names (repo paths, `path:symbol` / `path::symbol` pairs,
backticked or called identifiers, `file:line` citations) that do not resolve in the tree at the
ref (criterion C2), and the longest sentence in words (criterion C5, fail over 40).
Count key: a reference resolves when the tracked tree at --ref holds the path (from the root,
the unit's own directory, or as a tracked suffix), or when the identifier occurs as a whole word
in the code of a tracked file other than inside the unit itself (comments stripped from .py,
.js, .mjs and .sh; Markdown is never evidence of a code symbol).

Command (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s8/m4_ledger.py \
      --repo <git repo holding the ref> --ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 \
      [--ledger OUT.tsv] [--file F ...] [--perturb FILE:OLD=>NEW ...]
Without --file it takes the seat's cells from tools/audit/check_scopes.py --seat D5-s8.
--perturb rewrites FILE's text in memory (OLD replaced by NEW) before units are enumerated, so
a fixed comment can be re-measured without touching the tree.
Expected at 92d38ecb: RESULT units=3628, units_with_unresolved_ref=25, units_with_sentence_over_40_words=657,
exact (counts, contention-immune); per-file lines as REPORT.md quotes them.
Ledger verdicts: stale = a C2-unresolved reference the seat did not adjudicate (ADJ below); true = every
reference resolves; unverifiable = the unit names nothing resolvable. C5 rides in the result column. Machine: box B12, Linux x86_64, 4 vCPU.
Instrumented symbol: tools/audit/text_ledger.py:units_of over each production file's text.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, fnmatch, io, re, subprocess, sys, time, tokenize
from pathlib import Path

sys.path.insert(0, "tools/audit")
import text_ledger as TL  # noqa: E402

SEAT = "D5-s8"
CODE_SUF = (".py", ".js", ".mjs", ".sh", ".cjs", ".yml", ".yaml", ".json", ".toml", ".cfg", ".ini", ".txt")
TOP = ("tests/", "tools/", "dev/", "docs/", "custom_components/", ".github/", ".claude/", "blueprints/",
       ".cursor/", "www/")
PATH_RE = re.compile(r"(?<![\w/.$-])((?:\.{0,2}[\w*{},.-]+/)+[\w*{},.-]*[\w*}])")
FILE_RE = re.compile(r"(?<![\w/.$-])([A-Za-z_][\w-]*\.(?:py|mjs|js|sh|json|md|yml|yaml|txt|tsv|mdc|cjs))\b")
PATHSYM_RE = re.compile(r"([\w./-]+\.(?:py|mjs|js|sh)):{1,2}([A-Za-z_]\w*)")
PATHLINE_RE = re.compile(r"([\w./-]+\.(?:py|mjs|js|sh|md|json|yml)):(\d+)\b")
TICK_RE = re.compile(r"`{1,2}([^`\n]{1,80}?)`{1,2}")
CALL_RE = re.compile(r"(?<![\w.$])([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\(\)")
IDENT = re.compile(r"^[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*(?:\(\))?$")
WORD = re.compile(r"[A-Za-z_$][\w$]*")


def git(repo, *a):
    return subprocess.check_output(["git", "-C", repo, *a], text=True)


def strip_code(path, text):
    """The file's text with its comments removed, so a symbol named only in a comment is not 'defined'."""
    suf = Path(path).suffix
    if suf == ".py":
        try:
            toks = [t.string for t in tokenize.generate_tokens(io.StringIO(text).readline)
                    if t.type in (tokenize.NAME, tokenize.STRING, tokenize.OP)]
            return " ".join(toks)
        except (tokenize.TokenError, SyntaxError, IndentationError):
            return text
    if suf in (".js", ".mjs", ".cjs", ".sh"):
        for _l, _k, c in TL.scan_c_like(text, suf == ".sh")[0]:
            text = text.replace(c, " ", 1)
        return text
    return text


def build_corpus(root, tree):
    words = {}
    lines = {}
    for p in tree:
        if p.startswith("dev/audit/rounds/") or not p.endswith(CODE_SUF):
            continue
        fp = Path(root) / p
        if not fp.is_file():
            continue
        try:
            t = fp.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        lines[p] = t.count("\n") + 1
        for w in set(WORD.findall(strip_code(p, t))):
            words.setdefault(w, set()).add(p)
    return words, lines


def strip_markers(t):
    t = re.sub(r"(?m)^\s*(#+|//+|/\*+|\*+/?|\*/)", " ", t)
    return t.replace("*/", " ")


def resolve_path(p, here, tree, tree_set, dirs):
    p = p.rstrip(".,;:)").rstrip("/")
    if not p or p.startswith(("http", "www.")) or "{" in p and "}" not in p:
        return True
    if "*" in p or "{" in p:
        pat = re.sub(r"\{([^}]*)\}", lambda m: "[" + "".join(x[0] for x in m.group(1).split(",")) + "]*" if "," in m.group(1) else "*", p)
        return any(fnmatch.fnmatch(t, pat) or fnmatch.fnmatch(t, "*/" + pat) for t in tree)
    cands = [p, os.path.normpath(p), str(Path(here).parent / p), os.path.normpath(str(Path(here).parent / p))]
    if any(c in tree_set or c in dirs for c in cands):
        return True
    if any(t.endswith("/" + p) for t in tree) or any(d.endswith("/" + p) for d in dirs):
        return True
    # a prefix cut by a placeholder (`dev/audit/rounds/round<N>/`) resolves when some tracked path extends it
    return any(t.startswith(p) for t in tree)


def refs_of(text):
    """(kind, ref) pairs a unit names; kinds path, file, pathsym, pathline, ident."""
    t = strip_markers(text)
    out = []
    for m in PATHSYM_RE.finditer(t):
        out.append(("pathsym", (m.group(1), m.group(2))))
    for m in PATHLINE_RE.finditer(t):
        out.append(("pathline", (m.group(1), int(m.group(2)))))
    for m in PATH_RE.finditer(t):
        s = m.group(1)
        if s.startswith(TOP) or s.startswith(("./", "../")) and "/" in s[3:]:
            out.append(("path", s))
    for m in FILE_RE.finditer(t):
        out.append(("file", m.group(1)))
    idents = set()
    for m in TICK_RE.finditer(t):
        s = m.group(1).strip()
        if IDENT.match(s) and ("_" in s or "." in s or s.endswith("()") or re.search(r"[a-z][A-Z]", s)) \
                and not re.search(r"\.(py|mjs|js|sh|json|md|yml|yaml|txt|tsv)$", s):
            idents.add(s.rstrip("()"))
    for m in CALL_RE.finditer(t):
        idents.add(m.group(1))
    for s in idents:
        out.append(("ident", s))
    return out


LIST_LINE = re.compile(r"^\s*([-*+\u2022]\s|\d+[.)]\s|(node|python3?|bash|sh|git|PYTHONPATH=\S*|\$)\s|\.\.\.|[A-Z][A-Z_ -]{3,}[.:])")


def blocks_of(text):
    """Paragraphs of a comment: split at blank lines, list or command lines and indented (code) lines,
    so a list or usage block without full stops is not read as one sentence."""
    out, cur = [], []
    for raw in strip_markers(text).splitlines():
        body = raw.rstrip()
        if not body.strip() or LIST_LINE.match(body) or re.match(r"^ {5,}\S", body):
            if cur:
                out.append(" ".join(cur)); cur = []
            if body.strip():
                out.append(body.strip())
            continue
        cur.append(body.strip())
    if cur:
        out.append(" ".join(cur))
    return out


def max_sentence_words(text):
    t = re.sub(r"(?s)```.*?```", " ", text)
    return max((len(s.split()) for b in blocks_of(t) for s in TL.sentences(b)), default=0)


# Unresolved references this seat read and adjudicated as not stale, each with its reason: a fixture
# or example name, a generated artefact, a file outside the repository, a history sentence about
# what was moved or deleted, or a citation pinned to a SHA or branch. Everything else that does not
# resolve is a stale row.
ADJ = {
    ("tests/card.mjs", "HARMONY.md"): "pinned: probe/card-harmony-design 6aea0d10",
    ("tests/card_browser.mjs", "easylist_general_hide.txt"): "external: an EasyList file",
    ("tests/ci_ratchet.py", "ci-metrics-fast.tsv"): "generated artefact name",
    ("tests/closure.py", "scripts.txt"): "generated artefact name",
    ("tests/closure.py", "check.txt"): "generated artefact name",
    ("tests/closure.py", "record_status.py"): "history: 'which replaced'",
    ("tests/closure.py", "tools/audit/briefs"): "history: 'moved out of'",
    ("tests/closure.py", "docs/handover*.md"): "hypothetical glob: any OTHER handover file",
    ("tests/config_flow_steps.py", "tools/audit/round2/D10/B/harness.py"): "pinned: at 757e164",
    ("tests/config_flow_steps.py", "docs/modbus/rotenso_windmi_gchv.yaml"): "pinned: another repository at fda9bed",
    ("tests/delivery_status.py", "tests/record_status.py"): "history",
    ("tests/delivery_status.py", "record_status.py"): "history",
    ("tests/delivery_status.py", "ledger.json"): "example output name in a usage line",
    ("tests/derive_closures.sh", "scripts.txt"): "generated artefact name",
    ("tests/doc_claims.py", "a.py"): "example token shape",
    ("tests/doc_claims.py", "configuration.yaml"): "the user's own file, stated as such",
    ("tools/policy/agreement.mjs", "zz2.mjs"): "fixture",
    ("tools/policy/agreement_py.py", "_budgets.json"): "extraction artefact of the glob *_budgets.json",
    ("tools/policy/agreement_py.py", "tools/seat"): "true of the code: the list beside it names tools/seat",
    ("tools/policy/agreement_py.py", "tests/deep.py"): "fixture",
    ("tools/policy/brief_lint.mjs", "model_sanity.py"): "example",
    ("tools/policy/brief_lint.mjs", "card.js"): "example",
    ("tools/policy/brief_lint.mjs", "tools/audit/round2"): "history",
    ("tools/policy/brief_lint.mjs", "card_geometry.mjs"): "example",
    ("tools/policy/brief_lint.mjs", "docs/plan-2026-09-open-issues.md"): "history: 'had no destination but'",
    ("tools/policy/brief_lint.mjs", "b.txt"): "fixture",
    ("tools/policy/brief_lint.mjs", "a.txt"): "fixture",
    ("tools/policy/budget_raise_gate.py", "_budgets.json"): "extraction artefact of the glob *_budgets.json",
    ("tools/policy/budget_raise_gate.py", "budget-raise-gate-rerun.yml"): "history: 'retired with'",
    ("tools/policy/check-wave-script.mjs", "tools/audit/briefs"): "the move map's old key, stated as such",
    ("tools/policy/counts.mjs", "tools/audit/briefs"): "old names, stated as such",
    ("tools/policy/counts.mjs", "docs/HANDOVER.md"): "a quoted historical message",
    ("tools/policy/figure_lint.mjs", "../../x/y.sh"): "fixture",
    ("tools/policy/figure_lint.mjs", "../x/y.sh"): "fixture",
    ("tools/policy/policy_lint.mjs", "file.mdc"): "example",
    ("tools/policy/policy_lint.mjs", ".claude/workflows/*.mjs"): "history: 'was measured and refused' / the workflow's dual-layout restore",
    ("tools/policy/policy_lint.mjs", "docs/Zednotes.md"): "example: a citation 0003 makes on purpose",
    ("tools/policy/policy_lint.mjs", "docs/plan-2026-09-governance-audit.md"): "stated as not in this tree",
    ("tools/policy/policy_lint.mjs", "tests/POLICY-NOTES.md"): "a measured escape, history",
    ("tools/policy/policy_lint.mjs", "docs/POLICY-NOTES.md"): "a measured escape, history",
    ("tools/policy/policy_lint.mjs", "POLICY-NOTES.md"): "a measured escape, history",
    ("tools/policy/policy_lint.mjs", "./docs/NOTES.md"): "a measured escape, history",
    ("tools/policy/policy_lint.mjs", "docs/NOTES.MD"): "a measured escape, history",
    ("tools/policy/policy_lint.mjs", "docs/NOTES.txt"): "a measured escape, history",
    ("tools/policy/policy_lint.mjs", "docs/X.md"): "a measured escape, history",
    ("tools/policy/policy_lint.mjs", "docs/COMMON.md"): "a measured escape, history",
    ("tools/policy/policy_lint.mjs", "docs/fixer.md"): "a measured escape, history",
    ("tools/policy/policy_lint.mjs", "docs/gate-scoping.md"): "a measured escape, history",
    ("tools/policy/policy_lint.mjs", "Zednotes.md"): "a measured escape, history",
    ("tools/policy/policy_lint.mjs", "tools/audit/round2/**"): "history",
    ("tools/policy/policy_lint.mjs", "tools/audit/round2/HARNESSES.md"): "history: 'it deletes'",
    ("tools/policy/policy_lint.mjs", "tools/audit/round2/JUDGE.md"): "history: 'until this branch deleted'",
    ("tools/policy/policy_lint.mjs", "tools/audit/briefs/fixer.md"): "history: 'neither cites the record any more'",
    ("tools/policy/policy_lint.mjs", "b.md"): "example",
    ("tools/policy/policy_lint.mjs", "docs/delivery"): "both homes, stated as the old spelling",
    ("tools/policy/policy_lint.mjs", "docs/plan.md"): "a counter-example path",
    ("tools/policy/policy_lint.mjs", ".claude/workflows/carry.json"): "a counter-example path",
    ("tools/policy/policy_lint.mjs", ".claude/rules/fixer-dispatch.md"): "hypothetical: 'add ...'",
    ("tools/policy/policy_lint.mjs", "tools/audit/gate_lock.py"): "a quoted friction entry",
    ("tools/policy/policy_lint.mjs", "docs/delivery/*.md"): "history: v6.7.10's window",
    ("tools/policy/policy_lint.mjs", "docs/plan-*.md"): "history in 4849; see the header row for the present-tense one",
    ("tools/policy/policy_lint.mjs", "CaSe.md"): "fixture",
    ("tools/policy/policy_lint.mjs", "_budgets.json"): "extraction artefact of the glob *_budgets.json",
    ("tools/policy/policy_lint.mjs", "docs/settings"): "external: Claude Code's settings reference",
    ("tools/policy/policy_lint.mjs", ".claude/workflows/policy_lint_envmatrix.mjs"): "a matrix row's own name",
}
# Units whose unresolved reference is present tense even though the same name is adjudicated
# elsewhere in the file: (file, line) -> the names that are stale there.
PRESENT = {
    ("tools/policy/policy_lint.mjs", 1): {"docs/plan-*.md", "docs/HANDOVER.md", "tools/audit/briefs",
                                          ".claude/workflows/policy_lint.mjs"},
    ("tools/policy/policy_lint.mjs", 1985): {"docs/delivery"},
    ("tools/policy/policy_lint.mjs", 2328): {"docs/delivery/N.md"},
}
THIRD_PARTY = ("tools/policy/vendor/",)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--ledger")
    ap.add_argument("--file", action="append")
    ap.add_argument("--perturb", action="append", default=[])
    ap.add_argument("--show", action="store_true", help="print every failing unit")
    ap.add_argument("--drop", action="append", default=[], help="unit id whose text is blanked in memory")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    tree = git(a.repo, "ls-tree", "-r", "--name-only", a.ref).split("\n")
    tree = [x for x in tree if x]
    tree_set = set(tree)
    dirs = {str(Path(x).parent) for x in tree}
    dirs |= {d2 for d in list(dirs) for d2 in [str(p) for p in Path(d).parents]}
    files = a.file or TL.seat_files(SEAT, a.repo, a.ref)
    over = {}
    for spec in a.perturb:
        f, rest = spec.split(":", 1)
        old, new = rest.split("=>", 1)
        base = over.get(f, TL.read(".", f))
        if old not in base:
            sys.exit(f"perturb: {old!r} not in {f}")
        over[f] = base.replace(old, new, 1)
    for uid in a.drop:
        f = uid.split("#")[0]
        base = over.get(f, TL.read(".", f))
        u = next(x for x in TL.units_of(f, base, "D5") if x[0] == uid)
        if u[2] == "docstring":
            over[f] = base.replace(u[3], "", 1)
        else:
            # located by text, not by u[1]: text_ledger's JavaScript line field drifts (ledger_lines.py)
            L, cl = base.split("\n"), [x.lstrip("\0").strip() for x in u[3].split("\n")]
            i = next(i for i in range(len(L)) if all(i + k < len(L) and c in L[i + k] for k, c in enumerate(cl)))
            for k in range(len(cl)):
                L[i + k] = L[i + k].replace(cl[k], "") if L[i + k].strip() != cl[k] else ""
            over[f] = "\n".join(L)
    words, lines = build_corpus(".", tree)
    for f, txt in over.items():
        for w in set(WORD.findall(strip_code(f, txt))):
            words.setdefault(w, set()).add(f)
    git_cache = {}

    def word_at_ref(w):
        if w not in git_cache:
            r = subprocess.run(["git", "-C", a.repo, "grep", "-l", "-w", "-F", w, a.ref, "--",
                                ":(exclude)dev/audit/rounds/**", ":(exclude)*.md"],
                               capture_output=True, text=True)
            git_cache[w] = len([l for l in r.stdout.splitlines() if l])
        return git_cache[w]

    rows = [TL.HEADER]
    per_file = {}
    n_units = n_ref = n_unres = n_long = n_noref = 0
    for f in files:
        text = over.get(f, TL.read(".", f))
        own_words = {}
        units = TL.units_of(f, text, "D5")
        for uid, line, kind, utext in units:
            n_units += 1
            stat = per_file.setdefault(f, {"units": 0, "unresolved": 0, "long": 0, "items": []})
            stat["units"] += 1
            if kind == "file":
                rows.append([uid, str(line), "no-claim", "", "", "-", ""])
                continue
            refs = refs_of(utext)
            bad, adjudicated = [], []
            for k, r in refs:
                if k == "path":
                    ok = resolve_path(r, f, tree, tree_set, dirs)
                elif k == "file":
                    ok = resolve_path(r, f, tree, tree_set, dirs)
                elif k == "pathsym":
                    p, s = r
                    hits = [t for t in tree if t == p or t.endswith("/" + p.lstrip("./"))]
                    ok = any(t in words.get(s, ()) for t in hits) if hits else False
                    if not ok and hits:
                        ok = any(subprocess.run(["git", "-C", a.repo, "grep", "-q", "-w", "-F", s, a.ref, "--", h]).returncode == 0
                                 for h in hits) and s in words
                elif k == "pathline":
                    p, n = r
                    hits = [t for t in tree if t == p or t.endswith("/" + p.lstrip("./"))]
                    ok = (not hits) or any(lines.get(h, 10**9) >= n for h in hits)
                else:
                    leaf = r.split(".")[-1]
                    ok = bool(words.get(leaf))
                    if not ok:
                        ok = word_at_ref(leaf) > 0
                name = r if isinstance(r, str) else str(r[0])
                if not ok and f.startswith(THIRD_PARTY):
                    adjudicated.append(f"{name} (third-party vendored file)")
                elif not ok and (f, name) in ADJ and name not in PRESENT.get((f, line), ()):
                    adjudicated.append(f"{name} ({ADJ[(f, name)]})")
                elif not ok:
                    bad.append(f"{k}:{r if isinstance(r, str) else ':'.join(map(str, r))}")
            msw = max_sentence_words(utext)
            n_ref += len(refs)
            cmd = f"m4_ledger.py --repo R --ref {a.ref[:12]} --file {f} --show"
            res = f"refs={len(refs)} unresolved={len(bad)} adjudicated={len(adjudicated)} max_sentence_words={msw}"
            if adjudicated:
                res += " adjudicated: " + "; ".join(sorted(set(adjudicated)))[:300]
            if msw > 40 and f.startswith(THIRD_PARTY):
                res += " C5=n/a (third-party vendored file)"
            elif msw > 40:
                res += " C5=fail"
                stat["long"] += 1
                n_long += 1
                stat["items"].append((uid, line, f"C5: sentence of {msw} words > 40"))
            if bad:
                truth = "unresolved " + ", ".join(bad)
                stat["unresolved"] += 1
                n_unres += 1
                stat["items"].append((uid, line, "C2: " + truth))
                rows.append([uid, str(line), "claim", cmd, res, "stale", truth])
            elif refs:
                rows.append([uid, str(line), "claim", cmd, res, "true", ""])
            else:
                n_noref += 1
                rows.append([uid, str(line), "claim", cmd, res, "unverifiable",
                             "names no path or symbol; its behavioural truth (C1) was not executed by this harness"])
    if a.ledger:
        Path(a.ledger).write_text("\n".join("\t".join(c.replace("\t", " ").replace("\n", " ") for c in r) for r in rows) + "\n")
    if a.show:
        for f, s in per_file.items():
            for uid, line, truth in s["items"]:
                print(f"  {f}:{line}\t{uid}\t{truth}")
    for f, s in per_file.items():
        print(f"RESULT file={f} units={s['units']} unresolved_units={s['unresolved']} long_sentence_units={s['long']}")
    print(f"RESULT units={n_units} count")
    print(f"RESULT references={n_ref} count")
    print(f"RESULT units_with_unresolved_ref={n_unres} count")
    print(f"RESULT units_with_sentence_over_40_words={n_long} count")
    print(f"RESULT units_naming_no_reference={n_noref} count")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        sw = int(next(l.split()[1] for l in open("/proc/vmstat") if l.startswith("pswpin ")))
    except (OSError, StopIteration):
        pass
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
