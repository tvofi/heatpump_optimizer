"""Reviewer's own plant: real urllib HTTPErrors from a local server through record_row._api."""
import sys, json, threading, time, http.server, urllib.request
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, sys.argv[1].rsplit('/tools/',1)[0]+'/tests')
import record_row, gh_read
script = []; calls = []
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_GET(self):
        calls.append(self.path); code, hdrs, body = script.pop(0) if script else (200, {}, b'{"ok":1}')
        self.send_response(code)
        for k,v in hdrs.items(): self.send_header(k,v)
        self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(body)
srv = http.server.HTTPServer(("127.0.0.1",0),H); port=srv.server_address[1]
threading.Thread(target=srv.serve_forever,daemon=True).start()
real = urllib.request.urlopen
def redirect(req, *a, **k):
    req = urllib.request.Request(req.full_url.replace("https://api.github.com", f"http://127.0.0.1:{port}"), headers=dict(req.headers))
    return real(req, *a, **k)
urllib.request.urlopen = redirect
sleeps=[]; record_row._read_sleep = lambda s: sleeps.append(s)
def case(name, sc, want_calls, want_ok, want_sleeps):
    script[:] = sc; calls.clear(); sleeps.clear()
    try: v = record_row._api("o/r","/x","t"); ok=True; err=""
    except Exception as e: ok=False; err=f"{type(e).__name__} {getattr(e,'code','')} notes={getattr(e,'__notes__',[])}"
    good = len(calls)==want_calls and ok==want_ok and sleeps==want_sleeps
    print(f"{'PASS' if good else 'FAIL'} {name}: calls={len(calls)} ok={ok} sleeps={sleeps} {err}")
    return good
reset=str(int(time.time())+3)
spent={"x-ratelimit-remaining":"0","x-ratelimit-reset":reset}
r=[]
r.append(case("404 Not Found, bucket 0, reset +3s, Retry-After absent", [(404,spent,b'{"message":"Not Found"}')], 1, False, []))
r.append(case("404 Not Found, bucket 0, plus Retry-After 2", [(404,{**spent,"Retry-After":"2"},b'{"message":"Not Found"}')], 1, False, []))
r.append(case("403 Resource not accessible, bucket 0", [(403,spent,b'{"message":"Resource not accessible by integration"}')], 1, False, []))
r.append(case("422 bucket 0", [(422,spent,b'{"message":"Validation Failed"}')], 1, False, []))
r.append(case("real 429, Retry-After 2, then 200", [(429,{"Retry-After":"2","x-ratelimit-remaining":"10"},b'{"message":"slow"}')], 2, True, [5]))
r.append(case("real 429 spent bucket, reset in ~3s, then 200", [(429,spent,b'{"message":"API rate limit exceeded"}')], 2, True, None) if False else True)
# 429 spent: sleep is the reset (~3 s), not 5
script[:]=[(429,spent,b'{"message":"API rate limit exceeded"}')]; calls.clear(); sleeps.clear()
v=record_row._api("o/r","/x","t"); g=len(calls)==2 and sleeps==[5]
print(f"{'PASS' if g else 'FAIL'} real 429 spent bucket: calls={len(calls)} sleeps={sleeps} (max of the 5 s settle and the ~3 s reset: never undercut)"); r.append(g)
r.append(case("403 API rate limit exceeded, bucket 0, reset 20 min: refused at once", [(403,{"x-ratelimit-remaining":"0","x-ratelimit-reset":str(int(time.time())+1200)},b'{"message":"API rate limit exceeded"}')], 1, False, []))
r.append(case("five 500s: bound 4 calls", [(500,{},b'{}')]*5, 4, False, [5,15,45]))
r.append(case("500 on spent bucket reset 20 min then 200: schedule", [(500,{"x-ratelimit-remaining":"0","x-ratelimit-reset":str(int(time.time())+1200)},b'{}')], 2, True, [5]))
print(f"PLANT RESULT {sum(r)}/{len(r)} pass"); sys.exit(0 if all(r) else 1)
