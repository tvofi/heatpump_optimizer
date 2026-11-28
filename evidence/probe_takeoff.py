import sys
sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
exec(open(sys.argv[1]).read().split("for sw in")[0])
for sw in ("switch.hp", None):
    for out in (-3.0, 5.0):
        held = pa.ArbiterState()
        print(f"take_off switch={sw!s:10} out={out:5} ->{fh.take_off(held, inp(out, sw), T0)} frost_holding={held.frost_holding}")
