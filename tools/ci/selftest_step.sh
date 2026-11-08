#!/usr/bin/env bash
# One shell for every step of governance.yml's `instrument-self-tests` job,
# and the tracer of its detached self-tests (R10-CI-SELFTEST-SCOPE).
#
#   bash tools/ci/selftest_step.sh SCRIPT          # a step: `shell:` hands it {0}
#   bash tools/ci/selftest_step.sh --as NAME CMD... # a detached self-test (bg_run)
#
# With SELFTEST_TRACE empty, a step runs as the runner's default bash shell
# runs it (`bash --noprofile --norc -eo pipefail {0}`) and --as executes CMD
# as it is: this file changes nothing about a run that records nothing.
#
# With SELFTEST_TRACE set (every push to main, and `selftest_scope.py record`),
# the step runs under `strace -f` into
# $RUNNER_TEMP/selftest-trace/step-$GITHUB_ACTION.trace -- GITHUB_ACTION is the
# step's `id:` -- and --as NAME into bg-NAME.trace. selftest_scope.py folds
# those traces into each step's read set and refuses a committed table
# (tools/ci/selftest_closures.json) that misses a file a step read.
#
# The launcher step (id `launch`) is never traced itself: it only starts the
# detached self-tests, which trace themselves through --as, and a tracer on
# it would follow them, wait for them, and hold the ptrace slot each of their
# own tracers needs.
set -u
SYSCALLS=%file
if [ "${1:-}" = --as ]; then
  name=$2
  shift 2
  if [ -z "${SELFTEST_TRACE:-}" ]; then exec "$@"; fi
  d="$RUNNER_TEMP/selftest-trace"
  mkdir -p "$d"
  exec strace -f -qq -y -e trace="$SYSCALLS" -o "$d/bg-$name.trace" -- "$@"
fi
if [ -z "${SELFTEST_TRACE:-}" ] || [ "${GITHUB_ACTION:-}" = launch ]; then
  exec bash --noprofile --norc -eo pipefail "$1"
fi
d="$RUNNER_TEMP/selftest-trace"
mkdir -p "$d"
exec strace -f -qq -y -e trace="$SYSCALLS" -o "$d/step-${GITHUB_ACTION:-unnamed}.trace" \
  -- bash --noprofile --norc -eo pipefail "$1"
