"""gn_ghost_2d.py — 2D Self-Writing XOR Ring Array & Jitter-Resistant Coincidence.

Run: python gn_ghost_2d.py
"""
from __future__ import annotations
import numpy as np

# Window parameters from GeometricNeuronV27 / KultaaVaiKatinkultaaOpus
WIRE = 2.0
BAND_LOW = -14.7
BAND_HIGH = -6.1


def window_fire(drive: np.ndarray) -> np.ndarray:
    """Band-pass window activation: fires 1 iff -14.7 < drive < -6.1."""
    return ((drive < BAND_HIGH) & (drive > BAND_LOW)).astype(np.int32)


def test_2d_moving_movie(H: int = 32, W: int = 32, period: int = 16, laps: int = 4):
    """Test 1,024 parallel 1-wire XOR rings on a moving 2D periodic scene."""
    ring = np.zeros((period, H, W), dtype=np.int32)
    yy, xx = np.mgrid[0:H, 0:W]

    errors_per_lap = []
    for lap in range(laps):
        lap_errors = 0
        for s in range(period):
            # Moving 2D target orbiting the canvas with period `period`
            angle = 2 * np.pi * s / period
            cx = W / 2 + 9 * np.cos(angle)
            cy = H / 2 + 9 * np.sin(angle)
            world = (((xx - cx) ** 2 + (yy - cy) ** 2) <= 20).astype(np.int32)

            pred = ring[s]

            # 1. Error unit (w = -4.5 on both World and Ring)
            err_drive = (-4.5 * WIRE * world) + (-4.5 * WIRE * pred)
            err = window_fire(err_drive)

            # 2. 1-Wire Self-Writing & Self-Erasing Ring update:
            # Ring self-weight = -6.0, Error feedback weight = -4.5
            # (1, 0) -> -12.0 (keeps 1)
            # (0, 1) ->  -9.0 (writes 1)
            # (1, 1) -> -21.0 (overshoots band -> erases to 0!)
            ring_drive = (-6.0 * WIRE * pred) + (-4.5 * WIRE * err)
            ring[s] = window_fire(ring_drive)

            lap_errors += int(err.sum())
        errors_per_lap.append(lap_errors)

    return errors_per_lap


def test_jitter_cure(ticks: int = 640, period: int = 32, max_jitter: int = 1, seed: int = 42):
    """Compare raw 2-tick XOR vs. Plateau-Sustained XOR under +/-1 tick timing jitter."""
    rng = np.random.default_rng(seed)

    # Prediction fires at exact period multiples for 2 ticks
    pred_trace = np.zeros(ticks, dtype=np.int32)
    world_trace = np.zeros(ticks, dtype=np.int32)

    for cycle_start in range(16, ticks - 8, period):
        pred_trace[cycle_start : cycle_start + 2] = 1
        shift = int(rng.integers(-max_jitter, max_jitter + 1))
        w_start = cycle_start + shift
        world_trace[w_start : w_start + 2] = 1

    # Baseline GN-XOR (raw 2-tick pulses)
    raw_drive = -4.5 * WIRE * (world_trace + pred_trace)
    raw_err = window_fire(raw_drive)

    # Sustained Dendritic Plateau ( widen pulse envelope to 4 ticks + require 3 consecutive
    # mismatch ticks to trigger an error burst, filtering out 1-tick phase-edge slivers )
    def widen(x: np.ndarray, width: int = 2) -> np.ndarray:
        out = x.copy()
        for d in range(1, width + 1):
            out[d:] |= x[:-d]
        return out

    w_wide = widen(world_trace, width=2)
    p_wide = widen(pred_trace, width=2)
    inst_err = window_fire(-4.5 * WIRE * (w_wide + p_wide))

    # 3-tick temporal integrator (only sustained mismatch > 2 ticks fires)
    sustained_err = (inst_err & np.roll(inst_err, 1) & np.roll(inst_err, 2)).astype(np.int32)
    sustained_err[:2] = 0

    return {
        "raw_false_error_ticks": int(raw_err.sum()),
        "plateau_false_error_ticks": int(sustained_err.sum()),
    }


if __name__ == "__main__":
    movie_errors = test_2d_moving_movie()
    print("2D Moving Movie (1,024 rings) Error Spikes per Lap:", movie_errors)
    assert movie_errors[0] > 0 and movie_errors[1] == 0 and movie_errors[3] == 0

    jitter_stats = test_jitter_cure(max_jitter=1)
    print("Jitter (+/-1 tick) False Error Ticks:", jitter_stats)
    assert jitter_stats["raw_false_error_ticks"] > 0
    assert jitter_stats["plateau_false_error_ticks"] == 0
    print("ALL CHECKS PASSED.")