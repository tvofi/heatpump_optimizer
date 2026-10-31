# shellcheck shell=bash
# The shell twin of tests/throwaway_git.py: the one way a tracked shell script
# builds a throwaway git repository. Source it, then
#
#   throwaway_git_init <dir> [git init args...]   # e.g. throwaway_git_init "$W/r" -q -b main
#   throwaway_git_clone [git clone args...] <src> <dest>
#   throwaway_git_env                              # in the subshell that runs git in <dir>
#
# throwaway_git_env EXPORTS into the calling shell, so call it inside the
# subshell or self-test that owns the repository, never at a script's top
# level. throwaway_git_init and throwaway_git_clone run in their own subshell
# and change nothing in the caller. What each sets and why -- auto-maintenance off through the
# environment AND the repository's own config, GIT_CONFIG_PARAMETERS dropped
# because git reads it after GIT_CONFIG_COUNT -- is the Python module's
# docstring; `python3 tests/throwaway_git.py --self-test` pins that this file
# sets the same variables to the same values.

throwaway_git_env() {
  local v
  unset GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_CONFIG GIT_CONFIG_PARAMETERS \
    GIT_CONFIG_COUNT GIT_OBJECT_DIRECTORY GIT_DIR GIT_WORK_TREE \
    GIT_IMPLICIT_WORK_TREE GIT_GRAFT_FILE GIT_INDEX_FILE GIT_NO_REPLACE_OBJECTS \
    GIT_REPLACE_REF_BASE GIT_PREFIX GIT_INTERNAL_SUPER_PREFIX GIT_SHALLOW_FILE \
    GIT_COMMON_DIR
  for v in $(compgen -v GIT_CONFIG_KEY_; compgen -v GIT_CONFIG_VALUE_); do
    unset "$v"
  done
  export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t \
    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_COUNT=2 \
    GIT_CONFIG_KEY_0=maintenance.auto GIT_CONFIG_VALUE_0=false \
    GIT_CONFIG_KEY_1=gc.auto GIT_CONFIG_VALUE_1=0
}

throwaway_git_init() {
  local d="$1"
  shift
  mkdir -p "$d" && (
    cd "$d" && throwaway_git_env && git init "$@" >/dev/null &&
      git config maintenance.auto false && git config gc.auto 0
  )
}

throwaway_git_clone() {
  (throwaway_git_env && git clone -c maintenance.auto=false -c gc.auto=0 "$@")
}
