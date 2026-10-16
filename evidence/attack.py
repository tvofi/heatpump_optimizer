import json, subprocess, sys, os
root = os.getcwd(); rn = os.path.join(root, "RELEASE_NOTES.md"); H = "## v9.9.9"
def me(*ns): return {"file_path": rn, "edits": [{"old_string": f"o{i}", "new_string": n} for i, n in enumerate(ns)]}
CASES = [
 # (label, tool_input, want) want = what a correct heading rule should say
 ("A01 Write CRLF heading",                {"file_path": rn, "content": "- b\r\n" + H + "\r\n"}, "refuse"),
 ("A02 Edit CRLF heading",                 {"file_path": rn, "old_string": "x", "new_string": "- b\r\n" + H + "\r\n"}, "refuse"),
 ("A03 MultiEdit CRLF heading, edit 2",    me("- b\r\n", "- c\r\n" + H + "\r\n"), "refuse"),
 ("A04 MultiEdit CR-only heading",         me("- b\r" + H), "refuse"),
 ("A05 MultiEdit indented heading",        me("   " + H), "refuse"),
 ("A06 MultiEdit heading mid new_string",  me("- a\n" + H + "\n- c\n"), "refuse"),
 ("A07 MultiEdit heading in edit 3 of 3",  me("- a", "- b", H), "refuse"),
 ("A08 MultiEdit no trailing newline prev",me("- a no newline", H), "refuse"),
 ("A09 MultiEdit split '##' + ' v9.9.9'",  me("##", " v9.9.9"), "escape-by-design?"),
 ("A10 Edit split '##' (rest in file)",    {"file_path": rn, "old_string": "XX", "new_string": "##"}, "escape-by-design?"),
 ("A11 MultiEdit tab heading",             me("##\tv9.9.9"), "escape-by-design?"),
 ("A12 NotebookEdit notebook_path+new_source", {"notebook_path": rn, "new_source": H}, "refuse"),
 ("A13 MultiEdit + top-level new_string",  {"file_path": rn, "new_string": "- a", "edits": [{"old_string": "x", "new_string": H}]}, "refuse"),
 ("A14 MultiEdit edits is dict",           {"file_path": rn, "edits": {"new_string": H}}, "allow(fail-open)"),
 ("A15 MultiEdit mixed [7, heading]",      {"file_path": rn, "edits": [7, {"old_string": "x", "new_string": H}]}, "refuse"),
 ("A16 MultiEdit body only (null)",        me("- a", "- b\r\n"), "allow"),
 ("A17 MultiEdit '###' subheading",        me("### Fixes"), "allow?"),
 ("A18 MultiEdit 'v9.9.9 ##' not heading", me("text ## v9"), "allow"),
 ("A19 MultiEdit on main",                 me(H), "allow(main)"),
]
def decide(branch, ti, hook):
    r = subprocess.run(["bash", "-c", 'eval "$(sed -n "/^decide()/,/^}/p" "$0")"; decide "$1" "$2"', hook, branch,
                        json.dumps({"tool_name": "X", "tool_input": ti})], capture_output=True, text=True,
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=root))
    return "refuse" if r.stdout.strip() else "allow"
for lab, ti, want in CASES:
    br = "main" if "on main" in lab else "feature"
    print(f"{lab:42s} got={decide(br, ti, '.claude/hooks/pre-edit.sh'):6s} want={want}")
