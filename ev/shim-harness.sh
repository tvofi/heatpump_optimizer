#!/bin/bash
# $1 = tree root; rest = args for merge_train job-log or a direct gh call
T=$1; shift; W=$(mktemp -d)
mkdir -p $W/own $W/real $W/state
sed "s|gcpy=@HPO_GH_COMMENT@|gcpy=$T/tools/pr/gh_comment.py|" $T/tools/audit/seat/shims/seat-gh > $W/own/gh; chmod +x $W/own/gh
cat > $W/real/gh <<'S'
#!/bin/sh
case "$*" in *actions/jobs/*/logs*) echo "REAL-LOG-LINE args=[$*]"; exit 0;; esac
echo "REAL args=[$*]"; exit 0
S
chmod +x $W/real/gh
export PATH=$W/own:$W/real:$PATH HPO_STATE_DIR=$W/state
"$@"
