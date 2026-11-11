"""Reviewer's probe: the refusal's predicate (dispatch_group, --part k>1) against roster shapes
the live roster does not hold: a branch spelled in upper case or with '_', and another group whose
resume.branch is fix/<topic>. Synthetic groups in a throwaway local commit; nothing pushed."""
import sys, json, subprocess
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import roster_lib, cloud_dispatch as cd
base = sys.argv[2]
path = roster_lib.roster_path(".", base, None)
roster = json.loads(subprocess.run(["git", "show", f"{base}:{path}"], capture_output=True, text=True, check=True).stdout)
C = [f"Carry {i}." for i in range(8)]
M = {"fixer": "opus"}
cases = [("R10-ZCASE", {"group": "R10-ZCASE", "brief": "x\n", "carry": C, "model": M, "resume": {"branch": "handoff/R10-ZCASE"}},
          {"group": "R10-ZCASE-P2", "brief": "y\n"}),
         ("R10-ZUS", {"group": "R10-ZUS", "brief": "x\n", "carry": C, "model": M, "resume": {"branch": "handoff/r10_zus"}},
          {"group": "R10-ZUS-P2", "brief": "y\n"}),
         ("R10-ZBR", {"group": "R10-ZBR", "brief": "x\n", "carry": C, "model": M},
          {"group": "R10-ZOTHER", "brief": "y\n", "resume": {"branch": "fix/r10-zbr-p2"}}),
         ("R10-ZFREE", {"group": "R10-ZFREE", "brief": "x\n", "carry": C, "model": M}, None)]
for _, a, b in cases:
    roster["groups"] += [a] + ([b] if b else [])
blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], input=json.dumps(roster, indent=2), capture_output=True, text=True, check=True).stdout.strip()
subprocess.run(["git", "update-index", "--add", "--cacheinfo", f"100644,{blob},{path}"], env={"GIT_INDEX_FILE": "/tmp/rv-idx", "PATH": "/usr/bin:/bin"}, check=True)
tree = subprocess.run(["git", "write-tree"], env={"GIT_INDEX_FILE": "/tmp/rv-idx", "PATH": "/usr/bin:/bin"}, capture_output=True, text=True, check=True).stdout.strip()
ref = subprocess.run(["git", "-c", "user.name=r", "-c", "user.email=r@r", "commit-tree", tree, "-m", "probe"], capture_output=True, text=True, check=True).stdout.strip()
cd.publish_seat = lambda *a, **k: {}
cd.design_approved = lambda *a: True
env = {"HPO_CLOUD_ENV_ID": "env_0000000000000000000000000"}
for gid, a, b in cases:
    t = cd._topic_of(a) + "-p2"
    credit = {p: roster_lib.group_for_branch(roster, f"{p}/{t}") for p in ("fix", "handoff")}
    try:
        out = "published " + cd.dispatch_group("fixer", gid, "", repo_dir=".", roster_ref=ref, head="0" * 40, environ=env, design_exempt="probe", part=2)
    except cd.Refusal as e:
        out = "refused: " + str(e)
    print(f"RESULT group={gid} part=2 topic={t} credit={credit} -> {out}")
