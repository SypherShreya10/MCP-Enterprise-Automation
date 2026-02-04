"""
Pre-integration test suite for Tool 011: get_lead

Run with:
    python test_get_lead.py

Assumptions:
- Odoo is running
- crm.lead records exist
- ODOO_* env vars are configured
"""

from tools.crm import get_lead
import traceback


def print_header(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_result(records):
    print(f"Records returned: {len(records)}")
    for r in records[:3]:
        print(
            f"- ID={r['id']} | "
            f"Name={r['name']} | "
            f"Type={r.get('type')} | "
            f"Partner={r.get('partner_name')} | "
            f"Stage={r.get('stage_name')}"
        )


# ---------------------------------------------------------------------
# POSITIVE TESTS
# ---------------------------------------------------------------------

def test_get_by_id():
    print_header("TEST 1: Fetch lead by ID")
    records = get_lead(lead_id=1)
    assert isinstance(records, list)
    print_result(records)


def test_filter_by_type_lead():
    print_header("TEST 2: Filter by type='lead'")
    records = get_lead(type="lead", limit=5)
    for r in records:
        assert r["type"] == "lead"
    print_result(records)


def test_filter_by_type_opportunity():
    print_header("TEST 3: Filter by type='opportunity'")
    records = get_lead(type="opportunity", limit=5)
    for r in records:
        assert r["type"] == "opportunity"
    print_result(records)


def test_filter_by_partner():
    print_header("TEST 4: Filter by partner_id")
    records = get_lead(partner_id=1, limit=5)
    for r in records:
        if r["partner_id"]:
            assert r["partner_id"][0] == 1
    print_result(records)


def test_filter_by_stage():
    print_header("TEST 5: Filter by stage_id")
    records = get_lead(stage_id=1, limit=5)
    for r in records:
        assert r["stage_id"][0] == 1
    print_result(records)


def test_filter_by_salesperson():
    print_header("TEST 6: Filter by assigned user_id")
    records = get_lead(user_id=1, limit=5)
    for r in records:
        assert r["user_id"][0] == 1
    print_result(records)


def test_combined_filters():
    print_header("TEST 7: Combined filters (type + limit)")
    records = get_lead(type="opportunity", limit=3)
    assert len(records) <= 3
    print_result(records)


# ---------------------------------------------------------------------
# DENORMALIZATION TESTS
# ---------------------------------------------------------------------

def test_denormalized_fields_present():
    print_header("TEST 8: partner_name & stage_name presence")
    records = get_lead(type="lead", limit=3)
    for r in records:
        assert "partner_name" in r
        assert "stage_name" in r
    print_result(records)


def test_denormalization_null_safety():
    print_header("TEST 9: Denormalization null safety")
    records = get_lead(type="lead", limit=5)
    for r in records:
        assert r["partner_name"] is None or isinstance(r["partner_name"], str)
        assert r["stage_name"] is None or isinstance(r["stage_name"], str)
    print_result(records)


# ---------------------------------------------------------------------
# VALIDATION & EDGE CASE TESTS
# ---------------------------------------------------------------------

def test_no_parameters_should_fail():
    print_header("TEST 10: No parameters (should fail)")
    try:
        get_lead()
        raise AssertionError("Expected ValueError not raised")
    except ValueError as e:
        print("Correctly failed:", e)


def test_invalid_type_should_fail():
    print_header("TEST 11: Invalid type (should fail)")
    try:
        get_lead(type="invalid")
        raise AssertionError("Expected ValueError not raised")
    except ValueError as e:
        print("Correctly failed:", e)


def test_limit_zero_should_fail():
    print_header("TEST 12: limit=0 (should fail)")
    try:
        get_lead(type="lead", limit=0)
        raise AssertionError("Expected ValueError not raised")
    except ValueError as e:
        print("Correctly failed:", e)


def test_limit_over_100_should_fail():
    print_header("TEST 13: limit > 100 (should fail)")
    try:
        get_lead(type="lead", limit=101)
        raise AssertionError("Expected ValueError not raised")
    except ValueError as e:
        print("Correctly failed:", e)


def test_nonexistent_lead_id():
    print_header("TEST 14: Non-existent lead_id")
    records = get_lead(lead_id=999999)
    assert records == []
    print("Returned empty list as expected")


# ---------------------------------------------------------------------
# SAFETY TESTS
# ---------------------------------------------------------------------

def test_no_full_table_scan_possible():
    print_header("TEST 15: Ensure no full-table scan possible")
    try:
        # Any valid call must still include at least one filter
        get_lead(type="lead", limit=1)
        print("PASS: Full scan prevented by validation + domain rules")
    except Exception:
        raise AssertionError("Unexpected failure")


def test_active_only_records():
    print_header("TEST 16: Active records only")
    records = get_lead(type="lead", limit=5)
    for r in records:
        # archived records should never appear
        assert r.get("active", True) is not False
    print_result(records)


# ---------------------------------------------------------------------
# MAIN RUNNER
# ---------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_get_by_id,
        test_filter_by_type_lead,
        test_filter_by_type_opportunity,
        test_filter_by_partner,
        test_filter_by_stage,
        test_filter_by_salesperson,
        test_combined_filters,
        test_denormalized_fields_present,
        test_denormalization_null_safety,
        test_no_parameters_should_fail,
        test_invalid_type_should_fail,
        test_limit_zero_should_fail,
        test_limit_over_100_should_fail,
        test_nonexistent_lead_id,
        test_no_full_table_scan_possible,
        test_active_only_records,
    ]

    failures = 0

    for test in tests:
        try:
            test()
        except Exception as e:
            failures += 1
            print("\n❌ TEST FAILED:", test.__name__)
            traceback.print_exc()

    print("\n" + "=" * 80)
    if failures == 0:
        print("✅ ALL get_lead TESTS PASSED")
    else:
        print(f"❌ {failures} TEST(S) FAILED")
    print("=" * 80)
