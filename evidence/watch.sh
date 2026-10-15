#!/bin/bash
# Exit when every required check has a completed run at the head, or the head moves.
H=f3cbd393c8aa12ae5406b66ee894c500bac0a1cb
REQ='fast (3.14)|browser|briefs|closure-scope|closures|typing|hassfest|validate-hacs|policy-docs|wave-script|pr-contract|env-matrix|Analyze (actions)|Analyze (javascript-typescript)|Analyze (python)|mutation|budget-raise-gate'
while true; do
  cur=$(gh pr view 2281 --repo tvofi/heatpump_optimizer --json headRefOid -q .headRefOid 2>/dev/null)
  if [ -n "$cur" ] && [ "$cur" != "$H" ]; then echo "HEAD MOVED $cur"; exit 0; fi
  runs=$(gh api --paginate "repos/tvofi/heatpump_optimizer/commits/$H/check-runs?per_page=100" -q '.check_runs[] | [.name,.status,(.conclusion//"null")] | @tsv' 2>/dev/null) || { sleep 300; continue; }
  pending=0; red=""
  IFS='|' read -ra names <<< "$REQ"
  for n in "${names[@]}"; do
    rows=$(printf '%s\n' "$runs" | awk -F'\t' -v n="$n" '$1==n')
    [ -z "$rows" ] && { pending=1; continue; }
    printf '%s\n' "$rows" | grep -qv $'\tcompleted\t' && pending=1
    bad=$(printf '%s\n' "$rows" | awk -F'\t' '$2=="completed" && $3!="success" && $3!="neutral" && $3!="skipped"{print $1":"$3}')
    [ -n "$bad" ] && red="$red $bad"
  done
  echo "$(date -u +%H:%MZ) pending=$pending red=[$red]"
  [ $pending = 0 ] && { echo DONE; exit 0; }
  sleep 300
done
