import sys
P = {"O-guard-three-way": ("    if both_changed and _parse_claims(ours)[0] != _parse_claims(theirs)[0]:\n",
        "    if both_changed and not (_parse_claims(base)[0] == _parse_claims(ours)[0] == _parse_claims(theirs)[0]):\n"),
     "O-no-guard": ("    if both_changed and _parse_claims(ours)[0] != _parse_claims(theirs)[0]:\n", "    if False:\n"),
     "O-guard-base-vs-ours": ("    if both_changed and _parse_claims(ours)[0] != _parse_claims(theirs)[0]:\n", "    if both_changed and _parse_claims(base)[0] != _parse_claims(ours)[0]:\n")}
a,b=P[sys.argv[1]]; s=open(sys.argv[2]).read(); assert s.count(a)==1; open(sys.argv[2],"w").write(s.replace(a,b))
