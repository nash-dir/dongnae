"""Loading, encoding auto-detection fallback, and coefficient calibration.

The engine tries encodings in the order ``utf-8-sig -> cp949 -> utf-8`` and
falls through on ``UnicodeDecodeError``, ``KeyError`` (missing columns), or
``ValueError`` (non-numeric coordinates). These tests pin both the happy paths
for each encoding and the boundary where every candidate encoding is exhausted.
"""

import math

import pytest

from dongnae import DongnaeEngine, __version__

from conftest import CSV_HEADER, rows_to_csv


def test_version_is_exposed():
    assert __version__ == "0.2.0"


def test_eager_load_via_constructor(sample_csv):
    eng = DongnaeEngine(sample_csv)
    assert len(eng._dongnaes) == 3


def test_lazy_load_via_method(sample_csv):
    eng = DongnaeEngine()
    # Before loading, defaults apply and there is no data.
    assert eng._lat_coef == 111.0
    assert eng._lon_coef == 88.8
    assert eng._dongnaes == []

    eng.load(sample_csv)
    assert len(eng._dongnaes) == 3


# --- Encoding auto-detection: each supported encoding round-trips correctly ---


@pytest.mark.parametrize("encoding", ["utf-8-sig", "utf-8", "cp949"])
def test_loads_each_supported_encoding_without_garbling(write_csv, encoding):
    path = write_csv(rows_to_csv(), encoding=encoding)
    eng = DongnaeEngine(path)

    # Korean names must survive the decode untouched, proving the right
    # encoding won (a wrong decode would mojibake the name, not raise).
    assert eng.get("1000000000")["dnname"] == "서울특별시 강남구 역삼동"
    assert len(eng._dongnaes) == 3


def test_utf8_sig_bom_does_not_leak_into_first_column(write_csv):
    # A UTF-8 BOM precedes the header; utf-8-sig must strip it so the first
    # column key is a clean "dnid" and the id index keys are unpolluted.
    path = write_csv(rows_to_csv(), encoding="utf-8-sig")
    eng = DongnaeEngine(path)

    assert "1000000000" in eng._id_map
    assert eng.get("1000000000") is not None


def test_cp949_falls_through_utf8_sig(write_csv):
    # cp949-encoded Korean bytes are not valid UTF-8, so utf-8-sig raises and
    # the engine must fall through to cp949 — the fallback boundary itself.
    path = write_csv(rows_to_csv(), encoding="cp949")
    eng = DongnaeEngine(path)

    assert eng.get("2000000000")["dnname"] == "서울특별시 서초구 서초동"


# --- Fallback exhaustion: every encoding fails -> ValueError ---


def test_missing_columns_with_data_row_exhausts_and_raises(write_csv):
    # Wrong header + a data row -> KeyError on row["dnid"] for every encoding.
    path = write_csv("id,name\n1,foo\n", encoding="utf-8")
    with pytest.raises(ValueError):
        DongnaeEngine(path)


def test_non_numeric_coordinate_exhausts_and_raises(write_csv):
    # Correct header but a non-numeric latitude -> float() ValueError everywhere.
    bad = "dnid,dnname,dnlatitude,dnlongitude,dnradius\n1,foo,not_a_number,127.0,1.0\n"
    path = write_csv(bad, encoding="utf-8")
    with pytest.raises(ValueError):
        DongnaeEngine(path)


def test_error_message_lists_attempted_encodings(write_csv):
    path = write_csv("id,name\n1,foo\n", encoding="utf-8")
    with pytest.raises(ValueError) as excinfo:
        DongnaeEngine(path)
    message = str(excinfo.value)
    assert "utf-8-sig" in message and "cp949" in message


def test_wrong_columns_raise_even_without_data_rows(write_csv):
    # A wrong header must fail consistently whether or not data rows follow:
    # the loader validates required columns from the header itself, so a
    # malformed schema never loads silently as an empty engine.
    path = write_csv("id,name\n", encoding="utf-8")
    with pytest.raises(ValueError):
        DongnaeEngine(path)


def test_correct_header_no_rows_loads_empty(write_csv):
    # A well-formed header with zero data rows is a legitimately empty dataset,
    # not an error.
    path = write_csv(CSV_HEADER + "\n", encoding="utf-8")
    eng = DongnaeEngine(path)
    assert eng._dongnaes == []
    assert eng.where(36.0, 127.0) is None


# --- Auto-calibration of equirectangular (planar) coefficients ---


def test_coefficients_calibrated_from_dataset_latitude(engine):
    # All sample nodes sit at latitude 36.0 -> avg_lat 36.0.
    assert engine._lat_coef == 111.0
    assert engine._lon_coef == round(111.0 * math.cos(math.radians(36.0)), 2)
    assert engine._lon_coef == 89.8


def test_coefficients_use_min_max_midpoint(write_csv):
    rows = [
        ("1", "A", 34.0, 127.0, 1.0),
        ("2", "B", 38.0, 127.0, 1.0),
    ]
    path = write_csv(rows_to_csv(rows), encoding="utf-8")
    eng = DongnaeEngine(path)
    # Midpoint of [34, 38] is 36.0.
    assert eng._lon_coef == round(111.0 * math.cos(math.radians(36.0)), 2)
