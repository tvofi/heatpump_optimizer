import sys
MUT = {
 "M1": ('    echo "$p at $h is not the reviewed head $v merged onto $mh, main\'s driver output on them, nor what a carried bot commit wrote"; return 1\n', '    :\n'),
 "M2": ('    while IFS= read -r e; do [ -z "$e" ] || botc="$botc$c $e"$\'\\n\'; done <<<"$b"\n', '    :\n'),
 "M3": ('    driver_wrote "$main" "$h" "$v" "$mh" "$p" "$drv" && continue\n', ''),
 "M4": ('    ledgermerge) src=tools/merge/ledger_merge.py flag=--merge ;;\n', ''),
 "M5": ('      [ "$got" = "$want" ] && continue\n', ''),
 "M6": ('    [ -n "$t" ] && [ "$(git rev-parse -q --verify "$t:$p")" = "$(git rev-parse -q --verify "$h:$p")" ] && continue\n', ''),
 "M7": ('    [ -n "$lb" ] && [ "$(git rev-parse -q --verify "$lb:$p")" = "$(git rev-parse -q --verify "$h:$p")" ] && continue\n', '    [ -n "$lb" ] && continue\n'),
 "M8": ('      [ "$e" = "$p" ] || continue\n', '      :\n'),
}
m, path = sys.argv[1], sys.argv[2]
s = open(path).read()
o, n = MUT[m]
c = s.count(o)
if c != 1:
    sys.exit(f"{m}: {c} occurrences")
open(path, "w").write(s.replace(o, n))
print(f"{m}: applied")
