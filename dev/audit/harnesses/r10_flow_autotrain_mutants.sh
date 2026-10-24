#!/bin/bash
# R10-FLOW-AUTOTRAIN: the mutation drive for merge_train.py's queue builder and
# pitch, and tick_loop.sh's --pitch step. Each mutant removes or inverts one
# admission or pitch rule, runs the owning self-test, restores the file, and
# prints the self-test's last line and its FAIL lines: a killed mutant prints
# failures, a survivor "0 failed". The CI mutation lane does not cover these
# files: its scope is production code, and nothing under tools/ is in it.
# Run from a clean checkout of the branch, all mutants or the ones named:
#   bash dev/audit/harnesses/r10_flow_autotrain_mutants.sh [A1 P3 ...]
cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
F=tools/audit/seat/merge_train.py L=tools/audit/seat/tick_loop.sh
git diff --quiet -- $F $L || { echo "$F or $L has uncommitted edits; the restore would erase them"; exit 2; }
want=" $* "
mut() { # name, file, python replace old->new (exactly one occurrence)
  name=$1; f=$2; old=$3; new=$4
  [ "$want" = "  " ] || [[ "$want" == *" $name "* ]] || return 0
  python3 - "$f" "$old" "$new" 2>/dev/null <<'P' || { echo "== $name: PATTERN NOT FOUND"; return; }
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); assert s.count(o)==1; open(p,'w').write(s.replace(o,n))
P
  if [ "$f" = "$L" ]; then out=$(bash $L --self-test 2>&1); else out=$(python3 $F --self-test 2>&1); fi
  git checkout -q -- "$f"
  echo "== $name: $(echo "$out" | tail -1)"; echo "$out" | grep FAIL | sed 's/^/     /'
}
if [ "$want" = "  " ] || [[ "$want" == *" M0 "* ]]; then
  echo "== M0 baseline: $(python3 $F --self-test 2>&1 | tail -1); $(bash $L --self-test 2>&1 | tail -1)"
fi
# The admission rules (Train.admit_verdict, Train.build_queue).
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
mut A7 $F '        m = self.VERDICT_MERGE.match(first)
        if not m:' '        m = self.VERDICT_MERGE.match(first) or self.VERDICT_BLOCKED.match(first)
        if not m:'
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
# The pitch (pitch, live_train, PITCH_FLAGS) and the loop's step.
mut P1 $F '    held = live_train(t.state)
    if held:' '    held = live_train(t.state)
    if False:'
mut P2 $F '    if not queue:
        t.log("PITCH EMPTY' '    if False:
        t.log("PITCH EMPTY'
mut P3 $F '    if last.get("key") == key:' '    if False:'
mut P4 $F '    if not any(ln.startswith("PRE-FLIGHT: ") for ln in o.splitlines()):' '    if False:'
mut P5 $F 'PITCH_FLAGS = ("--bot-prs", "--approval-carry", "--pre-flight")' 'PITCH_FLAGS = ("--bot-prs", "--approval-carry")'
mut P6 $F '    if not pid:
        t.log(f"PITCH REFUSED train' '    if False:
        t.log(f"PITCH REFUSED train'
mut P7 $F '    except ProcessLookupError:
        return None
    except PermissionError:' '    except ProcessLookupError:
        return pid
    except PermissionError:'
mut T1 $L '  [ -z "$pitch" ] || pitch_pass "$out"  # mut:pitch' '  pitch_pass "$out"  # mut:pitch'
mut T2 $L '  [ -z "$pitch" ] || pitch_pass "$out"  # mut:pitch' '  :  # mut:pitch'
mut P8 $F '    if stops:
        _, subj, sha, when, _ = stops[0]' '    if False:
        _, subj, sha, when, _ = stops[0]'
mut P9 $F '            if a.once:
                return rc' '            if True:
                return rc'
mut P10 $F '            time.sleep(max(a.every, 60))' '            time.sleep(60)'
mut T3 $L '  [ $(( $(date +%s) - last )) -ge "$every" ] || return 0  # mut:due' '  true || return 0  # mut:due'
