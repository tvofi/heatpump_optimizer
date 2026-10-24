PROBE, throwaway draft, closed unmerged. P2b live arm, not for merge. Part of #2495

Arm A of R10-CI-LAYOUT-P2b: U0 events on a draft PR against the umbrella skeleton probe ref ci-probe/u0c (65f112ec51dfa1f3d1617dda2bac74adab394eda).

## Head

`d7505428267e2a1c89f15329046fb86630eb44df` merges the authored code head `c89de8fd4d85c69424c9e59fd299baf7dd1f4382` and then merges origin/main `8a6e5826b` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`83de34568bab45dccdb3b0b9bcdb8552b6662a94` merges the authored code head `305196daf8665ada01eefc3e54c3e7ffbb6ab66f` and then merges origin/main `57b7b4994` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`aa77d6cd15cd5dce225d05fe8fda27953b3c3279` merges the authored code head `305196daf8665ada01eefc3e54c3e7ffbb6ab66f` and then merges origin/main `57b7b4994` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`06b077f884414cbd08b4cba7a913423dade8b110` merges the authored code head `251a9461d91cf0dce9f4284fc4ff7ba5c52aeede` and then merges origin/main `a243a79f4` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head, and then adds one commit containing only this PR's own row, `dev/programme/delivery/2649.md`.

`4176367cd8f2c81e6803702bdf89532383d5868d` merges the authored code head `251a9461d91cf0dce9f4284fc4ff7ba5c52aeede` and then merges origin/main `c26499e01` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head, and then adds one commit containing only this PR's own row, `dev/programme/delivery/2649.md`.

`b2647af984ce1483fec0e77c66f7144d10e42e19` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2649.md`. The authored code head is `f61793f80dc40c1db1bae01405b451a9d8cbfc3b`.

`dd3d6306c233f8d15fb3a2e031eab8329a056060` merges origin/main `c26499e01` into the authored code head `f61793f80dc40c1db1bae01405b451a9d8cbfc3b` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

n/a: probe PR, nothing is measured at this head.

## Mutation proof

n/a: probe PR, no fix is proposed.

## Null control

n/a: probe PR, the arm itself is the control (see the evidence file probe-runner-A.txt).

## Figures

`none`

## Red checks

`gate` and `pr-contract` are red at the first head dd3d6306c: that head carries no delivery row, so `pr-contract` fails and `gate` follows. This is a known finding owned by U9b (main ruled to leave it as is); no cheaper detector is proposed because this is a throwaway probe that is closed unmerged. `instrument-self-tests` is red by construction: the probe tip cuts `tools/ci/gate.py` `REQUIRED` down to `probe / probe`, so gate.py's own self-test (`gate self-test: 27 checks, 7 failed`) cannot match the 17-context fixture; there is no cheaper detector, since this branch is closed unmerged. This push adds the row. At head 06b077f884414cbd also red: `closures`, `closures-autofix` and `fast (3.14)`; they are red on the probe tip, which is a hand-cut ci.yml/REQUIRED and an INERT-classified probe.yml, were not investigated further, and there is no cheaper detector proposed because this branch is closed unmerged.

## Forward-carry

`none`

## Friction

`none`






