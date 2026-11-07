import re, sys, glob, os
sys.path.insert(0, "/home/user/mut"); import spec
def fails(path):
    s=set(); txt=open(path).read()
    for l in txt.splitlines():
        m=re.match(r"\s*FAIL\s+(.*?)(\s{2}\[.*)?$", l)
        if m: s.add(m.group(1).strip())
    summ=[l for l in txt.splitlines() if re.search(r"CHECKS (FAILED|PASSED)", l)]
    return s, (summ[-1].strip() if summ else "NO-SUMMARY (crash?)"), txt
if __name__ == "__main__":
    base={}
    for sc in ("dst_checks","entities","features"):
        p=f"/home/user/base_{sc}.log"
        if os.path.exists(p): base[sc]=fails(p)[:2]
    for m in spec.CALLER+spec.OWNER:
        mid, expect = m[0], m[5]
        logs=sorted(glob.glob(f"/home/user/mut/log_{mid}_*.txt"))
        if not logs: continue
        new_all=[]; lines=[]
        for lp in logs:
            sc=lp.rsplit("_",1)[1][:-4]
            if sc=="checks": sc="dst_checks"
            f,summ,txt=fails(lp)
            b=base.get(sc,(set(),""))[0]
            new=sorted(f-b); new_all+=new
            crash = summ.startswith("NO-SUMMARY")
            lines.append(f"   {sc}: {summ}; new FAIL {len(new)}" + (" CRASH:"+txt.strip().splitlines()[-1][:160] if crash else ""))
            for n in new[:4]: lines.append(f"      + {n[:170]}")
            if crash: new_all.append("CRASH")
        killed=bool(new_all)
        named = expect is None or any(expect in n for n in new_all)
        print(f"RESULT mutant[{mid}] {'KILLED' if killed else 'SURVIVED'}" + ("" if expect is None else f" expected_check_red={named}"))
        print("\n".join(lines))
