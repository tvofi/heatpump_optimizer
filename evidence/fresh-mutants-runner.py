import subprocess, sys, pathlib
W = pathlib.Path(sys.argv[1]); f = W/"mut/tools/pr/app_approve.sh"
orig = f.read_text()
SED = "s/^gh: (.*\\()?HTTP ([0-9]{3})\\)?$/\\2/p"
TR = "'^Get \"https?://[^\"]*\": |^error connecting to '"
M = [
 ("F0 null", None, None),
 ("F2 sed {3}->{3,}", SED, SED.replace("{3}", "{3,}")),
 ("F3 sed \\)?$ -> \\)$", SED, SED.replace("\\)?$", "\\)$")),
 ("F4 sed [0-9]{3} -> [0-9]+", SED, SED.replace("[0-9]{3}", "[0-9]+")),
 ("F5 label 5?? -> 5*", "    5??|429) return 0 ;;", "    5*|429) return 0 ;;"),
 ("F6 label 403 -> 40?", "    403) printf", "    40?) printf"),
 ("F7 label 429 -> 42?", "    5??|429) return 0 ;;", "    5??|42?) return 0 ;;"),
 ("F8 transport [^\"]* -> .*", TR, TR.replace('[^"]*', '.*')),
 ("F9 transport grep -qE -> -q", "grep -qE '^Get", "grep -q '^Get"),
 ("F10 tail -1 -> tail -2", "\\2/p' | tail -1)", "\\2/p' | tail -2)"),
 ("F11 drop trailing space of 'error connecting to '", "|^error connecting to '", "|^error connecting to'"),
 ("F12 drop trailing space of Get pattern", '[^"]*": |', '[^"]*":|'),
 ("F13 403 grep only the status line", "403) printf '%s\\n' \"$1\" | grep", "403) printf '%s\\n' \"$1\" | tail -1 | grep"),
 ("F14 secondary grep -qi -> -qiw", "grep -qi 'secondary rate limit'", "grep -qiw 'secondary rate limit'"),
 ("F15 ?*) return 1 -> ???) return 1", "    ?*) return 1 ;;", "    ???) return 1 ;;"),
 ("F16 GH_ERR fold drops sed trim", "GH_ERR=$(tr '\\n' ' ' < \"$_ef\" | sed 's/ *$//')", "GH_ERR=$(tr '\\n' ' ' < \"$_ef\")"),
 ("F17 sed -nE -> -n", "sed -nE 's/^gh:", "sed -n 's/^gh:"),
 ("F18 secondary phrase -> 'secondary rate limit exceeded'", "grep -qi 'secondary rate limit'", "grep -qi 'secondary rate limit exceeded'"),
]
for name, a, b in M:
    if a is not None:
        assert orig.count(a) >= 1, (name, a)
        f.write_text(orig.replace(a, b, 1))
    p = subprocess.run(["bash", "tools/pr/app_approve.sh", "--self-test"], cwd=W/"mut", capture_output=True, text=True)
    f.write_text(orig)
    out = (p.stdout+p.stderr).splitlines()
    fails = [l for l in out if l.startswith("FAIL")]
    summ = [l for l in out if "checks," in l]
    print(f"{name}: rc={p.returncode} {summ[-1] if summ else ''} {'KILLED' if p.returncode else 'SURVIVED'}")
    for l in fails[:4]: print("    ", l)
    sys.stdout.flush()
