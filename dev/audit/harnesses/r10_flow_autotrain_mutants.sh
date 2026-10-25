#!/bin/bash
# R10-FLOW-AUTOTRAIN: the mutation drive for merge_train.py's queue builder, its
# add admission (Train.admit_add, the `verdict` rule this group adds), the
# backstop sweep, bus.sh's event add and tick_loop.sh's --sweep step. Each mutant
# removes or inverts one rule, runs the owning self-test, restores the file, and
# prints the self-test's last line and its FAIL lines: a killed mutant prints
# failures, a survivor "0 failed". The CI mutation lane does not cover these
# files: its scope is production code, and nothing under tools/ is in it.
# G1 and G2 re-inline the verdict grammar in the queue (merge_train.py) or the
# verdict levels (orchestrator_tick.py) instead of reading it through
# proof_watch.parse_verdict; each prints agreement_py's RESULT too.
# Run from a clean checkout of the branch, all mutants or the ones named:
#   bash dev/audit/harnesses/r10_flow_autotrain_mutants.sh [A1 V3 ...]
cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
F=tools/audit/seat/merge_train.py L=tools/audit/seat/tick_loop.sh O=tools/audit/seat/orchestrator_tick.py
B=tools/audit/seat/bus.sh
git diff --quiet -- $F $L $O $B || { echo "$F, $L, $O or $B has uncommitted edits; the restore would erase them"; exit 2; }
want=" $* "
mut() { # name, file, python replace old->new (exactly one occurrence)
  name=$1; f=$2; old=$3; new=$4
  [ "$want" = "  " ] || [[ "$want" == *" $name "* ]] || return 0
  python3 - "$f" "$old" "$new" 2>/dev/null <<'P' || { echo "== $name: PATTERN NOT FOUND"; return; }
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); assert s.count(o)==1; open(p,'w').write(s.replace(o,n))
P
  case $f in
    "$L"|"$B") out=$(bash "$f" --self-test 2>&1) ;;
    *) out=$(python3 "$f" --self-test 2>&1) ;;
  esac
  [[ $name == G* ]] && agr=$(python3 -I tools/policy/agreement_py.py --run 2>&1 | grep '^RESULT')
  git checkout -q -- "$f"
  echo "== $name: $(echo "$out" | tail -1)"; echo "$out" | grep FAIL | sed 's/^/     /'
  [[ $name == G* ]] && echo "     agreement_py: $agr"
}
if [ "$want" = "  " ] || [[ "$want" == *" M0 "* ]]; then
  echo "== M0 baseline: $(python3 $F --self-test 2>&1 | tail -1); $(bash $L --self-test 2>&1 | tail -1); $(bash $B --self-test 2>&1 | tail -1)"
fi
# The queue builder's rules (Train.admit_verdict, Train.posted_verdict, Train.build_queue).
mut A1 $F '        if pr.get("headRefName") == record_row.RECORD_BRANCH:' '        if False:'
mut A2 $F '        if tip is None:
            return f"no confirmed' '        if False:
            return f"no confirmed'
mut A3 $F 'vs = [c for c in cs if (c.get("user") or {}).get("login") in authors
              and (c.get("user") or {}).get("id") == vid' 'vs = [c for c in cs if (c.get("user") or {}).get("id") == vid'
mut A4 $F 'vs = [c for c in cs if (c.get("user") or {}).get("login") in authors
              and (c.get("user") or {}).get("id") == vid and' 'vs = [c for c in cs if (c.get("user") or {}).get("login") in authors
              and'
mut A5 $F '        v = max(vs, key=lambda c: (c.get("created_at") or "", c.get("id") or 0))
        body = v.get("body") or ""' '        v = min(vs, key=lambda c: (c.get("created_at") or "", c.get("id") or 0))
        body = v.get("body") or ""'
mut A6 $F '        if f"\nbus: verdict/{n} at {tip}," not in body:' '        if False:'
mut A7 $F '        if got is None or got[0] != "merge":' '        if got is None:'
mut A8 $F '            if "CARRY: yes" not in o:
                return f"the verdict' '            if False:
                return f"the verdict'
mut A9 $F '        if verdict != h:
            self.run(["git", "fetch", "-q", "origin", verdict, h])' '        if True:
            self.run(["git", "fetch", "-q", "origin", verdict, h])'
mut A10 $F '        for pr in sorted(prs, key=lambda p: int(p.get("number") or 0)):' '        for pr in prs:'
mut A11 $F '            prs = json.loads(o) if code == 0 else None' '            prs = json.loads(o) if code == 0 else []'
mut A12 $F '        code, o = self.run(["git", "ls-remote", "origin", "refs/heads/verdict/*"])
        if code:' '        code, o = self.run(["git", "ls-remote", "origin", "refs/heads/verdict/*"])
        if False:'
# The add admission (Train.admit_add): its `verdict` rule (Train.add_verdict), then
# each rule R10-TRAIN-UPGRADE gave it, one mutant per rule.
mut V1 $F '            why = self.add_verdict(pr, v, item) if self.real else None' '            why = None'
mut V2 $F '        if got[0] != v:' '        if False:'
mut V3 $F '        elif str(item["verdict_comment"]) != got[1]:' '        elif False:'
mut V4 $F '            item["verdict_comment"] = got[1]' '            pass'
mut V5 $F '        if code:
            return f"the verdict bus could not be read' '        if False:
            return f"the verdict bus could not be read'
mut V6 $F '        tip = next((ln.split()[0] for ln in o.splitlines() if ln.split() and is_sha(ln.split()[0])), None)' '        tip = "7" * 40'
mut R1 $F '        if not is_sha(v):
            return f"shape: verdict' '        if False:
            return f"shape: verdict'
mut R2 $F '            if view.get("state") != "OPEN":' '            if False:'
mut R3 $F '            if view.get("baseRefName") != self.base:' '            if False:'
mut R4 $F '                if "CARRY: yes" not in o:
                    return (f"carry:' '                if False:
                    return (f"carry:'
mut R5 $F '            if f"{ROW_DIR}/{pr}.md" not in files:
                return f"row: #{pr} has no' '            if False:
                return f"row: #{pr} has no'
mut R6 $F '            if raises and not held:' '            if False:'
mut R7 $F '            if pol and not self.mandate_id():' '            if False:'
# P96(b), the carried single into a live train: the add reads its carry without
# the queue lock (C1), or never reads it at all (C2).
mut C1 $F '    with queue_lock(t.state):
        live = read_pid(t.state / QUEUE_OPEN)' '    with contextlib.nullcontext():
        live = read_pid(t.state / QUEUE_OPEN)'
mut C2 $F '            if v != h:
                o = self.run(["bash", tool("app_approve"), "--carry", v, h])[1]' '            if False:
                o = self.run(["bash", tool("app_approve"), "--carry", v, h])[1]'
# The sweep (sweep, AUTO_TRAIN_FLAGS) and train_add's one-train rule under it.
mut S1 $F '        if seen.get(str(pr)) == head:' '        if False:'
mut S2 $F '        if rc == 2:
            t.log(f"SWEEP REFUSED start' '        if False:
            t.log(f"SWEEP REFUSED start'
mut S3 $F '        if rc:
            refused += 1' '        if False:
            refused += 1'
mut S4 $F '    if stops:
        _, subj, sha, when, _ = stops[0]' '    if False:
        _, subj, sha, when, _ = stops[0]'
mut S5 $F 'AUTO_TRAIN_FLAGS = ("--bot-prs", "--approval-carry", "--pre-flight")' 'AUTO_TRAIN_FLAGS = ("--bot-prs", "--approval-carry")'
mut S6 $F '        seen[str(pr)] = head' '        seen[str(pr)] = None'
mut S7 $F '        if live:
            spool_append(t.state, entry)' '        if False:
            spool_append(t.state, entry)'
mut S8 $F '        if a.auto and rest:' '        if False:'
# The event add (bus.sh's train_add, after a post) and the loop's step.
mut B1 $B '  [ -n "${HPO_BUS_TRAIN_STATE:-}" ] || return 0' '  true || return 0'
mut B2 $B '  case $2 in "Fix review: merge "*) sha=$(verdict_sha "$2") || return 0 ;; *) return 0 ;; esac' '  sha=$(verdict_sha "$2") || return 0'
mut B3 $B '  train_add "$pr" "$first"
}' '  :
}'
mut T1 $L '  [ -z "$sweep" ] || sweep_pass "$out"  # mut:sweep' '  sweep_pass "$out"  # mut:sweep'
mut T2 $L '  [ -z "$sweep" ] || sweep_pass "$out"  # mut:sweep' '  :  # mut:sweep'
mut T3 $L '  [ $(( $(date +%s) - last )) -ge "$every" ] || return 0  # mut:due' '  true || return 0  # mut:due'
# The grammar's one reader: a copy of the merge pattern inlined at either call
# site, the shape agreement_py refused at the r1 head.
RX='^Fix review: merge ([0-9a-f]{40})$'
mut G1 $F '        got = proof_watch.parse_verdict(first)' "        got = (lambda m: (\"merge\", m.group(1)) if m else None)(re.match(r\"$RX\", first))"
mut G2 $O '            kind, at = pw.parse_verdict(first) or ("", "")' "            m = re.match(r\"$RX\", first)
            kind, at = (\"merge\", m.group(1)) if m else (pw.parse_verdict(first) or (\"\", \"\"))"
