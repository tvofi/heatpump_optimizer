import sys, json, subprocess
WT="/home/user/wt"; sys.path[:0]=[WT+"/tools/audit/seat", WT+"/tools/audit"]
import roster_lib as L
REL="dev/programme/rosters/wave-r10-groups.json"; REPO="/home/user/heatpump_optimizer"
leg=L.read_legacy(REPO, REL)
live=json.loads(subprocess.run(["git","-C",REPO,"show",f"origin/handoff/audit-r10-roster:{REL}"],capture_output=True,text=True).stdout)
cut=L.groups_of(L.show_roster(REPO,L.CARRY_CUTOVER[REL],REL))
g=L.groups_of(live)["R10-NIGHTLY-HB-RESPAWN"]
print("RESULT NIGHTLY-HB-RESPAWN at cut-over:", cut["R10-NIGHTLY-HB-RESPAWN"]["resume"]["stage"], len(cut["R10-NIGHTLY-HB-RESPAWN"]["carry"]), "carries; live:", g["resume"]["stage"], len(g["carry"]), "pending idx:", L.pending_carries(g, leg), "legacy held:", len(leg.get("R10-NIGHTLY-HB-RESPAWN",())))
# unreadable cut-over
L.CARRY_CUTOVER[REL]="f"*40
try: L.read_legacy(REPO, REL); print("RESULT bogus cut-over: returned (BAD)")
except L.RosterNotFound as e: print("RESULT bogus cut-over: RosterNotFound:", str(e)[:120])
except Exception as e: print("RESULT bogus cut-over: other", type(e).__name__, e)
print("RESULT no entry ->", L.read_legacy(REPO, "dev/programme/rosters/wave-r11-groups.json"))
