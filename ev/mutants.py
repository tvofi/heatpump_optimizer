import sys
F="tools/pr/app_push.sh"
M={
"M0":("",""),
"W1":('[ "$d" = "$(printf \'A\\t%s\' "$row")" ]','printf \'%s\' "$d" | grep -qF "$row"'),
"W2":('[ "${#ps[@]}" -eq 1 ]','[ "${#ps[@]}" -ge 1 ]'),
"W3":('== b.rstrip("\\n")))\' "$body"','== b.rstrip("\\n")) and 0)\' "$body"'),
"W4":(' and OPEN_STATUS in ls[0]',''),
"W5":('|| row_only_checks "$wt" "$body" "$RV_HEAD" "$RV_TITLE"','|| true'),
"W7":('[ "$recarry$rowonly" = 00 ] || [ "$head" = "$RV_HEAD" ]','[ "$recarry" = 0 ] || [ "$head" = "$RV_HEAD" ]'),
"W8":('[ -n "$tok" ] || tok=$(gh auth token 2>/dev/null) || tok=""','[ -n "$tok" ] || :'),
"W9":('    python3 -I tools/audit/carry_audit.py check --body "$2" )','    true )'),
"W10":('[ "${ps[0]}" = "$live" ] ||','true ||'),
"W11":('len(ls) == 1 and ',''),
"W12":('anchored(int(sys.argv[1]), ls[0]) and ',''),
"W13":('[ "$rc" = 0 ] || exit "$rc"',':'),
"W15":('--head "$3"','--head HEAD'),
"W21":('sys.exit(not (len(ls) == 1','sys.exit(not (len(ls) >= 1'),
"W22":('ls = sys.stdin.read().splitlines()','ls = sys.stdin.read().splitlines()[:1]'),
"W23":('[ "$rowonly$bonly" != 11 ] ||','true ||'),
}
k=sys.argv[1]; a,b=M[k]
s=open(F).read()
if k!="M0":
    n=s.count(a)
    if n!=1: sys.exit(f"{k}: matches {n}")
    s=s.replace(a,b)
open(F,"w").write(s)
