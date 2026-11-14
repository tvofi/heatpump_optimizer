#!/bin/bash
# body_push.sh <topic> <body.md> [note.md]
# Publishes a handoff's transport on the orphan ref handoff-body/<topic>, so it
# never enters the code head's ancestry (`prepr.sh` step 1a refuses that).
# Each call appends one commit whose tree is BODY.md, plus RESUME.md when a note
# is given. The first commit has no parent, so the ref shares no history with
# the code; later ones are fast-forwards, so a re-bodied handoff needs neither a
# force-push nor a `-vN` branch. A fetch that fails for any reason but a missing
# ref leaves a parentless commit the push then refuses as a non-fast-forward,
# never a rewrite. `handoff_push.sh` reads BODY.md from the ref's tip.
# Plain variables, no arrays: macOS /bin/bash 3.2 rejects an empty array under -u.
set -euo pipefail
if [ "${1:-}" = "--self-test" ]; then
  # A local bare origin, stub predictor / lint / packet / landing, the real ref_privacy guard. Each
  # refusal path must keep the body on handoff-wip/t-body and still exit 1; each `# mut:keep` call is
  # then deleted from a copy and the same arms must fail.
  set +e; SELF=$(cd "$(dirname "$0")" && pwd)/$(basename "$0"); SH=$(dirname "$SELF")
  W=$(mktemp -d) || exit 2; trap 'rm -rf "$W"' EXIT
  FAILS=0; N=0; st() { N=$((N + 1)); if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (got '$1', want '$2')"; FAILS=$((FAILS + 1)); fi; }
  # shellcheck source=../../../tests/throwaway_git.sh
  . "$SH/../../../tests/throwaway_git.sh"
  mkcopy() { mkdir -p "$W/$1/audit/seat" "$W/$1/pr"; cp "$SH/ref_privacy.py" "$W/$1/audit/seat/"
    if [ "$2" = real ]; then cp "$SELF" "$W/$1/audit/seat/body_push.sh"; else sed '/# mut:keep$/s/.*/    :/' "$SELF" > "$W/$1/audit/seat/body_push.sh"; fi
    printf '#!/bin/bash\n[ "$1" = --body-check ] && [ -f "$FLAGS/lint" ] && { echo lint-stub-refuses; exit 1; }\nexit 0\n' > "$W/$1/pr/prepr.sh"
    printf 'import os\nopen(os.environ["FLAGS"] + "/refreshed", "w").close()\n' > "$W/$1/pr/figure_block.py"; }
  mkcopy t real; mkcopy m mutant
  printf '#!/bin/bash\nexit 0\n' > "$W/packer"; printf '#!/bin/bash\n[ -f "$FLAGS/packet" ] && exit 1\nexit 0\n' > "$W/packer"
  printf '#!/bin/bash\n[ -f "$FLAGS/landed" ] && exit 1\nexit 0\n' > "$W/landed"; chmod +x "$W/packer" "$W/landed"
  throwaway_git_init "$W/o.git" -q --bare; throwaway_git_init "$W/repo" -q
  mkdir -p "$W/repo/tools/pr"
  printf 'import os, sys\nsys.exit(1 if os.path.exists(os.environ["FLAGS"] + "/pred") else 0)\n' > "$W/repo/tools/pr/ci_predict.py"
  ( cd "$W/repo" && throwaway_git_env && echo a > a && git add . && git commit -qm code && git remote add origin "$W/o.git" \
    && git push -q origin HEAD:refs/heads/main && git fetch -q origin && git push -q origin HEAD:refs/heads/handoff/t ) >/dev/null 2>&1
  # A hook that refuses any push to handoff-wip/, installed for the failed-keep arm only.
  printf '#!/bin/sh\nwhile read o n r; do case $r in refs/heads/handoff-wip/*) exit 1;; esac; done\n' > "$W/hook"; chmod +x "$W/hook"
  run() { # copy -> rc ; FLAGS names the refusal switches, out in $W/out
    ( cd "$W/repo" && throwaway_git_env && FLAGS="$W/flags" HPO_HANDOFF_PACKER="$W/packer" HPO_HANDOFF_LANDED="$W/landed" \
        bash "$W/$1/audit/seat/body_push.sh" t "$W/body.md" > "$W/out" 2>&1 ); }
  keepsha() { git -C "$W/o.git" rev-parse -q --verify refs/heads/handoff-wip/t-body 2>/dev/null || echo none; }
  drop() { git -C "$W/o.git" update-ref -d refs/heads/handoff-wip/t-body 2>/dev/null; rm -rf "$W/flags"; mkdir -p "$W/flags"; }
  drop
  CODE=$(git -C "$W/repo" rev-parse HEAD)
  printf '## Head\n\n%s\n\n## Other\n\nthe body\n' "$CODE" > "$W/body.md"; BODYTXT=$(cat "$W/body.md")
  for arm in pred lint packet landed; do
    drop; : > "$W/flags/$arm"; run t; rc=$?
    want=1; [ "$arm" != landed ] || want=4  # CARRY-LANDED alone is exit 4, so the relay can fold it
    st "$rc" "$want" "REFUSE $arm: exit code ($want)"
    tok=$(echo "$arm" | tr a-z A-Z); case $arm in pred) tok=PREDICTOR;; lint) tok=BODY-LINT;; packet) tok=REVIEW-PACKET;; landed) tok=CARRY-LANDED;; esac
    st "$(grep -c "^body_push: REFUSED $tok\$" "$W/out")" 1 "... and the output names the refusal REFUSED $tok"
    k=$(keepsha)
    st "$(git -C "$W/o.git" show "$k:BODY.md" 2>/dev/null)" "$BODYTXT" "... and the refused body is kept at handoff-wip/t-body"
    st "$(grep -c "^body_push: refused body kept at handoff-wip/t-body $k\$" "$W/out")" 1 "... and the keep line names the ref and sha"
    st "$(git -C "$W/o.git" rev-list --count "$k" 2>/dev/null)" 1 "... as a parentless commit"
    st "$(git -C "$W/repo" merge-base --is-ancestor "$k" "$CODE" 2>/dev/null; echo $?)" 1 "(null) the kept body is not in the code head's ancestry"
    drop; : > "$W/flags/$arm"; run m; rc=$?
    st "$(keepsha)" none "MUTANT keep deleted ($arm): nothing is kept, so the arm above would fail"
  done
  drop; : > "$W/flags/lint"; run t; first=$(keepsha); run t
  st "$(git -C "$W/o.git" rev-parse "$(keepsha)^" 2>/dev/null)" "$first" "a second refusal fast-forwards the keep ref"
  drop; : > "$W/flags/lint"; cp "$W/hook" "$W/o.git/hooks/pre-receive"; run t; rc=$?
  st "$rc$(keepsha)" 1none "a keep whose push fails leaves the same refusal"
  st "$(grep -c 'could not be kept at handoff-wip/t-body; the refusal stands' "$W/out")" 1 "... and says the keep failed"
  rm -f "$W/o.git/hooks/pre-receive"
  drop; : > "$W/flags/lint"; run t; st "$(keepsha | grep -c .)" 1 "a refusal is kept before the healthy run"
  rm -rf "$W/flags"; mkdir -p "$W/flags"; run t; rc=$?
  st "$rc" 0 "the healthy run pushes"
  st "$(git -C "$W/o.git" show handoff-body/t:BODY.md 2>/dev/null)" "$BODYTXT" "... to handoff-body/t"
  st "$(keepsha)" none "... and the keep ref is gone"
  st "$([ -f "$W/flags/refreshed" ] && echo ran || echo no)" ran "the seat-side figure-block refresh ran"
  drop; run m; st "$([ -f "$W/flags/refreshed" ] && echo ran || echo no)" no "MUTANT refresh deleted: the arm above would fail"
  st "$(git -C "$W/repo" merge-base --is-ancestor "$(git -C "$W/o.git" rev-parse handoff-body/t)" "$CODE" 2>/dev/null; echo $?)" 1 "(null) the published body is not in the code head's ancestry"
  # head-stale: a body whose ## Head names another sha is refused and nothing is pushed; the fresh one (null) passes.
  OTHER=$(printf '%040d' 7); drop; git -C "$W/o.git" update-ref -d refs/heads/handoff-body/t
  printf '## Head\n\n%s\n\n## Other\n\n%s\n' "$OTHER" "$CODE" > "$W/body.md"; run t; rc=$?
  st "$rc$(grep -c "^body_push: REFUSE head-stale: ## Head does not name the handoff's code sha $CODE; it names $OTHER\$" "$W/out")" 11 "REFUSE head-stale: a stale ## Head is refused, naming both shas"
  st "$(git -C "$W/o.git" rev-parse -q --verify refs/heads/handoff-body/t 2>/dev/null || echo none)" none "... and nothing is pushed to handoff-body/t"
  printf '## Head\n\n%s\n' "$CODE" > "$W/body.md"; drop; run t; rc=$?
  st "$rc$(grep -c head-stale "$W/out")" 00 "(null) a ## Head naming the code sha passes the head check"
  echo "body_push self-test: $N checks, $FAILS failed"; [ "$FAILS" = 0 ]; exit $?
fi
TOPIC=${1:?topic}; BODY=${2:?body file}; NOTE=${3:-}
REF=handoff-body/$TOPIC
# The receipt (P386): prepr.sh's last passing full run in this checkout wrote
# `<sha> <tree>` to hpo-prepr-receipt in its git dir. When that sha is the code
# head this body describes and that tree is the head's, the body commit carries
# it as a `Prepr: <sha> <tree>` trailer, which app_push.sh --reuse reads so the
# run is not repeated at open or update. Anything else carries none.
prepr_trailer() { # checkout root, code head -> `Prepr: <sha> <tree>`, or nothing
  local f s t
  f=$(git -C "$1" rev-parse --absolute-git-dir 2>/dev/null)/hpo-prepr-receipt
  [ -f "$f" ] && read -r s t _ < "$f" || return 0
  [[ $s =~ ^[0-9a-f]{40}$ && $t =~ ^[0-9a-f]{40}$ ]] || return 0
  [ "$s" = "$2" ] && [ "$t" = "$(git -C "$1" rev-parse "$2^{tree}" 2>/dev/null)" ] || return 0
  printf 'Prepr: %s %s' "$s" "$t"
}
[ -f "$BODY" ] || { echo "body_push: no body at $BODY" >&2; exit 2; }
[ -z "$NOTE" ] || [ -f "$NOTE" ] || { echo "body_push: no note at $NOTE" >&2; exit 2; }
# A refusal after the body exists must not cost the body: keep_refused publishes it on the orphan
# ref handoff-wip/<topic>-body (parentless, then fast-forward, as the real push below), a prefix
# neither cloud_relay.sh's handoff arm nor `bus.sh orphans` lists. It changes neither the refusal
# nor its exit code; a failed keep is said and nothing else. drop_keep removes it after a success.
keep_refused() {
  local kref=handoff-wip/$TOPIC-body kdir; kdir=$(dirname "$0")
  (
    kt=$(git ls-remote origin "refs/heads/$kref" 2>/dev/null | awk 'NF { print $1; exit }') || kt=""
    kp=""
    if [ -n "$kt" ]; then git fetch -q origin "refs/heads/$kref" || exit 1; kp="-p $kt"; fi
    kf="${TMPDIR:-/tmp}/body_keep.$$"
    { printf '100644 blob %s\tBODY.md\n' "$(git hash-object -w -- "$BODY")"
      [ -z "$NOTE" ] || printf '100644 blob %s\tRESUME.md\n' "$(git hash-object -w -- "$NOTE")"; } > "$kf" || exit 1
    kx=$(git mktree < "$kf"); rm -f "$kf"
    # shellcheck disable=SC2086 # $kp is empty or exactly "-p <sha>"
    kc=$(git commit-tree "$kx" $kp -m "refused body: $TOPIC") || exit 1
    python3 -I "$kdir/ref_privacy.py" guard --ref "$kref" --commits "$kc" || exit 1
    git push -q origin "$kc:refs/heads/$kref" || exit 1
    echo "body_push: refused body kept at $kref $kc"
  ) || echo "body_push: the refused body could not be kept at $kref; the refusal stands" >&2
  return 0
}
drop_keep() {
  local kref=handoff-wip/$TOPIC-body
  [ -n "$(git ls-remote origin "refs/heads/$kref" 2>/dev/null)" ] || return 0
  git push -q origin ":refs/heads/$kref" 2>/dev/null || echo "body_push: could not delete the kept body $kref" >&2
  return 0
}
# The handoff gate (dev/audit/rca/R10-HANDOFF-PREPR-BOUNCE.md, M2): the static
# predictor, over the code head this body describes (the checkout it runs in),
# refuses before the push a head that `open_pr.sh`'s prepr step 6d would refuse
# for a reason a static read names. Seconds, where a full prepr here (M1) costs
# minutes on every handoff and failed the RCA's cost test. Its output names
# each arm's repair (M3). A checkout with no predictor is refused, never passed.

ROOT=$(git rev-parse --show-toplevel)
[ -f "$ROOT/tools/pr/ci_predict.py" ] || { echo "body_push: $ROOT carries no tools/pr/ci_predict.py; run it from the code head's worktree" >&2; exit 1; }
if ! PRED=$(cd "$ROOT" && PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main 2>&1); then
  printf '%s\n' "$PRED" >&2
  echo "body_push: the predictor refuses this head (above); repair it, push the code, then the body" >&2
  echo "body_push: REFUSED PREDICTOR" >&2
  keep_refused # mut:keep
  exit 1
fi
# The pr-body gate (dev/audit/rca/R10-RCA-BODY-LINT.md). A body for the head
# published at handoff/<topic> is the pull-request body `open_pr.sh` lints in
# prepr step 7, so that step runs here first (`prepr.sh --body-check`, this
# script's sibling copy) and its refusal is this push's. No handoff/<topic>
# means a result (probe, design, verdict), which is no PR body. A handoff/<topic>
# that is not this checkout's HEAD names a head the open will not run on.
HERE=$(cd "$(dirname "$0")" && pwd)
HREF=$(git ls-remote origin "refs/heads/handoff/$TOPIC") || { echo "body_push: could not read handoff/$TOPIC from origin" >&2; exit 1; }
HREF=$(printf '%s\n' "$HREF" | awk 'NF { print $1; exit }')
if [ -n "$HREF" ]; then
  [ "$HREF" = "$(git -C "$ROOT" rev-parse HEAD)" ] || { echo "body_push: handoff/$TOPIC is at ${HREF:0:12}, this checkout at $(git -C "$ROOT" rev-parse --short=12 HEAD); push the code, then the body" >&2; exit 1; }
  ABS=$(cd "$(dirname "$BODY")" && pwd)/$(basename "$BODY")
  # The identity refusal at the handoff (P274): the code head's commits over main are judged
  # as the opener would judge them (its guard and the author-identity guard), so a commit authored by a
  # runner default is refused here, before the body ref -- the return signal -- is written.
  python3 -I "$HERE/ref_privacy.py" guard --ref "handoff/$TOPIC" --commits "$HREF" --over refs/remotes/origin/main -C "$ROOT" || {
    echo "body_push: a commit of handoff/$TOPIC fails the push guard (above); re-author it, push the code again, then the body" >&2
    exit 1
  }
  # After the identity guard, which outranks it (ref_privacy's self-test pins that order):
  # a body's ## Head is a claim about what was measured: refused, never rewritten, when it does not name this code sha.
  HEADSEC=$(awk '/^## Head[[:space:]]*$/ { f = 1; next } /^## / { f = 0 } f' "$BODY")
  case $HEADSEC in *"$HREF"*) ;; *)
    NAMED=$(printf '%s\n' "$HEADSEC" | grep -oE '[0-9a-f]{40}' | head -1 || true)
    echo "body_push: REFUSE head-stale: ## Head does not name the handoff's code sha $HREF; it names ${NAMED:-none}" >&2
    keep_refused
    exit 1 ;;
  esac
  # The `mutation` red an unpinned site makes is derived, so it is written into
  # `## Red checks` before the lint, not refused at the open (P67).
  (cd "$ROOT" && bash "$HERE/../../pr/prepr.sh" --fill-red "$ABS")
  # The seat-side writer re-renders every registered figure block at the code head with no
  # agent turn (card 7 option C); pr-contract only verifies. A refusal aborts the push (set -e).
  (cd "$ROOT" && python3 -I "$HERE/../../pr/figure_block.py" refresh "$ABS") # mut:keep
  # The red-check arm reads the pull request's head ref over the network, so it
  # is asked for only when origin holds fix/<topic> (a first handoff has none).
  PRB=""
  [ -z "$(git ls-remote origin "refs/heads/fix/$TOPIC" 2>/dev/null)" ] || PRB="--pr-branch fix/$TOPIC"
  # shellcheck disable=SC2086 # PRB is empty or exactly two words
  if ! LINT=$(cd "$ROOT" && bash "$HERE/../../pr/prepr.sh" --body-check "$ABS" $PRB 2>&1); then
    printf '%s\n' "$LINT" >&2
    echo "body_push: the pr-body lint refuses this body (above), as open_pr.sh's prepr step 7 would; repair it and push again" >&2
    echo "body_push: REFUSED BODY-LINT" >&2
    keep_refused # mut:keep
    exit 1
  fi
  printf '%s\n' "$LINT" | tail -1
  # The review packet's refusals that need no CI run (P256): structure merged
  # with main, hot-file and brief-carries, answered here rather than after the
  # open. rc 3 is a seat that cannot read their inputs: said, never a refusal.
  # HPO_HANDOFF_PACKER replaces the checker (prepr's self-test stub).
  prc=0
  PK=$(cd "$ROOT" && ${HPO_HANDOFF_PACKER:-python3 -I "$HERE/review_packet.py"} handoff --topic "$TOPIC" --body "$ABS" 2>&1) || prc=$?
  printf '%s\n' "$PK"
  if [ "$prc" = 1 ]; then
    echo "body_push: the review packet refuses this head at the handoff (above); answer each, push the code, then the body" >&2
    echo "body_push: REFUSED REVIEW-PACKET" >&2
    keep_refused # mut:keep
    exit 1
  elif [ "$prc" != 0 ]; then
    echo "body_push: the review packet's handoff refusals were not run (rc $prc, above); dispatch still runs structure and hot-file" >&2
  fi
  # The carry landing (CARRY 11, P287): a body carry its group does not yet hold, on main's
  # roster or the round's branch, is refused here, so it lands before the open rather than after
  # a review round (2 of 15 blocked verdicts on 2026-10-29). bus.sh dispatch runs the same check.
  # rc 3 (the roster unreadable) is said, never a refusal. HPO_HANDOFF_LANDED replaces the check.
  lrc=0
  LD=$(cd "$ROOT" && ${HPO_HANDOFF_LANDED:-python3 -I "$ROOT/tools/audit/carry_audit.py" --roster-ref origin/main} \
    landed --body "$ABS" --topic "$TOPIC" 2>&1) || lrc=$?
  printf '%s\n' "$LD"
  if [ "$lrc" = 1 ]; then  # mut:landed
    echo "body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body" >&2
    # exit 4, not 1: CARRY-LANDED alone, the one refusal a cloud fixer cannot repair (it may not
    # write the roster). cloud_relay.sh's carry-fold arm keys on this line in the BLOCKED.md.
    echo "body_push: REFUSED CARRY-LANDED" >&2
    keep_refused # mut:keep
    exit 4
  elif [ "$lrc" != 0 ]; then
    echo "body_push: the carry landing was not checked (rc $lrc, above); bus.sh dispatch checks it again" >&2
  fi
else
  echo "body_push: no handoff/$TOPIC on origin, so a result body: the pr-body lint does not apply"
fi
P=""
# The parent is what ORIGIN ANSWERED, never FETCH_HEAD. `git fetch` rewrites
# FETCH_HEAD as per-worktree state of the checkout it runs in, so any other
# fetch landing between the fetch below and the read -- a sibling seat, the
# orchestrator, a watcher -- substitutes an unrelated ref's tip and the push is
# refused non-fast-forward (R9-RC-BUS-FETCHHEAD: the predicate bus.sh carried).
# The fetch stays for the objects: commit-tree cannot write a parent it cannot
# read.
tip=$(git ls-remote origin "refs/heads/$REF" 2>/dev/null | awk 'NF { print $1; exit }') || tip=""
if [ -n "$tip" ]; then
  git fetch -q origin "refs/heads/$REF" || { echo "body_push: could not fetch $REF" >&2; exit 1; }
  P="-p $tip"
fi
{ printf '100644 blob %s\tBODY.md\n' "$(git hash-object -w -- "$BODY")"
  [ -z "$NOTE" ] || printf '100644 blob %s\tRESUME.md\n' "$(git hash-object -w -- "$NOTE")"
} > "${TMPDIR:-/tmp}/body_push.$$"
TREE=$(git mktree < "${TMPDIR:-/tmp}/body_push.$$")
rm -f "${TMPDIR:-/tmp}/body_push.$$"
# A PR body names the code head it describes in a `Code:` trailer, the handoff/<topic> tip
# proved equal to this checkout's HEAD above; cloud_relay.sh updates a PR only with the body
# naming the handoff it applies (V147). A result body names none.
MSG="body: $TOPIC"
[ -z "$HREF" ] || MSG=$(printf 'body: %s\n\nCode: %s' "$TOPIC" "$HREF")
PT=""; [ -z "$HREF" ] || PT=$(prepr_trailer "$ROOT" "$HREF")
if [ -n "$PT" ]; then
  MSG=$(printf '%s\n%s' "$MSG" "$PT"); echo "body_push: $PT (prepr's receipt at this code head)"
elif [ -n "$HREF" ]; then
  echo "body_push: no Prepr: trailer -- no receipt of a passing full prepr.sh run at ${HREF:0:12} in this checkout, so the open runs the full prepr"
fi
# shellcheck disable=SC2086 # $P is empty or exactly "-p <sha>"
C=$(git commit-tree "$TREE" $P -m "$MSG")
# The topic names the ref and the message: refuse one that names this host
# (#2310). The commit is judged as written, not as composed: its message and
# identity, and any parent origin does not hold (R10-FLY-NO-FOOTERS-PUSH-PATHS).
python3 -I "$(dirname "$0")/ref_privacy.py" guard --ref "$REF" --commits "$C"
git push -q origin "$C:refs/heads/$REF"
drop_keep
echo "$REF $C"
