from datetime import date, timedelta
from tools.hr import check_employee_availability


def test_check_employee_availability():
    print("=" * 70)
    print("Testing check_employee_availability tool")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Test 1: Employee available for a future range
    # ------------------------------------------------------------------
    print("\nTest 1: Fully available employee")
    result = check_employee_availability(
        employee_id=1,
        date_from="2099-01-01",
        date_to="2099-01-05",
    )

    print(result)
    assert result["employee_id"] == 1
    assert result["total_days"] == 5
    assert result["available_days"] == 5
    assert result["unavailable_days"] == 0
    assert result["is_available"] is True
    assert result["conflicting_leaves"] == []
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 2: Employee unavailable due to approved leave
    # ------------------------------------------------------------------
    print("\nTest 2: Employee on approved leave")
    result = check_employee_availability(
        employee_id=1,
        date_from="2024-01-01",
        date_to="2024-01-10",
    )

    print(result)
    assert result["total_days"] >= result["unavailable_days"]
    assert result["available_days"] >= 0
    assert isinstance(result["conflicting_leaves"], list)
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 3: Partial overlap with leave
    # ------------------------------------------------------------------
    print("\nTest 3: Partial overlap with leave")
    result = check_employee_availability(
        employee_id=1,
        date_from="2024-01-05",
        date_to="2024-01-07",
    )

    print(result)
    assert result["total_days"] == 3
    assert result["available_days"] + result["unavailable_days"] == 3
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 4: Overlapping leaves should not double-count
    # ------------------------------------------------------------------
    print("\nTest 4: Overlapping leave handling")
    result = check_employee_availability(
        employee_id=1,
        date_from="2024-01-01",
        date_to="2024-01-31",
    )

    print(result)
    assert result["unavailable_days"] <= result["total_days"]
    assert isinstance(result["conflicting_leaves"], list)
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 5: Invalid date range
    # ------------------------------------------------------------------
    print("\nTest 5: Invalid date range (date_from > date_to)")
    try:
        check_employee_availability(
            employee_id=1,
            date_from="2024-02-01",
            date_to="2024-01-01",
        )
        assert False, "Expected ValueError"
    except ValueError as e:
        print(f"  Correctly rejected: {e}")
        print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 6: Non-existent employee
    # ------------------------------------------------------------------
    print("\nTest 6: Non-existent employee")
    try:
        check_employee_availability(
            employee_id=999999,
            date_from="2024-01-01",
            date_to="2024-01-02",
        )
        assert False, "Expected ValueError"
    except ValueError as e:
        print(f"  Correctly rejected: {e}")
        print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 7: Date object inputs
    # ------------------------------------------------------------------
    print("\nTest 7: Date object inputs")
    result = check_employee_availability(
        employee_id=1,
        date_from=date.today(),
        date_to=date.today() + timedelta(days=2),
    )

    print(result)
    assert isinstance(result["available_days"], int)
    print("  ✅ PASS")

    print("\n" + "=" * 70)
    print("✅ ALL check_employee_availability TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    test_check_employee_availability()
