set -Eeo pipefail; trap 'echo STOPPED rc=$? >&2' ERR
WT=$1
OP_REG=$(./prod.sh | awk -v w="worktree $WT" '$0==w{f=1;next} f&&/^branch /{sub("refs/heads/","",$2);print $2;exit} f&&$0==""{exit}')
echo "survived OP_REG=[$OP_REG]"
