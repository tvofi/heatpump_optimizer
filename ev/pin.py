import sys, subprocess, json, re, tempfile, os
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import cloud_dispatch as cd
td = tempfile.mkdtemp()
g = lambda *a, cwd=None: subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True, text=True).stdout
origin, work = f"{td}/o.git", f"{td}/w"
g("init", "-q", "--bare", origin); g("init", "-q", work)
g("-C", work, "-c", "user.name=x", "-c", "user.email=x@x", "commit", "-q", "--allow-empty", "-m", "base")
g("-C", work, "remote", "add", "origin", origin)
head = g("-C", work, "rev-parse", "HEAD").strip()
ref = "dispatch/fixer-t-1"
base = dict(env_id="env_x", model="m-1", repo="owner/name", topic="t-1")
msg = lambda p: p["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]
pinof = lambda p: re.search(r"at commit ([0-9a-f]{40}) of ", msg(p)).group(1)
p1 = cd.publish_seat(work, ref, "fixer", head, brief="FIRST brief.\n", **base); pin1 = pinof(p1)
first = g("-C", work, "show", f"{pin1}:PROMPT.md")
p1b = cd.publish_seat(work, ref, "fixer", head, brief="FIRST brief.\n", **base)
print("RESULT same-brief re-dispatch pin unchanged:", pinof(p1b) == pin1)
tip_a = g("-C", work, "ls-remote", origin, "refs/heads/" + ref).split()[0]
p2 = cd.publish_seat(work, ref, "fixer", head, brief="SECOND brief.\n", **base); pin2 = pinof(p2)
tip_b = g("-C", work, "ls-remote", origin, "refs/heads/" + ref).split()[0]
print("RESULT ref moved:", tip_a != tip_b, "pins differ:", pin1 != pin2)
# a fresh clone fetching pin1 by SHA from origin after the ref moved
c = f"{td}/c"; g("init", "-q", c); g("-C", c, "fetch", "-q", origin, pin1)
again = g("-C", c, "show", f"{pin1}:PROMPT.md")
print("RESULT first seat's pinned PROMPT.md unchanged after re-dispatch:", again == first and "FIRST brief." in again and "SECOND" not in again)
print("RESULT pin1 ancestor of moved tip:", subprocess.run(["git","-C",work,"merge-base","--is-ancestor",pin1,tip_b]).returncode == 0)
print("RESULT second pin reads second brief:", "SECOND brief." in g("-C", work, "show", f"{pin2}:PROMPT.md"))
# same prompt, changed payload (model) then same again
p3 = cd.publish_seat(work, ref, "fixer", head, brief="SECOND brief.\n", **{**base, "model": "m-2"})
print("RESULT model-only change keeps pin:", pinof(p3) == pin2)
p4 = cd.publish_seat(work, ref, "fixer", head, brief="SECOND brief.\n", **{**base, "model": "m-2"})
print("RESULT identical re-dispatch after model change pin:", pinof(p4) == pinof(p3), pinof(p4)[:8], pinof(p3)[:8])
print("RESULT payload size", len(json.dumps(p2)), "stub", len(msg(p2)))
