"""Reproduce the verification numbers recorded in data/crystals/*.yaml."""

import itertools

import numpy as np
import pytest

from sepsim.crystal_data import cell_matrix, expand_p21c, load_crystal

AVOGADRO = 6.02214076e23
TRANSLATIONS = np.array(list(itertools.product([-1, 0, 1], repeat=3)))


@pytest.fixture(scope="module")
def ipp():
    data = load_crystal("ipp_alpha2_hikosaka1973")
    cell = data["cell"]
    m = cell_matrix(cell["a"], cell["b"], cell["c"], cell["alpha"], cell["beta"], cell["gamma"])
    labels = [s["label"] for s in data["asymmetric_unit"]]
    frac = np.array([s["frac"] for s in data["asymmetric_unit"]])
    return data, m, labels, frac


def min_image(fi, fj, m):
    """Shortest Cartesian vector i->j over lattice translations; returns (vec, translation)."""
    vecs = (fj + TRANSLATIONS - fi) @ m
    k = np.argmin(np.linalg.norm(vecs, axis=1))
    return vecs[k], tuple(int(t) for t in TRANSLATIONS[k])


def angle(fi, fj, fk, m):
    u, _ = min_image(fj, fi, m)
    v, _ = min_image(fj, fk, m)
    return np.degrees(np.arccos(u @ v / np.linalg.norm(u) / np.linalg.norm(v)))


def test_bonds_match_yaml_and_lengths(ipp):
    data, m, labels, frac = ipp
    found = set()
    for i, j in itertools.combinations(range(len(labels)), 2):
        vec, t = min_image(frac[i], frac[j], m)
        if np.linalg.norm(vec) < 1.8:
            found.add((labels[i], labels[j], t))
            assert 1.5385 <= np.linalg.norm(vec) <= 1.5445
    expected = {(a, b, tuple(t)) for a, b, t in data["bonds"]}
    assert found == expected


def test_angles(ipp):
    _, m, labels, frac = ipp
    f = dict(zip(labels, frac))
    ch_backbone = [("C3", "C2", "C9"), ("C3", "C5", "C6"), ("C6", "C8", "C9")]
    ch2_vertex = [("C2", "C3", "C5"), ("C5", "C6", "C8"), ("C8", "C9", "C2")]
    methyl = [
        ("C1", "C2", "C3"),
        ("C1", "C2", "C9"),
        ("C4", "C5", "C3"),
        ("C4", "C5", "C6"),
        ("C7", "C8", "C6"),
        ("C7", "C8", "C9"),
    ]
    for group, target in [(ch_backbone, 110.4), (ch2_vertex, 115.3), (methyl, 110.5)]:
        for i, j, k in group:
            assert angle(f[i], f[j], f[k], m) == pytest.approx(target, abs=1.0), (i, j, k)


def test_31_helix_one_c_per_six_backbone_atoms(ipp):
    _, m, labels, frac = ipp
    f = dict(zip(labels, frac))
    backbone = ["C2", "C3", "C5", "C6", "C8", "C9", "C2"]
    pos = f["C2"].copy()  # unwrapped fractional position walked along the backbone
    for nxt in backbone[1:]:
        _, t = min_image(pos, f[nxt], m)
        pos = f[nxt] + np.array(t)
    np.testing.assert_allclose(pos - f["C2"], [0, 0, 1], atol=1e-12)


def _expanded(ipp):
    _, m, _, frac = ipp
    sites = expand_p21c(frac)
    n = len(sites)
    dist = np.array(
        [
            [
                np.linalg.norm((sites[j] + TRANSLATIONS - sites[i]) @ m, axis=1).min()
                for j in range(n)
            ]
            for i in range(n)
        ]
    )
    return sites, dist


def test_expansion_chains_and_interchain(ipp):
    data, _, _, _ = ipp
    sites, dist = _expanded(ipp)
    assert sites.shape == (36, 3)
    assert np.all((sites >= 0) & (sites < 1))
    assert len(sites) == 3 * data["monomers_per_cell"]

    parent = list(range(len(sites)))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for i, j in itertools.combinations(range(len(sites)), 2):
        if dist[i, j] < 1.8:
            parent[find(i)] = find(j)
    roots = np.array([find(i) for i in range(len(sites))])
    assert len(set(roots)) == data["chains_per_cell"] == 4

    inter = dist[roots[:, None] != roots[None, :]].min()
    assert inter == pytest.approx(data["verification"]["min_interchain_CC_A"], abs=0.01)


def test_ipp_density(ipp):
    data, m, _, _ = ipp
    vol_cm3 = abs(np.linalg.det(m)) * 1e-24
    mass_g = data["monomers_per_cell"] * data["monomer_molar_mass_g_mol"] / AVOGADRO
    assert mass_g / vol_cm3 == pytest.approx(0.947, abs=0.001)
    assert data["verification"]["density_g_cm3"] == 0.947


def test_pe_density():
    data = load_crystal("pe_orthorhombic_busing")
    c = data["cell"]
    vol_cm3 = c["a"] * c["b"] * c["c"] * 1e-24
    mass_g = data["ch2_per_cell"] * data["ch2_molar_mass_g_mol"] / AVOGADRO
    rho = mass_g / vol_cm3
    assert rho == pytest.approx(0.996, abs=0.002)
    assert rho == pytest.approx(data["verification"]["density_g_cm3"], abs=1e-4)
    assert data["setting_angle"]["value_deg"] == 41
    assert len(data["chains"]) == data["chains_per_cell"] == 2
