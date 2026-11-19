from hypothesis import given, example, strategies as st
import pytest
from photo_print_order import parse_order, file_size_average, payable_amount


# ---------------- parse_order ----------------
@given(st.text() | st.none())
@example("")
@example(None)
@example("4x6")
@example("4x6:abc")
@example("4x6:25:3")
def test_parse_order_no_crash(s):
    try:
        parse_order(s)
    except Exception as e:
        assert False, f"parse_order crashed with: {e!r}"


@given(st.text().filter(lambda s: ":" not in s))
def test_parse_order_rejects_missing_colon(s):
    assert parse_order(s) is None


@given(st.from_regex(r"[A-Za-z0-9]{1,6}", fullmatch=True),
       st.integers(min_value=0, max_value=10**6))
def test_parse_order_valid_input(size, copies):
    assert parse_order(f"{size}:{copies}") == (size.upper(), copies)


@given(st.from_regex(r"[A-Za-z0-9]{1,6}", fullmatch=True),
       st.integers(min_value=-10**6, max_value=-1))
def test_parse_order_rejects_negative_copies(size, copies):
    assert parse_order(f"{size}:{copies}") is None


# ---------------- file_size_average ----------------
@given(st.text() | st.none())
@example("")
@example(None)
@example("1,,3")
@example("a,b")
@example(",")
def test_file_size_average_no_crash(s):
    try:
        file_size_average(s)
    except Exception as e:
        assert False, f"file_size_average crashed with: {e!r}"


@given(st.lists(st.integers(min_value=0, max_value=10**6), min_size=1))
def test_file_size_average_valid_input(values):
    result = file_size_average(",".join(str(v) for v in values))
    assert result == sum(values) // len(values)
    assert min(values) <= result <= max(values)


@given(st.lists(st.integers(min_value=-10**6, max_value=-1), min_size=1))
def test_file_size_average_rejects_negative(values):
    assert file_size_average(",".join(str(v) for v in values)) is None


# ---------------- payable_amount ----------------
@given(st.text() | st.none())
@example("")
@example(None)
@example("450")
@example("450|50|10")
@example("nan|0")
@example("inf|0")
def test_payable_amount_no_crash(s):
    try:
        payable_amount(s)
    except Exception as e:
        assert False, f"payable_amount crashed with: {e!r}"


@pytest.mark.parametrize("text", ["nan|0", "inf|0", "1|nan", "1|inf", "-inf|0", "1e999|0"])
def test_payable_amount_rejects_non_finite(text):
    assert payable_amount(text) is None


@given(st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False))
def test_payable_amount_valid_input(amount, discount):
    result = payable_amount(f"{amount!r}|{discount!r}")
    assert result is not None
    assert result >= 0
    assert result == pytest.approx(max(amount * 1.18 - discount, 0))


@given(st.floats(min_value=-1e6, max_value=-1e-6, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0, max_value=1e6, allow_nan=False, allow_infinity=False))
def test_payable_amount_rejects_negative_amount(amount, discount):
    assert payable_amount(f"{amount!r}|{discount!r}") is None