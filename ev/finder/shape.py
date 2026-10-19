# Reviewer-built finder-shape measurement (no finder harness is committed for this group).
# Takes PR #2442's own live body (it quotes "`## Head` note" in its first line, above the heading,
# the #2400 shape), stubs its ## Head section to name the previous head, then applies one recarry
# with main's app_push.sh locator and with this head's head_note.prefix.
import re, sys
sys.path.insert(0, sys.argv[2] + "/tools/pr")
from head_note import prefix
body = open(sys.argv[1]).read()
a = body.index("\n## Head\n"); b = body.index("\n## Mutation proof")
stub = body[:a] + "\n## Head\n\n`bef08da499276ead55f0f8457479f116fa730e85` is the code head.\n" + body[b:]
open("stub.md", "w").write(stub)
note = "`b9f201f90efbb39422319426a7839c036b7b46af` merges main `c3530277` into the previous head."
s = stub; i = s.index('\n', s.index('## Head')) + 1
while s[i:i+1] == '\n': i += 1
open("base.md", "w").write(s[:i] + note + "\n\n" + s[i:])
open("head.md", "w").write(prefix(stub, note))
