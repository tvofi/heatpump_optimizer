TRANSPORT_ROOTS=(tools/audit/handoff/ handoff/)
transport_in_ancestry() { # merge base, head -> 0 clean, 1 found (prints `<sha> <path>`), 2 unreadable
  local out
  out=$(git log --full-history -c --diff-filter=ACMRT --name-only \
        --format='@%h' "$1..$2" -- "${TRANSPORT_ROOTS[@]}" 2>/dev/null) || return 2
  out=$(printf '%s\n' "$out" | awk '/^@/{c=substr($0,2);next} NF{print c" "$0}')
  [ -z "$out" ] && return 0
  printf '%s\n' "$out"
  return 1
}
