"""Reviewer-built (not the finder's: none is committed). Rebuild #2400's pre-recarry body
(its final body less the two misplaced recarry notes and the hand-written fd0f5d9 Head line),
apply two recarries (edc4484 then fd0f5d9) with BASE's app_push locator and HEAD's head_note.prefix,
and read each with pr-contract's reader at <wt>."""
import json, subprocess, sys, importlib.util
wt, src = sys.argv[1], sys.argv[2]
b = json.load(open(src))["body"]
E="`edc4484285a4008f8633764df390df3fe6d9a497` merges main `55dc8d9` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.\n\n"
F="`fd0f5d9459347e1d846d240fd0d3387bad44e275` merges main `5a41a56` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.\n\n"
HAND="`fd0f5d9459347e1d846d240fd0d3387bad44e275` merges origin/main `5a41a5669` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.\n\n"
for x in (F, E, HAND):
    assert x in b, x[:20]; b = b.replace(x, "", 1)
def base_note(s, note):  # origin/main app_push.sh NOTE heredoc locator
    i = s.index('\n', s.index('## Head')) + 1
    while s[i:i+1] == '\n': i += 1
    return s[:i] + note + "\n\n" + s[i:]
spec = importlib.util.spec_from_file_location("hn", wt + "/tools/pr/head_note.py"); hn = importlib.util.module_from_spec(spec); spec.loader.exec_module(hn)
def read(body, h):
    open("/tmp/seat/rev2442/ev/finder/b.md","w").write(body)
    out = subprocess.run(["node","tools/policy/policy_lint.mjs","--pr-body","/tmp/seat/rev2442/ev/finder/b.md","--head",h],cwd=wt,capture_output=True,text=True).stdout
    assert "PR-BODY:" in out
    return "unnamed" if "`## Head` does not name" in out else "named"
he, hf = "edc4484285a4008f8633764df390df3fe6d9a497", "fd0f5d9459347e1d846d240fd0d3387bad44e275"
for name, f in (("base", base_note), ("head", hn.prefix)):
    s1 = f(b, E.strip()); s2 = f(s1, F.strip())
    print("RESULT %s recarry1@edc4484=%s recarry2@fd0f5d9=%s" % (name, read(s1, he), read(s2, hf)))
print("RESULT null: pre-recarry body read at its own head 9f3ae9f? ->", read(b, "ca96324704b7fb88d18f7a474510a97ec6345433"))
