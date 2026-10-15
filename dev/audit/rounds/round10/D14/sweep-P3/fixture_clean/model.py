"""Clean fixture: every reader applies the ratio and the scale; one coercion owner."""


class Params:
    @property
    def lower_floor_heat_loss_learned(self) -> float:
        return self.lower_floor_heat_loss * self.lower_floor_loss_ratio


def demand(p, dt):
    u = p.upper_floor_heat_loss + p.lower_floor_heat_loss * p.lower_floor_loss_ratio
    return u * p.house_heat_loss_scale * dt


def finite_float(v) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
