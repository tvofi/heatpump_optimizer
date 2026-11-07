import os, pickle, sys, threading
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, sys.argv[1] + "/tests/hastub")
import custom_components.heatpump_optimizer.coordinator as c
c._REPLY_FRAME_MAX_BYTES = 1_000_000          # shortened cap, as the suite does
blob = pickle.dumps(("ok", [b"x" * 600_000, b"y" * 600_000]), protocol=5)  # 2 reads of 600 kB, 1.2 MB total
r, w = os.pipe()
threading.Thread(target=lambda: (os.write(w, blob) if False else [os.write(w, blob[i:i+65536]) for i in range(0, len(blob), 65536)], os.close(w)), daemon=True).start()
try:
    v = pickle.load(c._frame_reader(r, 10))
    print(f"RESULT {sys.argv[2]}: frame of {len(blob)} bytes ACCEPTED over cap {c._REPLY_FRAME_MAX_BYTES}")
except ValueError as e:
    print(f"RESULT {sys.argv[2]}: refused: {e}")
