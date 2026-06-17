"""Reverse geocoding and radius search: where / nearest / within.

Distances are "boundary distances" (geometric distance to the node centre minus
the node's radius), rounded to 4 decimals. Negative means the query point sits
inside the node's effective radius. Expected values below are hand-checked
against the fixture in conftest.py.
"""

import pytest

from dongnae import DongnaeEngine


# --- where ---------------------------------------------------------------


def test_where_returns_nearest_node(engine):
    result = engine.where(36.0, 127.0)
    assert result["dnname"] == "서울특별시 강남구 역삼동"
    assert result["distance"] == -2.0


def test_where_returns_dict_with_distance_key(engine):
    result = engine.where(36.0, 127.0)
    assert isinstance(result, dict)
    assert "distance" in result


def test_where_on_empty_engine_returns_none():
    assert DongnaeEngine().where(36.0, 127.0) is None


def test_where_result_is_a_copy(engine):
    result = engine.where(36.0, 127.0)
    result["dnname"] = "MUTATED"
    # The engine's stored record must be untouched.
    assert engine.get("1000000000")["dnname"] == "서울특별시 강남구 역삼동"


# --- nearest -------------------------------------------------------------


def test_nearest_default_k_is_one(engine):
    results = engine.nearest(36.0, 127.0)
    assert len(results) == 1
    assert results[0]["dnname"].endswith("역삼동")


def test_nearest_orders_by_boundary_distance(engine):
    results = engine.nearest(36.0, 127.0, k=3)
    names = [r["dnname"][-3:] for r in results]
    assert names == ["역삼동", "서초동", "잠실동"]
    distances = [r["distance"] for r in results]
    assert distances == sorted(distances)


def test_nearest_distances_are_hand_checked(engine):
    results = engine.nearest(36.0, 127.0, k=3)
    by_name = {r["dnname"][-3:]: r["distance"] for r in results}
    assert by_name["역삼동"] == -2.0
    assert by_name["서초동"] == pytest.approx(4.39, abs=1e-4)
    assert by_name["잠실동"] == pytest.approx(8.88, abs=1e-4)


def test_nearest_k_limits_result_count(engine):
    assert len(engine.nearest(36.0, 127.0, k=2)) == 2


def test_nearest_distance_rounded_to_four_decimals(engine):
    # 0.05 deg lon * 89.8 == 4.49 km centre distance, minus 0.1 radius == 4.39.
    dist = engine.nearest(36.0, 127.0, k=3)[1]["distance"]
    assert round(dist, 4) == dist


def test_nearest_radius_km_filters_out_far_nodes(engine):
    # Only the node we sit inside has boundary distance <= 0.
    results = engine.nearest(36.0, 127.0, k=10, radius_km=0.0)
    assert [r["dnname"][-3:] for r in results] == ["역삼동"]


def test_nearest_does_not_mutate_stored_records(engine):
    engine.nearest(36.0, 127.0, k=3)
    assert "distance" not in engine.get("2000000000")


# --- within --------------------------------------------------------------


def test_within_returns_nodes_inside_radius(engine):
    results = engine.within(36.0, 127.0, radius_km=5.0)
    assert [r["dnname"][-3:] for r in results] == ["역삼동", "서초동"]


def test_within_excludes_nodes_beyond_radius(engine):
    # 잠실동 boundary distance is ~8.88 km, outside a 5 km query.
    names = [r["dnname"][-3:] for r in engine.within(36.0, 127.0, radius_km=5.0)]
    assert "잠실동" not in names


def test_within_limit_caps_results(engine):
    results = engine.within(36.0, 127.0, radius_km=100.0, limit=1)
    assert len(results) == 1
    # The single result is still the nearest.
    assert results[0]["dnname"].endswith("역삼동")


def test_within_tight_radius_returns_only_enclosing_node(engine):
    results = engine.within(36.0, 127.0, radius_km=0.0)
    assert [r["dnname"][-3:] for r in results] == ["역삼동"]
