"""Planted positive control: B reads a stub-store save A made; A and B in two parts."""
import sys
sys.path.insert(0, "tests")
from harness import Results  # noqa: E402
from homeassistant.helpers import storage  # noqa: E402
from heatpump_optimizer import away as _away  # noqa: E402

R = Results("planted")

R.section("planted producer")
storage._DISK["planted-key"] = '{"v": 1}'
R.check("the producer saved", "planted-key" in storage._DISK)

R.section("planted consumer")
R.check("the consumer reads the producer's save", storage._DISK.get("planted-key") == '{"v": 1}')

R.section("planted seeder")
import random  # noqa: E402
random.seed(7)
_want = random.Random(7).random()

R.section("planted drawer")
R.check("the drawer sees the seeder's stream", random.random() == _want)

R.section("planted patcher")
from heatpump_optimizer import away as _away  # noqa: E402
_away.PLANTED = 1

R.section("planted patch reader")
R.check("the reader sees the patch", getattr(_away, "PLANTED", None) == 1)

sys.exit(R.close("PLANTED CHECKS"))
