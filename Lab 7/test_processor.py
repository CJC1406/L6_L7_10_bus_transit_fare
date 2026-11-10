
from hypothesis import given, strategies as st

from processor import (
    parse_transit_corridor,
    lookup_concession_discount,
    compute_passenger_density
)


# Test 1: Corridor parser
@given(st.one_of(st.text(), st.none()))
def test_parse_transit_corridor_safe(s):
    try:
        result = parse_transit_corridor(s)
        assert isinstance(result, str)
    except ValueError:
        pass


# Test 2: Concession discount lookup
@given(st.one_of(st.text(), st.none()))
def test_lookup_concession_discount_safe(s):
    try:
        result = lookup_concession_discount(s)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
    except ValueError:
        pass


# Test 3: Passenger density calculation
@given(st.one_of(st.text(), st.none()))
def test_compute_passenger_density_safe(s):
    try:
        result = compute_passenger_density(s)
        assert isinstance(result, float)
        assert result >= 0
    except ValueError:
        pass


# Test valid corridor inputs
@given(
    st.text(
        alphabet=st.characters(
            whitelist_categories=("Lu", "Ll")
        ),
        min_size=1,
        max_size=5
    ),
    st.text(
        alphabet=st.characters(
            whitelist_categories=("Lu", "Ll")
        ),
        min_size=1,
        max_size=5
    ),
    st.integers(min_value=1, max_value=100)
)
def test_valid_corridor(orig, dest, zones):
    result = parse_transit_corridor(f"{orig}-{dest}-{zones}")
    assert isinstance(result, str)


# Test valid concession categories
@given(st.sampled_from([
    "STANDARD", "STUDENT", "SENIOR", "MILITARY", "CHILD"
]))
def test_valid_concession_categories(category):
    result = lookup_concession_discount(category)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


# Test valid passenger density inputs
@given(
    st.floats(min_value=0, max_value=100000, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0.01, max_value=100000, allow_nan=False, allow_infinity=False)
)
def test_valid_passenger_density(passengers, km):
    result = compute_passenger_density(f"{passengers}/{km}")
    assert isinstance(result, float)
    assert result >= 0
