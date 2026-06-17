"""Shared pytest fixtures for the dongnae engine test suite.

The tests target the pure-Python core engine that lives in ``py-core/dongnae``.
We add that directory to ``sys.path`` so the suite runs from a clean checkout
without an editable install (``pip install ./py-core`` also works and is what CI
does). No runtime dependency is introduced — only pytest, a test-time dependency.
"""

import os
import sys

import pytest

_PY_CORE = os.path.join(os.path.dirname(__file__), "..", "py-core")
sys.path.insert(0, os.path.abspath(_PY_CORE))


# A tiny, hand-checked dataset. All nodes share latitude 36.0 so the engine's
# auto-calibrated coefficients are predictable: lat_coef == 111.0 and
# lon_coef == round(111 * cos(radians(36)), 2) == 89.8. With those, a 0.05 deg
# longitude step from the query at (36.0, 127.0) is 0.05 * 89.8 == 4.49 km.
#
#   id          name                       lat    lon      radius  boundary dist
#                                                                   from (36,127)
#   1000000000  ...강남구 역삼동           36.0   127.00   2.0     -2.0  (inside)
#   2000000000  ...서초구 서초동           36.0   127.05   0.1      4.39 (outside)
#   3000000000  ...송파구 잠실동           36.0   127.10   0.1      8.88 (outside)
SAMPLE_ROWS = [
    ("1000000000", "서울특별시 강남구 역삼동", 36.0, 127.00, 2.0),
    ("2000000000", "서울특별시 서초구 서초동", 36.0, 127.05, 0.1),
    ("3000000000", "서울특별시 송파구 잠실동", 36.0, 127.10, 0.1),
]

CSV_HEADER = "dnid,dnname,dnlatitude,dnlongitude,dnradius"


def rows_to_csv(rows=SAMPLE_ROWS):
    """Render dongnae rows as CSV text (no encoding applied yet)."""
    lines = [CSV_HEADER]
    for dnid, name, lat, lon, radius in rows:
        lines.append(f"{dnid},{name},{lat},{lon},{radius}")
    return "\n".join(lines) + "\n"


@pytest.fixture
def write_csv(tmp_path):
    """Return a helper that writes CSV text to a temp file in a given encoding.

    Usage: ``path = write_csv(text, encoding="cp949")``.
    """

    counter = {"n": 0}

    def _write(text, encoding="utf-8-sig", name=None):
        counter["n"] += 1
        filename = name or f"dongnae_{counter['n']}.csv"
        path = tmp_path / filename
        path.write_text(text, encoding=encoding)
        return str(path)

    return _write


@pytest.fixture
def sample_csv(write_csv):
    """A UTF-8-SIG sample CSV path with the three known nodes."""
    return write_csv(rows_to_csv())


@pytest.fixture
def engine(sample_csv):
    """A DongnaeEngine pre-loaded with the known sample dataset."""
    from dongnae import DongnaeEngine

    return DongnaeEngine(sample_csv)
