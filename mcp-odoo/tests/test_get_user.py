from tools.common import get_user


def test_get_user():
    """Test suite for get_user tool"""

    # Test 1: Get user by ID
    result = get_user(user_id=2)
    print(f"Test 1 - By ID: {result}")
    assert len(result) > 0
    assert result[0]["id"] == 2

    # Test 2: Get user by login (exact match)
    result = get_user(login="shreyamkhatavkar@gmail.com")
    print(f"Test 2 - By Login: {result}")
    assert len(result) > 0

    # Test 3: Search by name (partial, case-insensitive)
    result = get_user(name="admin")
    print(f"Test 3 - By Name: {result}")
    assert len(result) > 0

    # Test 4: No parameters - should raise ValueError
    try:
        get_user()
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"Test 4 - No params (PASS): {e}")

    # Test 5: Invalid limit - should raise ValueError
    try:
        get_user(name="test", limit=500)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"Test 5 - Invalid limit (PASS): {e}")

    # Test 6: Non-existent user - should return empty list
    result = get_user(user_id=999999)
    print(f"Test 6 - Non-existent: {result}")
    assert result == []

    # Test 7: Verify no forbidden fields returned
    result = get_user(user_id=2)
    if result:
        assert "password" not in result[0]
        assert "api_key" not in result[0]
        assert "groups_id" not in result[0]
        print("Test 7 - No forbidden fields (PASS)")

    # Test 8: Limit enforcement
    result = get_user(name="Admin", limit=1)
    print(f"Test 8 - Limit: {len(result)} record(s)")
    assert len(result) <= 1

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    test_get_user()
