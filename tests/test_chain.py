"""Tests for mean-square internal distances and the D24 chain-equilibration check."""

from itertools import pairwise
from pathlib import Path

import numpy as np
import pytest

from sepsim.analysis.chain import (
    backbone_chains,
    chain_com_rg2,
    characteristic_ratio,
    com_msd_over_rg2,
    decorrelation_time,
    drift_check,
    end_to_end_autocorrelation,
    internal_distances,
    msid_check,
)
from sepsim.build.datafile import read_data_file

SYSTEMS = Path(__file__).resolve().parents[1] / "systems"


def _freely_rotating(n_chains, n_sites, cos_a, l=1.5, seed=0):
    """Chains with fixed bond-direction change alpha (cos_a) and uniform random torsions.

    cos_a = 0 is not freely jointed; use ``_random_walk`` for that.
    Returns positions (n_chains * n_sites, 3) and the chain index arrays.
    """
    rng = np.random.default_rng(seed)
    sin_a = np.sqrt(1.0 - cos_a**2)
    b = np.zeros((n_chains, n_sites - 1, 3))
    u = rng.normal(size=(n_chains, 3))
    b[:, 0] = u / np.linalg.norm(u, axis=1, keepdims=True)
    for k in range(1, n_sites - 1):
        p = b[:, k - 1]
        e1 = np.cross(p, rng.normal(size=(n_chains, 3)))
        e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
        e2 = np.cross(p, e1)
        phi = rng.uniform(0, 2 * np.pi, size=(n_chains, 1))
        b[:, k] = cos_a * p + sin_a * (np.cos(phi) * e1 + np.sin(phi) * e2)
    r = np.concatenate([np.zeros((n_chains, 1, 3)), np.cumsum(l * b, axis=1)], axis=1)
    return r.reshape(-1, 3), list(np.arange(n_chains * n_sites).reshape(n_chains, n_sites))


def _random_walk(n_chains, n_sites, l=1.5, seed=0):
    u = np.random.default_rng(seed).normal(size=(n_chains, n_sites - 1, 3))
    u *= l / np.linalg.norm(u, axis=2, keepdims=True)
    r = np.concatenate([np.zeros((n_chains, 1, 3)), np.cumsum(u, axis=1)], axis=1)
    return r.reshape(-1, 3), list(np.arange(n_chains * n_sites).reshape(n_chains, n_sites))


def test_random_walk_r2_over_n_is_l2():
    pos, chains = _random_walk(2000, 30, l=1.5)
    n, r2 = internal_distances(pos, chains)
    assert n.tolist() == list(range(1, 30))
    np.testing.assert_allclose(r2 / n, 1.5**2, rtol=0.03)
    _, c_n = characteristic_ratio(pos, chains)
    np.testing.assert_allclose(c_n, 1.0, rtol=0.03)


def test_straight_rod_gives_n_l2():
    pos = np.zeros((20, 3))
    pos[:, 0] = 1.54 * np.arange(20)
    chains = [np.arange(10), np.arange(10, 20)[::-1]]  # direction does not matter
    n, r2 = internal_distances(np.stack([pos, pos]), chains)  # two identical frames
    np.testing.assert_allclose(r2 / n, n * 1.54**2)
    nc, c_n = characteristic_ratio(pos, chains, carbons_per_site=3)
    np.testing.assert_array_equal(nc, 3 * n)
    np.testing.assert_allclose(c_n, n)


@pytest.mark.parametrize("theta_deg", [109.47, 140.0])
def test_freely_rotating_chain_matches_analytic(theta_deg):
    c = np.cos(np.pi - np.radians(theta_deg))
    pos, chains = _freely_rotating(1500, 40, c)
    nc, c_n = characteristic_ratio(pos, chains)
    exact = (1 + c) / (1 - c) - 2 * c * (1 - c**nc) / (nc * (1 - c) ** 2)
    np.testing.assert_allclose(c_n, exact, rtol=0.04)


def test_unequal_chain_lengths_weight_pairs_equally():
    pos = np.zeros((7, 3))
    pos[:, 0] = np.arange(7.0)
    _, r2 = internal_distances(pos, [np.arange(3), np.arange(3, 7)])
    # n=1: 2 + 3 pairs, all 1; n=3 only from the 4-site chain.
    np.testing.assert_allclose(r2, [1.0, 4.0, 9.0])


@pytest.mark.parametrize(
    "name, n_sites",
    [
        ("pe_ua_amorph_n40_c240_s1", 240),
        ("pe_aa_amorph_n40_c240_s1", 240),
        ("ipp_ua_amorph_n40_c240_s1", 161),  # 2n/3 + 1 backbone carbons
        ("pe_cg_amorph_n40_c240_s1", 80),
    ],
)
def test_backbone_chains_on_committed_systems(name, n_sites):
    data = SYSTEMS / name / "data.lmp"
    chains = backbone_chains(data, SYSTEMS / name / "manifest.yaml")
    assert len(chains) == 40 and all(len(c) == n_sites for c in chains)
    df = read_data_file(data)
    atoms = df.sorted_atoms()
    row = {int(a): k for k, a in enumerate(atoms[:, 0])}
    bonds = {frozenset((row[a], row[b])) for a, b in df.topology("Bonds")[:, 2:4]}
    for c in chains:
        assert len(np.unique(atoms[c, 1])) == 1  # one molecule
        assert all(frozenset((int(a), int(b))) in bonds for a, b in pairwise(c))
    if name.startswith("ipp"):  # no methine H or pendant methyl in the backbone
        names = {v: k for k, v in {"CH3": 1, "CH2": 2, "CH": 3, "H": 4}.items()}
        types = [names[int(t)] for t in atoms[chains[0], 2]]
        assert types[0] == types[-1] == "CH3" and "CH3" not in types[1:-1] and "H" not in types


def _frames(cos_values, n_chains=200, n_sites=40):
    pos = [_freely_rotating(n_chains, n_sites, c, seed=k)[0] for k, c in enumerate(cos_values)]
    return np.stack(pos), list(np.arange(n_chains * n_sites).reshape(n_chains, n_sites))


def test_drift_check_series():
    rng = np.random.default_rng(1)
    noise = rng.normal(size=400)
    assert drift_check(5.0 + 0.05 * noise)[4] is False
    *_, drift = drift_check(5.0 + 0.05 * noise + np.linspace(0.0, 0.5, 400))
    assert drift is True


def test_msid_check_stationary_passes_and_drift_fails():
    c = np.cos(np.pi - np.radians(109.47))
    c_inf = (1 + c) / (1 - c)  # 2.0; plateau over n >= 20 sits a few % below
    pos, chains = _frames([c] * 20)
    res = msid_check(pos, chains, reference=(c_inf, c_inf), n_min=20)
    assert res.within_reference and res.drift is False and res.passed
    assert res.n_carbons[0] == 1 and len(res.c_n) == 39

    pos, chains = _frames(np.linspace(c - 0.15, c + 0.15, 20))
    res = msid_check(pos, chains, reference=(c_inf, c_inf), n_min=20)
    assert res.drift is True and not res.passed and res.delta > 0

    single = msid_check(pos[0], chains, reference=(1.0, 100.0), n_min=20)
    assert single.within_reference and single.drift is None and not single.passed
    with pytest.raises(ValueError):
        msid_check(pos[0], chains, reference=(1.0, 2.0), n_min=1000)


def _ou_vectors(n_frames, n_chains, tau, dt=1.0, seed=0):
    """Ornstein-Uhlenbeck vectors: <R(t).R(0)>/<R^2> = exp(-t/tau)."""
    rng = np.random.default_rng(seed)
    a = np.exp(-dt / tau)
    r = np.empty((n_frames, n_chains, 3))
    r[0] = rng.normal(size=(n_chains, 3))
    for k in range(1, n_frames):
        r[k] = a * r[k - 1] + np.sqrt(1 - a**2) * rng.normal(size=(n_chains, 3))
    return r


def test_end_to_end_autocorrelation_exponential():
    r = _ou_vectors(2000, 200, tau=20.0)
    lags, c = end_to_end_autocorrelation(r, dt=0.5, max_lag=200)
    assert lags[1] == 0.5 and c[0] == 1.0
    np.testing.assert_allclose(c[:60], np.exp(-np.arange(60) / 20.0), atol=0.03)
    assert decorrelation_time(lags, c) == pytest.approx(10.0, rel=0.1)  # tau * dt
    frozen = np.repeat(r[:1], 50, axis=0)
    lags, c = end_to_end_autocorrelation(frozen, dt=1.0)
    np.testing.assert_allclose(c, 1.0)
    assert decorrelation_time(lags, c) is None


def test_decorrelation_time_interpolates():
    assert decorrelation_time([0, 1, 2], [1.0, 0.5, 0.2], level=0.35) == pytest.approx(1.5)
    assert decorrelation_time([0, 1], [0.1, 0.0], level=0.5) == 0.0


def test_chain_com_rg2_rod_and_masses():
    # two molecules: a 3-site rod (spacing 1, equal masses) and a 2-site dumbbell (masses 1, 3)
    x = np.array([[0.0, 0, 0], [1, 0, 0], [2, 0, 0], [10, 0, 0], [14, 0, 0]])
    com, rg2 = chain_com_rg2(x, [0, 0, 0, 1, 1], [1.0, 1.0, 1.0, 1.0, 3.0])
    np.testing.assert_allclose(com[0], [[1, 0, 0], [13, 0, 0]])
    np.testing.assert_allclose(rg2[0], [2.0 / 3.0, (9 + 3 * 1) / 4.0])


def test_com_msd_over_rg2_ballistic_and_box_drift():
    n, dt = 101, 0.1
    t = np.arange(n)[:, None, None] * dt
    v = np.zeros((1, 4, 3))
    v[0, :, 0] = [1.0, -1.0, 1.0, -1.0]
    com = t * v + 5.0 * t  # every chain also drifts with the box: removed
    lag, msd_lag, rg2_mean, ratio = com_msd_over_rg2(com, np.full((n, 4), 2.0), dt)
    assert lag == pytest.approx(5.0) and msd_lag == pytest.approx(25.0)
    assert rg2_mean == 2.0 and ratio == pytest.approx(12.5)
