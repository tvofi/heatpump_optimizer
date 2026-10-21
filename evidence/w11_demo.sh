# W11 demo: the production row_only_verdict at the head, real git, a row file of TWO lines
# invoke: bash -c ". ev/w11_demo.sh" "$PWD/tools/pr/app_push.sh" <scratch dir>  ($0 must be app_push.sh: the verdict sources delivery_row.sh beside it)
# (the open #7 row, then a second line). At the head it refuses; under W11 it skips. Run from the head worktree.
set -u; Q=$1; SELF=tools/pr/app_push.sh
eval "$(sed -n '/^row_only_verdict() {/,/^}/p' "$SELF")"
git init -q -b main "$Q/wt"; cd "$Q/wt"; git config user.email x@x; git config user.name x
mkdir -p tests; cp "$OLDPWD"/tests/delivery_status.py "$OLDPWD"/tests/layout.py "$OLDPWD"/tests/layout.json tests/
echo x > x; git add -A; git commit -qm base; git checkout -qb fix; echo f > f; git add f; git commit -qm fix; live=$(git rev-parse HEAD)
mkdir -p dev/programme/delivery; printf -- '- [#7](https://github.com/o/r/pull/7) — **open**, t (none)\nsecond line\n' > dev/programme/delivery/7.md
git add -A; git commit -qm row
printf '## Head\n\n`live`\n\n## Figures\n\nf\n' > "$Q/live.md"; cp "$Q/live.md" "$Q/b.md"
python3 "$OLDPWD/tools/pr/head_note.py" "$Q/b.md" "\`$(git rev-parse HEAD)\` adds the row." >/dev/null
L=$(python3 -c 'import json,sys; print(json.dumps([{"number":7,"title":"t","head":{"sha":sys.argv[1]},"body":open(sys.argv[2]).read()}]))' "$live" "$Q/live.md")
cd "$OLDPWD"; row_only_verdict "$Q/wt" "$L" "$Q/b.md"; echo "rc=$?"
