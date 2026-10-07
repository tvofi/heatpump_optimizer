import sys; sys.path.insert(0, "tests"); import closure
p = "dev/audit/rounds/round3/D2/planted_live.py"
print("RESULT", closure.is_inert(p), closure._is_header_corpus(p), closure.inert_closure_violations({"tests/harness_headers.py": [p]}))
