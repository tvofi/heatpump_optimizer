import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1]); shim = root/"tools/audit/seat/shims/seat-gh"
orig = shim.read_text()
P = [
 ("tr allows =", "tr -c 'A-Za-z0-9_./: -' '?' | cut", "tr -c 'A-Za-z0-9_./: =-' '?' | cut"),
 ("80 cut removed", " | cut -c1-80)", ")"),
 ("--eval arm removed", "      --eval|--eval=*|--print|--print=*|--command|--command=*) pcmd=\"$pcmd ${a%%=*}\"; end=1 ;;\n", ""),
 ("long code option logged whole", "pcmd=\"$pcmd ${a%%=*}\"", "pcmd=\"$pcmd $a\""),
 ("code letter logs whole word", "c|e|s) pcmd=\"$pcmd ${a:0:$((j + 1))}\"", "c|e|s) pcmd=\"$pcmd $a\""),
 ("s dropped from code letters", "c|e|s) pcmd", "c|e) pcmd"),
 ("unknown letter passed over", "            *) end=1; break ;;", "            *) ;;"),
 ("unknown long passed over", "      --*) end=1 ;;", "      --*) ;;"),
 ("value letter no-value", "            $vals) [ \"$((j + 1))\" -eq \"${#a}\" ] && i=$((i + 1)); break ;;\n", ""),
 ("value next word not skipped", "&& i=$((i + 1)); break ;;", "; break ;;"),
 ("-m module dropped", "pcmd=\"$pcmd -m ${pw[$((i + 1))]}\"", "pcmd=\"$pcmd -m\""),
 ("script word not ending", "      *) pcmd=\"$pcmd $a\"; end=1 ;;", "      *) pcmd=\"$pcmd $a\" ;;"),
 ("python flags set empty", "flags='[bBdEhiIOqPRSuvVx]'", "flags='[x]'"),
 ("shell vals empty", "vals='[oO]'", "vals='[Q]'"),
 ("chmod 600 on log removed", "  chmod 600 \"$log\"\n", ""),
 ("umask 077 removed", "  umask 077\n", ""),
]
for name, a, b in P:
    assert orig.count(a) >= 1, name
    shim.write_text(orig.replace(a, b, 1))
    r = subprocess.run(["python3","-I","tools/audit/seat/gh_calls.py","--self-test"], cwd=root, capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or ["?"])[-1]
    fails = [l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
    print(f"RESULT plant {'KILLED' if r.returncode or 'failed' in last and not last.endswith(' 0 failed') else 'SURVIVED'} | {name} | {last} | first: {fails[:1]}")
shim.write_text(orig)
