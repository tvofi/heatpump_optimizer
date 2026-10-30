import json, re, subprocess, sys
# Rule: every "Fix review: blocked <sha> <word>:" issue comment on a PR merged in the window
# whose class word is one of the mutation family's members (policy_lint FRICTION_FAMILIES 'mutation'
# plus the untaught mutation-unpinned / unpinned-site / mutation-untriaged), with the
# mutation_table site keys its Block section cites (empty = no site key: a tools/ or hand mutant).
FAM = {"mutation","mutation-vacuous","mutation-survivor","test-vacuous","vacuous-test","vacuous-check",
       "mutant-survives","mutation-unpinned","unpinned-site","mutation-untriaged"}
KINDS = "GUARD_OFF|RETURN_DEL|CMP_BOUND|CLAMP_DROP|RAISE_DEL|BOOLOP|CONST"
SITE = re.compile(r"([\w/.-]+\.py):(\d+)\s+(%s)" % KINDS)
HEAD = re.compile(r"^Fix review: blocked [0-9a-f]{40} ([a-z][a-z0-9-]*)")
R = "repos/tvofi/heatpump_optimizer"
for n in open(sys.argv[1]).read().split():
    out = subprocess.run(["gh","api","--paginate","--slurp",f"{R}/issues/{n}/comments"],capture_output=True,text=True)
    if out.returncode: print(f"#{n}\tFETCH-FAILED", flush=True); continue
    for c in [c for p in json.loads(out.stdout) for c in p]:
        b = c.get("body") or ""
        m = HEAD.match(b)
        if not m: continue
        words = {m.group(1)} | set(re.findall(r";\s*([a-z][a-z0-9-]*):", b.splitlines()[0]))
        if not words & FAM: continue
        blk = b.split("## Findings")[0]
        sites = sorted({f"{p.split('/')[-1]}:{l} {k}" for p,l,k in SITE.findall(blk)})
        auto = "pinned by mutation-autofix" in blk or "pinned by `mutation-autofix`" in blk
        print(f"#{n}\t{c['created_at']}\t{','.join(sorted(words & FAM))}\tsites={len(sites)}\tautofix-claim={auto}\t{' ; '.join(sites)[:200]}", flush=True)
