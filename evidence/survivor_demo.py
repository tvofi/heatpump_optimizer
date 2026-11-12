"""Reviewer's demonstration that the three surviving reviewer mutants are not equivalent.
Run: cd <head tree> && PYTHONPATH=tests/hastub python3 survivor_demo.py"""
import os, sys
sys.path[:0] = [os.path.join(os.getcwd(), "tests"), os.path.join(os.getcwd(), "custom_components")]
import numpy as np
import heatpump_optimizer.optimizer as om
from heatpump_optimizer import duty_legs as dl
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters

def opt(clamp):
    p = ThermalParameters(); p.mixing_valve_mode = "none"; p.buffer_tank_volume = 750.0
    p.min_electrical_power, p.max_electrical_power = 1.5, 5.5; p.dhw_enabled = True
    c = OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=0.3)
    c.duty_switch_stop_probability, c.duty_switch_off_seconds = (1.0, 0.0), (501.0, 0.0)
    return HeatPumpOptimizer(ThermalModel(p), c)

# R9: a modulating clamped install, heating under p_min beside hot water, then heating alone.
o = opt(True)
start, dhw = np.array([0.0, 1.0, 2.5, 0.0]), np.array([0.0, 2.0, 0.0, 0.0])
space, tank = om._realize_joint(True, np.minimum(np.clip(start, 0, 5.5), np.maximum(0, 5.5 - dhw)), dhw, 1.5, 5.5)
lost = dl.lost_share((1.0, 0.0), (501.0, 0.0))
real = om._stop_availability(o, start, dhw, 5.5)
mutant = dl.availability(space, tank, lost, None)
print("R9 shipped space", space.tolist(), "tank", tank.tolist(), "lost", lost)
print("R9 availability at head      ", None if real is None else real.tolist())
print("R9 availability, floor None  ", None if mutant is None else mutant.tolist())
print("RESULT r9_vectors_differ=%s" % (not np.array_equal(real, mutant)))
print("RESULT r9_charged_step_space_under_floor_in_mutant=%s" % bool(np.any((mutant < 1) & (space < 1.5) & (space > 0))))

# R5: a duty-cycle install, heating at its charged bound in a two-leg step.
dhw = np.array([0.0, 2.0, 0.0]); start = np.array([0.0, 2.0, 2.0])
avail = dl.availability(start, dhw, lost, None)
bound = dl.space_headroom(5.5, dhw, avail, None)
solved = np.minimum(np.array([0.0, 5.5, 2.0]), bound)   # heating hard against its charged bound
pin_head = (dhw > 1e-6) & (solved >= dl.space_headroom(5.5, dhw, avail, None) - 1e-3)
pin_mut = (dhw > 1e-6) & (solved >= dl.space_headroom(5.5, dhw, None, None) - 1e-3)
print("R5 avail", avail.tolist(), "bound", bound.tolist(), "solved", solved.tolist())
print("R5 pinned at head", pin_head.tolist(), "pinned with the vector ignored", pin_mut.tolist())
print("RESULT r5_pinned_differs=%s" % (not np.array_equal(pin_head, pin_mut)))
