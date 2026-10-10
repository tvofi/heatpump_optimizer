RESULT evidence for fix review of #2107, head da2b6345011354ef7ec5b30b1cd57da2d95dbb83
reviewer worktree: /Users/timmalmstrom/hpo-seats/r9rev-2107/wt (detached at that SHA)
merge base: 1301d7e45df08bc224d420db4508195050b88972

MEASURED_HEAD da2b6345011354ef7ec5b30b1cd57da2d95dbb83

RESULT arm-refusal      PASS  dispatch 2107 1301d7e45... -> rc 1, "carries no dev/programme/delivery/2107.md", $S untouched
RESULT arm-control      PASS  dispatch 2107 da2b6345011354ef7ec5b30b1cd57da2d95dbb83 -> rc 0, "bus-nonce: fe49db91fd53d834b81f586b8b2630bc", record appended
RESULT arm-early        PASS  dispatch is the sole writer of $S/dispatched (bus.sh:281); confirm needs dispatched_to (bus.sh:292)
RESULT mutation-A       PASS  row predicate forced true -> "47 checks, 1 failed" on the named arm; restored -> 47/0
RESULT self-test-head   PASS  bash tools/audit/seat/bus.sh --self-test -> 47 checks, 0 failed
RESULT self-test-base   PASS  same at merge base -> 45 checks, 0 failed
RESULT arm-set-delta    PASS  45 -> 47, 0 removed, +2 new arms (arms-base.txt vs arms-head.txt)
RESULT null-control     PASS  #2075 addd6f45758ff90ab862bcbe62357c1373ed7786: merge-base rc 0 (nonce b94bc76d...), head rc 1
RESULT live-bus-intact  PASS  ~/.zcode/bus/dispatched 361 -> 361 (live-bus-before.txt)
RESULT conflict         PASS  git merge-tree --write-tree origin/main da2b6345011354ef7ec5b30b1cd57da2d95dbb83 -> rc 0
RESULT red-checks       PASS  no check-run conclusion "failure" at any head in the range (checkruns-head.txt)
RESULT census-rerun     NOTE  row_position.py --limit 60 -> 39/20/0/1 (census-rerun.txt; body 41/17/1/1, live state moved)
RESULT version-untouched PASS diff is 3 files: bus.sh, row_position.py, delivery/2107.md

Files here:
  arms-base.txt arms-head.txt          the self-test arm sets, merge base vs head
  census-rerun.txt                     my re-derivation of row_position.py --limit 60
  checkruns-head.txt                   check-runs at the head
  dispatch-record-phantom.txt          the live #2107 dispatch record naming a non-existent head
  bus.sh.head bus-copy.sh              the script and the copy my arms ran against
  live-bus-before.txt                  live bus line count before the arms
