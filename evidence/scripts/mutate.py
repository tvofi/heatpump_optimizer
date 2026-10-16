import subprocess, sys, os, time
MUT = sys.argv[1]; HEAD = sys.argv[2]; only = sys.argv[3:] 
RPF="tools/audit/seat/ref_privacy.py"; WT="tools/audit/seat/wt_sync.sh"
U="Users"
CHECKS = {
 "RP_ST": ["python3","-I",RPF,"--self-test"],
 "RP_CK": ["python3","-I",RPF,"--check"],
 "SD_ST": ["python3","tools/audit/seat/state_docs.py","--self-test"],
 "RE_ST": ["python3","tools/audit/seat/roster_edit.py","--self-test"],
 "AP_ST": ["bash","tools/pr/app_push.sh","--self-test"],
 "PS_ST": ["bash","tools/pr/push.sh","--self-test"],
 "BUS_ST": ["bash","tools/audit/seat/bus.sh","--self-test"],
 "STAMP_TITLE": ["bash","-c",f"out=$(python3 tools/release/stamp.py --bump patch --title '/{U}/exampleuser/y' --dry-run 2>&1); echo \"$out\" | tail -2; echo \"$out\" | grep -q 'would publish this host'"],
}
GUARD_WT1 = '  python3 -I "$RP" guard --ref "wip-sync/$slug" --message "$msg" --commits "$head" -C "$w" || return\n'
M = [
 ("M1 old wt_sync slug", [(WT,'slug=$(python3 -I "$RP" slug "$w" --root repo="$R") || continue',"slug=$(echo \"${w#$HOME/}\" | sed 's#^/##; s#[^A-Za-z0-9._-]#-#g')")], ["RP_ST"]),
 ("M2 wt_sync per-worktree guard deleted", [(WT,GUARD_WT1,"")], ["RP_ST","RP_CK"]),
 ("M3 refusal() returns None", [(RPF,'    ident = ident or Identity.of_host()\n    why = leaks(ref, ident)','    return None\n    ident = ident or Identity.of_host()\n    why = leaks(ref, ident)')], ["RP_ST"]),
 ("M4 slug fallback deleted", [(RPF,"if refusal(cand, (), ident) is not None or not cand:","if not cand:")], ["RP_ST"]),
 ("M5 account-name predicate deleted", [(RPF,'    if any(re.search(r"(?<![a-z0-9])"','    if False and any(re.search(r"(?<![a-z0-9])"')], ["RP_ST"]),
 ("M6 body_push guard deleted", [("tools/audit/seat/body_push.sh",'python3 -I "$(dirname "$0")/ref_privacy.py" guard --ref "$REF" --message "body: $TOPIC"\n',"")], ["RP_ST","RP_CK"]),
 ("M7 state_docs guard neutered", [("tools/audit/seat/state_docs.py",'        if why:\n            raise Refuse(f"{why} would publish this host (#2310); nothing committed")','        if False:\n            raise Refuse(f"{why} would publish this host (#2310); nothing committed")')], ["SD_ST","RP_CK"]),
 ("M8 roster_edit guard neutered", [("tools/audit/seat/roster_edit.py",'        if why:\n            raise Refuse(f"{why} would publish this host (#2310); nothing written")','        if False:\n            raise Refuse(f"{why} would publish this host (#2310); nothing written")')], ["RE_ST","RP_CK"]),
 ("M9 app_push guard deleted", [("tools/pr/app_push.sh",'  python3 -I "$(cd "$(dirname -- "$0")/../audit/seat" && pwd)/ref_privacy.py" guard --ref "$br" --commits "$head" -C "$wt" \\\n    || die "the branch or a commit it publishes would publish this host (#2310); NOTHING was minted or pushed"\n',"")], ["AP_ST","RP_CK"]),
 ("M10 bus guard deleted", [("tools/audit/seat/bus.sh",'  python3 -I "$ROOT/tools/audit/seat/ref_privacy.py" guard --ref "$fam/$pr" --message "$msg" \\\n    || { printf \'bus: REFUSE: %s/%s would publish this host (#2310)\\n\' "$fam" "$pr" >&2; return 1; }\n',"")], ["BUS_ST","RP_CK"]),
 ("M11 push.sh guard deleted", [("tools/pr/push.sh",'  python3 -I "$(cd "$(dirname -- "$0")/../audit/seat" && pwd)/ref_privacy.py" guard --ref "$BR" --commits HEAD \\\n    || { say REFUSE "push" "the branch or a commit it publishes would publish this host (#2310)"; exit 5; }\n',"")], ["PS_ST","RP_CK"]),
 ("M12 stamp guard deleted", [("tools/release/stamp.py",'    import ref_privacy\n    why = ref_privacy.refusal("main", (("the title", args.title),))\n    if why:\n        raise Refuse("title", why + " would publish this host; nothing was written")\n',"")], ["RP_CK","STAMP_TITLE"]),
 ("M13 wt_sync orchestrator-scratch guard deleted", [(WT,'python3 -I "$RP" guard --ref wip-sync/orchestrator-scratch --message "$msg" || exit 3\n',"")], ["RP_ST","RP_CK"]),
 ("M14 bus guard bypassed by name (true ||)", [("tools/audit/seat/bus.sh",'  python3 -I "$ROOT/tools/audit/seat/ref_privacy.py" guard','  true || python3 -I "$ROOT/tools/audit/seat/ref_privacy.py" guard')], ["BUS_ST","RP_CK"]),
 ("M15 stamp guard neutered (if False)", [("tools/release/stamp.py",'    if why:\n        raise Refuse("title"','    if False:\n        raise Refuse("title"')], ["RP_CK","STAMP_TITLE"]),
 ("M16 push.sh --commits dropped", [("tools/pr/push.sh",'guard --ref "$BR" --commits HEAD','guard --ref "$BR"')], ["PS_ST","RP_CK"]),
 ("M17 Users- dash arm dropped", [(RPF,'    r"|(?<![A-Za-z0-9])Users-(?!(?:root|runner|user)(?:-|$|[^A-Za-z0-9._]))[A-Za-z0-9._]")','    r"|(?!x)x")')], ["RP_ST"]),
 ("M18 scratch-root class dropped", [(RPF,"    if _SCRATCH_ROOT.search(text):","    if False:")], ["RP_ST"]),
 ("M19 uid class dropped", [(RPF,'    if ident.uid is not None and re.search','    if False and re.search')], ["RP_ST"]),
 ("M20 home-directory class dropped", [(RPF,'    if any(h.casefold() in folded for h in ident.homes):','    if False:')], ["RP_ST"]),
 ("M21 /var/folders arm dropped", [(RPF,'    r"|/var/folders/"\n','')], ["RP_ST"]),
 ("M22 --not --remotes dropped", [(RPF,'rev, "--not", "--remotes"],','rev],')], ["RP_ST"]),
 ("M23 calls_guard all->any", [(RPF,"return all(r.search(text) for r in _GUARD_CALL)","return any(r.search(text) for r in _GUARD_CALL)")], ["RP_ST"]),
 ("M24 unpublishable check dropped", [(RPF,"    if not _REF_CHARS.match(ref):","    if False:")], ["RP_ST"]),
 ("M25 app_push --commits dropped", [("tools/pr/app_push.sh",'guard --ref "$br" --commits "$head" -C "$wt"','guard --ref "$br"')], ["AP_ST"]),
 ("M26 wt_sync --commits dropped", [(WT,'--message "$msg" --commits "$head" -C "$w" || return','--message "$msg" || return')], ["RP_ST"]),
 ("M27 guard CLI exit 3 -> 0", [(RPF,"            return 3\n","            return 0\n")], ["RP_ST"]),
 ("M28 stale-entry refusal dropped", [(RPF,'        out.append(f"{path}: registered in PUSHERS but holds no push site; drop the entry")','        pass')], ["RP_ST"]),
 ("M29 site rule's Python-call arm dropped", [(RPF,'    r"|\\b(?:git|g|run|runner|sh|_git|_rg)\\([^)\\n]*[\\"\']push[\\"\']")','    r"|(?!x)x")')], ["RP_ST","RP_CK"]),
 ("M30 commit_messages fail-open on git error", [(RPF,'    if out.returncode != 0:\n        raise RuntimeError','    if False:\n        raise RuntimeError')], ["RP_ST"]),
]
def sh(cmd): return subprocess.run(cmd, cwd=MUT, capture_output=True, text=True)
for name, edits, checks in M:
    if only and name.split()[0] not in only: continue
    assert sh(["git","status","--porcelain","--untracked-files=no"]).stdout == "", "dirty"
    ok = True
    for f, old, new in edits:
        p = os.path.join(MUT, f); t = open(p).read()
        if t.count(old) != 1: print(f"{name}: SETUP-FAIL {f} count={t.count(old)}"); ok=False; break
        open(p,"w").write(t.replace(old,new))
    if not ok:
        sh(["git","checkout","--","."]); continue
    sh(["git","-c","user.name=rev","-c","user.email=rev@example.invalid","commit","-qam","mutant","--no-verify"])
    res = []
    for c in checks:
        t0=time.time(); r = sh(CHECKS[c]); out=(r.stdout+r.stderr)
        fails=[l.strip() for l in out.splitlines() if "FAIL" in l or "REFUSE" in l][:3]
        res.append(f"{c}={'RED' if r.returncode else 'green'}({time.time()-t0:.0f}s){' '+' | '.join(fails) if r.returncode and fails else ''}")
    killed = any("=RED" in x for x in res)
    print(f"{'KILLED  ' if killed else 'SURVIVED'} {name}: " + "; ".join(res)[:900], flush=True)
    sh(["git","reset","-q","--hard",HEAD])
