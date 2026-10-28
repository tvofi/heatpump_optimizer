#!/bin/bash
# The re-cut shim (spike beatd_shims/git) with HPO_REAL_GIT poisoned six ways, under /bin/bash 3.2.
# Usage: poisoned_real_git.sh <shim>
SH=${1:?shim}; W=$(mktemp -d); mkdir -p "$W/s"; cp "$SH" "$W/s/git"; cd "$W"
p() { out=$(PATH="$W/s:/usr/bin:/bin" HPO_REAL_GIT="$2" /bin/bash -c 'git --version' 2>&1); echo "$1: rc=$? ${out%%$'\n'*}" | sed "s,$W,<tmp>,g"; }
p "missing file" /nonexistent/git
p "a directory" /usr/bin
p "the shim itself" "$W/s/git"
p "a relative path to the shim" s/git
p "empty" ""
p "an arbitrary executable" /bin/echo
cd /; rm -rf "$W"
