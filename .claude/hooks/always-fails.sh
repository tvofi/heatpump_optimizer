#!/bin/bash
# A HOOK WHOSE SELF-TEST FAILS, and the only reason it is in the tree.
#
# `--hooks` checks two things: the script exists, and its `--self-test` passes.
# Existence alone is the weaker half and would have accepted the first draft of
# pre-edit.sh, which was present, executable, wired -- and inert on every path
# it was written to refuse. This file exists so the SECOND half can be shown
# failing, which is the only thing that separates a check from a claim.
#
# It is not wired into .claude/settings.json and never runs outside
# `policy_lint --hooks .claude/workflows/fixtures/policy-rot/hooks/self-test-fails.json`.
[ "${1:-}" = "--self-test" ] && { echo "  FAIL this hook's self-test is meant to fail"; echo; echo "0 passed, 1 failed"; exit 2; }
exit 0
