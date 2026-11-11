# I3 class sweep, arm A: every (PreToolUse hook refusal x tool shape its matcher admits).
# Seam: a hook refusal that inspects a field of tool_input, and a tool the matcher admits
# whose payload carries the refusable content (or path) in a different field.
# Method: read .claude/settings.json PreToolUse matchers; for each matched tool take the
# documented tool_input shape (SHAPES below: where the path and the written text live);
# derive the refusal targets from the hook's own program block (STAMPED tuple, the
# RELEASE_NOTES.md branch, the .cursor/rules/ prefix); drive the REAL hook end to end on a
# non-main branch name and record which (target, tool) pairs exit 0 (ESCAPE).
# Also lists the writing tools the matcher does NOT admit (MATCHER-GAP rows).
# RESULT seams=<n> escapes=<n>
# --clean     null control: run against a fixed copy (edits[*].new_string flattened) -> escapes=0
# --perturb   one-line re-introduction: drop "new_string" from the inspected tuple -> escapes+1 (Edit)
# Run from repo root: python3 dev/audit/rounds/round10/D14/I3/hook_shape_seams.py [--clean|--perturb]
import json, os, re, subprocess, sys, tempfile, shutil

ROOT = os.getcwd()
HOOK_REL = ".claude/hooks/pre-edit.sh"
SHAPES = {  # tool -> (path field, text fields builder)
    "Edit": lambda p, t: {"file_path": p, "old_string": "x", "new_string": t},
    "Write": lambda p, t: {"file_path": p, "content": t},
    "MultiEdit": lambda p, t: {"file_path": p, "edits": [{"old_string": "x", "new_string": t}]},
    "NotebookEdit": lambda p, t: {"notebook_path": p, "new_source": t},
}
WRITERS = set(SHAPES) | {"Bash"}  # tools that can write a tracked file

settings = json.load(open(os.path.join(ROOT, ".claude/settings.json")))
matched = {}
for ent in settings.get("hooks", {}).get("PreToolUse", []):
    for h in ent.get("hooks", []):
        m = re.search(r"\.claude/hooks/[\w.-]+", h.get("command", ""))
        if m:
            for tool in (ent.get("matcher") or "").split("|"):
                matched.setdefault(m.group(0), set()).add(tool)

src = open(os.path.join(ROOT, HOOK_REL)).read()
if "--clean" in sys.argv:
    anchor = '#                     if k in ("new_string", "content", "new_source"))'
    assert anchor in src
    src = src.replace(anchor, anchor + '\n#     text += " ".join(str(e.get("new_string","")) for e in (ti.get("edits") or []) if isinstance(e, dict))')
if "--perturb" in sys.argv:
    a = 'if k in ("new_string", "content", "new_source"))'
    assert a in src
    src = src.replace(a, 'if k in ("content", "new_source"))')

targets = []
st = re.search(r"STAMPED = \(([^)]*)\)", src)
for p in re.findall(r'"([^"]+)"', st.group(1)) if st else []:
    targets.append((p, "path", ""))
if 'rel == "RELEASE_NOTES.md"' in src:
    targets.append(("RELEASE_NOTES.md", "content", "## v9.9.9\n"))
if 'rel.startswith(".cursor/rules/")' in src:
    targets.append((".cursor/rules/gate-scoping.mdc", "path", ""))

tmp = tempfile.mkdtemp(prefix="i3sweep-")
hook = os.path.join(tmp, "pre-edit.sh"); open(hook, "w").write(src)
seams = escapes = 0
for hrel, tools in matched.items():
    if hrel != HOOK_REL:
        continue
    for tgt, kind, text in targets:
        for tool in sorted(tools):
            seams += 1
            if tool == "NotebookEdit" and not tgt.endswith(".ipynb"):
                print(f"SEAM {hrel} {tgt} {tool} NA (NotebookEdit addresses .ipynb only)"); continue
            payload = {"tool_name": tool, "tool_input": SHAPES[tool](os.path.join(ROOT, tgt), text or "body\n")}
            # decide() reads "$0" for its program: run it through bash with $0 = hook
            r = subprocess.run(["bash", "-c", 'eval "$(sed -n "/^decide()/,/^}/p" "$0")"; decide feature "$1"', hook, json.dumps(payload)],
                               text=True, capture_output=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=ROOT))
            esc = not r.stdout.strip()
            escapes += esc
            print(f"SEAM {hrel} {tgt} {tool} {'ESCAPE' if esc else 'refused'}")
    for w in sorted(WRITERS - tools):
        print(f"MATCHER-GAP {hrel} {w} (not admitted; every refusal is bypassable by this tool)")
shutil.rmtree(tmp)
print(f"RESULT seams={seams} escapes={escapes}")
