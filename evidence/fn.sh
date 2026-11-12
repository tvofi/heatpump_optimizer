op_host_refusal() {
  local rows other diff
  rows=$(grep -cE '^  REFUSE +self-test( |$)' $D/p2.log || :)
  other=$(grep REFUSE $D/p2.log | grep -vE '^  REFUSE +self-test( |$)|^app_push: REFUSE: the body did not pass tools/pr/prepr\.sh' | grep -c . || :)
  [ "$other" = 0 ] || return 1  # mut:hostother
  [ "${rows:-0}" -gt 0 ] || return 1
  diff=$(git -C "$WT" diff --name-only origin/main...HEAD) || return 1  # an unread diff is the branch's own
  ! grep -qxE 'tools/(pr|audit)/prepr\.sh' <<<"$diff" || return 1  # mut:hostguard
}
