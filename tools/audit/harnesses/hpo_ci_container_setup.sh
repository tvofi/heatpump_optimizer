#!/bin/bash
# The standing hpo-ci container: the Linux environment this repository's
# kernel-sensitive measurements run in (#1725). CI's exact wheels on an
# amd64 Linux the Mac can reach (colima vz+rosetta; also runs on any amd64
# Docker host), kernel-switchable at run time with OPENBLAS_CORETYPE so one
# box reproduces Haswell / Sandybridge / Nehalem -- SkylakeX SIGILLs under
# Rosetta (no AVX-512); Apple Accelerate is the native Mac interpreter.
#
# Build (standing form on this Mac; <worktree> is the seat's checkout --
# the macfloat seat's standing mount source was /Users/timmalmstrom/macfloat-fix.
# If <worktree> is a linked worktree, its .git file points into the host
# repository, so mount that too (-v /Users:/Users) for git-based lanes like
# env_drift.py; the wheel provisioning below itself needs no git repo):
#   docker run -d --name hpo-ci -v <worktree>:/repo -v /Users:/Users \
#       python:3.14.7-slim sleep infinity
#   docker exec -w /repo hpo-ci bash tools/audit/harnesses/hpo_ci_container_setup.sh
# Run an instrument in it, kernel-pinned (the harness reports the kernel it got):
#   docker exec -e OPENBLAS_CORETYPE=Sandybridge -w /repo hpo-ci \
#       bash -c 'PYTHONPATH=tests/hastub python3 tools/audit/harnesses/k1725_blas_kernel_gap.py'
#
# REPO_MOUNT is the mount point inside the container (default /repo).
set -e
REPO_MOUNT="${REPO_MOUNT:-/repo}"
apt-get update -qq && apt-get install -y -qq build-essential tzdata git > /dev/null 2>&1
# from /, not $REPO_MOUNT: a mounted linked worktree's .git file points at a
# host path the container may not have, and git dies resolving it before the
# --global flag is even read (rc 128, measured in the fresh-container check)
( cd / && git config --global --add safe.directory "$REPO_MOUNT" )
pip install --require-hashes --build-constraint "$REPO_MOUNT/tests/requirements-build.txt" -r "$REPO_MOUNT/tests/requirements-ci.txt" 2>&1 | tail -1
python -c "import numpy; print('numpy', numpy.__version__)"
