"""Tests for methine chirality and inversion counting."""

import numpy as np
import pytest

from sepsim.analysis.tacticity import count_inversions, methine_chirality

# Tetrahedral directions around a methine carbon: backbone prev/next, methyl, H.
PREV, NEXT, ME, H = (
    1.54 / np.sqrt(3) * np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], dtype=float)
)


def _methines(n, flipped=(), spacing=5.0):
    """n separated methine centres; ``flipped`` ones have methyl and H swapped."""
    pos, idx = [], []
    for k in range(n):
        c = np.array([k * spacing, 0.0, 0.0])
        me, h = (H, ME) if k in flipped else (ME, H)
        pos.extend([c, c + PREV, c + NEXT, c + me, c + h])
        idx.append(5 * k + np.arange(5))
    idx = np.array(idx)
    return np.array(pos), idx[:, 0], idx[:, 3], idx[:, 4], idx[:, 1], idx[:, 2]


def test_flipped_methyl_is_counted():
    pos, c, me, h, prev, nxt = _methines(6)
    ref = methine_chirality(pos, c, me, h, prev, nxt)
    assert np.all(ref == ref[0]) and ref[0] != 0
    pos2, *_ = _methines(6, flipped={2, 4})
    signs = methine_chirality(pos2, c, me, h, prev, nxt)
    assert signs.tolist() == [ref[0], ref[0], -ref[0], ref[0], -ref[0], ref[0]]
    assert count_inversions(signs, ref) == 2
    assert count_inversions(ref, ref) == 0


def test_chirality_uses_minimum_image():
    pos, c, me, h, prev, nxt = _methines(3)
    cell = [15.0, 20.0, 20.0]
    ref = methine_chirality(pos, c, me, h, prev, nxt, cell=cell)
    wrapped = np.mod(pos - [0.5, 0.0, 0.0], cell)  # splits the first centre across x = 0
    assert np.ptp(wrapped[:5, 0]) > 7.5  # really split
    np.testing.assert_array_equal(methine_chirality(wrapped, c, me, h, prev, nxt, cell=cell), ref)


def test_count_inversions_shape_check():
    with pytest.raises(ValueError):
        count_inversions([1, 1], [1, 1, 1])
