#!/bin/bash
# CI watcher v3: alerts only on NEW states (per-PR signature file), exits 1 with a report.
#
# v3 (R9-RC-AUTOFIX-GOVERNANCE) also reports required contexts that are ABSENT
# at a SETTLED head. A GITHUB_TOKEN push -- the autofix jobs' bot commits --
# gets pull_request runs held action_required (every bot head from
# 2026-10-15T10:23Z, e.g. Tests run 38781421410), so until one is approved the
# required contexts only they write (the governance family, pr-contract,
# budget-raise-gate) do not report there: the head looks fully settled, every
# run it has completed, and GitHub refuses the merge with nothing saying why.
# On 2026-10-09 no such run was created at all (63084989/#2066 and
# a9ba0b88/#2070: 30 check-runs, none pending, the same 5 of the 17 required
# contexts absent; a v2 watcher printed nothing at either).
# ABSENT is judged only once every present run completed -- a head mid-push has
# its runs not queued yet, which is pending, not absent. The required list is
# read from the ruleset each cycle, never carried: when it cannot be read the
# ABSENT arm is skipped and the blindness is alerted once, because a watcher
# that cannot see absences is the defect this version exists for.
#
#   bash ci-watch.sh              # watch loop; alert-and-exit-1 on a NEW state
#   bash ci-watch.sh --self-test  # offline, against fixture heads (no GitHub)
#
# CI_WATCH_ONCE=1 runs a single cycle and exits 0 when nothing is new (the
# self-test drives the loop through it; a cron-style caller may too).
R=tvofi/heatpump_optimizer
S=${CI_WATCH_STATE:-${HPO_STATE_DIR:-$HOME/.local/state/hpo}/ci-watch-state}
RULESET=main-protect-checks

# --------------------------------------------------------------- self-test
self_test() {
  passed=0; failed=0
  ck() { # <name> <0|1>
    if [ "$2" = 1 ]; then passed=$((passed + 1)); printf '  ok   %s\n' "$1"
    else failed=$((failed + 1)); printf '  FAIL %s\n' "$1"; fi
  }
  WATCH=$0
  TMP=$(mktemp -d) || exit 1
  trap 'rm -rf "$TMP"' EXIT
  mkdir -p "$TMP/bin"
  # A fake gh serving recorded shapes: its answers are the post---jq ones, the
  # same convention merge_train.py's self-test stubs use.
  cat > "$TMP/bin/gh" <<'FAKE'
#!/bin/bash
a="$*"
case "$a" in
  *"pr list"*)        cat "$FIX/prs" ;;
  *"pr view"*)        cat "$FIX/head" ;;
  *"/rulesets/"*)     cat "$FIX/required" 2>/dev/null; exit $? ;;
  *"/rulesets "*)     cat "$FIX/ruleset-id" 2>/dev/null; exit $? ;;
  *"/commits/"*)      sha=$(printf '%s' "$a" | sed 's|.*/commits/||' | cut -d' ' -f1 | cut -d/ -f1)
                      cat "$FIX/cr-$sha.tsv" ;;
  *)                  exit 0 ;;
esac
FAKE
  chmod +x "$TMP/bin/gh"

  # The 17 required contexts of ruleset main-protect-checks, read from the API
  # 2026-10-09. W1's present set is exactly that reading's intersection with
  # the check-run names at the real bot head 6308498975f4 (the 12 below), so
  # the ABSENT arm is graded on the defect's own recorded shape, and W2 adds
  # the 5 the App-pushed recovery head 386b7e2ff798 reported.
  REQ17='Analyze (actions)
Analyze (javascript-typescript)
Analyze (python)
briefs
browser
budget-raise-gate
closure-scope
closures
env-matrix
fast (3.14)
hassfest
mutation
policy-docs
pr-contract
typing
validate-hacs
wave-script'
  PRESENT12='Analyze (actions)
Analyze (javascript-typescript)
Analyze (python)
briefs
browser
closure-scope
closures
fast (3.14)
hassfest
mutation
typing
validate-hacs'
  ABSENT5='budget-raise-gate env-matrix policy-docs pr-contract wave-script'
  mkfix() { # <dir> <sha> <mergeable> ; cr lines fed on stdin as names
    mkdir -p "$1"
    printf '2066\n' > "$1/prs"
    printf '%s %s\n' "$2" "$3" > "$1/head"
    printf '%s\n' "$REQ17" > "$1/required"
    printf '23698884\n' > "$1/ruleset-id"
    : > "$1/cr-$2.tsv"
    while IFS= read -r nm; do
      [ -n "$nm" ] && printf '%s\tcompleted\tsuccess\t2026-10-09T00:00:00Z\n' "$nm" >> "$1/cr-$2.tsv"
    done
  }
  watch() { # <fixdir> <statedir> -> stdout of one cycle; rc is the watcher's
    PATH="$TMP/bin:$PATH" FIX="$1" CI_WATCH_STATE="$2" CI_WATCH_ONCE=1 bash "$WATCH" 2>&1
  }
  says() { case "$2" in *"$1"*) return 0;; esac; return 1; }

  # W1: the defect's shape -- settled, every present run green, the 5 absent.
  F=$TMP/w1; mkfix "$F" 63084989bot MERGEABLE <<EOF
$PRESENT12
claims-autofix
graders-head-copy
nightly-status
EOF
  O=$(watch "$F" "$TMP/s1"); rc=$?
  n_absent=1
  for c in $ABSENT5; do says "$c" "$O" || n_absent=0; done
  ck "W1 settled-but-absent bot head: exit 1, alert says ABSENT and names all five" \
     "$([ $rc = 1 ] && says 'ABSENT' "$O" && [ $n_absent = 1 ] && echo 1 || echo 0)"
  ck "W1 is judged settled: no run pending at it" \
     "$(says 'pending' "$O" && echo 0 || echo 1)"

  # W2: the null control -- the recovery head's shape: every required context
  # present and green. Same watcher, same cycle; nothing to say.
  F=$TMP/w2; mkfix "$F" 386b7e2fapp MERGEABLE <<EOF
$REQ17
claims-autofix
graders-head-copy
nightly-status
EOF
  O=$(watch "$F" "$TMP/s2"); rc=$?
  ck "W2 settled all-present green head: exit 0 and no alert (null control for W1)" \
     "$([ $rc = 0 ] && [ -z "$O" ] && echo 1 || echo 0)"

  # W3: absent contexts but a run still queued -- not settled, so no ABSENT
  # alert: a head mid-push must not cry wolf while its runs are still coming.
  F=$TMP/w3; mkfix "$F" freshhead MERGEABLE <<EOF
$PRESENT12
EOF
  printf 'policy-docs\tqueued\t\t2026-10-09T00:00:00Z\n' >> "$F/cr-freshhead.tsv"
  O=$(watch "$F" "$TMP/s3"); rc=$?
  ck "W3 absent-but-pending head: no alert while a run is still queued" \
     "$([ $rc = 0 ] && [ -z "$O" ] && echo 1 || echo 0)"

  # W4: v2's arms survive -- a red at a settled head still alerts RED. Two reds,
  # written in an order that is NOT sorted, pin the sort: the signature file
  # dedups on this string, and awk's END loop iterates in its own order, so an
  # unsorted list re-alerts the same state as NEW on every cycle.
  F=$TMP/w4; mkfix "$F" redhead MERGEABLE <<EOF
$REQ17
EOF
  printf 'typing\tcompleted\tfailure\t2026-10-09T01:00:00Z\n' >> "$F/cr-redhead.tsv"
  printf 'mutation\tcompleted\tfailure\t2026-10-09T01:00:00Z\n' >> "$F/cr-redhead.tsv"
  O=$(watch "$F" "$TMP/s4"); rc=$?
  ck "W4 a red at a settled head still alerts RED, name-sorted (v2 behaviour kept, signature stable)" \
     "$([ $rc = 1 ] && says 'RED: mutation typing' "$O" && echo 1 || echo 0)"

  # W5: the signature dedup survives -- W1's state alerts once, then is quiet.
  O=$(watch "$TMP/w1" "$TMP/s1"); rc=$?
  ck "W5 the same settled-absent state is not re-alerted (signature file kept)" \
     "$([ $rc = 0 ] && [ -z "$O" ] && echo 1 || echo 0)"

  # W6: the ruleset unreadable -- the ABSENT arm is blind, and the blindness
  # itself alerts once rather than the watcher quietly judging nothing.
  F=$TMP/w6; mkfix "$F" blindhead MERGEABLE <<EOF
$PRESENT12
EOF
  : > "$F/ruleset-id"
  O=$(watch "$F" "$TMP/s6"); rc=$?
  O2=$(watch "$F" "$TMP/s6"); rc2=$?
  ck "W6 an unreadable ruleset alerts BLIND once, then is quiet until it can read again" \
     "$([ $rc = 1 ] && says 'required contexts unreadable' "$O" && [ $rc2 = 0 ] && [ -z "$O2" ] && echo 1 || echo 0)"

  # W7: v2's STALLED arm survives -- zero runs at a mergeable head.
  F=$TMP/w7; mkdir -p "$F"
  printf '2066\n' > "$F/prs"; printf 'zeroruns MERGEABLE\n' > "$F/head"
  printf '%s\n' "$REQ17" > "$F/required"; printf '23698884\n' > "$F/ruleset-id"
  : > "$F/cr-zeroruns.tsv"
  O=$(watch "$F" "$TMP/s7"); rc=$?
  ck "W7 zero runs at a mergeable head still alerts STALLED (v2 behaviour kept)" \
     "$([ $rc = 1 ] && says 'STALLED' "$O" && echo 1 || echo 0)"

  # W8-W12: the umbrella (R10-CI-LAYOUT P2b): the ruleset requires `gate`
  # alone, and every CI run is a check suite of its own, so one head carries a
  # gate per run (5th column: the check suite id).
  gatefix() { # <dir> <sha> ; cr lines (name|status|conclusion|started|suite) on stdin
    mkdir -p "$1"; printf '2066\n' > "$1/prs"; printf '%s MERGEABLE\n' "$2" > "$1/head"
    printf 'gate\n' > "$1/required"; printf '23698884\n' > "$1/ruleset-id"
    tr '|' '\t' > "$1/cr-$2.tsv"
  }
  F=$TMP/w8; gatefix "$F" newlayout <<EOF
gate|completed|success|2026-10-22T00:00:00Z|1
tests / fast (3.14)|completed|success|2026-10-22T00:00:00Z|1
EOF
  O=$(watch "$F" "$TMP/s8"); rc=$?
  ck "W8 a settled new-layout head with a green gate under the gate ruleset: no alert (null for W9, W10, W12)" \
     "$([ $rc = 0 ] && [ -z "$O" ] && echo 1 || echo 0)"
  F=$TMP/w9; mkfix "$F" oldlayout MERGEABLE <<EOF
$REQ17
EOF
  printf 'gate\n' > "$F/required"
  O=$(watch "$F" "$TMP/s9"); rc=$?
  ck "W9 a settled old-layout head (the 17, no gate) under the gate ruleset alerts gate ABSENT" \
     "$([ $rc = 1 ] && says 'ABSENT' "$O" && says 'gate' "$O" && echo 1 || echo 0)"
  F=$TMP/w10; gatefix "$F" oldred <<EOF
gate|completed|failure|2026-10-22T00:00:00Z|1
gate|completed|success|2026-10-22T01:00:00Z|2
EOF
  O=$(watch "$F" "$TMP/s10"); rc=$?
  ck "W10 A5: an older red gate suite beside a newer green one alerts RED: gate (the platform blocks on it)" \
     "$([ $rc = 1 ] && says 'RED: gate' "$O" && echo 1 || echo 0)"
  F=$TMP/w11; gatefix "$F" rerun <<EOF
gate|completed|failure|2026-10-22T00:00:00Z|1
gate|completed|success|2026-10-22T01:00:00Z|1
EOF
  O=$(watch "$F" "$TMP/s11"); rc=$?
  ck "W11 A5 null: a red gate re-run green inside ONE suite is no alert" \
     "$([ $rc = 0 ] && [ -z "$O" ] && echo 1 || echo 0)"
  F=$TMP/w12; gatefix "$F" skipgate <<EOF
gate|completed|skipped|2026-10-22T00:00:00Z|1
EOF
  O=$(watch "$F" "$TMP/s12"); rc=$?
  ck "W12 a gate that did not succeed (skipped; RATE-LIMITED is a failure) alerts RED: gate, never a pass" \
     "$([ $rc = 1 ] && says 'RED: gate' "$O" && echo 1 || echo 0)"

  printf 'ci-watch self-test: %d checks, %d failed\n' "$((passed + failed))" "$failed"
  [ "$failed" = 0 ]
  return $?
}
case "${1:-}" in --self-test) self_test; exit $?;; esac

# --------------------------------------------------------------- watch loop
mkdir -p "$S"
TAB=$(printf '\t')
while true; do
  OUT=""
  # The required contexts, fresh each cycle (a ruleset edit is live at once).
  RS=$(gh api "repos/$R/rulesets" --jq ".[] | select(.name==\"$RULESET\") | .id" 2>/dev/null)
  REQ=""
  [ -n "$RS" ] && REQ=$(gh api "repos/$R/rulesets/$RS" --jq '.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context' 2>/dev/null | sort -u)
  if [ -z "$REQ" ]; then
    if [ "$(cat "$S/req-blind" 2>/dev/null)" != blind ]; then
      echo blind > "$S/req-blind"
      OUT="$OUT\\nrequired contexts unreadable (ruleset $RULESET): ABSENT unjudged this cycle"
    fi
  else
    rm -f "$S/req-blind"
  fi
  for n in $(gh pr list --repo $R --state open --json number --jq '.[].number'); do
    sig_file="$S/$n"
    H=$(gh pr view $n --repo $R --json headRefOid,mergeable --jq '.headRefOid + " " + .mergeable' 2>/dev/null)
    sha=$(echo $H | cut -d' ' -f1); mb=$(echo $H | cut -d' ' -f2)
    issue=""
    [ "$mb" = "CONFLICTING" ] || [ "$mb" = "DIRTY" ] && issue=" | $mb — needs local main absorb"
    # ONE check-runs read per head per cycle (v2 made two), every page: past
    # 100 runs a first page alone misjudges both the reds and the absences.
    CR=$(gh api --paginate "repos/$R/commits/$sha/check-runs?per_page=100" --jq '.check_runs[] | [.name, .status, .conclusion, .started_at, (.check_suite.id // "")] | @tsv' 2>/dev/null)
    cr_rc=$?
    total=""
    if [ $cr_rc = 0 ]; then
      total=0
      if [ -n "$CR" ]; then
        total=$(printf '%s\n' "$CR" | wc -l | tr -d ' ')
        # Latest run per name, red when its conclusion is failure (v2's rule);
        # `gate` per check suite, red when a completed one did not succeed
        # (A5: GitHub blocks on any suite's red gate; RATE-LIMITED fails).
        # Sorted: the signature file dedups on this string, and awk's END-loop
        # order is arbitrary -- an unsorted list would re-alert the same reds
        # as a NEW state every cycle (v2's jq group_by was name-sorted).
        reds=$(printf '%s\n' "$CR" | sort -s -t "$TAB" -k1,1 -k4,4 | awk -F "$TAB" '{k = ($1 == "gate") ? $1 SUBSEP $5 : $1; nm[k] = $1; bad[k] = ($1 == "gate") ? ($2 == "completed" && $3 != "success") : ($3 == "failure")} END {for (x in bad) if (bad[x]) print nm[x]}' | sort -u | tr '\n' ' ')
        [ -n "$reds" ] && issue="$issue | RED: $reds"
        # ABSENT, judged only at a settled head: every run it has completed.
        pending=$(printf '%s\n' "$CR" | awk -F "$TAB" '$2 != "completed"' | wc -l | tr -d ' ')
        if [ -n "$REQ" ] && [ "$pending" = 0 ]; then
          absent=$(comm -23 <(printf '%s\n' "$REQ") <(printf '%s\n' "$CR" | cut -f1 | sort -u) | tr '\n' ' ')
          [ -n "$absent" ] && issue="$issue | ABSENT required (settled; these never report at a bot GITHUB_TOKEN head -- an App push repairs): $absent"
        fi
      fi
    fi
    [ "$total" = "0" ] && [ "$mb" = "MERGEABLE" ] && issue="$issue | STALLED zero-runs"
    sig="${sha:0:8}${issue}"
    if [ -n "$issue" ] && [ "$(cat $sig_file 2>/dev/null)" != "$sig" ]; then
      OUT="$OUT\nPR#$n at ${sha:0:8}:$issue"
      echo "$sig" > $sig_file
    fi
    [ -z "$issue" ] && rm -f $sig_file
  done
  if [ -n "$OUT" ]; then echo -e "CI-WATCH ALERT ($(date -u +%H:%MZ)): NEW state(s):$OUT"; exit 1; fi
  [ -n "${CI_WATCH_ONCE:-}" ] && exit 0
  sleep 300
done
