"""Equivalence of the base and head replay-job regexes over a generated corpus."""
import itertools, re, sys
BASE = r"\n  replay:\n(?:    .*\n|[ \t]*\n)*?    timeout-minutes: (\d+)\n"
HEAD = (r"\n  replay:\n(?:    .*\n| {0,3}\n| {0,3}\t[ \t]*\n)*?"
        r"    timeout-minutes: (\d+)\n")
NOTAB = r"\n  replay:\n(?:    .*\n| {0,3}\n)*?    timeout-minutes: (\d+)\n"
LINES = ["\n", " \n", "   \n", "    \n", "     \n", "\t\n", "  \t \n", "   \t\n",
         "\t    \n", "    \t\n", "    needs: [x]\n", "      run: y\n", "   x\n",
         "  next:\n", "    timeout-minutes: 45\n", "      timeout-minutes: 7\n",
         "    timeout-minutes: x\n", "  \n  replay:\n", "\t timeout-minutes: 3\n"]
HEADS = ["\n  replay:\n", "jobs:\n  replay:\n", "\n  replay:\n\n  replay:\n", "x"]
TAILS = ["", "  next:\n", "    timeout-minutes: 9\n", "\n"]
def key(pat, s):
    m = re.search(pat, s)
    return (m.span(), m.group(1)) if m else None
n = dh = dn = matched = 0
for k in range(4):
    for body in itertools.product(LINES, repeat=k):
        for h in HEADS:
            for t in TAILS:
                s = h + "".join(body) + t; n += 1
                b = key(BASE, s); matched += b is not None
                dh += b != key(HEAD, s); dn += b != key(NOTAB, s)
print(f"corpus {n} strings, base matched {matched}; head disagrees on {dh}; null control disagrees on {dn}")
sys.exit(0 if dh == 0 and dn > 0 else 1)
