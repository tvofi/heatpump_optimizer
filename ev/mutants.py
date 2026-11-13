import json,sys
F="tools/audit/seat/cloud_relay.sh"
M=[
("carry-off",'if ${HPO_RELAY_CARRY:-python3 -I "$HERE/review_carry.py"} "$head" "$live" --verdict-only >/dev/null 2>&1; then','if false; then'),
("carry-classifies-drafted",'cl=$live; carried=','cl=$head; carried='),
("red-bound-never",'[ $(($(date +%s) - seen)) -ge "$redsecs" ]','false'),
("red-refuses-first",'if [ -n "$seen" ] && [ $(($(date +%s)','if [ -z "$seen" ] || [ $(($(date +%s)'),
("red-hold-rc2",'(classify RED)"; return 75 ;;','(classify RED)"; return 2 ;;'),
("wait-no-clear",'3) pending_red_clear "$state" "$rkey"; ','3) '),
("green-no-clear",'0|4) pending_red_clear "$state" "$rkey"; ','0|4) '),
("rkey-no-head",'rkey="$ref $sha $cl"','rkey="$ref $sha"'),
("redsecs-validate-off","case $redsecs in ''|*[!0-9]*) echo \"cloud_relay: HPO_RELAY_PENDING_RED_SECS must be seconds; the pending-ci draft is held\" >&2; return 75;; esac",":"),
("owed-line-moved-off",'        echo "cloud_relay: OWED re-dispatch #$pr $live"\n',''),
("probe-dispose-off",'    if disposed "$ref" "$sha"; then continue; fi  # mut:probedispose','    :'),
("nr-rev-age-zero",'[ "$age" -gt "$rlim" ] && [ "$age" -le "$win" ] || continue  # mut:noreturnrevage','[ "$age" -gt 0 ] && [ "$age" -le "$win" ] || continue'),
("nr-rev-window-off",'[ "$age" -gt "$rlim" ] && [ "$age" -le "$win" ] || continue  # mut:noreturnrevage','[ "$age" -gt "$rlim" ] || continue'),
("nr-rev-ret-off",'[ -s "$state/cloud-nrr.$$" ] && continue  # mut:noreturnrevret','true'),
("nr-rev-revt-off",'"refs/heads/probe/rev-*-$rn8" "refs/heads/probe/revt-*-$rn8"','"refs/heads/probe/rev-*-$rn8"'),
("nr-rev-moved-off",'[ "$rlive" = "$rhead" ] || continue','true'),
("nr-rev-level-off",'        level_line seat-no-return "$ref" "$sha" "SEAT ENDED NO RETURN reviewer','        : level_line seat-no-return "$ref" "$sha" "SEAT ENDED NO RETURN reviewer'),
("nr-rev-lsremote-fail-continue",'"refs/heads/probe/revt-*-$rn8" > "$state/cloud-nrr.$$" || continue','"refs/heads/probe/revt-*-$rn8" > "$state/cloud-nrr.$$" || :'),
("nr-rev-default-bound",'rlim=${HPO_RELAY_NORETURN_REVIEWER_SECS:-5400}','rlim=${HPO_RELAY_NORETURN_REVIEWER_SECS:-7200}'),
("red-default-bound",'redsecs=${HPO_RELAY_PENDING_RED_SECS:-21600}','redsecs=${HPO_RELAY_PENDING_RED_SECS:-0}'),
]
json.dump([{"name":n,"file":F,"old":o,"new":w} for n,o,w in M],open(sys.argv[1],"w"),indent=1)
