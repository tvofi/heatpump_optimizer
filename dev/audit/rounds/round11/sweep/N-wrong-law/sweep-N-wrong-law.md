# Class sweep: N-wrong-law (round 11, phase D)

Class mechanism: a physical law is coded with the wrong operator or sign, then
clamped, so the effect it models never acts on any input.
Judged finding: D2-s2-02 (verified, high). On the planted copy,
`derate_from_duty` returns `min(DERATE_MAX=1.0, max(DERATE_MIN, 1.0 + duty*1.5))`,
which is pinned at 1.0. The real tree reads `1.0 - duty * ...` at the baseline
`92d38ecb` and at the register head, so the judged site is a planted seam.
Ledger status: the class is new this round.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep/wrong_law.py` lists every
`min`/`max`/`clip`/`clamp` call in the package (nested pairs counted once) that
has an argument of the form `c ± term`, where `c` is a float literal or a named
constant (integer offsets, which are index arithmetic, are excluded). It marks a
seam **PINNED** when the clamp bound equals `c` on the side the operator pushes
towards, which is the D2-s2-02 signature: for a nonnegative term, the result can
never leave the bound.

At the register head it lists 28 seams, none of them pinned. Controls (`wrong_law_controls.sh`):

| control | result |
|---|---|
| positive: the D2-s2-02 sign planted in a copy of `defrost.py` | listed PINNED at `defrost.py:205` (pinned 0 -> 1) |
| null: a clean fixture of correctly signed clamped laws | pinned 0 |
| perturbation: one sign flipped at `dhw_planner.py:105` (`_tank_decay`) | pinned 0 -> 1 |

## Dispositions

- **Judged site (1, beyond_finding false):** `defrost.py:205 derate_from_duty`.
  Its probe is the finding's `m2_cop_laws.py` on the planted copy.
- **Not applicable, sign agrees with the documented law (19).** The JSON gives
  each law's direction. They are trust vs MAE, the boost settle tail, five
  tank-minus-ambient excess terms, tank decay and retention, external-heat decay,
  the flow-bias headroom, price-guess weights, solar anticipation weights, the
  draw scale, the wood-tank headroom, `_cop_law` and `_batch_cop` (COP rises
  with outdoor temperature; the batch path is pinned bitwise to the scalar
  one), and the hold-hours bound.
- **Not applicable, not a law (8):** count, time and degrees-of-freedom arithmetic.

## Count and barrier

There are 0 instances beyond the finding, and the class is not barriered.
Proposed barrier: `wrong_law.py` as a `tests/` check that refuses any PINNED
seam (under 1 s of gate time), plus `m2_cop_laws.py`'s duty-law identity as a
unit pin on `derate_from_duty`.

Limit: the enumerator sees the clamped-affine shape only. A wrong sign with no
clamp moves its output and is left to the D2 law harnesses.
