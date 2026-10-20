"""UA -> AA conversion (decision D32): small systems, round trip, robustness, errors, CLI."""

import shutil

import numpy as np
import pytest
import yaml

from sepsim.build import growth as G
from sepsim.build.amorphous import (
    DATA_NAME,
    MANIFEST_NAME,
    DirectAAiPPError,
    build_amorphous,
)
from sepsim.build.datafile import read_data_file
from sepsim.build.topology import build_chain, typed_chain
from sepsim.build.ua2aa import ConversionError, convert_ua_to_aa, ua_to_aa_index_map
from sepsim.cli import main
from sepsim.ff.params import to_lammps_real

N_CHAINS, N_CARBONS = 3, 30


@pytest.fixture(scope="module")
def ua_system(tmp_path_factory):
    root = tmp_path_factory.mktemp("ua")
    return build_amorphous("ipp", "ua", N_CHAINS, N_CARBONS, 0.3, 5, root)


@pytest.fixture(scope="module")
def converted(ua_system, tmp_path_factory):
    out = tmp_path_factory.mktemp("aa")
    return convert_ua_to_aa(ua_system / DATA_NAME, ua_system, out)


def _strip(path, keys=("git", "source")):
    m = yaml.safe_load(path.read_text())
    for k in keys:
        m.pop(k)
    return m


def test_round_trip_topology_matches_typed_chain(converted):
    aa, _ = typed_chain("ipp", "aa", N_CARBONS)
    df = read_data_file(converted / DATA_NAME)
    nper = aa.n_atoms
    names = {sec: df.names[f"{sec} Coeffs"] for sec in ("Bond", "Angle", "Dihedral")}
    atom_names = df.names["Masses"]
    types = df.sorted_atoms()[:, 2].astype(int)
    assert [atom_names[t] for t in types] == aa.types * N_CHAINS
    for section, entries, kinds, key in (
        ("Bonds", aa.bonds, aa.bond_types, "Bond"),
        ("Angles", aa.angles, aa.angle_types, "Angle"),
        ("Dihedrals", aa.dihedrals, aa.dihedral_types, "Dihedral"),
    ):
        rows = df.topology(section)
        expected = [
            (kind, *(a + c * nper + 1 for a in e))
            for c in range(N_CHAINS)
            for e, kind in zip(entries, kinds, strict=True)
        ]
        got = [(names[key][r[1]], *r[2:].tolist()) for r in rows]
        assert got == expected


def test_carbons_unchanged_and_chirality_preserved(ua_system, converted):
    ua, aa = build_chain("ipp", "ua", N_CARBONS), build_chain("ipp", "aa", N_CARBONS)
    index = ua_to_aa_index_map(ua, aa)
    upos = read_data_file(ua_system / DATA_NAME).unwrapped()
    apos = read_data_file(converted / DATA_NAME).unwrapped()
    ua_h = ua.is_hydrogen()
    for c in range(N_CHAINS):
        u = upos[c * ua.n_atoms : (c + 1) * ua.n_atoms]
        a = apos[c * aa.n_atoms : (c + 1) * aa.n_atoms]
        for i, j in index.items():
            if not ua_h[i]:
                assert np.allclose(a[j], u[i], atol=2e-6)
        assert G.chirality_signs(aa, a) == G.chirality_signs(ua, u)
        assert set(G.chirality_signs(aa, a)) == {G.CHIRAL_SIGN}


def test_hydrogen_geometry_matches_ff(converted):
    aa, ff = typed_chain("ipp", "aa", N_CARBONS)
    real = to_lammps_real(ff)
    pos = read_data_file(converted / DATA_NAME).unwrapped()[: aa.n_atoms]
    is_h = aa.is_hydrogen()
    nbr = aa.neighbors()
    for (a, b), t in zip(aa.bonds, aa.bond_types, strict=True):
        if is_h[a] or is_h[b]:
            assert np.linalg.norm(pos[a] - pos[b]) == pytest.approx(real["bond"][t]["r0"], abs=2e-5)
    for (a, j, b), t in zip(aa.angles, aa.angle_types, strict=True):
        if not (is_h[a] or is_h[b]):
            continue
        ang = float(G.angle_deg(pos[a], pos[j], pos[b]))
        th0 = real["angle"][t]["theta0"]
        assert abs(ang - th0) < 5.0
        heavy = [x for x in nbr[j] if not is_h[x]]
        if is_h[a] and is_h[b] and len(heavy) == 2:  # CH2: H-C-H set exactly
            assert ang == pytest.approx(th0, abs=1e-3)
        if len(heavy) == 1 and (is_h[a] != is_h[b]):  # CH3: H-C-C set exactly
            assert ang == pytest.approx(th0, abs=1e-3)


def test_shuffled_ids_images_and_velocities_give_same_output(ua_system, converted, tmp_path):
    """write_data-like input: shuffled atoms, shifted images, Velocities, no coefficients."""
    df = read_data_file(ua_system / DATA_NAME)
    lo, hi = df.box[0]
    length = hi - lo
    rng = np.random.default_rng(0)
    atoms = df.sorted_atoms()
    shift = rng.integers(-1, 2, size=(len(atoms), 3))
    atoms[:, 4:7] += shift * length  # same unwrapped position, other image
    atoms[:, 7:10] -= shift
    order = rng.permutation(len(atoms))
    text = ["LAMMPS data file via write_data, version test, timestep = 1000, units = real", ""]
    text += [f"{len(atoms)} atoms", f"{df.counts['atom types']} atom types"]
    text += [f"{df.counts['bonds']} bonds", f"{df.counts['bond types']} bond types", ""]
    text += [f"{float(lo)!r} {float(hi)!r} {ax}lo {ax}hi" for ax in "xyz"]
    text += ["", "Masses", ""] + [" ".join(r) for r in df.sections["Masses"]]
    text += ["", "Atoms # full", ""]
    for i in order:
        r = atoms[i]
        text.append(
            f"{int(r[0])} {int(r[1])} {int(r[2])} {r[3]} {float(r[4])!r} {float(r[5])!r} {float(r[6])!r} "
            f"{int(r[7])} {int(r[8])} {int(r[9])}"
        )
    text += ["", "Velocities", ""]
    text += [f"{int(atoms[i, 0])} 0.001 -0.002 0.003" for i in order]
    text += ["", "Bonds", ""] + [" ".join(r) for r in df.sections["Bonds"]]
    variant = tmp_path / "relaxed.data"
    variant.write_text("\n".join(text) + "\n")
    out = convert_ua_to_aa(variant, ua_system, tmp_path / "out")
    assert (out / DATA_NAME).read_bytes() == (converted / DATA_NAME).read_bytes()
    assert _strip(out / MANIFEST_NAME) == _strip(converted / MANIFEST_NAME)

    # Without image flags the chains are made whole by minimum image: same wrapped atoms.
    start = text.index("Atoms # full") + 2
    for k in range(start, start + len(atoms)):
        text[k] = " ".join(text[k].split()[:7])
    no_img = tmp_path / "noimg.data"
    no_img.write_text("\n".join(text) + "\n")
    out2 = convert_ua_to_aa(no_img, ua_system, tmp_path / "out2")
    a = read_data_file(out2 / DATA_NAME).sorted_atoms()
    b = read_data_file(converted / DATA_NAME).sorted_atoms()
    assert np.array_equal(a[:, :7], b[:, :7])


def test_conversion_is_deterministic(ua_system, converted, tmp_path):
    out = convert_ua_to_aa(ua_system / DATA_NAME, ua_system, tmp_path)
    assert (out / DATA_NAME).read_bytes() == (converted / DATA_NAME).read_bytes()
    assert _strip(out / MANIFEST_NAME, ("git",)) == _strip(converted / MANIFEST_NAME, ("git",))


def test_manifest_provenance(ua_system, converted):
    m = yaml.safe_load((converted / MANIFEST_NAME).read_text())
    assert m["id"] == f"ipp_aa_amorph_n{N_CHAINS}_c{N_CARBONS}_s5_from_ua"
    assert m["resolution"] == "aa" and m["seed"] == 5
    assert m["source"]["id"] == ua_system.name
    assert len(m["source"]["data_sha256"]) == 64 and len(m["source"]["manifest_sha256"]) == 64
    assert m["formula"]["per_chain"] == f"C{N_CARBONS}H{2 * N_CARBONS + 2}"
    assert m["density_g_cm3"] == pytest.approx(0.3, rel=1e-6)
    assert m["overlap_minima_angstrom"]["local"]["bonds"] == [4, 6]


@pytest.mark.parametrize(
    "edit",
    [
        lambda m: m.update(n_chains=m["n_chains"] + 1),
        lambda m: m.update(n_carbons=33),
        lambda m: m.update(polymer="pe"),
        lambda m: m.update(resolution="aa"),
        lambda m: m["type_ids"]["atom"].update(CH3=2, CH2=1),
    ],
    ids=["n_chains", "n_carbons", "polymer", "resolution", "type_ids"],
)
def test_mismatched_manifest_raises(ua_system, tmp_path, edit):
    src = tmp_path / "src"
    shutil.copytree(ua_system, src)
    m = yaml.safe_load((src / MANIFEST_NAME).read_text())
    edit(m)
    (src / MANIFEST_NAME).write_text(yaml.safe_dump(m, sort_keys=False))
    with pytest.raises(ConversionError):
        convert_ua_to_aa(ua_system / DATA_NAME, src, tmp_path / "out")


def test_pe_ua_converts_too(tmp_path):
    ua = build_amorphous("pe", "ua", 2, 12, 0.3, 1, tmp_path)
    out = convert_ua_to_aa(ua / DATA_NAME, ua, tmp_path)
    m = yaml.safe_load((out / MANIFEST_NAME).read_text())
    assert m["counts"]["per_chain"]["atoms"] == 3 * 12 + 2
    assert m["formula"]["per_chain"] == "C12H26"
    assert m["overlap_minima_angstrom"]["local"]["bonds"] is None


def test_direct_aa_ipp_growth_errors(tmp_path, capsys):
    with pytest.raises(DirectAAiPPError, match="ua2aa"):
        build_amorphous("ipp", "aa", 2, 12, 0.3, 1, tmp_path)
    argv = ["build", "amorphous", "--polymer", "ipp", "--res", "aa", "--out", str(tmp_path)]
    assert main(argv) == 1
    assert "sepsim build ua2aa" in capsys.readouterr().err
    assert not any(tmp_path.iterdir())


def test_cli_ua2aa_end_to_end(ua_system, converted, tmp_path, capsys):
    argv = ["build", "ua2aa", "--data", str(ua_system / DATA_NAME)]
    argv += ["--source", str(ua_system), "--out", str(tmp_path)]
    assert main(argv) == 0
    out = tmp_path / converted.name
    assert str(out) in capsys.readouterr().out
    assert (out / DATA_NAME).read_bytes() == (converted / DATA_NAME).read_bytes()


def test_cli_ua2aa_bad_source(ua_system, tmp_path, capsys):
    argv = ["build", "ua2aa", "--data", str(ua_system / DATA_NAME)]
    argv += ["--source", str(tmp_path), "--out", str(tmp_path / "o")]
    assert main(argv) == 1
    assert "manifest not found" in capsys.readouterr().err
