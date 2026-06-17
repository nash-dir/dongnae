"""ID lookup and boundary-distance calculation: get / howfar.

``get`` is an O(1) hash-map lookup keyed by ``dnid`` (string). ``howfar`` returns
the boundary distance from a coordinate to a node identified by id — negative
inside the node's radius, positive outside, and None when the id is unknown.
"""

import pytest

from dongnae import DongnaeEngine


# --- get -----------------------------------------------------------------


def test_get_returns_matching_node(engine):
    node = engine.get("1000000000")
    assert node["dnname"] == "서울특별시 강남구 역삼동"


def test_get_coerces_numeric_id_to_string(engine):
    # Ids are stored as strings; an int argument is coerced via str().
    assert engine.get(1000000000)["dnname"].endswith("역삼동")


def test_get_unknown_id_returns_none(engine):
    assert engine.get("0000000000") is None


def test_get_result_has_no_distance_or_score_keys(engine):
    node = engine.get("2000000000")
    assert "distance" not in node
    assert "score" not in node


# --- howfar --------------------------------------------------------------


def test_howfar_inside_boundary_is_negative(engine):
    # Query at 역삼동's centre; radius 2.0 -> boundary distance -2.0.
    assert engine.howfar(36.0, 127.0, "1000000000") == -2.0


def test_howfar_outside_boundary_is_positive(engine):
    # 서초동 (radius 0.1) is 4.49 km away from the query centre -> +4.39.
    assert engine.howfar(36.0, 127.0, "2000000000") == pytest.approx(4.39, abs=1e-4)


def test_howfar_unknown_id_returns_none(engine):
    assert engine.howfar(36.0, 127.0, "0000000000") is None


def test_howfar_matches_nearest_boundary_distance(engine):
    # howfar to a node must agree with the distance nearest() reports for it.
    nearest = {r["dnname"]: r["distance"] for r in engine.nearest(36.0, 127.0, k=3)}
    node = engine.get("2000000000")
    assert engine.howfar(36.0, 127.0, "2000000000") == pytest.approx(
        nearest[node["dnname"]], abs=1e-4
    )


def test_howfar_on_empty_engine_returns_none():
    assert DongnaeEngine().howfar(36.0, 127.0, "1000000000") is None
