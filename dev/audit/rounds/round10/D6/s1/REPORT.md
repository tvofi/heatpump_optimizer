# D6-s1 report (README.md, DISCLAIMER.md; M1-M3), baseline 17f1c55fad1b

Method: I pulled every numeric, default, count and version claim out of README.md and DISCLAIMER.md.
Then I took the 20 claims that production code can check and ran them through `claims.py`.
The harness collects entities through the real `async_setup_entry` for all six platforms.
It registers services through `services.async_register_services` and counts schema keys.
It reads defaults from `const.py` and versions from VERSION, the manifest and hacs.json.

Result: claims_checked=20, claims_false=0, claims_stale=0.
Under the in-memory `--perturb` arm, which drops one sensor, claims_false goes from 0 to 2 (C01 and C02).
The claims table is the harness output.

Findings: none.

Unverifiable or not checked:
- 23 options pages, up to 20 manual-plan hours, 8 weekly snapshots and ±12 %. There is no direct const for these; reaching them needs flow or engine harnesses.
- Link HEAD requests: no network was used.
- DISCLAIMER.md: it is legal prose with no quantified claims that code can check.

Exposure: README.md, DISCLAIMER.md.
