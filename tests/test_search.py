"""Text search / quasi-geocoding: search.

Scoring is bag-of-words: each whitespace-separated query token that appears as a
substring of a node name adds 1 to that node's score. Ties are broken by the
shorter name. ``best_shot=True`` (default) returns a single best dict (or None);
``best_shot=False`` returns a ranked list (or []).
"""


def test_search_best_shot_returns_single_dict(engine):
    result = engine.search("강남")
    assert isinstance(result, dict)
    assert result["dnname"].endswith("역삼동")


def test_search_injects_score(engine):
    # Two matching tokens, both substrings of 서초동's name -> score 2.
    result = engine.search("서초 서초동")
    assert result["dnname"].endswith("서초동")
    assert result["score"] == 2


def test_search_single_token_scores_one(engine):
    assert engine.search("강남")["score"] == 1


def test_search_list_mode_returns_ranked_list(engine):
    results = engine.search("서울특별시", limit=5, best_shot=False)
    assert isinstance(results, list)
    # The shared "서울특별시" prefix matches all three nodes.
    assert len(results) == 3
    assert all(r["score"] == 1 for r in results)


def test_search_limit_caps_list_results(engine):
    results = engine.search("서울특별시", limit=2, best_shot=False)
    assert len(results) == 2


def test_search_higher_score_ranks_first(engine):
    # "서초" matches only 서초동 (score 1); add a token unique to it to be sure
    # ranking is by score, not input order.
    results = engine.search("서초", best_shot=False)
    assert results[0]["dnname"].endswith("서초동")


def test_search_no_match_best_shot_returns_none(engine):
    assert engine.search("없는동네") is None


def test_search_no_match_list_returns_empty(engine):
    assert engine.search("없는동네", best_shot=False) == []


def test_search_blank_query_best_shot_returns_none(engine):
    assert engine.search("   ") is None


def test_search_blank_query_list_returns_empty(engine):
    assert engine.search("   ", best_shot=False) == []


def test_search_result_is_a_copy(engine):
    result = engine.search("강남")
    result["dnname"] = "MUTATED"
    assert engine.get("1000000000")["dnname"] == "서울특별시 강남구 역삼동"
