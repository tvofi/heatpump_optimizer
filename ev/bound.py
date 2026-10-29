import sys
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import ref_privacy as rp
R = "/" + "root"; M = "/" + "Users/" + "tim"
rid = rp.Identity.made({R}, {"root"}, 0)
mid = rp.Identity.made({M}, {"tim"}, 501)
cases = [(rid, R + "/x", True), (rid, R, True), (rid, "cd " + R + ".", True), (rid, "'" + R + "/wt'", True),
         (rid, "HOME=" + R, True), (rid, "PATH=/bin:" + R + "/bin", True), (rid, "file://" + R + "/x", True),
         (rid, '"' + R + '"', True), (rid, "(" + R + ")", True), (rid, "`" + R + "/.cache`", True), (rid, R + ":", True),
         (rid, "%2F" + "root%2Fx", True), (rid, R + "/", True), (rid, R + ".\n", True), (rid, R + "...", True),
         (rid, "roles/root-cause.md", False), (rid, "x" + R + "/y", False), (rid, R + "-old", False),
         (rid, R + ".d/x", False), (rid, "." + R + "/x", False), (rid, ".." + R + "/x", False), (rid, R + "fs/x", False),
         (rid, "a-" + R, False), (rid, "_" + R, False),
         (mid, M.upper() + "/x", True), (mid, "/users/TIM/x", True), (mid, "file://" + M + "/x", True),
         (mid, "file://" + M.lower() + "/x", True), (mid, M + "/Library", True), (mid, M + "s/x", False), (mid, M + "-x", False)]
bad = 0
for ident, t, want in cases:
    got = "home-directory" in rp.leaks(t, ident)
    s = rp.scrub(t, ident); after = "home-directory" in rp.leaks(s, ident)
    agree = (got == (s != t) or t.startswith("%2F")) and not after
    flag = "" if got == want and agree else "  <-- MISMATCH"
    bad += bool(flag)
    print(f"{'refuse' if got else 'pass  '} want={'refuse' if want else 'pass'} scrub={s!r} after={after}{flag}  {t!r}")
print(f"RESULT {sys.argv[2]} boundary cases={len(cases)} mismatches={bad}")
