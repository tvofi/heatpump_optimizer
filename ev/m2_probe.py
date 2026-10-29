import sys; sys.path.insert(0,"tools/audit/seat")
import review_packet as r
H="a"*40; B="b"*40
body=f"## Head\n{H}\n\n## Red checks\nnone\n"
for reds,t,e in [(["governance / delivery-status"],{"dev/programme/delivery/9999.md"},set()),
                 (["governance / delivery-status"],{"dev/programme/delivery/9999.md"},{"dev/programme/delivery/9999.md"})]:
    print(reds,t,e,"->",r.unanswered_reds(body,H,B,reds,t,e))
