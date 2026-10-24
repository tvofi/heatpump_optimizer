#!/bin/bash
# M-5b and M-7 on #2649 (Arm A). Polls at 60 s. Writes evidence/m57.txt.
# M-7: one jobs?filter=latest listing of the new code run while `probe / probe` is in progress.
# M-5b: while that newer code run is in progress, re-run the COMPLETED gate job of run OLD;
#       then read back that the newer run is unaffected and the re-run attempt concluded.
set -u
R=tvofi/heatpump_optimizer; PR=2649; OLDHEAD=83de34568bab45dccdb3b0b9bcdb8552b6662a94; OLD=39920652005
CP=/Users/timmalmstrom/hpo-seats/r10s4/p2b-coord/tools/audit/seat/ci_probe.py
E=/Users/timmalmstrom/hpo-orch/r10s4/cloud/p2b/evidence; O=$E/m57.txt
PY=/Users/timmalmstrom/hpo-seats/r10s4/p2b-coord/tools/audit/seat/shims/seat-python3
now() { date -u +%FT%TZ; }
log() { echo "$(now) $*" >> "$O"; }
log "--- M-5b/M-7 on #$PR; old head $OLDHEAD; completed run for M-5b: $OLD"
for i in $(seq 1 60); do
  H=$(gh api repos/$R/pulls/$PR --jq .head.sha) || { log "pulls read failed"; sleep 60; continue; }
  [ "$H" != "$OLDHEAD" ] && break; sleep 60
done
log "new head $H"
held=$(gh api "repos/$R/actions/runs?head_sha=$H&status=action_required" --jq .total_count); log "held action_required at head: $held"
[ "${held:-0}" -gt 0 ] && bash /Users/timmalmstrom/hpo-seats/r10s4/probe-runner/tools/pr/approve_held_runs.sh $R fix/r10-ci-layout-p2-probe-A >> "$O" 2>&1
M7=; M5=
for i in $(seq 1 40); do
  RUN=$(gh api "repos/$R/actions/runs?head_sha=$H&per_page=50" --jq '[.workflow_runs[]|select(.display_title|startswith("CI code"))][0]|"\(.id)\t\(.status)\t\(.display_title)"')
  RID=${RUN%%$'\t'*}
  if [ -n "$RID" ] && [ "$RID" != null ]; then
    J=$(gh api "repos/$R/actions/runs/$RID/jobs?filter=latest&per_page=100" --jq '.jobs[]|[.id,.name,.status,(.conclusion//"-"),(.started_at//"-")]|@tsv')
    PS=$(printf '%s\n' "$J" | awk -F'\t' '$2=="probe / probe"{print $3}')
    if [ -z "$M7" ] && [ "$PS" = in_progress ]; then
      log "M-7 listing of code run $RUN while probe / probe is in_progress (jobs?filter=latest, once):"
      printf '%s\n' "$J" | sed 's/^/    /' >> "$O"
      if printf '%s\n' "$J" | awk -F'\t' '$2=="gate"' | grep -q .; then log "M-7: gate APPEARS in the listing before its needs finish"; else log "M-7: gate does NOT appear before its needs finish"; fi
      M7=done
      GJ=$(gh api "repos/$R/actions/runs/$OLD/jobs?filter=latest" --jq '.jobs[]|select(.name=="gate")|"\(.id) \(.status) \(.conclusion)"')
      log "M-5b: run $OLD gate job before re-run: $GJ; newer code run $RID status $(echo "$RUN"|cut -f2)"
      "$PY" -I "$CP" --repo $R --log $E/ci_probe.log rerun-job "${GJ%% *}" >> "$O" 2>&1; log "M-5b: rerun-job rc=$?"
      M5=$RID
    fi
    st=$(echo "$RUN"|cut -f2)
    if [ -n "$M5" ] && [ "$st" = completed ]; then
      sleep 60
      log "newer code run $RID final: $(gh api repos/$R/actions/runs/$RID --jq '"\(.status) \(.conclusion) attempt=\(.run_attempt)"')"
      log "its jobs: $(gh api "repos/$R/actions/runs/$RID/jobs?filter=latest" --jq '[.jobs[]|"\(.name)=\(.conclusion)"]|join(", ")')"
      log "re-run $OLD: $(gh api repos/$R/actions/runs/$OLD --jq '"\(.status) \(.conclusion) attempt=\(.run_attempt) title=\(.display_title)"')"
      log "re-run $OLD gate: $(gh api "repos/$R/actions/runs/$OLD/jobs?filter=latest" --jq '[.jobs[]|select(.name=="gate")|"\(.id) \(.status) \(.conclusion) \(.started_at)-\(.completed_at)"]|join(" ")')"
      log "cancelled runs at $H (none expected): $(gh api "repos/$R/actions/runs?head_sha=$H&per_page=50" --jq '[.workflow_runs[]|select(.conclusion=="cancelled")|.id]|join(",")')"
      log "DONE"; exit 0
    fi
    [ -z "$M7" ] && [ "$st" = completed ] && { log "MISSED: code run $RID completed before a probe in_progress listing"; exit 2; }
  fi
  sleep 60
done
log "TIMEOUT"; exit 3
