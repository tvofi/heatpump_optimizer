# id | file | old | new  (exact single replacement; asserts the old string occurs once)
M = [
("W1","tools/pr/app_push.sh",'[ "$d" = "$(printf \'A\\t%s\' "$row")" ]','printf \'%s\\n\' "$d" | grep -qxF "$(printf \'A\\t%s\' "$row")"'),
("W2","tools/pr/app_push.sh",'[ "${#ps[@]}" -eq 1 ]','[ "${#ps[@]}" -ge 1 ]'),
("W3","tools/pr/app_push.sh",'sys.exit(not (j > i and prefix(live, b[i:j]).rstrip("\\n") == b.rstrip("\\n")))','sys.exit(0)'),
("W4","tools/pr/app_push.sh",' and OPEN_STATUS in ls[0]',''),
("W5","tools/pr/app_push.sh",'[ "$rowonly$skip" != 11 ] || row_only_checks "$wt" "$body" "$RV_HEAD" "$RV_TITLE"','[ "$rowonly$skip" != 11 ] || true'),
("W6","tools/audit/seat/update_pr.sh",'RO=""; [ "$C" != - ] || RO=--row-only','RO=--row-only'),
("W7","tools/pr/app_push.sh",'[ "$recarry$rowonly" = 00 ] || [ "$head" = "$RV_HEAD" ]','[ "$recarry" = 0 ] || [ "$head" = "$RV_HEAD" ]'),
("W8","tools/pr/app_push.sh",'[ -n "$tok" ] || tok=$(gh auth token 2>/dev/null) || tok=""',':'),
("W9","tools/pr/app_push.sh",'python3 -I tools/audit/carry_audit.py check --body "$2" )','true )'),
("W10","tools/pr/app_push.sh",'[ "${ps[0]}" = "$live" ] ||','true ||'),
("W11","tools/pr/app_push.sh",'len(ls) == 1 and anchored','anchored'),
("W12","tools/pr/app_push.sh",'anchored(int(sys.argv[1]), ls[0]) and OPEN','OPEN'),
("W13","tools/pr/app_push.sh",'[ "$rc" = 0 ] || exit "$rc"',':'),
("W14","tools/pr/app_push.sh",'row_only_verdict "$wt" "$listing" "$body" >/dev/null && skip=1','row_only_verdict "$wt" "$listing" "$body" >/dev/null; skip=1'),
("W15","tools/pr/app_push.sh",'--head "$3" --title "$4"','--head HEAD --title "$4"'),
]
import sys
mid=sys.argv[1]
for i,f,o,n in M:
    if i==mid:
        s=open(f).read(); c=s.count(o); assert c==1,(mid,c); open(f,"w").write(s.replace(o,n)); print(f); break
else: sys.exit("no such mutant")
