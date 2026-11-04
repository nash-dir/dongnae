"""Sanity checks on the CSV shipped in dongnae-kr, loaded by the real engine."""

from pathlib import Path

import pytest

from dongnae import DongnaeEngine

DATA_DIR = Path(__file__).resolve().parent.parent / "py-data-kr" / "dongnae_kr" / "data"


@pytest.fixture(scope="module")
def nodes():
    (csv_path,) = DATA_DIR.glob("*.csv")
    return DongnaeEngine(str(csv_path))._dongnaes


def test_ids_are_unique_ten_digit_codes(nodes):
    ids = [n["dnid"] for n in nodes]
    assert len(ids) > 20000
    assert len(set(ids)) == len(ids)
    assert all(len(i) == 10 and i.isdigit() for i in ids)


def test_no_abolished_jeonbuk_codes(nodes):
    # Code 45 became 52 in 2024; keeping both duplicates every Jeonbuk node.
    assert not [n for n in nodes if n["dnid"].startswith("45")]


def test_stray_fragment_nodes_have_sane_radii(nodes):
    # These read 50 km+ when a shifted source fragment leaked into the radius.
    radii = {n["dnid"]: n["dnradius"] for n in nodes}
    for dnid in ("4885025021", "4885025000", "4885036022", "4689034023", "5213015000"):
        assert radii[dnid] < 15, dnid


def test_coordinates_are_inside_south_korea(nodes):
    assert all(33 < n["dnlatitude"] < 39 and 124 < n["dnlongitude"] < 132 for n in nodes)
