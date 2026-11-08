# Reviewer's own mutant driver: apply one textual mutation to a copy of the hook, run its --self-test.
import subprocess, sys, shutil, os, tempfile
HOOK = sys.argv[1]
src = open(HOOK).read()
M = [
 ("P1 bash -c body never parsed", "#         if shellc:\n#             shellc = False", "#         if False:\n#             shellc = False"),
 ("P2 eval words never collected", "#                         body = []\n", "#                         body = None\n"),
 ("P3 ( no longer reopens command position", "#         if c == \"(\":\n#             end(); at = True", "#         if c == \"(\":\n#             end(); at = False"),
 ("P4 unquoted $( ) skipped", "#             elif s[i:i+2] == \"$(\":\n#                 i = parse(s, i + 2, \")\"); quoted_sub = True\n#             elif ch == \"`\":", "#             elif s[i:i+2] == \"$(\":\n#                 i = s.find(\")\", i) + 1 or n; quoted_sub = True\n#             elif ch == \"`\":"),
 ("P5 guard ignores cd", "#                 cur = under(cur, to[0])", "#                 pass"),
 ("P6 guard arm reads its own split (cmds emptied)", "# MOVERS = {", "# cmds = [(0, x.split()[0], x.split()) for x in re.split(r'\\n|;|&&|\\|\\||\\||&', cmd) if x.split()]\n# MOVERS = {"),
 ("P7 end() drops eval body", "#         if body:\n#             parse(", "#         if False:\n#             parse("),
 ("N0 null control: comment-only", "# # Second arm:", "# # Second arm (comment edited):"),
]
for name, a, b in M:
    if src.count(a) != 1:
        print(f"RESULT {name}: ANCHOR-MISSING count={src.count(a)}"); continue
    d = tempfile.mkdtemp(); os.makedirs(d+"/.claude/hooks"); os.makedirs(d+"/tests"); shutil.copy(os.path.join(os.path.dirname(HOOK),"../../tests/throwaway_git.sh"), d+"/tests/"); p = os.path.join(d, ".claude/hooks/pre-bash.sh")
    open(p, "w").write(src.replace(a, b)); os.chmod(p, 0o755)
    r = subprocess.run(["bash", p, "--self-test"], capture_output=True, text=True)
    fails = [l.strip() for l in r.stdout.splitlines() if "FAIL" in l]
    print(f"RESULT {name}: {'KILLED' if fails or r.returncode else 'SURVIVED'} rc={r.returncode} {fails[:4]}")
    shutil.rmtree(d)
