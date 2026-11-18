# reviewer's driver: run only check_ha_free_imports from tests/doc_claims.py
import runpy, sys
g = runpy.run_path("tests/doc_claims.py", run_name="doc_claims_review")
g["check_ha_free_imports"]()
sys.exit(g["R"].close("checks"))
