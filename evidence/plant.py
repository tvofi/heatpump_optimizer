import sys, io, time, urllib.error, email.message
sys.path.insert(0, sys.argv[1]); import gh_read as g
def err(code, hdr=None, body=b"{}"):
    m = email.message.Message()
    for k,v in (hdr or {}).items(): m[k]=v
    return urllib.error.HTTPError("https://api.github.com/x", code, "R", m, io.BytesIO(body))
def run(name, make, n_fail=9):
    calls=[0]; sleeps=[]
    def attempt():
        calls[0]+=1
        return (None, make()) if calls[0]<=n_fail else ("ok", None)
    v,f,n,why = g.retry(attempt, g.urllib_wait, sleeps.append)
    print(f"RESULT plant={name} calls={calls[0]} sleeps={sleeps} answered={f is None} why={why!r}")
run("404", lambda: err(404))
run("500", lambda: err(500))
run("500x2", lambda: err(500), n_fail=2)
run("422", lambda: err(422))
run("403perm", lambda: err(403, body=b'{"message":"Resource not accessible by integration"}'))
run("403secondary", lambda: err(403, body=b'{"message":"You have exceeded a secondary rate limit"}'))
run("urlerror", lambda: urllib.error.URLError("conn reset"))
run("404_bucket0", lambda: err(404, {"x-ratelimit-remaining":"0","x-ratelimit-reset":str(int(time.time())+10)}))
for t,exp in [("gh: Not Found (HTTP 404)",False),("gh: Server Error (HTTP 500)",True),('Get "https://api.github.com/x": net/http: timeout',True),("HTTP 502: Bad gateway (https://api.github.com/graphql)",True),("HTTP 404: nope (https://api.github.com/graphql)",False)]:
    print(f"RESULT gh_transient {t!r} -> {g.gh_transient(t)} expect {exp}")
for a in [["gh","api","repos/o/r"],["gh","api","-X","PATCH","x"],["gh","api","x","-fbody=1"],["gh","api","--input","f","x"],["gh","pr","merge","1"],["gh","pr","view","1"]]:
    print("RESULT is_read", a, g.is_read(a))
