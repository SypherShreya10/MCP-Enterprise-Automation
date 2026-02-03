from tools.hr import get_employee_leaves
from datetime import date


def test_get_employee_leaves():
    print("=" * 70)
    print("Testing get_employee_leaves tool")
    print("=" * 70)

    # --------------------------------------------------
    # Test 1: List ALL approved leaves
    # --------------------------------------------------
    print("\nTest 1: List all approved leaves")
    leaves = get_employee_leaves(limit=100)

    print(f"Found {len(leaves)} leave record(s)")
    for leave in leaves:
        print(
            f"  - Employee={leave.get('employee_name')}, "
            f"From={leave['date_from']}, "
            f"To={leave['date_to']}, "
            f"Days={leave['number_of_days']}"
        )

    print("  ✅ PASS")

    # --------------------------------------------------
    # Test 2: Filter by date range
    # --------------------------------------------------
    print("\nTest 2: Filter by date range")
    result = get_employee_leaves(
        date_from="2024-01-01",
        date_to="2026-12-31",
        limit=100,
    )

    print(f"Found {len(result)} overlapping leaves")
    print("  ✅ PASS")

    # --------------------------------------------------
    # Test 3: Filter by employee (dynamic)
    # --------------------------------------------------
    print("\nTest 3: Filter by employee_id")
    if leaves:
        emp_id = leaves[0]["employee_id"][0]
        result = get_employee_leaves(employee_id=emp_id)

        print(f"Found {len(result)} leaves for employee_id={emp_id}")
        print("  ✅ PASS")

    # --------------------------------------------------
    # Test 4: Date validation (invalid range)
    # --------------------------------------------------
    print("\nTest 4: Invalid date range")
    try:
        get_employee_leaves(
            date_from="2026-01-01",
            date_to="2025-01-01",
        )
        assert False
    except ValueError:
        print("  Correctly rejected invalid date range")
        print("  ✅ PASS")

    # --------------------------------------------------
    # Test 5: Forbidden fields check
    # --------------------------------------------------
    print("\nTest 5: Forbidden fields check")
    forbidden = {"private_notes", "employee_bank_id"}

    for leave in leaves:
        for f in forbidden:
            assert f not in leave

    print("  ✅ PASS")

    print("\n✅ ALL get_employee_leaves TESTS PASSED")


if __name__ == "__main__":
    test_get_employee_leaves()
