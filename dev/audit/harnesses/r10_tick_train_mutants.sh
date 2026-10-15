#!/bin/bash
# R10-TICK-TRAIN (#2305): the mutation drive for the 2026-10-15 merge_train.py
# options. R1-R17 are rev-2305's planted mutants, verbatim; J1 drops the gate's
# justification from _owner_at_head. Each removes one predicate, runs the
# self-test, restores the file, and prints the self-test's last line and its
# FAIL lines: a killed mutant prints failures, a survivor "0 failed". R2 is
# equivalent (the bound raises before the extra range is reached) and
# survives by construction. The CI mutation lane does not cover this file:
# its scope is production code, and nothing under tools/ is in it.
# Run from a clean checkout of the branch, all mutants or the ones named:
#   bash dev/audit/harnesses/r10_tick_train_mutants.sh [R4 R11 ...]
cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
git diff --quiet -- tools/audit/seat/merge_train.py || { echo "merge_train.py has uncommitted edits; the restore would erase them"; exit 2; }
F=tools/audit/seat/merge_train.py
want=" $* "
mut() { # name, python replace old->new
  name=$1; old=$2; new=$3
  [ "$want" = "  " ] || [[ "$want" == *" $name "* ]] || return 0
  python3 - "$F" "$old" "$new" 2>/dev/null <<'P' || { echo "== $name: PATTERN NOT FOUND"; return; }
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); assert s.count(o)==1; open(p,'w').write(s.replace(o,n))
P
  out=$(python3 $F --self-test 2>&1); git checkout -q -- $F
  echo "== $name: $(echo "$out" | tail -1)"; echo "$out" | grep FAIL | sed 's/^/     /'
}
[ "$want" = "  " ] || [[ "$want" == *" M0 "* ]] && echo "== M0 baseline: $(python3 $F --self-test 2>&1 | tail -1)"
mut R1 '        if not is_sha(here) or here != there:' '        if here != there:'
mut R2 '        for n in range(self.main_moved_tries + 1):' '        for n in range(self.main_moved_tries + 2):'
mut R3 'and recover and moves < self.main_moved_tries:' 'and recover and moves <= self.main_moved_tries:'
mut R4 '                    recover = recover and phase != "post-merge"' '                    recover = True'
mut R5 '        return why if ok else None
' "        return why or 'mut'
"
mut R6 '        if n == "0":
            return
' ''
mut R7 '        self.run(["gh", "pr", "merge", n, "--repo", self.repo, "--merge", "--match-head-commit", h])' '        self.run(["gh", "pr", "merge", n, "--repo", self.repo, "--merge"])'
mut R8 '        if not (self.pre_flight and self.real):
            return list(queue)' '        if not (self.pre_flight):
            return list(queue)'
mut R9 '        return 1 if self.skipped else 0' '        return 0'
mut R10 '        if why is None and self.ok("git", "-C", holder, "checkout"' '        if self.free_holders and holder and self.ok("git", "-C", holder, "checkout"'
mut R11 '        chain = [c for c in item.get("carried_chain") or [item.get("carried_from")] if is_sha(c or "") and c != h]' '        chain = [c for c in [item.get("carried_from")] if is_sha(c or "") and c != h]'
mut R12 '            if [f for f in out.split() if f in files]:
                return None  # a branch-own file moved' '            if False:
                return None  # a branch-own file moved'
mut R13 'BASE_MOVED = re.compile(r"base branch was modified|not up to date|head branch is behind|is behind the base", re.I)' 'BASE_MOVED = re.compile(r"not up to date|head branch is behind|is behind the base", re.I)'
mut R14 '        if not (self.bot_prs and self.real):
            return' '        if not (self.bot_prs):
            return'
mut R15 '                        todo, first = list(zip(k2, p2)), True' '                        todo, first = list(zip(k2, p2)), False'
mut R16 '            self.sweep_bots()  # before the base is read' '            pass  # before the base is read'
mut R17 '                        prev = self.git("rev-parse", f"origin/{self.base}")
                        rest' '                        rest'
mut J1 ',
                                 justify=lambda: g.justification(self._body(pr)))' ')'
