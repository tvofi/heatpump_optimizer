#!/bin/bash
# R9-RO-12: the mutation drive for merge_train.py batch. Each mutant removes one
# predicate, runs the self-test, and restores the file; every mutant must print
# failures. Run from a clean checkout of the branch: bash dev/audit/harnesses/r9_ro12_batch_mutants.sh
cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
git diff --quiet -- tools/audit/seat/merge_train.py || { echo "merge_train.py has uncommitted edits; the restore would erase them"; exit 2; }
F=tools/audit/seat/merge_train.py
mut() { # name, python replace old->new
  name=$1; old=$2; new=$3
  python3 - "$F" "$old" "$new" <<'P' || { echo "$name: PATTERN NOT FOUND"; return; }
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); assert s.count(o)==1; open(p,'w').write(s.replace(o,n))
P
  out=$(python3 $F --self-test 2>&1); git checkout -q -- $F
  echo "== $name: $(echo "$out" | tail -1)"; echo "$out" | grep FAIL | sed 's/^/     /'
}
echo "== M0 baseline: $(python3 $F --self-test 2>&1 | tail -1)"
mut M1-no-driver-override 'for x in ("-c", f"merge.{n}.driver=git merge-file %A %O %B")]' 'for x in ()]'
mut M2-no-post-merge-tree-check 'if self.tree(tip) != self.tree(p):' 'if False:'
mut M3-no-pre-merge-guard 'if self.tree(f"origin/{self.base}") != self.tree(prev):' 'if False:'
mut M4-no-serial-routing 'route = sorted({c for f in files if (c := mf.file_class(f, graders))})' 'route = []'
mut M5-no-proof 'if len(kept) < 2:
                return kept, proofs, dropped' 'if True:
                return kept, proofs, dropped'
mut M6-no-pr-only 'names = sorted({n.strip() for n in o.splitlines() if n.strip()} - set(PR_ONLY))' 'names = sorted({n.strip() for n in o.splitlines() if n.strip()})'
mut M7-no-culprit 'return owners.pop() if len(owners) == 1 else None' 'return None'
mut M8-no-conflict-route 'if code == 1:
                self.log' 'if False:
                self.log'
mut M9-no-admission-ci 'if red:
            raise Stop("ci", f"#{pr} red at its head: "' 'if False:
            raise Stop("ci", f"#{pr} red at its head: "'
mut M10-log-read-without-escapes '"gh", "api", "--allow-escape-sequences",' '"gh", "api",'
