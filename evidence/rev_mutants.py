# Reviewer-built mutants for PR #3143 (not the fixer's): extends the in-tree driver's PLANTS.
import importlib.util, sys
p = sys.argv[1]
spec = importlib.util.spec_from_file_location("m", p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.PLANTS.clear()
m.PLANTS.update({
 # drop set-size's unknown-group refusal
 "R1": ('    g = _need(roster, group)\n    if not size:', f'    {m.DETACHED}\n    if not size:'),
 # drop hot-token refusal entirely (different spelling from Z8)
 "R2": ('        bad = [t for t in hot if t not in base and t not in known]\n', '        bad = []\n'),
 # hot-token check ignores the basename arm (only known tokens)
 "R3": ('        base = {f.rstrip("/").rsplit("/", 1)[-1] for f in files} | set(files)\n', '        base = set()\n'),
 # drop set-files resume.note record
 "R4": ('        _note_append(g, _cited("set-files " + "; ".join(notes), cite))\n', '        pass\n'),
 # drop set-size resume.note record
 "R5": ('    _note_append(g, _cited(f"set-size {old or \'unset\'} -> {size}", cite))\n', '    pass\n'),
 # note omits the cite
 "R6": ('    return f"{text} (cite {cite})" if cite else text\n', '    return text\n'),
 # set-files touches another field
 "R7": ('    if notes:\n        _note_append', '    if notes:\n        g["brief"] = (g.get("brief") or "") + " x"\n        _note_append'),
 # set-files touches another field (stage)
 "R8": ('    if notes:\n        _note_append', '    if notes:\n        g["stage"] = "done"\n        _note_append'),
 # skip the lint for the new ops
 "R9": ('        ok, detail = lint_gate(checkout, lint_cwd, path)\n', '        ok, detail = (True, "") if label.startswith(("set-files", "set-size")) else lint_gate(checkout, lint_cwd, path)\n'),
 # path_in_tree ignores the cited sha
 "R10": ('    revs = ["origin/main"] + ([CITE_RE.match(cite).group(2)] if cite else [])\n', '    revs = ["origin/main"]\n'),
 # cite_why drops the ancestry check
 "R11": ('                    and _git_ok(checkout, "merge-base", "--is-ancestor",\n                                sha, cand):', '                    and True:'),
 # set-size writes on a no-op but still note? (write without old==size return, already Z4) -> instead: --set-files ignored when --add given
 "R12": ('    if set_files is not None:\n        files = _paths(set_files, "path")\n', ''),
 # --add duplicates not deduped against existing
 "R13": ('    files += [p for p in dict.fromkeys(add) if p not in files]\n', '    files += list(add)\n'),
 # path check applied only to --add, not --set-files: check skipped when set_files given
 "R14": ('        if p not in old_files and in_tree and not in_tree(p, cite):\n', '        if p not in old_files and in_tree and set_files is None and not in_tree(p, cite):\n'),
})
sys.exit(m.main(sys.argv[2:]))
