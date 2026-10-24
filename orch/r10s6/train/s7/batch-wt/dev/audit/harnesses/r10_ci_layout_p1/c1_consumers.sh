#!/bin/sh
# W1's census (R10-CI-LAYOUT PR 1): every tracked reader or writer of the
# round-9 C1 composition at a revision, by the design's own grep, read from
# the archived design ref rather than copied.
#   sh dev/audit/harnesses/r10_ci_layout_p1/c1_consumers.sh [REV]   (default HEAD)
# Prints the design script's matching lines and its `--- files:` list.
git show archive/probe/design-ci-rev4:measure/rev/c1_consumers.sh | sh -s "${1:-HEAD}"
