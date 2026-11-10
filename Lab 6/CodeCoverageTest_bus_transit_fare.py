
import pytest

from bus_transit_fare import (
    process_commute_manifest,
    inspect_smartcard_turnstiles
)


# 1. Invalid input: manifests must be a list
def test_invalid_manifests():
    with pytest.raises(ValueError):
        process_commute_manifest("invalid", 0)


# 2. Invalid input: booking fee cannot be negative
def test_negative_booking_fee():
    with pytest.raises(ValueError):
        process_commute_manifest([], -1)


# 3. Empty manifest list
def test_zero_ridership():
    result = process_commute_manifest([], 0)
    assert result == {
        "total_fare": 0.0,
        "status": "ZERO_RIDERSHIP"
    }


# 4. Inactive route should be ignored
def test_inactive_route():
    manifests = [
        {
            "route_active": False,
            "route_type": "local",
            "commuters": [{"zones": 2, "type": "regular"}]
        }
    ]
    result = process_commute_manifest(manifests, 0)
    assert result["total_fare"] == 0.0
    assert result["status"] == "ZERO_RIDERSHIP"


# 5. Test all supported route types
def test_all_route_types():
    manifests = [
        {
            "route_active": True,
            "route_type": "express",
            "commuters": [{"zones": 2, "type": "regular"}]
        },
        {
            "route_active": True,
            "route_type": "shuttle",
            "commuters": [{"zones": 2, "type": "regular"}]
        },
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 2, "type": "regular"}]
        }
    ]
    result = process_commute_manifest(manifests, 0)
    assert result["total_fare"] == 18.5
    assert result["status"] == "COMPLETED"


# 6. Unsupported route type
def test_unknown_route():
    manifests = [
        {
            "route_active": True,
            "route_type": "unknown",
            "commuters": []
        }
    ]
    result = process_commute_manifest(manifests, 0)
    assert result["status"] == "ZERO_RIDERSHIP"


# 7. Test student, senior and regular passenger fares
def test_passenger_categories():
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [
                {"zones": 2, "type": "student"},
                {"zones": 2, "type": "senior"},
                {"zones": 2, "type": "regular"}
            ]
        }
    ]
    result = process_commute_manifest(manifests, 0)
    assert result["total_fare"] == 8.7
    assert result["status"] == "COMPLETED"


# 8. Invalid zones
def test_invalid_zones():
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 0, "type": "regular"}]
        }
    ]
    result = process_commute_manifest(manifests, 0)
    assert result["status"] == "ZERO_RIDERSHIP"


# 9. Blacklisted passenger on local route
def test_blacklisted_local_passenger():
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 2, "blacklisted": True}]
        }
    ]
    result = process_commute_manifest(manifests, 0)
    assert result["status"] == "ZERO_RIDERSHIP"


# 10. Blacklisted passenger on express route
def test_blacklisted_express_passenger():
    manifests = [
        {
            "route_active": True,
            "route_type": "express",
            "commuters": [
                {"zones": 2, "type": "regular"},
                {"zones": 2, "blacklisted": True},
                {"zones": 2, "type": "student"}
            ]
        }
    ]
    result = process_commute_manifest(manifests, 0)
    assert result["total_fare"] == 0.0
    assert result["status"] == "ZERO_RIDERSHIP"


# 11. Priority boarding fee
def test_priority_boarding():
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "priority_boarding": True,
            "commuters": [{"zones": 2, "type": "regular"}]
        }
    ]
    result = process_commute_manifest(manifests, 5)
    assert result["total_fare"] == 9.5


# 12. More than four rejected rides
def test_audit_rejection():
    manifests = [
        {
            "route_active": True,
            "route_type": "unknown",
            "commuters": []
        }
        for _ in range(5)
    ]
    result = process_commute_manifest(manifests, 0)
    assert result["status"] == "AUDIT_REJECTED"


# 13. Empty turnstile data
def test_turnstile_no_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


# 14. Turnstile operating normally
def test_turnstile_operational():
    matrix = [
        [1, 4, 2, 5, 1],
        [0, 1, 2]
    ]
    assert inspect_smartcard_turnstiles(matrix) == "OPERATIONAL"


# 15. Consecutive turnstile failures
def test_turnstile_jam():
    matrix = [
        [4, 5, 1],
        [0, 1, 2]
    ]
    assert inspect_smartcard_turnstiles(matrix) == "TURNSTILE_JAM"
