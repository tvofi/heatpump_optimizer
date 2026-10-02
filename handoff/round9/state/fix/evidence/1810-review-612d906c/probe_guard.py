import ast, sys
sys.path.insert(0, "tests")
import mutation_table as mt
from pathlib import Path
bad = 0; nonascii = 0; total = 0; kinds = {}
for p in sorted(mt.PRODUCTION.rglob("*.py")):
    src = p.read_text()
    lines = src.splitlines(keepends=False)
    for c in mt.candidates(p):
        if c["kind"] not in ("GUARD_OFF", "CLAMP_DROP"):
            continue
        total += 1
        kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
        ln = c["line"]
        if not c["old"].isascii():
            nonascii += 1
        mutated = lines[:]
        mutated[ln-1] = c["new"]
        try:
            ast.parse("\n".join(mutated))
        except SyntaxError as e:
            bad += 1
            print("SYNTAX", c["file"], ln, repr(c["old"].strip()[:80]), "->", repr(c["new"].strip()[:80]))
print(f"RESULT total={total} kinds={kinds} nonascii_lines={nonascii} syntax_errors={bad}")
