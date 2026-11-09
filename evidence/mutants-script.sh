R=$HOME/mut/run.sh
$R ge_over 'if not (over := ~held & (spread > cap)).any():' 'if not (over := ~held & (spread >= cap)).any():'
$R held_assign 'held |= over' 'held = over'
$R no_subtract 'steady * ((energy - cap * int(np.sum(held))) / total)' 'steady * (energy / total)'
$R uncapped 'if not (over := ~held & (spread > cap)).any():' 'if True:'
$R held_not_cap 'spread = np.where(held, cap, ' 'spread = np.where(held, 0.0, '
$R return_sim_fallback_zero '            held |= over
        return simulated' '            held |= over
        return np.zeros_like(simulated)'
$R seed_reclip 'seed_power,  # inside the bounds: the reference never passes the pump' 'np.clip(seed_power, 0.0, p_max),'
$R old_code '        held = np.zeros(len(steady), dtype=bool)
        while (total := float(np.sum(steady[~held]))) > 0.0:
            spread = np.where(held, cap, steady * ((energy - cap * int(np.sum(held))) / total))
            if not (over := ~held & (spread > cap)).any():
                return spread
            held |= over
        return simulated' '        total = float(np.sum(steady))
        return simulated if total <= 0.0 else steady * (energy / total)'
echo DONE
