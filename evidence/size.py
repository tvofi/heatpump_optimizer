import sys, json
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import cloud_dispatch as cd
h = "883e8452fafbef8ecc6c686924e27c054f85bf54"
for role, kw, ref in (("fixer", dict(topic="r10-flow-design-stages-p2"), "dispatch/fixer-r10-flow-design-stages-p2"),
                      ("reviewer", dict(pr="3012", nonce="2e5f24db902519aef2721cd550fdec97"), "dispatch/reviewer-rev-3012"),
                      ("design-reviewer", dict(topic="R10-FLOW-DESIGN-STAGES", design=h), "dispatch/design-reviewer-R10-FLOW-DESIGN-STAGES")):
    try:
        p = cd.render(role, h, env_id="env_01MWCXY5ByfCeQwVGRLhMrGH", model="claude-sonnet-5-5", repo="tvofi/heatpump_optimizer",
                      publish_ref=ref, pin=h, **kw)
        print("RESULT", role, "payload_bytes", len(json.dumps(p)))
    except cd.Refusal as e:
        print("RESULT", role, "refused", e)
