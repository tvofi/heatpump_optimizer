#!/bin/sh
# Round-9 local, UNPUSHED patch to .claude/workflows/audit-find.js (apply AFTER r9-prepare-patch.sh).
# tvofi 2026-09-26T11:25Z (cmsg_01EL5jLi4rokGBbkaevYXSJV4UhugKT9souwD18jygSeVk): intake the findings in,
# let the last three seats catch up later. Adds args.defer (seat ids intake does not wait for) and
# args.judge_flags (text the register carries to the judge); the leads seat strips earlier rounds.
f="${1:-.claude/workflows/audit-find.js}"
python3 - "$f" <<'PY'
import sys
p=sys.argv[1]; s=open(p).read()
def rep(old,new):
    global s
    assert s.count(old)==1, 'anchor not found: '+old[:60]
    s=s.replace(old,new)
rep("const from = args?.from\n",
    "const from = args?.from\nconst defer = Array.isArray(args?.defer) ? args.defer : []\nconst judgeFlags = typeof args?.judge_flags === 'string' ? args.judge_flags : ''\n")
rep("const missing = SEATS.map((s) => s.id).filter((id) => !reports[id])\n",
    "const missing = SEATS.map((s) => s.id).filter((id) => !reports[id] && !defer.includes(id))\nif (defer.length) log(`deferred to the catch-up batch (tvofi 2026-09-26): ${defer.join(', ')}`)\n")
rep("docs/audit-*.md and docs/backlog.md deleted; tools/audit/ copied in), and work only there,",
    "docs/audit-*.md and docs/backlog.md deleted; tools/audit/ copied in; then run handoff/round9/r9-strip-rounds.sh from origin/handoff/audit-r9-plan on that export so no tools/audit/round[0-8] evidence the gate does not read is left in it), and work only there,")
rep("Every finding below gets its own row.",
    "Every finding below gets its own row.${defer.length ? ` This is BATCH 1 of round ${round}: seats ${defer.join(', ')} have not reported and are deferred to a catch-up batch by tvofi's decision of 2026-09-26; list them in the dimension status table as \"deferred (catch-up)\", and note that the catch-up batch adds their rows and updates their dimensions' rotation entries.` : ''}${judgeFlags ? ` Add a \"Judge flags\" subsection to the register section with exactly this text: ${JSON.stringify(judgeFlags)}.` : ''}")
open(p,'w').write(s); print('patched', p)
PY
