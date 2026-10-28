M = {
 "H1": (r'[A-Z0-9][A-Z0-9-]*[A-Z0-9])\b")', r'[A-Z0-9][A-Z0-9]*[A-Z0-9])\b")'),
 "H9": ('f.startswith(("custom_components/", "blueprints/"))', 'f.startswith(("custom_components/", "blueprints/", "tests/"))'),
 "H5": ('"--format=%H%x09%cI%x09%s"', '"--format=%H%x09%aI%x09%s"'),
 "X2b": ('(int(m[1]), nonce[:8]) in probes', '(int(m[1]), nonce[8:16]) in probes'),
 "X2c": ('(int(m[1]), nonce[:8]) in probes', '(int(m[1]), nonce[1:9]) in probes'),
 "X19": ('nonce = n[1] if n else ""', 'nonce = n[1][::-1] if n else ""'),
}
