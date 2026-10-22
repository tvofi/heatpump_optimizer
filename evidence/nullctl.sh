# Null controls: which new 403 rows kill the operand revert ("$status" -> "$1") and F13.
set -u
F=g/mut/tools/pr/app_approve.sh; cp $F orig.sh
r1='403	refuse	gh: Resource not accessible by integration (HTTP 403)\nsee the secondary rate limit docs'
r2='403	refuse	gh: You have exceeded a secondary rate limit.\ngh: Forbidden (HTTP 403)'
r3='403	transient	gh: You have exceeded a secondary rate limit. (HTTP 403)\nRetry the request in a few minutes.'
run(){ (cd g/mut && bash tools/pr/app_approve.sh --self-test 2>&1 | grep -E '^FAIL|checks,' | head -3); cp orig.sh $F; }
py(){ python3 - "$F" "$@" <<'P'
import sys; f,*ops=sys.argv[1:]; s=open(f).read()
for op in ops:
    a,b=op.split("=>",1); a=a.replace("\\t","\t"); b=b.replace("\\t","\t")
    assert a in s,(a,); s=s.replace(a+("\n" if b=="" else ""),b,1) if b=="" else s.replace(a,b,1)
open(f,"w").write(s)
P
}
P403='403) printf '"'"'%s\n'"'"' "$status" | grep'
for row in r1 r2 r3; do
  eval "R=\$$row"
  echo "== row $row deleted, unmutated"; py "${R//	/\\t}=>"; run
  echo "== row $row deleted, operand -> \"\$1\" (G3)"; py "${R//	/\\t}=>" "$P403=>403) printf '%s\n' \"\$1\" | grep"; run
  echo "== row $row deleted, F13 (\"\$1\" | tail -1)"; py "${R//	/\\t}=>" "$P403=>403) printf '%s\n' \"\$1\" | tail -1 | grep"; run
  echo "== row $row deleted, \"\$1\" | head -1"; py "${R//	/\\t}=>" "$P403=>403) printf '%s\n' \"\$1\" | head -1 | grep"; run
done
