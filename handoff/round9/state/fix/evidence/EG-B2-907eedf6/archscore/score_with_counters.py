import json, sys
sys.path.insert(0, sys.argv[1]); O = sys.argv[2]
import arch_score as A
SWAP = {"untyped_payload_keys": "untyped_payload_keys_v2", "dup_pairs_v1": "dup_pairs_v2",
        "private_reach": "private_reach_v2", "a1_params_over_10": "params_over_10_v2"}
GATE = ("reflective_writes", "computed_attr_access", "family_orphan_overrides", "unread_private_globals")
w1 = A.weights()
A.SCORE_METRICS = {SWAP.get(k, k): v for k, v in A.SCORE_METRICS.items()}
for g in GATE: A.SCORE_METRICS[g] = (None, "gate only")
W = {SWAP.get(k, k): v for k, v in w1.items()}; W.update({g: 0.0 for g in GATE})
def vec(n):
    v = json.load(open(f"{O}/{n}.json")); v.update(json.load(open(f"{O}/{n}.counters.json"))); return v
b, h = vec("base"), vec("head")
print(json.dumps(A.delta(b, h, W), indent=1, sort_keys=True))
print("\nmetric base head delta (score metrics + counters)")
for k in sorted(set(A.SCORE_METRICS)|set(json.load(open(f"{O}/base.counters.json")))):
    print(f"{k:30} {b.get(k)} {h.get(k)} {None if b.get(k) is None or h.get(k) is None else h[k]-b[k]}")
