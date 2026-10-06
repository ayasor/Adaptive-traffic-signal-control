"""Phase-pressure functional of the adaptive controller (thesis, section 6.2).

For every green phase k the controller computes

    P_k = s_k * [ sum_{i in C_k} w_i * (N_i / mu_i) * 1 / (1 - rho_i)
                + sum_{j in V_k} (beta * Nv_j + gamma * Tv_j + delta * max(0, Tv_j - T_crit)) ]

with rho_i = min(lambda_i / mu_i, RHO_MAX).

Vehicle term.  A queue of N_i vehicles that is discharged at the saturation
flow mu_i while new vehicles keep arriving at rate lambda_i shrinks at a net
rate (mu_i - lambda_i).  The time needed to clear it is therefore

    W_i = N_i / (mu_i - lambda_i) = (N_i / mu_i) * 1 / (1 - rho_i).

The original version of the thesis replaced 1 / (1 - rho) by its first-order
Taylor expansion (1 + rho).  That approximation is only valid for rho << 1,
which is exactly the opposite of the congested regime the controller must
react to, so the exact expression is used here.  rho is capped at RHO_MAX so
that the pressure stays finite when the measured arrival rate approaches or
exceeds the saturation flow.

Pedestrian term.  Nv_j is the number of pedestrians waiting at crossing j and
Tv_j the waiting time of the one that has waited longest.  The delta term only
activates after T_crit seconds and grows without bound, which guarantees that
a crossing is eventually served (no starvation).

All functions here are pure so they can be unit-tested without SUMO.
"""

from __future__ import annotations

from dataclasses import dataclass

RHO_MAX = 0.95


@dataclass(frozen=True)
class PedestrianWeights:
    beta: float = 2.0     # pressure per waiting pedestrian
    gamma: float = 0.2    # pressure per second waited by the oldest pedestrian
    delta: float = 5.0    # extra pressure per second beyond T_crit
    t_crit: float = 90.0  # critical pedestrian waiting time [s] (tune.py)


def saturation_factor(lam: float, mu: float, rho_max: float = RHO_MAX) -> float:
    """Exact M/M/1-style amplification 1 / (1 - rho), with rho capped."""
    if mu <= 0:
        raise ValueError("service rate mu must be positive")
    rho = min(max(lam, 0.0) / mu, rho_max)
    return 1.0 / (1.0 - rho)


def vehicle_pressure(n: int, lam: float, mu: float, w: float = 1.0,
                     rho_max: float = RHO_MAX) -> float:
    """Weighted time [s] needed to clear a lane queue of n vehicles."""
    if n <= 0:
        return 0.0
    return w * (n / mu) * saturation_factor(lam, mu, rho_max)


def pedestrian_pressure(n: int, t_oldest: float,
                        weights: PedestrianWeights = PedestrianWeights()) -> float:
    """Pressure exerted by the pedestrians waiting at one crossing."""
    if n <= 0:
        return 0.0
    return (weights.beta * n
            + weights.gamma * t_oldest
            + weights.delta * max(0.0, t_oldest - weights.t_crit))


def phase_pressure(lanes: list[tuple[int, float, float, float]],
                   crossings: list[tuple[int, float]],
                   weights: PedestrianWeights = PedestrianWeights(),
                   s_k: float = 1.0) -> float:
    """P_k for one phase.

    lanes:     (N_i, lambda_i, mu_i, w_i) for every lane served by the phase
    crossings: (Nv_j, Tv_j) for every crossing served by the phase
    s_k:       compatibility factor (0 = phase not allowed, 1 = allowed)
    """
    veh = sum(vehicle_pressure(n, lam, mu, w) for n, lam, mu, w in lanes)
    ped = sum(pedestrian_pressure(n, t, weights) for n, t in crossings)
    return s_k * (veh + ped)
