"""
Pre-integration tests for Tool 013: get_stage
"""

from tools.crm import get_stage
from odoo_client import OdooClient
import traceback

client = OdooClient()


def print_header(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

def test_list_all_stages():
    print_header("TEST 1: List all stages")

    stages = get_stage(limit=50)
    assert isinstance(stages, list)
    assert len(stages) > 0

    for s in stages[:3]:
        assert "id" in s
        assert "name" in s
        assert "sequence" in s
        assert "is_won" in s
        assert "fold" in s

    print(f"PASS: Retrieved {len(stages)} stages")


def test_filter_by_stage_id():
    print_header("TEST 2: Filter by stage_id")

    stages = get_stage(limit=1)
    stage_id = stages[0]["id"]

    result = get_stage(stage_id=stage_id)
    assert len(result) == 1
    assert result[0]["id"] == stage_id

    print("PASS:", result[0])


def test_filter_by_name():
    print_header("TEST 3: Filter by name")

    result = get_stage(name="Won")
    assert isinstance(result, list)

    for s in result:
        assert "won" in s["name"].lower()

    print(f"PASS: Found {len(result)} matching stages")


def test_filter_by_is_won_true():
    print_header("TEST 4: Filter by is_won=True")

    result = get_stage(is_won=True)
    assert isinstance(result, list)
    assert len(result) > 0

    for s in result:
        assert s["is_won"] is True

    print("PASS: All returned stages are won stages")


def test_filter_by_is_won_false():
    print_header("TEST 5: Filter by is_won=False")

    result = get_stage(is_won=False)
    assert isinstance(result, list)

    for s in result:
        assert s["is_won"] is False

    print("PASS: All returned stages are non-won stages")


def test_combined_filters():
    print_header("TEST 6: Combined filters (name + is_won)")

    result = get_stage(name="Won", is_won=True)
    for s in result:
        assert s["is_won"] is True
        assert "won" in s["name"].lower()

    print("PASS:", result)


def test_limit_enforced():
    print_header("TEST 7: Limit enforcement")

    result = get_stage(limit=2)
    assert len(result) <= 2

    print("PASS: Limit respected")


def test_invalid_limit_low():
    print_header("TEST 8: Invalid limit (low)")

    try:
        get_stage(limit=0)
        raise AssertionError("Expected ValueError not raised")
    except ValueError as e:
        print("Correctly failed:", e)


def test_invalid_limit_high():
    print_header("TEST 9: Invalid limit (high)")

    try:
        get_stage(limit=500)
        raise AssertionError("Expected ValueError not raised")
    except ValueError as e:
        print("Correctly failed:", e)


# ------------------------------------------------------------------
# RUNNER
# ------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_list_all_stages,
        test_filter_by_stage_id,
        test_filter_by_name,
        test_filter_by_is_won_true,
        test_filter_by_is_won_false,
        test_combined_filters,
        test_limit_enforced,
        test_invalid_limit_low,
        test_invalid_limit_high,
    ]

    failures = 0

    for test in tests:
        try:
            test()
        except Exception:
            failures += 1
            print("\n❌ TEST FAILED:", test.__name__)
            traceback.print_exc()

    print("\n" + "=" * 80)
    if failures == 0:
        print("✅ ALL get_stage TESTS PASSED")
    else:
        print(f"❌ {failures} TEST(S) FAILED")
    print("=" * 80)
