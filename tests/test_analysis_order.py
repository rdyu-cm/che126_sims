"""Tests for the local chain-alignment crystallinity order parameter."""

import itertools

import numpy as np
import pytest

from sepsim.analysis.order import (
    _neighbour_pairs,
    calibrate_threshold,
    crystallinity,
)

DZ = 1.277  # PE zigzag rise per carbon, Angstrom (1.54 A bond, 112 deg angle)
ZIG = 0.43  # lateral zigzag offset, Angstrom
RC = 5.6
THR = 0.5


def _pe_stem(x0, y0, n, dz=DZ):
    k = np.arange(n)
    return np.column_stack([x0 + ZIG * (-1) ** k, np.full(n, y0), k * dz])


def _pe_crystal(xs, ys, n, dz=DZ):
    pos, cid = [], []
    for c, (x0, y0) in enumerate(itertools.product(xs, ys)):
        pos.append(_pe_stem(x0, y0, n, dz))
        cid.append(np.full(n, c))
    return np.vstack(pos), np.concatenate(cid)


def _random_chains(rng, n_chains, n, lo, hi, first_id=0, bond=1.54):
    """Freely jointed chains; coordinates folded (reflected) into [lo, hi) per axis."""
    pos, cid = [], []
    for c in range(n_chains):
        steps = rng.normal(size=(n, 3))
        steps *= bond / np.linalg.norm(steps, axis=1, keepdims=True)
        r = rng.uniform(lo, hi, size=3) + np.cumsum(steps, axis=0)
        span = hi - lo
        f = np.mod(r - lo, 2 * span)
        pos.append(lo + np.where(f > span, 2 * span - f, f))
        cid.append(np.full(n, first_id + c))
    return np.vstack(pos), np.concatenate(cid)


def test_perfect_pe_crystal_is_fully_crystalline_one_cluster():
    xs = ys = 4.5 * np.arange(4)
    pos, cid = _pe_crystal(xs, ys, 20)
    cell = [18.0, 18.0, 20 * DZ]
    res = crystallinity(pos, cid, cell, r_c=RC, threshold=THR, half_span=1)
    assert res.n_sites == 16 * 18  # two chain-end sites per chain excluded
    assert res.fraction == pytest.approx(1.0)
    assert np.nanmin(res.p2) == pytest.approx(1.0)
    assert res.n_clusters == 1 and res.largest_cluster == res.n_sites
    assert np.isnan(res.p2[cid == 0][[0, -1]]).all()


def test_random_chains_are_amorphous():
    rng = np.random.default_rng(1)
    pos, cid = _random_chains(rng, 30, 30, 0.0, 30.0)
    res = crystallinity(pos, cid, [30.0] * 3, r_c=RC, threshold=THR, half_span=1)
    assert np.nanmean(res.n_neighbours[res.n_neighbours > 0]) > 10
    assert abs(np.nanmean(res.p2)) < 0.05
    assert res.fraction < 0.02


def test_half_crystal_half_melt():
    rng = np.random.default_rng(2)
    n = 20
    Lz = n * DZ
    xs = 2.25 + 4.5 * np.arange(4)  # crystal in x in [0, 18)
    ys = 4.5 * np.arange(4)
    pc, cc = _pe_crystal(xs, ys, n)
    # random chains folded into the other half x in [18, 36); y, z periodic
    pm, cm = _random_chains(rng, 16, n, 18.0, 36.0, first_id=100)
    pm[:, 1] = np.mod(pm[:, 1], 18.0)
    pm[:, 2] = np.mod(pm[:, 2], Lz)
    pos, cid = np.vstack([pc, pm]), np.concatenate([cc, cm])
    res = crystallinity(pos, cid, [36.0, 18.0, Lz], r_c=RC, threshold=THR, half_span=1)
    assert res.fraction == pytest.approx(0.5, abs=0.07)
    scored = ~np.isnan(res.p2)  # sites with a chord and neighbours
    nc = len(pc)
    assert res.crystalline[:nc].sum() / scored[:nc].sum() > 0.85
    assert res.crystalline[nc:].sum() / scored[nc:].sum() < 0.1


def _helices(rng, half_turns_per_site=6, turns=4, spacing=6.6, ncell=3, radius=1.09, pitch=6.5):
    """Synthetic 3_1 helices (6 backbone carbons per turn) along z, random phases.

    Illustrative geometry: radius chosen so consecutive backbone carbons are
    1.54 A apart at a 6.5 A pitch; not a validated iPP crystal structure.
    """
    n = half_turns_per_site * turns
    k = np.arange(n)
    pos, cid = [], []
    for c, (x0, y0) in enumerate(itertools.product(spacing * np.arange(ncell), repeat=2)):
        phi = 2 * np.pi * k / 6 + rng.uniform(0, 2 * np.pi)
        pos.append(
            np.column_stack([x0 + radius * np.cos(phi), y0 + radius * np.sin(phi), k * pitch / 6])
        )
        cid.append(np.full(n, c))
    return np.vstack(pos), np.concatenate(cid), [spacing * ncell] * 2 + [turns * pitch]


def test_ipp_helix_needs_one_turn_chord():
    rng = np.random.default_rng(3)
    pos, cid, cell = _helices(rng)
    bond = np.linalg.norm(pos[1] - pos[0])
    assert bond == pytest.approx(1.54, abs=0.01)
    turn = crystallinity(pos, cid, cell, r_c=7.0, threshold=THR, half_span=3)
    short = crystallinity(pos, cid, cell, r_c=7.0, threshold=THR, half_span=1)
    assert turn.fraction == pytest.approx(1.0)
    assert np.nanmin(turn.p2) == pytest.approx(1.0)
    assert short.fraction < 0.5
    assert np.nanmean(short.p2) < 0.6


def test_monoclinic_cell_matches_equivalent_orthorhombic():
    # Orthorhombic crystal; the sheared cell c' = c - d x_hat (d = chain spacing,
    # a crystal translation) generates the same infinite structure with beta = 99.8 deg.
    d, n = 4.5, 20
    Lz = d / np.tan(np.deg2rad(9.8))
    xs = ys = d * np.arange(4)
    pos, cid = _pe_crystal(xs, ys, n, dz=Lz / n)
    ortho = np.diag([4 * d, 4 * d, Lz])
    mono = ortho.copy()
    mono[2, 0] = -d
    beta = np.degrees(
        np.arccos(mono[0] @ mono[2] / np.linalg.norm(mono[0]) / np.linalg.norm(mono[2]))
    )
    assert beta == pytest.approx(99.8)
    ro = crystallinity(pos, cid, ortho, r_c=RC, threshold=THR, half_span=1)
    rm = crystallinity(pos, cid, mono, r_c=RC, threshold=THR, half_span=1)
    assert rm.fraction == pytest.approx(1.0) and rm.n_clusters == 1
    np.testing.assert_array_equal(rm.n_neighbours, ro.n_neighbours)
    np.testing.assert_allclose(rm.p2, ro.p2, atol=1e-6, equal_nan=True)  # MDAnalysis float32 box


def test_triclinic_neighbour_search_matches_brute_force():
    rng = np.random.default_rng(4)
    tri = np.array([[20.0, 0.0, 0.0], [5.0, 19.0, 0.0], [-4.0, 3.0, 18.0]])
    x = rng.uniform(-30, 30, size=(150, 3))  # unwrapped, outside the cell
    i, j = _neighbour_pairs(x, tri, RC)
    got = {(min(p, q), max(p, q)) for p, q in zip(i.tolist(), j.tolist(), strict=True)}
    shifts = np.array(list(itertools.product(range(-4, 5), repeat=3))) @ tri
    d = x[None, :, None, :] - x[:, None, None, :] + shifts[None, None, :, :]
    close = (np.linalg.norm(d, axis=-1) < RC).any(axis=-1)
    want = {(p, q) for p, q in zip(*np.nonzero(close), strict=True) if p < q}
    assert got == want and len(want) > 0


def test_non_lower_triangular_cell_rejected():
    pos, cid = _pe_crystal([0.0], [0.0], 10)
    cell = np.array([[20.0, 1.0, 0.0], [0.0, 20.0, 0.0], [0.0, 0.0, 20.0]])
    with pytest.raises(ValueError, match="lower triangular"):
        crystallinity(pos, cid, cell, r_c=RC, threshold=THR, half_span=1)


def test_isolated_stem_has_no_neighbours():
    # Same-chain sites within ceil(r_c / l_proj) + h of each other are excluded, so a
    # lone all-trans stem has nothing to align with.
    pos, cid = _pe_crystal([10.0], [10.0], 40)
    res = crystallinity(pos, cid, [30.0, 30.0, 80.0], r_c=RC, threshold=THR, half_span=1)
    assert res.n_sites == 38
    assert np.isnan(res.p2).all()
    assert (res.n_neighbours == 0).all()
    assert res.fraction == 0.0 and res.largest_cluster == 0


def test_folded_stem_counts_own_chain():
    # Two antiparallel stems of one chain (a hairpin): beyond the window, own-chain
    # sites on the returning stem are neighbours.
    n = 20
    up = _pe_stem(10.0, 10.0, n)
    down = _pe_stem(14.5, 10.0, n)[::-1]
    pos = np.vstack([up, down])
    res = crystallinity(
        pos, np.zeros(2 * n), [30.0, 30.0, 80.0], r_c=RC, threshold=THR, half_span=1
    )
    assert res.fraction > 0.8
    assert np.nanmin(res.p2) == pytest.approx(1.0)


def test_crystal_straddling_periodic_boundary():
    xs = ys = 4.5 * np.arange(3)
    pos, cid = _pe_crystal(xs, ys, 20)
    cell = np.array([30.0, 30.0, 20 * DZ])
    ref = crystallinity(pos + [10.0, 10.0, 0.0], cid, cell, r_c=RC, threshold=THR, half_span=1)
    shifted = np.mod(pos - [4.0, 6.0, 7.0], cell)  # block cut by the x, y and z boundaries
    res = crystallinity(shifted, cid, cell, r_c=RC, threshold=THR, half_span=1)
    np.testing.assert_allclose(res.p2, ref.p2, atol=1e-6, equal_nan=True)
    assert res.fraction == pytest.approx(1.0)
    assert res.n_clusters == 1 and res.largest_cluster == res.n_sites


def test_rc_too_large_for_cell_rejected():
    pos, cid = _pe_crystal([0.0], [0.0], 10)
    with pytest.raises(ValueError, match="half the smallest"):
        crystallinity(pos, cid, [10.0, 10.0, 10 * DZ], r_c=5.6, threshold=THR, half_span=1)


def test_calibrate_threshold_equal_error_point():
    rng = np.random.default_rng(5)
    crystal = rng.normal(0.8, 0.1, 20000)
    melt = rng.normal(0.2, 0.2, 20000)
    t = calibrate_threshold(crystal, melt)
    # analytic equal-error point: (t - 0.2)/0.2 = (0.8 - t)/0.1  ->  t = 0.6 (midpoint is 0.5)
    assert t == pytest.approx(0.6, abs=0.01)
    miss_c = np.mean(crystal < t)
    false_m = np.mean(melt >= t)
    assert miss_c == pytest.approx(false_m, abs=2e-4)
