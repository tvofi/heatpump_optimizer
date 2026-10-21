# finder harness (reviewer-built from the brief's description: jq over the roster JSON), $1=base $2=head
F=dev/programme/rosters/wave-r10-groups.json
for r in $1 $2; do echo "RESULT $r groups=$(git show $r:$F | jq '.groups|length') done=$(git show $r:$F | jq '[.groups[]|select(.resume.stage=="done")]|length') carries=$(git show $r:$F | jq '[.groups[]|(.carry//[])|length]|add')"; done
t(){ git show $1:$F | jq -r '.groups[]|[.group,(.resume.stage//"none"),((.carry//[])|length),((.brief|tostring)+(.issues|tostring)+(.fixes|tostring)+(.findings|tostring)|@base64|.[0:0]+(explode|add|tostring))]|@tsv' | sort; }
join -t$'\t' -a1 -a2 -e NEW -o 0,1.2,1.3,2.2,2.3 <(t $1) <(t $2) | awk -F'\t' '$2!=$4||$3!=$5'
echo "-- text-edited groups (brief/issues/fixes/findings differ)"
join -t$'\t' <(git show $1:$F | jq -r '.groups[]|[.group,([.brief,.issues,.fixes,.findings]|tostring)]|@tsv'|sort) <(git show $2:$F | jq -r '.groups[]|[.group,([.brief,.issues,.fixes,.findings]|tostring)]|@tsv'|sort) | awk -F'\t' '$2!=$3{print $1}'
echo "-- carries removed (base carry text absent at head)"
comm -23 <(git show $1:$F | jq -r '.groups[]|.group as $g|(.carry//[])[]|"\($g)\t\(.|tostring)"'|sort) <(git show $2:$F | jq -r '.groups[]|.group as $g|(.carry//[])[]|"\($g)\t\(.|tostring)"'|sort) | cut -c1-160
