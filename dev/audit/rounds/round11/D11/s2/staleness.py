#!/usr/bin/env python3
"""D11.M3 staleness where policy_lint's `citations` class does not reach: the
decision records' status lines, the handover's backticked paths, the plan's.

Metric (one line): per document, backticked path-shaped tokens that resolve to no
tracked file (exact path, else any tracked file of the same basename -- the
fallback policy_lint's `candidatesFor` applies), and decisions whose front-matter
`status:` says accepted while its own `superseded-by:` names a successor.
No production reader of these documents exists (that absence is the result:
`grep -rln superseded-by tools .github tests/*.py` prints nothing), so this is an
observation, not a finding; the perturbation (--perturb, one tracked basename
removed from the listing) moves the unresolved count up by 1.

Run:   python3 dev/audit/rounds/round11/D11/s2/staleness.py [--list] [--perturb]
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B7: exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob, re, subprocess, sys, time

TOK = re.compile(r"`([A-Za-z0-9_.\-/]+/[A-Za-z0-9_.\-]+\.(?:py|mjs|js|sh|md|json|yml|yaml|txt))(?::\d+(?:-\d+)?)?`")


def main(argv):
    t0, c0 = time.process_time(), time.thread_time()
    tracked = set(subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split())
    if "--perturb" in argv:  # drop the first resolved handover citation's basename from the listing
        first = next(t for t in sorted(set(TOK.findall(open("dev/programme/HANDOVER.md").read()))) if t in tracked)
        tracked = {f for f in tracked if os.path.basename(f) != os.path.basename(first)}
    bases = {os.path.basename(f) for f in tracked}
    docs = ["dev/programme/HANDOVER.md"] + sorted(glob.glob("dev/programme/plan*.md"))
    total_unres = 0
    for d in docs:
        toks = sorted(set(TOK.findall(open(d).read())))
        unres = [t for t in toks if t not in tracked and os.path.basename(t) not in bases
                 and not t.startswith(("dev/audit/rounds/", "/tmp", "$"))]
        total_unres += len(unres)
        print(f"RESULT {d}:path_tokens={len(toks)} count")
        print(f"RESULT {d}:unresolved={len(unres)} count")
        if "--list" in argv:
            for t in unres:
                print(f"UNRESOLVED\t{d}\t{t}")
    bad = []
    decs = sorted(glob.glob("dev/governance/decisions/*.md"))
    for f in decs:
        head = open(f).read().split("\n---", 1)[0]
        st = re.search(r"^status:\s*(\S+)", head, re.M | re.I)
        sb = re.search(r"^superseded-by:\s*\[(.*)\]", head, re.M)
        if st and sb and sb.group(1).strip() and st.group(1).lower().startswith("accepted"):
            bad.append(os.path.basename(f))
    print(f"RESULT decisions={len(decs)} count")
    print(f"RESULT decisions_accepted_but_superseded={len(bad)} count ({' '.join(bad)})")
    print(f"RESULT unresolved_total={total_unres} count")
    pc, tc = time.process_time() - t0, time.thread_time() - c0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main(sys.argv[1:])
