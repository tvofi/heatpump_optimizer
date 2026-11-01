import sys
P = {
 "P-D2-no-cut": [("    comments = [ln for ln in comments if _marker_key(ln) is None or ln in keep]\n", "")],
 "P-D2-no-cut-no-defect": [("    comments = [ln for ln in comments if _marker_key(ln) is None or ln in keep]\n", ""),
                           ("    if got_md != want_md:\n", "    if False:\n")],
 "P-D3-ignore-marker-refusal": [("    if decided is None or marker_refused:\n        return None", "    if decided is None:\n        return None")],
 "P-D3-ignore-refusal-and-defect": [("    if decided is None or marker_refused:\n        return None", "    if decided is None:\n        return None"),
                           ("    if got_md != want_md:\n", "    if False:\n")],
 "P-stamp-not-marker": [("    if note.startswith(CLAIM_VERSION_MARKER):\n        return CLAIM_VERSION_MARKER\n", "")],
}
s = open(sys.argv[2]).read()
for a, b in P[sys.argv[1]]:
    assert s.count(a) == 1, a; s = s.replace(a, b)
open(sys.argv[2], "w").write(s)
