from tools.hr import get_department


def test_get_department():
    print("=" * 70)
    print("Testing get_department tool")
    print("=" * 70)

    # --------------------------------------------------
    # Test 1: List ALL departments (full visibility)
    # --------------------------------------------------
    print("\nTest 1: List all departments")
    departments = get_department(limit=100)

    print(f"Found {len(departments)} department(s)")
    for dept in departments:
        print(
            f"  - ID={dept['id']}, "
            f"Name={dept['name']}, "
            f"Manager={dept.get('manager_id')}, "
            f"Parent={dept.get('parent_id')}"
        )

    assert isinstance(departments, list)
    print("  ✅ PASS")

    # --------------------------------------------------
    # Test 2: Search by department name (partial)
    # --------------------------------------------------
    print("\nTest 2: Search by name (partial match)")
    result = get_department(name="a", limit=50)

    print(f"Found {len(result)} matching departments")
    for d in result:
        print(f"  - {d['name']}")

    print("  ✅ PASS")

    # --------------------------------------------------
    # Test 3: Search by department_id (dynamic)
    # --------------------------------------------------
    print("\nTest 3: Search by department_id")
    if departments:
        dept_id = departments[0]["id"]
        result = get_department(department_id=dept_id)

        assert len(result) == 1
        print(f"  Found department: {result[0]['name']}")
        print("  ✅ PASS")
    else:
        print("  No departments available to test ID lookup")

    # --------------------------------------------------
    # Test 4: Verify allowed fields ONLY
    # --------------------------------------------------
    print("\nTest 4: Verify no forbidden fields")
    forbidden = {"private_email", "create_uid", "write_uid"}

    for dept in departments:
        for f in forbidden:
            assert f not in dept

    print("  ✅ PASS")

    # --------------------------------------------------
    # Test 5: Invalid limit
    # --------------------------------------------------
    print("\nTest 5: Invalid limit")
    try:
        get_department(limit=1000)
        assert False
    except ValueError:
        print("  Correctly rejected invalid limit")
        print("  ✅ PASS")

    print("\n✅ ALL get_department TESTS PASSED")


if __name__ == "__main__":
    test_get_department()
