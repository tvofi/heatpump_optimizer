"""Round-2 reviewer: round-1 reviewer's ev/replay.py, worktree at the round-2 head, range ended at the round-1 tip ce4a2386,
and each roster_sync replay also taken through apply_plan (the write path) to compare written vs derived. Reviewer's own replay: every done-flip on the roster branch since 2026-10-31T00:00,
re-run through the head's closing_stage / roster_edit.apply_op / roster_sync.derive
on the parent commit's roster."""
import json, subprocess, sys, copy
WT = "/home/user/wt-head"
sys.path[:0] = [WT + "/tools/audit/seat", WT + "/tools/audit"]
import roster_lib, roster_edit, roster_sync
REL = "dev/programme/rosters/wave-r10-groups.json"
REPO = "/home/user/heatpump_optimizer"
def git(*a): return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True).stdout
legacy = roster_lib.read_legacy(REPO, REL)
print(f"legacy at cut-over: {sum(len(v) for v in legacy.values())} carries over {len(legacy)} groups")
commits = git("log", "--reverse", "--first-parent", "--format=%H %cI %s", "--since=2026-10-31T00:00", "ce4a238673ecba94bbacb194ef74492437738f9e").splitlines()
def load(sha):
    t = subprocess.run(["git", "-C", REPO, "show", f"{sha}:{REL}"], capture_output=True, text=True)
    return json.loads(t.stdout) if t.returncode == 0 else None
flips = 0; refused = []
for line in commits:
    sha, when, subj = line.split(" ", 2)
    par = git("rev-parse", sha + "^1").strip()
    a, b = load(par), load(sha)
    if not a or not b: continue
    ga, gb = roster_lib.groups_of(a), roster_lib.groups_of(b)
    for gid, g in gb.items():
        was = (ga.get(gid, {}).get("resume") or {}).get("stage")
        now = (g.get("resume") or {}).get("stage")
        if now != "done" or was == "done": continue
        flips += 1
        if gid not in ga:
            print(f"{sha[:9]} {when} {gid}: new group appended done"); continue
        pa = ga[gid]
        replay = None
        if "roster_edit set-stage" in subj or "roster_edit set-resume" in subj:
            r = copy.deepcopy(a)
            import io, contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                if "set-stage" in subj:
                    roster_edit.apply_op(r, "set-stage", gid, "done", None, None, None, REL, (), legacy)
                else:
                    roster_edit.apply_op(r, "set-resume", gid, "done", "stage", None, None, REL, (), legacy)
            replay = (roster_lib.groups_of(r)[gid]["resume"]["stage"], buf.getvalue().strip())
        elif "roster_sync" in subj:
            br = (pa.get("resume") or {}).get("branch") or (g.get("resume") or {}).get("branch")
            if not br:
                replay = (roster_lib.closing_stage(pa, "done", legacy)[0], "no branch: closing_stage direct")
            else:
             ch, _, _ = roster_sync.derive(a, [roster_sync.PR(1, roster_sync.MERGED, br, (g.get("resume") or {}).get("commit") or "0"*40, "")], legacy)
             c = [c for c in ch if c.group == gid]
             w = copy.deepcopy(a)
             import io, contextlib
             with contextlib.redirect_stdout(io.StringIO()):
                 roster_sync.apply_plan(w, ch, [], legacy)
             written = (roster_lib.groups_of(w)[gid].get("resume") or {}).get("stage")
             dstage = c[0].stage if c else "no change"
             replay = (written if c else "no change", f"derive branch={br} derived={dstage} written={written} AGREE={dstage==written}")
        else:
            replay = ("(not a roster op)", "")
        pend = roster_lib.pending_carries(pa, legacy)
        mark = "REFUSED->carries-open" if replay[0] == "carries-open" else "stays " + replay[0]
        if replay[0] == "carries-open": refused.append(gid)
        print(f"RESULT {sha[:9]} {when} {gid}: was={was} pending_at_parent={len(pend)} head-code={mark} | {subj[:60]} | {replay[1][:120]}")
print(f"RESULT done-flips today: {flips}; would now be carries-open: {len(refused)} {refused}")
