"""Tests for slit-pore widths from density profiles."""

import numpy as np
import pytest

from sepsim.analysis.pore import local_pore_widths, pore_width

LZ = 100.0
BULK = 0.85  # g/cm^3


def _profile(zc, w, delta=1.5, nbins=400, bulk=BULK):
    """Polymer density with a pore of half-density width ``w`` centred at ``zc`` (periodic)."""
    z = (np.arange(nbins) + 0.5) * LZ / nbins
    d = np.abs(np.mod(z - zc + LZ / 2, LZ) - LZ / 2)
    return z, 0.5 * bulk * (1.0 + np.tanh((d - w / 2) / delta))


def test_tanh_pore_width_exact():
    z, rho = _profile(zc=50.0, w=30.0)
    res = pore_width(z, rho, Lz_A=LZ)
    assert res.bulk_density == pytest.approx(BULK, rel=1e-9)
    assert res.width == pytest.approx(30.0, abs=1e-3)
    assert res.z_lower == pytest.approx(35.0, abs=1e-3)
    assert res.z_upper == pytest.approx(65.0, abs=1e-3)
    assert res.n_pores == 1
    given = pore_width(z, rho, Lz_A=LZ, bulk_density=BULK)
    assert given.width == pytest.approx(30.0, abs=1e-3)


def test_pore_wrapping_across_boundary():
    z, rho = _profile(zc=5.0, w=30.0)  # pore spans z in [-10, 20) -> wraps
    res = pore_width(z, rho, Lz_A=LZ)
    assert res.width == pytest.approx(30.0, abs=1e-3)
    assert res.z_lower == pytest.approx(90.0, abs=1e-3)
    assert res.z_upper == pytest.approx(20.0, abs=1e-3)
    # wide pore: the polymer slab (not the pore) is the part that is contiguous in z
    z, rho = _profile(zc=0.0, w=70.0)
    assert pore_width(z, rho, Lz_A=LZ).width == pytest.approx(70.0, abs=1e-3)


def test_closed_pore_has_zero_width():
    z = np.linspace(0.5, 99.5, 100)
    res = pore_width(z, np.full(100, BULK), Lz_A=LZ)
    assert res.width == 0.0 and res.n_pores == 0


def test_local_widths_detect_narrowed_region():
    nx, ny = 6, 5
    w = np.full((nx, ny), 30.0)
    w[2, 3] = 18.0  # narrowed column
    profiles = np.stack(
        [np.stack([_profile(50.0, w[i, j])[1] for j in range(ny)]) for i in range(nx)]
    )
    z = _profile(50.0, 30.0)[0]
    res = local_pore_widths(z, profiles, Lz_A=LZ)
    np.testing.assert_allclose(res.widths, w, atol=1e-3)
    assert res.min == pytest.approx(18.0, abs=1e-3)
    assert res.max == pytest.approx(30.0, abs=1e-3)
    assert res.mean == pytest.approx(w.mean(), abs=1e-3)
