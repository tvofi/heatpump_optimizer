#!/usr/bin/env bash
# The throwaway-repository cleanup race (R9-RCA-stamp-race): a git that
# detaches auto-maintenance after `commit`/`merge` keeps writing into
# .git/objects/pack while tempfile.TemporaryDirectory removes the repository,
# and the removal fails with `OSError: [Errno 39|66] Directory not empty`.
#
# Git >= 2.54 (CI's runner ships 2.55.0) runs the "geometric" maintenance
# strategy on every auto-maintenance, detached by default; its repack fires
# once two loose objects share the objects/17 shard (builtin/gc.c
# geometric_repack_auto_condition, odb/source-loose.c's approximate count).
# The seat's git (2.38) never reaches that condition on a small repository,
# so this harness MODELS it: a `git` shim on PATH runs the real git, then --
# after commit or merge, and only when git 2.55's own gate would
# (run-command.c prepare_auto_maintenance: `maintenance.auto`, falling back
# to `gc.auto > 0`) -- forks a detached writer that keeps creating files in
# objects/pack for WRITE_S seconds, as the repack's temporary pack files do.
# The gate is read through the real `git config`, so the shim honours the
# same config the fix sets, by whatever route it is set.
#
#   bash dev/audit/harnesses/git_auto_maintenance_race.sh [RUNS] [shim|plain]
#   bash dev/audit/harnesses/git_auto_maintenance_race.sh 0 spawn
#
# Arm `spawn` uses no model: it asks the real git (GIT_TRACE) whether a
# commit spawns `git maintenance run --auto`, with no config and with the
# env-config `maintenance.auto=false` the fix sets.
#
# Arm `shim` (default) is the perturbation; arm `plain` is the null control
# (no shim). It runs `tools/release/stamp.py --self-test` RUNS times and
# prints, per arm: runs, runs whose output names "Directory not empty",
# and runs that exited non-zero for any reason, after the last such line.
set -u
RUNS="${1:-3}"
ARM="${2:-shim}"
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
W="$(mktemp -d)"
trap 'rm -rf "$W"' EXIT
REAL_GIT="$(command -v git)"
if [ "$ARM" = spawn ]; then
  ( cd "$W" && "$REAL_GIT" init -q r && cd r && : > a && "$REAL_GIT" add a
    for cfg in default off; do
      [ "$cfg" = off ] && export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=maintenance.auto GIT_CONFIG_VALUE_0=false
      echo "$cfg" >> a
      n=$(GIT_TRACE=1 "$REAL_GIT" -c user.name=t -c user.email=t@t commit -qam x 2>&1 \
          | grep -c "run_command: git maintenance run --auto")
      echo "arm=spawn config=$cfg git=$("$REAL_GIT" --version | cut -d' ' -f3) maintenance_spawns=$n"
    done )
  exit 0
fi
mkdir -p "$W/bin"
cat > "$W/bin/git" <<EOF
#!/usr/bin/env bash
"$REAL_GIT" "\$@"; rc=\$?
case " \$* " in *" commit "*|*" merge "*) ;; *) exit \$rc ;; esac
en=\$("$REAL_GIT" config --type=bool --get maintenance.auto 2>/dev/null)
if [ -z "\$en" ]; then
  ga=\$("$REAL_GIT" config --type=int --get gc.auto 2>/dev/null)
  if [ -n "\$ga" ] && [ "\$ga" -le 0 ]; then en=false; else en=true; fi
fi
[ "\$en" = false ] && exit \$rc
pack="\$("$REAL_GIT" rev-parse --absolute-git-dir 2>/dev/null)/objects/pack"
[ -d "\$pack" ] || exit \$rc
( end=\$((SECONDS + \${WRITE_S:-4})); i=0
  while [ \$SECONDS -lt \$end ]; do
    i=\$((i + 1)); : > "\$pack/.tmp-\$\$-pack-\$i" 2>/dev/null
  done ) </dev/null >/dev/null 2>&1 &
disown
exit \$rc
EOF
chmod +x "$W/bin/git"
P="$PATH"
[ "$ARM" = shim ] && P="$W/bin:$PATH"
race=0 fail=0 last=
for i in $(seq 1 "$RUNS"); do
  out="$(cd "$ROOT" && PATH="$P" python3 tools/release/stamp.py --self-test 2>&1)"; rc=$?
  case "$out" in *"Directory not empty"*) race=$((race + 1)); last="$(grep -m1 "Directory not empty" <<<"$out")" ;; esac
  [ "$rc" -ne 0 ] && fail=$((fail + 1))
done
sleep "${WRITE_S:-4}"
[ -n "$last" ] && echo "last: ${last#"${last%%[![:space:]]*}"}"
echo "arm=$ARM git=$("$REAL_GIT" --version | cut -d' ' -f3) runs=$RUNS directory_not_empty=$race nonzero_exit=$fail"
