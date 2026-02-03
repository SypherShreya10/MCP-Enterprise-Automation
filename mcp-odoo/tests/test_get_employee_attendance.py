from datetime import date
from tools.hr import get_employee_attendance


def test_get_employee_attendance():
    print("=" * 70)
    print("Testing get_employee_attendance tool")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Test 1: Fetch all attendance records
    # ------------------------------------------------------------------
    print("\nTest 1: Fetch all attendance records")
    records = get_employee_attendance(limit=50)

    print(f"Found {len(records)} record(s)")
    for rec in records[:5]:
        print(rec)

    assert isinstance(records, list)
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 2: Filter by employee
    # ------------------------------------------------------------------
    print("\nTest 2: Filter by employee_id")
    records = get_employee_attendance(employee_id=1, limit=20)

    for rec in records:
        assert rec["employee_id"][0] == 1

    print(f"Found {len(records)} record(s)")
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 3: Filter by date
    # ------------------------------------------------------------------
    print("\nTest 3: Filter by date")
    records = get_employee_attendance(
        date_filter="2024-01-15",
        limit=20,
    )

    for rec in records:
        assert rec["check_in"].startswith("2024-01-15")

    print(f"Found {len(records)} record(s)")
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 4: Employee + date filter
    # ------------------------------------------------------------------
    print("\nTest 4: Employee + date filter")
    records = get_employee_attendance(
        employee_id=1,
        date_filter="2024-01-15",
        limit=20,
    )

    for rec in records:
        assert rec["employee_id"][0] == 1
        assert rec["check_in"].startswith("2024-01-15")

    print(f"Found {len(records)} record(s)")
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 5: Date object input
    # ------------------------------------------------------------------
    print("\nTest 5: Date object input")
    records = get_employee_attendance(
        date_filter=date.today(),
        limit=10,
    )

    assert isinstance(records, list)
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 6: Invalid date format
    # ------------------------------------------------------------------
    print("\nTest 6: Invalid date format")
    try:
        get_employee_attendance(date_filter="15-01-2024")
        assert False, "Expected ValueError"
    except ValueError as e:
        print(f"  Correctly rejected: {e}")
        print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 7: Invalid limit
    # ------------------------------------------------------------------
    print("\nTest 7: Invalid limit")
    try:
        get_employee_attendance(limit=500)
        assert False, "Expected ValueError"
    except ValueError as e:
        print(f"  Correctly rejected: {e}")
        print("  ✅ PASS")

    print("\n" + "=" * 70)
    print("✅ ALL get_employee_attendance TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    test_get_employee_attendance()
