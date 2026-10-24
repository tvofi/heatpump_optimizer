# Repository root for an audit harness. The same function is inlined in each
# script; this file is the copy a test reads, and the two texts match.

repo_root() {
  local d="$1"
  if [ -f "$d" ]; then
    d=$(dirname "$d")
  fi
  d=$(cd "$d" && pwd) || return 1
  while [ "$d" != "/" ]; do
    if [ -f "$d/custom_components/heatpump_optimizer/manifest.json" ]; then
      printf '%s\n' "$d"
      return 0
    fi
    d=$(dirname "$d")
  done
  printf 'no repository root above %s\n' "$1" >&2
  return 1
}
