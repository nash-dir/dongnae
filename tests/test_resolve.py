"""Soft geofencing: resolve.

``resolve`` returns the nodes whose effective radius (optionally inflated by a
tolerance ``threshold``) contains the query point. A node matches when its
boundary distance ``<= radius * (threshold - 1.0)``:

* threshold 1.0  -> strict: point must be within the node's true radius.
* threshold 1.2  -> 20% buffer around the node.

Each match carries a ``score`` of ``centre_distance / (radius * threshold)``
(<= 1.0 inside the tolerance zone), and matches are sorted ascending by score.
"""

import pytest


def test_resolve_strict_threshold_matches_enclosing_node(engine):
    matches = engine.resolve(36.0, 127.0, threshold=1.0)
    assert [m["dnname"][-3:] for m in matches] == ["역삼동"]


def test_resolve_match_carries_score_and_distance(engine):
    match = engine.resolve(36.0, 127.0, threshold=1.0)[0]
    assert "score" in match
    assert "distance" in match
    # Query at the exact centre -> centre distance 0 -> score 0.0.
    assert match["score"] == 0.0
    assert match["distance"] == -2.0


def test_resolve_score_reflects_offset_from_centre(engine):
    # 0.01 deg lon east of 역삼동 centre: centre distance 0.898 km, radius 2.0,
    # threshold 1.2 -> score 0.898 / (2.0 * 1.2) == 0.37.
    match = engine.resolve(36.0, 127.01, threshold=1.2)[0]
    assert match["dnname"].endswith("역삼동")
    assert match["score"] == pytest.approx(0.37, abs=0.01)


def test_resolve_outside_radius_returns_no_match(engine):
    # (36.0, 127.03) sits ~2.7 km from 역삼동's centre (radius 2.0) and ~1.8 km
    # from 서초동's centre (radius 0.1): outside every node's strict radius.
    matches = engine.resolve(36.0, 127.03, threshold=1.0)
    assert matches == []


def test_resolve_threshold_widens_match_set(engine):
    # Far enough out that the strict check fails but a generous buffer passes.
    strict = engine.resolve(36.0, 127.028, threshold=1.0)
    loose = engine.resolve(36.0, 127.028, threshold=1.6)
    assert len(loose) >= len(strict)


def test_resolve_sorted_by_score_ascending(engine):
    # An exaggerated threshold pulls in both 역삼동 and 서초동 so there is more
    # than one match to order; scores must come back ascending.
    matches = engine.resolve(36.0, 127.0, threshold=50.0)
    assert len(matches) >= 2
    scores = [m["score"] for m in matches]
    assert scores == sorted(scores)


def test_resolve_on_empty_engine_returns_empty():
    from dongnae import DongnaeEngine

    assert DongnaeEngine().resolve(36.0, 127.0) == []
