# Box D3-g15 working notes (checkpointed; per-key classification as decided from the probes)
Probe outputs: probe-out/probe_<key>.out. Builders: probes/_box_tools/build_g15.py (A dict = the per-key step-4 answers).
Provisional class if the gate survives (candidate = probe moves on an in-range input):
- candidate: a1ebeff0870dfa76 (784 tie need==boost_top), f1549576a94b99be (784 guard off, heavy draw), 7cd9b966a3bd0008 (793 floor tie), 31c1881164f2dcdf (626 reach tie), 7640e80a994db479 (628 deadline==n, reachable 15-min window)
- equivalent-candidate (unreachable through production): 0e752f692873e876 (n<0), 3e26ea9048504c31 (n=0 with step), 77d5e6c8ea98273a (decay 0), 79ba0b9f6b3cf22d (interval 0), 56d2279a568e8891 (n=0)
- equivalent-candidate (no input separates): 1d455987c970dfde, 8e9a502f439ceeeb, f9c1b49fde6e1d52, 5224cce5f7a150cb, c124ea447555a04a, 8fb9093f7470e6aa
Probes were checked against tests/harness_headers.py inline_scan with them present (rc 0, no depth seams): _lg_common.py carries the canonical repo_root.
