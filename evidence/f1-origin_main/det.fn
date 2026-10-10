pipe_grep_q_sites() { # files... -> one `file:line: text` per site; rc 0 none, 1 found
  local pat out
  pat='(printf|echo)[^|]*[|][[:space:]]*grep[[:space:]]+-[a-zA-Z]*'"q"
  out=$(grep -nE "$pat" "$@" 2>/dev/null | grep -vE '^[^:]+:[0-9]+:[[:space:]]*#')
  [ -z "$out" ] && return 0
  printf '%s\n' "$out"; return 1
}
