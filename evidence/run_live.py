# runs each open shape for real: does "_LOGGER.error('x')" reach the logger?
import logging, sys, types, io
buf = io.StringIO(); h = logging.StreamHandler(buf)
P = "cbuiltins\nexec\n(S\"_LOGGER.error('x')\"\ntR."
cases = {
 "typing_get_type_hints": "import typing\ndef g(x: \"_LOGGER.error('x')\"): pass\ntyping.get_type_hints(g)\n",
 "inspect_eval_str": "import inspect\ndef g(x: \"_LOGGER.error('x')\"): pass\ninspect.get_annotations(g, eval_str=True)\n",
 "pickle_str_payload": "import pickle\ndef f():\n    pickle.loads(" + repr(P) + ".encode())\nf()\n",
}
for k, s in cases.items():
    lg = logging.getLogger("probe." + k); lg.handlers[:] = [h]; lg.propagate = False
    buf.seek(0); buf.truncate()
    g = {"__name__": "probe." + k, "logging": logging, "_LOGGER": lg}
    try:
        exec(compile(s, k, "exec"), g)
    except Exception as e:
        print(k, "raised", type(e).__name__, e)
    print(f"{k:22s} logged={buf.getvalue().strip()!r}")
