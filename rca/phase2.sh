#!/bin/bash
R=tvofi/heatpump_optimizer; : > p2.tsv; : > p2.err
awk -F'\t' '$5=="failure" && $7!="none"' jobs.tsv | while IFS=$'\t' read id sha br ts cc cid ac aid; do
  alog=$(gh api --allow-escape-sequences "repos/$R/actions/jobs/$aid/logs" 2>/dev/null) || { echo "LOGFAIL autofix $aid" >> p2.err; }
  st=$(printf '%s' "$alog" | grep -o 'AUTOFIX: [a-z-]*' | tail -1 | cut -d' ' -f2)
  clog=$(gh api --allow-escape-sequences "repos/$R/actions/jobs/$cid/logs" 2>/dev/null) || { echo "LOGFAIL closures $cid" >> p2.err; }
  us=$(printf '%s' "$clog" | grep -c ' UNDER-SCOPED: ')
  ir=$(printf '%s' "$clog" | grep -c 'INERT READS UNDER-APPROXIMATED')
  ph=$(printf '%s' "$clog" | grep -c 'PHANTOM:')
  nf=$(printf '%s' "$clog" | grep -c 'NOT A FILE:')
  ic=$(printf '%s' "$clog" | grep -c 'files on the INERT list')
  printf '%s\t%s\t%s\t%s\tac=%s\tst=%s\tUS=%s\tIR=%s\tPH=%s\tNF=%s\tIC=%s\tclen=%s\n' "$id" "${sha:0:8}" "$br" "$ts" "$ac" "${st:-?}" "$us" "$ir" "$ph" "$nf" "$ic" "${#clog}" >> p2.tsv
done
echo "phase2 rows: $(wc -l < p2.tsv) logfails: $(cat p2.err 2>/dev/null | wc -l)"
