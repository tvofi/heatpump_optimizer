import sys
p=sys.argv[1]; s=open(p).read()
old='''kill -"$2" "$up"; wait "$up" 2>/dev/null;'''
new='''T0=$(date +%s.%N); kill -"$2" "$up"; wait "$up" 2>/dev/null; T1=$(date +%s.%N); echo "$1 $2 kill->run1-exit $(echo "$T1 - $T0" | bc) push-ended-before-run1-exit=$([ -e "$t/ended" ] && echo yes || echo no)" >> "$TRACE";'''
assert old in s; s=s.replace(old,new)
old2='''k=0; while [ ! -e "$t/ended" ] && [ $k -lt 200 ]; do sleep 0.05; k=$((k + 1)); done'''
new2=old2+'''; echo "$1 $2 run2-BUSY=$(grep -qF 'update_pr: BUSY' "$t/out2" && echo yes || echo no) push-end-after-kill $(echo "$(stat -c %.9Y "$t/ended" 2>/dev/null || echo 0) - $T0" | bc)" >> "$TRACE"'''
assert old2 in s; s=s.replace(old2,new2)
open(p,'w').write(s)
