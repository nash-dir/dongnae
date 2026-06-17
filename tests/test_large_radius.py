"""Regression tests: the bbox pre-filter must not miss large-radius nodes.

The candidate pre-filter is a bounding box sized from the search range plus a
buffer. If that buffer is a fixed constant (the old 5 km), any node whose radius
exceeds it can be silently dropped from `where` / `nearest` / `within` /
`resolve` even when the query point lies deep inside it — while `howfar` (a
direct id lookup, not bbox-filtered) still reports the point as inside. That
disagreement is the bug these tests pin down. The buffer must instead track the
dataset's largest radius.

Fixture (all at latitude 36.0 -> lon_coef 89.8):

    id  name        lat    lon      radius   boundary dist from (36.0, 127.2)
    9   큰동네      36.0   127.00   30.0     17.96 - 30 = -12.04  (deep inside)
    1   작은동네    36.0   127.20    0.1      0.00 -  0.1 =  -0.10  (just inside)

The query sits 0.2 deg (~17.96 km) east of 큰동네's centre — outside the old
15 km bbox, but well within its 30 km radius.
"""

import pytest

from dongnae import DongnaeEngine

from conftest import rows_to_csv

LARGE_RADIUS_ROWS = [
    ("9", "큰동네", 36.0, 127.00, 30.0),
    ("1", "작은동네", 36.0, 127.20, 0.1),
]

QUERY = (36.0, 127.2)


@pytest.fixture
def big_engine(write_csv):
    path = write_csv(rows_to_csv(LARGE_RADIUS_ROWS), encoding="utf-8")
    return DongnaeEngine(path)


def test_max_radius_is_tracked(big_engine):
    assert big_engine._max_radius == 30.0


def test_where_returns_the_enclosing_large_node(big_engine):
    # By boundary distance the big node (-12.04) beats the small one (-0.10),
    # so reverse geocoding must return it, not the nearer-by-centre small node.
    assert big_engine.where(*QUERY)["dnname"] == "큰동네"


def test_nearest_includes_large_node_first(big_engine):
    names = [r["dnname"] for r in big_engine.nearest(*QUERY, k=2)]
    assert names == ["큰동네", "작은동네"]


def test_within_includes_large_node(big_engine):
    names = [r["dnname"] for r in big_engine.within(*QUERY, radius_km=5.0)]
    assert "큰동네" in names


def test_resolve_includes_large_node(big_engine):
    names = [r["dnname"] for r in big_engine.resolve(*QUERY, threshold=1.0)]
    assert "큰동네" in names


def test_where_and_howfar_agree_on_enclosing_node(big_engine):
    # The core consistency contract: if howfar says we are inside a node, the
    # spatial queries must be able to surface that same node.
    where_id = big_engine.where(*QUERY)["dnid"]
    assert big_engine.howfar(*QUERY, "9") < 0  # inside 큰동네
    assert where_id == "9"
