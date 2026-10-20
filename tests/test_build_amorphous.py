"""Phase 2 amorphous builders: topology, growth, data file, manifest, CLI (small systems)."""

import math
import re

import numpy as np
import pytest
import yaml
from _build_helpers import (
    ANGLE,
    build_fixed_conformation,
    derive_ipp_dyad_states,
    expected_counts,
    methyl_clearance,
    reversal_conformation,
    ris_stationary,
)
from scipy.integrate import quad

from sepsim.analysis.units import AVOGADRO
from sepsim.build import growth as G
from sepsim.build.amorphous import DATA_NAME, MANIFEST_NAME, build_amorphous
from sepsim.build.datafile import read_data_file
from sepsim.build.topology import TopologyError, build_chain, formula, match_type, typed_chain
from sepsim.build.ua2aa import convert_ua_to_aa
from sepsim.cli import main
from sepsim.crystal_data import load_crystal
from sepsim.ff.params import KB_KCAL, to_lammps_real

COMBOS = [("pe", "aa"), ("ipp", "aa"), ("pe", "ua"), ("ipp", "ua"), ("pe", "cg")]
N_CHAINS, N_CARBONS = 4, 30
OVERLAP_MIN = {"aa": 2.5, "ua": 3.0, "cg": 3.5}
PHANTOM_CHAINS = 30


class System:
    """A built system parsed back from disk, with the molecule it came from.

    AA iPP is made the D32 way: grow UA iPP, then convert it (here without relaxation).
    """

    def __init__(self, root, polymer, res, n_chains=N_CHAINS, n_carbons=N_CARBONS, seed=1):
        self.polymer, self.res, self.n_chains, self.n = polymer, res, n_chains, n_carbons
        self.converted = polymer == "ipp" and res == "aa"
        if self.converted:
            ua = build_amorphous(polymer, "ua", n_chains, n_carbons, 0.3, seed, root)
            self.dir = convert_ua_to_aa(ua / DATA_NAME, ua, root)
        else:
            self.dir = build_amorphous(polymer, res, n_chains, n_carbons, 0.3, seed, root)
        self.mol, self.ff = typed_chain(polymer, res, n_carbons)
        self.df = read_data_file(self.dir / DATA_NAME)
        self.manifest = yaml.safe_load((self.dir / MANIFEST_NAME).read_text())
        self.pos = self.df.unwrapped()
        self.box = self.df.box[0][1] - self.df.box[0][0]
        self.real = to_lammps_real(self.ff)

    def chain(self, c):
        nper = self.mol.n_atoms
        return self.pos[c * nper : (c + 1) * nper]

    def names(self, section):
        return self.df.names[section]


@pytest.fixture(scope="module")
def systems(tmp_path_factory):
    root = tmp_path_factory.mktemp("systems")
    return {(p, r): System(root, p, r) for p, r in COMBOS}


@pytest.fixture(params=COMBOS, ids=lambda c: f"{c[0]}-{c[1]}")
def system(request, systems):
    return systems[request.param]


# --------------------------------------------------------------------------- counts


def test_counts_per_chain_formulas(system):
    n, nc = system.n, system.n_chains
    atoms = {
        ("pe", "aa"): 3 * n + 2,
        ("ipp", "aa"): 3 * n + 2,
        ("pe", "ua"): n,
        ("ipp", "ua"): n + n // 3 - 1,  # n/3 - 1 methines carry an explicit H
        ("pe", "cg"): n // 3,
    }[(system.polymer, system.res)]
    exp = expected_counts(system.polymer, system.res, n)
    assert exp["atoms"] == atoms
    mol = system.mol
    assert (mol.n_atoms, len(mol.bonds), len(mol.angles), len(mol.dihedrals)) == (
        exp["atoms"],
        exp["bonds"],
        exp["angles"],
        exp["dihedrals"],
    )
    for key in ("atoms", "bonds", "angles", "dihedrals"):
        assert system.df.counts[key] == nc * exp[key]
        assert system.manifest["counts"]["total"][key] == nc * exp[key]


def test_linear_chain_bond_count(system):
    """A single linear/branched tree: bonds = atoms - 1 per chain."""
    assert len(system.mol.bonds) == system.mol.n_atoms - 1


def test_molecule_ids_are_chain_indices(system):
    mol_ids = system.df.atoms[:, 1].astype(int)
    expected = np.repeat(np.arange(1, system.n_chains + 1), system.mol.n_atoms)
    assert np.array_equal(mol_ids, expected)


# --------------------------------------------------------------------------- physics


@pytest.mark.parametrize("polymer", ["pe", "ipp"])
def test_charge_neutral_aa(systems, polymer):
    s = systems[(polymer, "aa")]
    q = s.df.atoms[:, 3]
    assert abs(q.sum()) < 1e-9
    for c in range(s.n_chains):
        assert abs(q[c * s.mol.n_atoms : (c + 1) * s.mol.n_atoms].sum()) < 1e-9


def test_total_mass_equals_formula_mass(system):
    masses = {int(r[0]): float(r[1]) for r in system.df.sections["Masses"]}
    total = sum(masses[int(t)] for t in system.df.atoms[:, 2])
    counts, text = formula(system.mol.types)
    assert text == f"C{system.n}H{2 * system.n + 2}"
    formula_mass = system.n_chains * (counts["C"] * 12.011 + counts["H"] * 1.008)
    # SDK bead masses differ from the element sums in the 5th significant digit.
    assert total == pytest.approx(formula_mass, rel=1e-4)
    assert system.manifest["total_mass_g_mol"] == pytest.approx(total, rel=1e-9)


def test_box_volume_matches_density(system):
    mass = system.manifest["total_mass_g_mol"]
    volume = mass / (AVOGADRO * 0.3) * 1e24
    assert system.box**3 == pytest.approx(volume, rel=1e-6)
    assert all(hi - lo == pytest.approx(system.box) for lo, hi in system.df.box)


def test_no_overlaps(system):
    d = G.min_nonbonded_distances(system.mol, system.pos, system.box, system.n_chains)
    local = d["local"]
    recorded = system.manifest["overlap_minima_angstrom"]  # from unrounded coordinates
    assert recorded["heavy"] == pytest.approx(d["heavy"], abs=1e-5)
    assert recorded["local"] == pytest.approx(local, abs=1e-5)
    if system.converted:
        # Carbons come from UA growth, so checked (> 6-bond) heavy pairs keep the UA
        # threshold; the added H's are not checked (unrelaxed input here).
        assert d["heavy"] >= G.MIN_DIST["ua"][0] - 1e-5
        assert d["all"] > 0.3
    else:
        assert d["heavy"] > OVERLAP_MIN[system.res]
        assert d["all"] > {"aa": 1.5, "ua": 1.7, "cg": 3.5}[system.res]
    if system.polymer == "ipp":
        # D31: iPP local pairs (4-6 bonds) are not growth-checked; only a sanity floor here.
        assert local["bonds"] == [4, 6]
        assert min(v for k, v in local.items() if k != "bonds") > 0.5
    else:
        assert local == {"bonds": None, "heavy_heavy": None, "heavy_h": None, "h_h": None}


def test_wrapped_coordinates_inside_box(system):
    xyz = system.df.atoms[:, 4:7]
    assert xyz.min() >= 0.0 and xyz.max() <= system.box


# --------------------------------------------------------------------------- geometry


def test_bond_lengths_equal_r0(system):
    r0 = {i: float(r[2]) for r in system.df.sections["Bond Coeffs"] for i in [int(r[0])]}
    b = system.df.topology("Bonds")
    d = np.linalg.norm(system.pos[b[:, 2] - 1] - system.pos[b[:, 3] - 1], axis=1)
    target = np.array([r0[t] for t in b[:, 1]])
    if system.converted:  # carbons keep UA positions: C-C = 1.54 until AA minimization
        is_ch = np.array([system.names("Bond Coeffs")[t] == "CT-HC" for t in b[:, 1]])
        assert np.allclose(d[is_ch], target[is_ch], atol=2e-5)
        assert np.allclose(d[~is_ch], 1.54, atol=2e-5)
    else:
        assert np.allclose(d, target, atol=2e-5)


def test_angles_within_tolerance(system):
    if system.res == "cg":
        pytest.skip("CG angles are sampled; see test_cg_angle_distribution")
    th0 = {int(r[0]): float(r[2]) for r in system.df.sections["Angle Coeffs"]}
    a = system.df.topology("Angles")
    p = system.pos
    ang = G.angle_deg(p[a[:, 2] - 1], p[a[:, 3] - 1], p[a[:, 4] - 1])
    target = np.array([th0[t] for t in a[:, 1]])
    assert np.all(np.abs(ang - target) < 5.0)  # H placement is near-tetrahedral
    is_h = np.tile(system.mol.is_hydrogen(), system.n_chains)
    backbone = set()
    for c in range(system.n_chains):
        backbone.update(c * system.mol.n_atoms + i + 1 for i in system.mol.backbone)
    bb = np.array([all(x in backbone for x in row[2:]) for row in a])
    heavy = ~is_h[a[:, 2:] - 1].any(axis=1)
    # converted AA iPP keeps the UA backbone angles (114/112 vs 112.7)
    tol = 1.5 if system.converted else 1e-3
    assert np.all(np.abs(ang - target)[bb & heavy] < tol)


def boltzmann_mean(K, theta0, T, r1=0.0, r2=0.0, pair=None):
    def w(t):
        e = float(G.cg_angle_energy(math.degrees(t), K, theta0, r1, r2, pair))
        return math.sin(t) * math.exp(-e / (KB_KCAL * T))

    norm = quad(w, 0, math.pi)[0]
    return math.degrees(quad(lambda t: t * w(t), 0, math.pi)[0] / norm)


def test_cg_angle_distribution(tmp_path):
    s = System(tmp_path, "pe", "cg", n_chains=10, n_carbons=300)
    a = s.df.topology("Angles")
    p = s.pos
    ang = G.angle_deg(p[a[:, 2] - 1], p[a[:, 3] - 1], p[a[:, 4] - 1])
    ff = s.real["angle"]["CM-CM-CM"]
    r0 = s.real["bond"]["CM-CM"]["r0"]
    expected = boltzmann_mean(ff["K"], ff["theta0"], 500.0, r0, r0, s.real["pair"][("CM", "CM")])
    assert expected == pytest.approx(135.0, abs=1.5)
    assert ang.mean() == pytest.approx(expected, abs=3.0)
    assert ang.std() > 15.0  # far broader than the old 10 deg spread
    assert ang.min() > 60.0  # D33: 1-3 repulsion keeps the end beads apart
    assert "D33" in s.manifest["growth"]["params"]["cg_angle_energy"]


def lammps_spica_e13(rsq, eps, sigma):
    """angle_spica.cpp lj9_6 branch, with lj3/lj4/rminsq/emin from pair_lj_spica.cpp init_one."""
    lj3, lj4 = 6.75 * eps * sigma**9, 6.75 * eps * sigma**6
    rmin = sigma * math.exp(1.0 / (9 - 6) * math.log(9 / 6))
    ratio = sigma / rmin
    emin = 6.75 * eps * (ratio**9 - ratio**6)
    if rsq >= rmin * rmin:
        return 0.0
    r3inv = (1.0 / rsq) ** 1.5
    return r3inv * r3inv * (lj3 * r3inv - lj4) - emin


@pytest.mark.parametrize(
    ("theta", "r1", "r2", "pair", "angle"),
    [
        (60.0, 3.64, 3.64, ("CM", "CM"), "CM-CM-CM"),  # equilateral: r13 = 3.64
        (80.0, 3.64, 3.64, ("CM", "CM"), "CM-CM-CM"),
        (100.0, 3.64, 3.64, ("CM", "CM"), "CM-CM-CM"),  # r13 5.58 > r_min 5.16: harmonic only
        (90.0, 3.64, 3.65, ("CM", "CT"), "CM-CM-CT"),  # r13 5.155 < r_min(CM-CT) 5.203
    ],
)
def test_cg_angle_energy_matches_lammps_spica(theta, r1, r2, pair, angle):
    real = to_lammps_real(typed_chain("pe", "cg", 30)[1])
    p, a = real["pair"][pair], real["angle"][angle]
    rsq = r1 * r1 + r2 * r2 - 2 * r1 * r2 * math.cos(math.radians(theta))
    e13 = lammps_spica_e13(rsq, p["epsilon"], p["sigma"])
    expected = a["K"] * math.radians(theta - a["theta0"]) ** 2 + e13
    got = float(G.cg_angle_energy(theta, a["K"], a["theta0"], r1, r2, p))
    assert got == pytest.approx(expected, rel=1e-12)
    assert (e13 > 0) == (theta < 100.0)
    if theta == 60.0:  # hand value: 6.75 * 0.42 * ((4.506/3.64)^9 - (4.506/3.64)^6) + 0.42
        assert e13 == pytest.approx(9.5714, abs=1e-3)


def test_cg_angle_sampling_has_no_13_overlap():
    """Many draws from the D33 tables never give the tight angles harmonic-only growth did."""
    mol, ff = typed_chain("pe", "cg", 30)
    grower = G._Grower(mol, ff, 1, 100.0, G.GrowthParams(), np.random.default_rng(0))
    bb = mol.backbone
    for a, j, b in [(bb[0], bb[1], bb[2]), (bb[1], bb[2], bb[3])]:  # CT-CM-CM, CM-CM-CM
        draws = np.array([grower._theta(a, j, b) for _ in range(200_000)])
        assert draws.min() > 60.0
    real = to_lammps_real(ff)
    harmonic = G.cg_angle_grid(1.19, 173.0, 500.0)
    full = G.cg_angle_grid(1.19, 173.0, 500.0, 3.64, 3.64, real["pair"][("CM", "CM")])
    assert np.interp(60.0, *harmonic) > 1e-3  # the pre-D33 table: 0.3 % below 60 deg
    assert np.interp(60.0, *full) < 1e-7


def test_cg_angle_grid_is_normalized():
    grid, cdf = G.cg_angle_grid(1.19, 173.0, 500.0)
    assert cdf[0] == 0.0 and cdf[-1] == 1.0 and np.all(np.diff(cdf) >= 0)
    mean = np.trapezoid(grid[1:] * np.diff(cdf) / np.diff(grid), grid[1:])
    assert mean == pytest.approx(boltzmann_mean(1.19, 173.0, 500.0), abs=0.5)


def backbone_dihedrals(s):
    out = []
    bb = np.array(s.mol.backbone)
    for c in range(s.n_chains):
        p = s.chain(c)[bb]
        out.append(G.dihedral_deg(p[:-3], p[1:-2], p[2:-1], p[3:]))
    return np.array(out)


def ris_fractions(phi):
    phi = np.ravel(phi)
    t = np.abs(phi) > 120
    gp = (phi > 0) & ~t
    return {"t": t.mean(), "g+": gp.mean(), "g-": (~t & ~gp).mean()}


@pytest.mark.parametrize("res", ["aa", "ua"])
def test_torsion_statistics_match_ris(tmp_path, res):
    s = System(tmp_path, "pe", res, n_chains=8, n_carbons=90)
    phi = backbone_dihedrals(s)
    frac = ris_fractions(phi)
    target = ris_stationary(G.GrowthParams())
    for k in target:
        assert frac[k] == pytest.approx(target[k], abs=0.07)
    # D29 jitter: deviation from the nearest RIS state has sd ~ torsion_sd_deg (10 deg)
    dev = (phi[..., None] - np.array([180.0, 60.0, -60.0]) + 180.0) % 360.0 - 180.0
    nearest = np.take_along_axis(dev, np.abs(dev).argmin(axis=-1)[..., None], -1)
    assert nearest.std() == pytest.approx(G.GrowthParams().torsion_sd_deg, abs=1.5)


def test_torsion_jitter_required():
    with pytest.raises(ValueError, match="torsion_sd_deg"):
        G.GrowthParams(torsion_sd_deg=0.0)


def test_pentane_rule_holds(systems):
    phi = backbone_dihedrals(systems[("pe", "ua")])
    g = np.where(np.abs(phi) > 120, 0, np.sign(phi))
    assert not np.any(g[:, :-1] * g[:, 1:] == -1)


# --------------------------------------------------------------------------- iPP tacticity


@pytest.mark.parametrize("res", ["aa", "ua"])
def test_isotactic(systems, res):
    s = systems[("ipp", res)]
    for c in range(s.n_chains):
        signs = G.chirality_signs(s.mol, s.chain(c))
        assert len(signs) == s.n // 3 - 1
        assert set(signs) == {G.CHIRAL_SIGN}


@pytest.mark.parametrize("res", ["aa", "ua"])
def test_flipped_methyl_fails_isotacticity(systems, res):
    s = systems[("ipp", res)]
    pos = s.chain(0).copy()
    i = next(
        i
        for i in range(3, len(s.mol.backbone))
        if len(s.mol.subs[i]) == 2 and not s.mol.is_hydrogen()[s.mol.subs[i][0]]
    )
    me, h = s.mol.subs[i]
    c = pos[s.mol.backbone[i]]
    # Swap the methyl and H directions (bond lengths kept): inverts that stereocenter.
    d_me, d_h = pos[me] - c, pos[h] - c
    pos[me] = c + d_h / np.linalg.norm(d_h) * np.linalg.norm(d_me)
    pos[h] = c + d_me / np.linalg.norm(d_me) * np.linalg.norm(d_h)
    signs = G.chirality_signs(s.mol, pos)
    assert set(signs) == {1, -1}


# --------------------------------------------------------------------------- iPP dyad rule (D30)


@pytest.mark.parametrize("res", ["aa", "ua"])
def test_ipp_dyad_states_derived_geometrically(res):
    assert derive_ipp_dyad_states(res) == (G.IPP_DYAD_TG, G.IPP_DYAD_GT)


@pytest.mark.parametrize("res", ["aa", "ua"])
@pytest.mark.parametrize("pair", ["tg", "gt"])
def test_ipp_helix_matches_crystal_repeat(res, pair):
    """A uniform allowed-dyad chain is a 3_1 helix with c close to the alpha-form c axis."""
    mol, ff = typed_chain("ipp", res, 60)
    states = G.IPP_DYAD_TG if pair == "tg" else G.IPP_DYAD_GT
    phis = [ANGLE[states[r - 1]] if r else 180.0 for r in G.ipp_dyad_roles(mol)]
    pos = build_fixed_conformation(mol, ff, phis)
    assert set(G.chirality_signs(mol, pos)) == {G.CHIRAL_SIGN}
    assert methyl_clearance(mol, pos) > 3.5
    bb = pos[mol.backbone]
    c_cryst = load_crystal("ipp_alpha2_hikosaka1973")["cell"]["c"]
    middle = range(4, len(bb) - 12)
    repeat = [np.linalg.norm(bb[i + 6] - bb[i]) for i in middle]
    assert np.ptp(repeat) < 1e-6  # strictly periodic: 3 monomers per turn
    assert np.mean(repeat) == pytest.approx(c_cryst, abs=0.3)
    # 3 monomers = 6 backbone bonds per turn: atoms 2 and 4 bonds apart are off-axis
    assert np.linalg.norm(bb[10] - bb[4]) > np.linalg.norm(bb[7] - bb[4])


@pytest.mark.parametrize("res", ["aa", "ua"])
def test_grown_ipp_dyads_use_allowed_pairs(systems, res):
    s = systems[("ipp", res)]
    roles = G.ipp_dyad_roles(s.mol)
    phi = backbone_dihedrals(s)  # phi[:, j] is the torsion set at growth step j + 3
    state = np.where(np.abs(phi) > 120, 0, np.where(phi > 0, 1, 2))
    for c in range(s.n_chains):
        for k, r in enumerate(roles):
            if r == 1:
                pair = (state[c, k - 3], state[c, k - 2])
                assert pair in (G.IPP_DYAD_TG, G.IPP_DYAD_GT)


def test_bond_distances():
    mol = build_chain("pe", "ua", 12)
    d = G.bond_distances(mol, 6)
    assert d[0, 6] == 6 and d[0, 7] == -1 and d[3, 3] == 0
    assert np.array_equal(G.exclusion_matrix(mol, 6), d >= 0)


def _replay(mol, ff, pos, n_chains=1, stop=None):
    """Re-place a chain step by step (steps < ``stop``) through the growth overlap check.

    Returns (grower, list of growth steps whose atoms were rejected).
    """
    bb = mol.backbone
    gr = G._Grower(mol, ff, n_chains, 500.0, G.GrowthParams(), np.random.default_rng(0))
    rejected = []
    for s in range(len(bb) if stop is None else stop):
        new = [bb[s]] + (list(mol.subs[s - 1]) if s >= 2 else [])
        if s == len(bb) - 1:
            new += list(mol.subs[s])
        new += [h for m in list(new) for h in mol.sub_hs.get(m, [])]
        if s and gr._clashes(0, {a: pos[a] for a in new}):
            rejected.append(s)
        for a in new:
            gr.pos[a] = pos[a]
            gr.cells.add(a, pos[a])
    return gr, rejected


def test_ua_reversal_junction_accepted_and_genuine_clash_rejected():
    """D31: a UA helix reversal passes the overlap check; real clashes still fail."""
    mol, ff, k, pos = reversal_conformation("ua")
    gr, rejected = _replay(mol, ff, pos, n_chains=2)
    assert rejected == []
    local = G.min_nonbonded_distances(mol, pos, 500.0, 1)["local"]
    assert local["heavy_heavy"] == pytest.approx(2.805, abs=0.01)  # the junction contact
    bb = mol.backbone
    # the same contact between two chains is checked
    assert gr._clashes(1, {bb[k]: pos[bb[k]]})
    # an intra-chain pair 8 bonds apart is checked: next atom 2.8 A from bb[k - 8],
    # pointing away from the chain so nothing else is near
    gr, _ = _replay(mol, ff, pos, stop=k)
    placed = np.nonzero(gr.cells.atom_cell >= 0)[0]
    bdist = G.bond_distances(mol, 200)
    new = bb[k]
    # partner bb[0] (k bonds away): every atom near the probe is > 6 bonds from bb[k]
    # partner bb[k-5] (5 bonds away): every atom near the probe is <= 6 bonds from bb[k]
    for partner, far, clash in ((bb[0], True, True), (bb[k - 5], False, False)):
        group = [a for a in placed if (bdist[new, a] > 6) == far]
        probe = _lonely_probe(pos[partner], pos[[a for a in placed if a not in group]], 2.8)
        near = [a for a in placed if np.linalg.norm(pos[a] - probe) < 3.3]
        assert partner in near and set(near) <= set(group)
        assert gr._clashes(0, {new: probe}) is clash


def _lonely_probe(center, avoid, r):
    """Point at distance r from ``center`` with the most clearance from ``avoid``."""
    n = 400
    z = 1 - 2 * (np.arange(n) + 0.5) / n
    phi = np.pi * (1 + 5**0.5) * np.arange(n)
    dirs = np.column_stack([np.sqrt(1 - z**2) * np.cos(phi), np.sqrt(1 - z**2) * np.sin(phi), z])
    pts = center + r * dirs
    d = np.linalg.norm(pts[:, None, :] - avoid[None, :, :], axis=2)
    return pts[np.argmax(d.min(axis=1))]


def test_local_window_derived_from_reversal():
    """The UA window is the largest bond count among the sub-threshold pairs a reversal creates.

    Pairs are taken from an ideal reversal in the middle of a C60 chain; a uniform helix has
    none. At UA these are the junction methines, their methyls and methine H's (4-6 bonds).
    """
    res = "ua"
    mol, ff, _, pos = reversal_conformation(res, n_carbons=60, at=9)
    helix = [ANGLE[G.IPP_DYAD_TG[r - 1]] if r else 180.0 for r in G.ipp_dyad_roles(mol)]
    uniform = build_fixed_conformation(mol, ff, helix)
    xx, xh, hh = G.MIN_DIST[res]
    thr = np.array([[xx, xh], [xh, hh]])
    is_h = np.array(mol.is_hydrogen()).astype(int)
    bd = G.bond_distances(mol, 200)

    def clashes(p):
        d = np.linalg.norm(p[:, None] - p[None], axis=2)
        mask = (d < thr[is_h[:, None], is_h[None, :]]) & (bd > 3)
        return {(i, j) for i, j in zip(*np.nonzero(mask), strict=True) if i < j}

    assert clashes(uniform) == set()
    created = clashes(pos)
    assert created
    window = max(int(bd[i, j]) for i, j in created)
    assert window == G.GrowthParams().exclusion_bonds(mol)


def test_phantom_ipp_cn_regression():
    """Phantom C_n at the default ipp_p_reversal (regression; D42 calibrates grown chains,
    which overlap rejection swells to ~6, so the phantom chain sits below that)."""
    mol, ff = typed_chain("ipp", "ua", 240)
    bb = np.array(mol.backbone)
    nper, nb, n = mol.n_atoms, len(bb) - 1, PHANTOM_CHAINS
    cn = []
    for seed in (1, 2, 3):
        pos, _, _ = G.grow_amorphous(mol, ff, n, 0.01, seed, G.GrowthParams(check_overlaps=False))
        ends = pos.reshape(n, nper, 3)[:, [bb[0], bb[-1]]]
        cn.append(np.sum((ends[:, 1] - ends[:, 0]) ** 2, axis=1).mean() / (nb * 1.54**2))
    assert 3.0 < np.mean(cn) < 4.0  # 3.50 at 0.50


def test_growth_stats_record_reversals(systems):
    stats = systems[("ipp", "ua")].manifest["growth"]["stats"]
    # C30: 9 methines -> 8 meso dyads -> 7 junctions per chain
    assert stats["dyads"] == N_CHAINS * (N_CARBONS // 3 - 3)
    assert 0 < stats["reversals"] < stats["dyads"]
    assert systems[("pe", "ua")].manifest["growth"]["stats"]["dyads"] == 0


# --------------------------------------------------------------------------- typing


def test_every_bonded_entry_typed(system):
    df, ff = system.df, system.ff
    sections = [
        ("Bonds", "Bond Coeffs", ff.bond_types),
        ("Angles", "Angle Coeffs", ff.angle_types),
        ("Dihedrals", "Dihedral Coeffs", ff.dihedral_types),
    ]
    atom_name = df.names["Masses"]
    atom_types = df.atoms[np.argsort(df.atoms[:, 0]), 2].astype(int)
    raw = yaml.safe_load(ff.path.read_text())
    for topo, coeffs, ff_section in sections:
        rows = df.topology(topo)
        if not len(rows):
            assert system.res == "cg" and topo == "Dihedrals"
            continue
        names = df.names[coeffs]
        assert set(rows[:, 1]) <= set(names)
        assert len(names) == len(df.sections[coeffs])
        for row in rows:
            key = tuple(atom_name[atom_types[a - 1]] for a in row[2:])
            assert match_type(key, ff_section, ff, raw.get("wildcards") or {}) == names[row[1]]


def test_unknown_pattern_fails_loudly():
    _, ff = typed_chain("pe", "aa", 6)
    with pytest.raises(TopologyError, match="matches no"):
        match_type(("HC", "HC"), ff.bond_types, ff, {})


@pytest.mark.parametrize("polymer", ["pe", "ipp"])
def test_ua_dihedrals_never_include_h(systems, polymer):
    s = systems[(polymer, "ua")]
    atom_name = s.df.names["Masses"]
    atom_types = s.df.atoms[np.argsort(s.df.atoms[:, 0]), 2].astype(int)
    rows = s.df.topology("Dihedrals")
    assert len(rows)
    assert all(atom_name[atom_types[a - 1]] != "H" for row in rows for a in row[2:])


# --------------------------------------------------------------------------- data file


def test_data_file_parses_back(system):
    df, real = system.df, system.real
    for key, section in [
        ("atom types", "Masses"),
        ("bond types", "Bond Coeffs"),
        ("angle types", "Angle Coeffs"),
    ]:
        assert df.counts[key] == len(df.sections[section])
    for key, section in [("atoms", "Atoms"), ("bonds", "Bonds"), ("angles", "Angles")]:
        assert df.counts[key] == len(df.sections[section])
    assert df.counts["dihedrals"] == len(df.sections.get("Dihedrals", []))
    used = set(system.mol.types)
    assert set(df.names["Masses"].values()) == used
    for i, name in df.names["Masses"].items():
        mass = float(df.sections["Masses"][i - 1][1])
        assert mass == pytest.approx(real["atoms"][name]["mass"])
    for row in df.sections["Bond Coeffs"]:
        b = real["bond"][df.names["Bond Coeffs"][int(row[0])]]
        assert (float(row[1]), float(row[2])) == pytest.approx((b["K"], b["r0"]))
    if system.res == "cg":
        rows = df.sections["PairIJ Coeffs"]
        assert len(rows) == 3 and all(r[2] == "lj9_6" for r in rows)
        assert "Pair Coeffs" not in df.sections
    else:
        rows = df.sections["Pair Coeffs"]
        assert len(rows) == len(used)
        for row in rows:
            p = real["pair"][(df.names["Masses"][int(row[0])],) * 2]
            assert (float(row[1]), float(row[2])) == pytest.approx((p["epsilon"], p["sigma"]))


def test_atoms_type_column_matches_manifest(system):
    type_ids = system.manifest["type_ids"]["atom"]
    expected = np.tile([type_ids[t] for t in system.mol.types], system.n_chains)
    assert np.array_equal(system.df.sorted_atoms()[:, 2].astype(int), expected)


def test_shake_bond_types(systems):
    """Only the UA methine C-H is SHAKE-constrained (D12a/D18)."""
    m = systems[("ipp", "ua")].manifest
    assert m["shake_bond_types"] == {"CH-H": m["type_ids"]["bond"]["CH-H"]}
    for key in [("pe", "aa"), ("ipp", "aa"), ("pe", "ua"), ("pe", "cg")]:
        assert systems[key].manifest["shake_bond_types"] == {}


# Tiny systems with hand-checked lines (independent of to_lammps_real): TraPPE K and eps in
# kcal/mol are k/kB * 0.0019872043 (bond: k0 / 2 / 4.184 / 100; angle: k/2; torsion: 2c_n).
TINY_LINES = {
    ("pe", "ua", 4): [
        "4 atoms",
        "1 dihedrals",
        "1 15.035  # CH3",
        "1 0.1947460214 3.75  # CH3",
        "2 0.0914113978 3.95  # CH2",
        "1 600.401529637 1.54  # CHx-CHy",
        "1 62.100134375 114  # CHx-CH2-CHy",
        "1 1.41103428526 -0.271014922434 3.14502901335 0  # CHx-CH2-CH2-CHy",
        "1 1 1 2",
        "1 1 1 2 3",
        "1 1 1 2 3 4",
    ],
    ("ipp", "ua", 9): [
        "4 0 0  # H",  # D18: explicit methine H has no LJ
        "2 340 1.09  # CH-H",
        "3 37.5 110.7  # H-CH-CHx",
    ],
    ("pe", "aa", 4): [
        "1 0.066 3.55  # CT_CH3",
        "3 0.026 2.48  # HC",
        "1 268 1.529  # CT-CT",
        "1 0.85 -0.2 0.2 0  # CT-CT-CT-CT",
    ],
    ("pe", "cg", 15): [
        "PairIJ Coeffs # lj/spica",
        "1 1 lj9_6 0.42 4.506  # CM-CM",
        "1 2 lj9_6 0.444 4.5455  # CM-CT",
        "2 2 lj9_6 0.469 4.585  # CT-CT",
        "Angle Coeffs # spica",
        "1 1.19 173  # CM-CM-CM",
        "2 1.19 175  # CM-CM-CT",
    ],
}


@pytest.mark.parametrize("key", list(TINY_LINES), ids=lambda k: f"{k[0]}-{k[1]}-c{k[2]}")
def test_data_file_format_tiny(tmp_path, key):
    polymer, res, n = key
    d = build_amorphous(polymer, res, 1, n, 0.3, 1, tmp_path)
    lines = (d / DATA_NAME).read_text().splitlines()
    for line in TINY_LINES[key]:
        assert line in lines
    atoms = lines[lines.index("Atoms # full") + 2 :]
    row = r"\d+ 1 \d+ -?\d+(\.\d+)?( -?\d+\.\d{6}){3}( -?\d+){3}"
    assert all(re.fullmatch(row, a) for a in atoms[: build_chain(polymer, res, n).n_atoms])


# --------------------------------------------------------------------------- determinism


def _strip_git(path):
    m = yaml.safe_load(path.read_text())
    m.pop("git")
    return m


@pytest.mark.parametrize("polymer,res", [("ipp", "ua"), ("pe", "aa"), ("pe", "cg")])
def test_determinism(tmp_path, polymer, res):
    a = build_amorphous(polymer, res, 3, 30, 0.3, 7, tmp_path / "a")
    b = build_amorphous(polymer, res, 3, 30, 0.3, 7, tmp_path / "b")
    c = build_amorphous(polymer, res, 3, 30, 0.3, 8, tmp_path / "c")
    assert (a / DATA_NAME).read_bytes() == (b / DATA_NAME).read_bytes()
    assert _strip_git(a / MANIFEST_NAME) == _strip_git(b / MANIFEST_NAME)
    assert (a / DATA_NAME).read_bytes() != (c / DATA_NAME).read_bytes()


# --------------------------------------------------------------------------- errors / CLI


def test_cg_ipp_raises():
    with pytest.raises(TopologyError, match="PE only"):
        build_chain("ipp", "cg", 240)


def test_cli_build_amorphous(tmp_path, capsys):
    argv = ["build", "amorphous", "--polymer", "pe", "--res", "ua"]
    argv += ["--chains", "2", "--carbons", "12", "--seed", "3", "--out", str(tmp_path)]
    assert main(argv) == 0
    sysdir = tmp_path / "pe_ua_amorph_n2_c12_s3"
    assert (sysdir / DATA_NAME).is_file() and (sysdir / MANIFEST_NAME).is_file()
    assert str(sysdir) in capsys.readouterr().out


def test_cli_build_cg_ipp_errors(tmp_path, capsys):
    argv = ["build", "amorphous", "--polymer", "ipp", "--res", "cg", "--out", str(tmp_path)]
    assert main(argv) == 1
    assert "PE only" in capsys.readouterr().err
    assert not any(tmp_path.iterdir())
