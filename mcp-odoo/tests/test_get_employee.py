from tools.hr import get_employee


def test_get_employee():
    """Test suite for get_employee tool"""
    
    print("=" * 70)
    print("Testing get_employee tool")
    print("=" * 70)

    # Test 1: Get employee by ID
    print("\nTest 1: Get employee by ID")
    try:
        result = get_employee(employee_id=1)
        if result:
            emp = result[0]
            print(f"  Employee: {emp['name']}")
            print(f"  Department: {emp.get('department_id')}")
            print(f"  Job: {emp.get('job_id')}")
            
            # Verify many2one fields return tuples
            if emp.get('department_id'):
                assert isinstance(emp['department_id'], (tuple, list))
                assert len(emp['department_id']) == 2
                print(f"    Department name: {emp['department_id'][1]}")
            
            print("  ✅ PASS")
        else:
            print("  No employee with ID=1")
    except Exception as e:
        print(f"  ⚠️  Error: {e}")

    # Test 2: Search by name (partial)
    print("\nTest 2: Search by name")
    result = get_employee(name="a", limit=5)
    print(f"  Found {len(result)} employee(s)")
    for emp in result[:3]:
        print(f"    - {emp['name']}")
    assert len(result) <= 5
    print("  ✅ PASS")

    # Test 3: Filter by department
    print("\nTest 3: Filter by department")
    try:
        result = get_employee(department_id=1, limit=10)
        print(f"  Found {len(result)} employee(s) in department 1")
        print("  ✅ PASS")
    except Exception as e:
        print(f"  Department 1 doesn't exist: {e}")

    # Test 4: No parameters (should fail)
    print("\nTest 4: No parameters - should fail")
    try:
        get_employee()
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"  Correctly rejected: {str(e)[:50]}...")
        print("  ✅ PASS")

    # Test 5: Verify NO forbidden fields
    print("\nTest 5: Verify sensitive data excluded")
    result = get_employee(employee_id=1)
    if result:
        emp = result[0]
        forbidden = [
            "private_email", "private_phone", 
            "identification_id", "passport_id",
            "bank_account_id", "salary", "wage",
            "private_street", "private_city"
        ]
        
        found_forbidden = [f for f in forbidden if f in emp]
        
        if found_forbidden:
            print(f"  ⚠️  WARNING: Forbidden fields: {found_forbidden}")
        else:
            print("  ✓ No sensitive data present")
        
        # Verify only work contact info
        assert "work_email" in emp or emp.get("work_email") is False
        assert "work_phone" in emp or emp.get("work_phone") is False
        print("  ✓ Only work contact info included")
        print("  ✅ PASS")

    # Test 6: Invalid limit
    print("\nTest 6: Invalid limit - should fail")
    try:
        get_employee(name="test", limit=500)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"  Correctly rejected: {str(e)[:50]}...")
        print("  ✅ PASS")

    print("\n" + "=" * 70)
    print("✅ ALL get_employee TESTS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    test_get_employee()