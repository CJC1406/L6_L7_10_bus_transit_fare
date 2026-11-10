
from bus_transit_fare import (
    process_commute_manifest,
    inspect_smartcard_turnstiles
)


def test_manifest_validation_branches():
    # Invalid manifest type
    try:
        process_commute_manifest("invalid", 0)
        assert False
    except ValueError:
        pass

    # Negative booking fee
    try:
        process_commute_manifest([], -1)
        assert False
    except ValueError:
        pass


def test_route_active_branches():
    manifests = [
        {"route_active": False, "route_type": "local", "commuters": []},
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 1, "type": "regular"}]
        }
    ]
    result = process_commute_manifest(manifests, 0)
    assert result["total_fare"] == 3.5


def test_route_type_branches():
    for route_type, expected in [
        ("express", 7.0),
        ("shuttle", 5.0),
        ("local", 3.5),
        ("unknown", 0.0)
    ]:
        result = process_commute_manifest(
            [{
                "route_active": True,
                "route_type": route_type,
                "commuters": [{"zones": 1, "type": "regular"}]
            }],
            0
        )
        assert result["total_fare"] == expected


def test_passenger_type_branches():
    manifests = [{
        "route_active": True,
        "route_type": "local",
        "commuters": [
            {"zones": 1, "type": "student"},
            {"zones": 1, "type": "senior"},
            {"zones": 1, "type": "regular"}
        ]
    }]
    result = process_commute_manifest(manifests, 0)
    assert result["total_fare"] == 7.1


def test_zone_and_blacklist_branches():
    manifests = [{
        "route_active": True,
        "route_type": "local",
        "commuters": [
            {"zones": 0, "type": "regular"},
            {"zones": 1, "type": "regular", "blacklisted": True},
            {"zones": 1, "type": "regular"}
        ]
    }]
    result = process_commute_manifest(manifests, 0)
    assert result["total_fare"] == 3.5


def test_express_blacklist_branch():
    manifests = [{
        "route_active": True,
        "route_type": "express",
        "commuters": [
            {"zones": 1, "type": "regular"},
            {"zones": 1, "blacklisted": True},
            {"zones": 1, "type": "student"}
        ]
    }]
    result = process_commute_manifest(manifests, 0)
    assert result["total_fare"] == 0.0


def test_priority_boarding_branches():
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "priority_boarding": True,
            "commuters": [{"zones": 1, "type": "regular"}]
        },
        {
            "route_active": True,
            "route_type": "local",
            "priority_boarding": False,
            "commuters": [{"zones": 1, "type": "regular"}]
        }
    ]
    result = process_commute_manifest(manifests, 2)
    assert result["total_fare"] == 9.0


def test_final_status_branches():
    # Audit rejected
    manifests = [
        {"route_active": True, "route_type": "unknown", "commuters": []}
        for _ in range(5)
    ]
    assert process_commute_manifest(manifests, 0)["status"] == "AUDIT_REJECTED"

    # Zero ridership
    assert process_commute_manifest([], 0)["status"] == "ZERO_RIDERSHIP"

    # Completed
    manifests = [{
        "route_active": True,
        "route_type": "local",
        "commuters": [{"zones": 1, "type": "regular"}]
    }]
    assert process_commute_manifest(manifests, 0)["status"] == "COMPLETED"


def test_turnstile_branches():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"
    assert inspect_smartcard_turnstiles([[1, 4, 2, 5]]) == "OPERATIONAL"
    assert inspect_smartcard_turnstiles([[4, 5]]) == "TURNSTILE_JAM"
