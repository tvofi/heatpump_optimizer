#!/usr/bin/env python3
"""Build the reviewer's mutants of head's tools/pr/app_approve.sh.

no_literal : drop the `,literal` pathspec token (the body's named mutant)
no_narrow  : revert the accumulation to main's whole-declared-subtree form
             (the body's named mutant; also the null control's mechanism)
vbase      : the reviewer's own SOUND VARIANT -- an added path is excluded only
             if it did not exist at the verdict head. Not a mutant of the fix;
             the perturbation that shows the DELREADD seam is closable by the
             same mechanism rather than inherent to `carry`.
"""
import sys, pathlib

src = pathlib.Path(sys.argv[1]).read_text()
out = pathlib.Path(sys.argv[2])

NARROW = '''        ba=$(git diff --no-renames --diff-filter=A --name-only "$c^" "$c")
        bt=$(git diff --no-renames --name-only "$c^" "$c")
        while IFS= read -r e; do
          [ -z "$e" ] && continue
          if printf '%s\\n' "$bt" | grep -qxF "$e"; then
            bots="$bots$e"$'\\n'
          else
            while IFS= read -r p; do
              case "$p" in "$e"/*) bots="$bots$p"$'\\n' ;; esac
            done <<<"$ba"
          fi
        done <<<"$b"
'''

MAINFORM = '''        bots="$bots$b"$'\\n'
'''

VBASE = '''        ba=$(git diff --no-renames --diff-filter=A --name-only "$c^" "$c")
        bt=$(git diff --no-renames --name-only "$c^" "$c")
        while IFS= read -r e; do
          [ -z "$e" ] && continue
          if printf '%s\\n' "$bt" | grep -qxF "$e"; then
            bots="$bots$e"$'\\n'
          else
            while IFS= read -r p; do
              case "$p" in "$e"/*) ;; *) continue ;; esac
              git cat-file -e "$v:$p" 2>/dev/null && continue
              bots="$bots$p"$'\\n'
            done <<<"$ba"
          fi
        done <<<"$b"
'''

kind = out.name.replace("mut_", "")
if kind.startswith("no_literal"):
    assert '":(exclude,literal)$p"' in src, "literal token not found"
    txt = src.replace('":(exclude,literal)$p"', '":(exclude)$p"')
elif kind.startswith("no_narrow"):
    assert NARROW in src, "narrowing block not found verbatim"
    txt = src.replace(NARROW, MAINFORM)
elif kind.startswith("vbase"):
    assert NARROW in src, "narrowing block not found verbatim"
    txt = src.replace(NARROW, VBASE)
else:
    sys.exit("unknown mutant " + kind)

assert txt != src, "mutant is byte-identical to its source"
out.write_text(txt)
print("wrote %s (%d -> %d bytes)" % (out, len(src), len(txt)))
