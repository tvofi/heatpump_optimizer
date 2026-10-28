"""Reviewer-built drive (round 5, PR #2577): one-occurrence mutants of main()'s --group
pass-throughs, the refusal arm and GROUP_FLAGS; each applied alone, self-test run, file restored."""
import re, subprocess, sys
from pathlib import Path
F = Path(sys.argv[1]).resolve() / "tools/audit/seat/cloud_dispatch.py"
CALL = 'print(dispatch_group(args.role, args.group, args.model, roster_ref=args.roster_ref,\n                                 head=args.head or "", pr=args.pr, nonce=args.nonce, overlay=args.overlay))'
def call(**sub):
    s = CALL
    for a, b in sub.items():
        s = s.replace(a, b, 1)
    return s
M = [
 ("M0", None, None),
 ("role-const", CALL, call(**{"args.role,": '"fixer",'})),
 ("role-reviewer", CALL, call(**{"args.role,": '"reviewer",'})),
 ("group-const", CALL, call(**{"args.group,": '"R10-Y",'})),
 ("model-const", CALL, call(**{"args.model,": '"m-9",'})),
 ("roster-ref-none", CALL, call(**{"roster_ref=args.roster_ref": "roster_ref=None"})),
 ("head-empty", CALL, call(**{'head=args.head or ""': 'head=""'})),
 ("head-rosterref-swap", CALL, call(**{"roster_ref=args.roster_ref": "roster_ref=args.head", 'head=args.head or ""': 'head=args.roster_ref or ""'})),
 ("pr-empty", CALL, call(**{"pr=args.pr": 'pr=""'})),
 ("nonce-empty", CALL, call(**{"nonce=args.nonce": 'nonce=""'})),
 ("pr-nonce-swap", CALL, call(**{"pr=args.pr": "pr=args.nonce", "nonce=args.nonce": "nonce=args.pr"})),
 ("pr-suffix-1", CALL, call(**{"pr=args.pr": "pr=(args.pr or '')[-1:]"})),
 ("nonce-trunc-3", CALL, call(**{"nonce=args.nonce": "nonce=(args.nonce or '')[:3]"})),
 ("overlay-none", CALL, call(**{"overlay=args.overlay": "overlay=None"})),
 ("refusal-truthy", "getattr(args, dest) != ap.get_default(dest)", "getattr(args, dest)"),
 ("refusal-warn-only", 'raise Refusal(f"--{dest.replace(\'_\', \'-\')} does not apply', 'print(f"--{dest.replace(\'_\', \'-\')} does not apply'),
 ("refusal-after-dispatch-skip-first", "for dest, why in GROUP_FLAGS.items():", "for dest, why in list(GROUP_FLAGS.items())[1:]:"),
 ("refusal-skip-last", "for dest, why in GROUP_FLAGS.items():", "for dest, why in list(GROUP_FLAGS.items())[:-1]:"),
 ("topic-forwarded", '"topic": "the roster gives', '"topic": None and "the roster gives'),
 ("brief-forwarded", '"brief": "the roster gives', '"brief": None and "the roster gives'),
 ("repo-forwarded", '"repo": "the roster gives', '"repo": None and "the roster gives'),
 ("out-forwarded", '"out": "--group publishes', '"out": None and "--group publishes'),
 ("brief-entry-deleted", '    "brief": "the roster gives the brief",\n', ''),
 ("pr-refused", '"pr": None, "nonce": None,', '"pr": "x", "nonce": None,'),
 ("overlay-refused", '"nonce": None, "overlay": None,', '"nonce": None, "overlay": "x",'),
 ("model-check-off", 'if not args.model:\n                raise Refusal("--group needs --model")', 'if False:\n                raise Refusal("--group needs --model")'),
 ("flag-checks-unrun", "    _flag_checks(check)\n", ""),
]
SUM = re.compile(r"cloud_dispatch self-test: (\d+) checks, (\d+) failed")
orig = F.read_bytes()
st = subprocess.run(["git", "-C", str(F.parent), "status", "--porcelain", "--", F.name], capture_output=True, text=True).stdout
if st.strip(): sys.exit("dirty")
surv = n = 0
try:
    for name, a, b in M:
        if a is not None:
            t = orig.decode()
            if t.count(a) < 1: print(f"RESULT mutant={name} NOT-APPLIED"); continue
            F.write_text(t.replace(a, b, 1))
        r = subprocess.run([sys.executable, str(F), "--self-test"], capture_output=True, text=True, timeout=900)
        F.write_bytes(orig)
        m = SUM.search(r.stdout)
        reds = [l.strip() for l in r.stdout.splitlines() if l.lstrip().startswith("FAIL")]
        if name == "M0":
            print(f"RESULT mutant=M0 failed={m.group(2) if m else 'CRASHED'} verdict={'null-ok' if m and m.group(2)=='0' else 'NULL-BAD'}"); continue
        n += 1
        if not m: print(f"RESULT mutant={name} CRASHED rc={r.returncode}"); continue
        f = int(m.group(2)); surv += f == 0
        print(f"RESULT mutant={name} failed={f} {'SURVIVED' if f==0 else 'killed'} {reds[:6]}")
finally:
    F.write_bytes(orig)
print(f"RESULT mutants={n} survived={surv}")
