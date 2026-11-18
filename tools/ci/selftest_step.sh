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
# The ungated steps (selftest_scope.py's UNGATED, which its self-test holds
# equal to UNTRACED here) are never traced: no table entry reads their trace,
# and a tracer breaks three of them. `launch` only starts the detached
# self-tests, which trace themselves through --as; a tracer on it would follow
# them, wait for them, and hold the ptrace slot each of their own tracers
# needs. `strace` runs sudo, which refuses under --seccomp-bpf's
# no_new_privs (run 42623897209, step 5). `drift` folds every trace; under
# ptrace each lstat its realpath calls makes is a stop, and the fold never
# finished inside the job's timeout (R10-HOTFIX-SELFTEST-SCOPE-HANG).
#
# -q, not -qq: each traced process's exit line stays in the trace, and
# selftest_scope.py refuses a trace whose first process has none (strace
# stopped before the step ended). With SELFTEST_TRACE set and no strace on
# PATH the step runs untraced, saying so; the drift check then refuses every
# step it left unmeasured, by name, instead of every step dying unexplained.
set -u
SYSCALLS=%file
UNTRACED=" scope strace launch drift unread "
traced() { # <trace file> <command...>: run the command under strace into the file
  if ! command -v strace > /dev/null 2>&1; then
    echo "selftest_step: SELFTEST_TRACE is set and no strace is on PATH: $1 not written, running untraced" >&2
    shift
    exec "$@"
  fi
  mkdir -p "${1%/*}"
  local out=$1
  shift
  exec strace -f -q -y --seccomp-bpf -e trace="$SYSCALLS" -o "$out" -- "$@"
}
if [ "${1:-}" = --as ]; then
  name=$2
  shift 2
  if [ -z "${SELFTEST_TRACE:-}" ]; then exec "$@"; fi
  traced "$RUNNER_TEMP/selftest-trace/bg-$name.trace" "$@"
fi
case "$UNTRACED" in *" ${GITHUB_ACTION:-} "*) untraced=1 ;; *) untraced= ;; esac
if [ -z "${SELFTEST_TRACE:-}" ] || [ -n "$untraced" ]; then
  exec bash --noprofile --norc -eo pipefail "$1"
fi
traced "$RUNNER_TEMP/selftest-trace/step-${GITHUB_ACTION:-unnamed}.trace" \
  bash --noprofile --norc -eo pipefail "$1"
