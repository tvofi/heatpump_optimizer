import os, subprocess, sys, json
A, T = sys.argv[1], sys.argv[2]
W = "re" + "vo" + "ke" + "d"          # built at runtime, never a literal
MID = "fixture-mandate-0000"
KILL = f"body={W} mandate {MID}"
ENV = {"HOME": f"{A}/home", "PATH": f"{A}/own:{A}/stub:{A}/tools", "HPO_STATE_DIR": f"{A}/home/state"}
LOG = f"{A}/stub.log"
def run(argv, shell=False, cwd=None):
    open(LOG, "w").close()
    p = subprocess.run(argv if not shell else ["bash", "-c", argv], env=ENV, capture_output=True, text=True, cwd=cwd)
    return p.returncode, open(LOG).read()
res = []
def case(label, argv, want, **kw):
    rc, log = run(["gh", *argv] if isinstance(argv, list) else argv, **kw)
    got = "refused" if (rc == 1 and log == "") else ("passed" if log else f"rc{rc}-nolog")
    ok = got == want
    res.append(ok); print(("OK  " if ok else "FAIL"), f"{label}: want {want} got {got} rc={rc} stub={log.strip()[:90]!r}")
R = "repos/tvofi/heatpump_optimizer"
case("planted raw gh api POST kill pairing #201", ["api", "-X", "POST", f"{R}/issues/201/comments", "-f", KILL], "refused")
case("planted, from a bash parent", f"gh api {R}/issues/201/comments -f '{KILL}'", "refused", shell=True)
case("trailing slash", ["api", f"{R}/issues/201/comments/", "-f", KILL], "refused")
case("graphql mutation", ["api", "graphql", "-f", "query=mutation{addComment(input:{subjectId:\"I_x\",body:\"" + W + "\"}){clientMutationId}}"], "refused")
case("graphql mutation upper-case", ["api", "graphql", "-f", "query=MUTATION{addComment(input:{})}"], "refused")
case("graphql mutation via -F query=", ["api", "graphql", "-F", "query=mutation{x}"], "refused")
case("graphql mutation via --raw-field=", ["api", "graphql", "--raw-field=query=mutation{x}"], "refused")
case("graphql variables only, query read query", ["api", "graphql", "-f", "query=query{viewer{login}}"], "passed")
case("gh issue comment 201", ["issue", "comment", "201", "-b", W], "refused")
case("gh issue comment --repo order", ["issue", "comment", "--repo", "tvofi/heatpump_optimizer", "201", "--body", W], "refused")
case("gh issue comment -R after", ["issue", "comment", "201", "--body", W, "-R", "tvofi/heatpump_optimizer"], "refused")
case("gh issue comment --repo=", ["issue", "comment", "--repo=tvofi/heatpump_optimizer", "201", "-b", "x"], "refused")
case("gh -R before issue", ["-R", "tvofi/heatpump_optimizer", "issue", "comment", "201", "-b", "x"], "refused")
case("api full URL", ["api", f"https://api.github.com/{R}/issues/201/comments", "-f", KILL], "refused")
case("api http:// (not https) host", ["api", f"http://api.github.com/{R}/issues/201/comments", "-f", KILL], "refused")
case("api leading slash", ["api", f"/{R}/issues/201/comments", "-f", KILL], "refused")
case("api placeholder {owner}/{repo}", ["api", "repos/{owner}/{repo}/issues/201/comments", "-f", KILL], "refused")
case("api --method POST no field", ["api", "--method", "POST", f"{R}/issues/201/comments"], "refused")
case("api -F body", ["api", f"{R}/issues/201/comments", "-F", KILL], "refused")
case("api --field=body", ["api", f"{R}/issues/201/comments", f"--field={KILL}"], "refused")
case("api --input file", ["api", f"{R}/issues/201/comments", "--input", "/dev/null"], "refused")
case("api stdin --input -", ["api", f"{R}/issues/201/comments", "--input", "-"], "refused")
case("api issues/201 PATCH (issue body)", ["api", "-X", "PATCH", f"{R}/issues/201", "-f", "body=x"], "passed-or-refused")
case("api pulls/201 comments? (PR path)", ["api", f"{R}/pulls/201/comments", "-f", "body=x"], "passed-or-refused")
case("api env var GH_REPO-free -X post lowercase", ["api", "-X", "post", f"{R}/issues/201/comments", "-f", "body=x"], "refused")
case("api uppercase ISSUES segment", ["api", f"{R}/ISSUES/201/comments", "-f", "body=x"], "refused")
case("api uppercase COMMENTS segment", ["api", f"{R}/issues/201/COMMENTS", "-f", "body=x"], "refused")
case("api issue with + sign", ["api", f"{R}/issues/+201/comments", "-f", "body=x"], "refused")
case("gh issue comment via gh alias set? (alias word)", ["co", "201"], "refused")
case("gh pr comment 201", ["pr", "comment", "201", "-b", "x"], "refused")
case("gh pr comment 0x? hex", ["issue", "comment", "0xC9", "-b", "x"], "refused")
case("null: api GET #201 comments", ["api", f"{R}/issues/201/comments"], "passed")
case("null: post #202", ["api", f"{R}/issues/202/comments", "-f", "body=x"], "passed")
case("null: issue comment 202", ["issue", "comment", "202", "-b", "x"], "passed")
case("null: pr view", ["pr", "view", "3223"], "passed")
gc = f"{T}/tools/pr/gh_comment.py"
bf = f"{A}/home/body.md"; open(bf, "w").write("a normal state comment\n")
case("control: normal post via gh_comment.py reaches stub", ["python3", "-I", gc, "post", "--repo", "tvofi/heatpump_optimizer", "--issue", "201", "--body-file", bf], "passed")
print("STUB argv of that control:", open(LOG).read().strip()[:200])
case("spoof: python -c naming gh_comment.py", ["python3", "-c", f"import subprocess;subprocess.run(['gh','api','{R}/issues/201/comments','-f','body=x'])", gc], "refused")
case("spoof: python runpy -m", ["python3", "-m", "runpy", gc], "refused")
print(f"RESULT controls: {sum(res)}/{len(res)} as expected")
