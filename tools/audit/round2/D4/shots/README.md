# D4 screenshots are not committed

The 182 PNGs the D4 finder took (3 widths x light/dark x sv/en x every state in
`tests/card_drift.mjs`) live here after a run and are deliberately untracked:
14 MB of regenerable output does not belong in the repository.

Regenerate them with the finder's own harness:

    PLAYWRIGHT_BROWSERS_PATH=~/.cache/pw-browsers \
      node tools/audit/round2/D4/shoot.mjs --out tools/audit/round2/D4/shots

Every D4 finding names the exact file it rests on; the harness writes the same
names each run.
