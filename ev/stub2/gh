#!/opt/hpo/venv-ci/bin/python3 -I
import json, os, sys
a = sys.argv[1:]
with open(os.environ["STUBLOG"], "a") as f: f.write("\x1f".join(a) + "\n")
st = os.environ["STUBLOG"] + ".body"
if "--input" in a:
    b = json.load(open(a[a.index("--input") + 1]))["body"]; open(st, "w").write(b)
    print(json.dumps({"id": 1, "body": b, "html_url": "stub://1"}))
elif "--slurp" in a: print("[[]]")
elif a and a[-1].endswith("issues/comments/1"): print(json.dumps({"id": 1, "body": open(st).read(), "issue_url": "stub"}))
