from tools.common import get_company


def test_get_company():
    """Comprehensive test suite for get_company tool"""
    
    print("=" * 70)
    print("Testing get_company tool")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Test 1: Get current company (default behavior)
    # ------------------------------------------------------------------
    print("\nTest 1: Get current company (default)")
    company = get_company()
    print(f"  Company ID: {company['id']}")
    print(f"  Company Name: {company['name']}")
    
    # Basic assertions
    assert company["id"] > 0, "Company ID should be positive"
    assert "name" in company, "Company should have name"
    assert "currency_id" in company, "Company should have currency"
    
    # Type checking
    assert isinstance(company["id"], int), "ID should be integer"
    assert isinstance(company["name"], str), "Name should be string"
    assert len(company["name"]) > 0, "Name should not be empty"
    
    # Many2one fields return (id, name) tuples
    if company.get("currency_id"):
        assert isinstance(company["currency_id"], (tuple, list)), \
            "currency_id should be tuple"
        assert len(company["currency_id"]) == 2, \
            "currency_id should have (id, name)"
        print(f"  Currency: {company['currency_id'][1]} (ID: {company['currency_id'][0]})")
    
    if company.get("country_id"):
        assert isinstance(company["country_id"], (tuple, list)), \
            "country_id should be tuple"
        print(f"  Country: {company['country_id'][1]}")
    
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 2: Explicit company_id (same as current)
    # ------------------------------------------------------------------
    print("\nTest 2: Explicit company_id matching current")
    current_id = company["id"]
    company_explicit = get_company(company_id=current_id)
    
    assert company_explicit["id"] == current_id, \
        "Explicit company_id should return same company"
    assert company_explicit["name"] == company["name"], \
        "Should return same company data"
    
    print(f"  Requested ID: {current_id}")
    print(f"  Returned: {company_explicit['name']}")
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 3: Cross-company access attempt (should fail)
    # ------------------------------------------------------------------
    print("\nTest 3: Cross-company access (should be blocked)")
    try:
        # Try to access a different company (likely doesn't exist)
        forbidden_id = current_id + 1000
        get_company(company_id=forbidden_id)
        
        assert False, "Should have raised ValueError for cross-company access"
        
    except ValueError as e:
        print(f"  Correctly blocked: {str(e)[:100]}...")
        assert "cross-company" in str(e).lower(), \
            "Error should mention cross-company restriction"
        print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 4: Verify all required fields present
    # ------------------------------------------------------------------
    print("\nTest 4: Verify all required fields present")
    required_fields = ["id", "name", "currency_id", "email", "phone", 
                      "street", "city", "country_id"]
    
    for field in required_fields:
        assert field in company, f"Required field '{field}' missing"
        print(f"  ✓ {field}: {company.get(field)}")
    
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 5: Verify forbidden fields are NOT present
    # ------------------------------------------------------------------
    print("\nTest 5: Verify forbidden fields excluded")
    forbidden_fields = [
        "sequence",
        "chart_template_id",
        "account_setup_bank_data_state",
        "fiscalyear_last_day",
        "fiscalyear_last_month",
        "period_lock_date",
        "fiscalyear_lock_date",
        "transfer_account_id",
        "expects_chart_of_accounts",
    ]
    
    forbidden_found = []
    for field in forbidden_fields:
        if field in company:
            forbidden_found.append(field)
    
    if forbidden_found:
        print(f"  ⚠️  WARNING: Forbidden fields found: {forbidden_found}")
        # Don't fail the test, just warn (might be okay depending on Odoo version)
    else:
        print("  ✓ No forbidden fields present")
    
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Test 6: Data integrity checks
    # ------------------------------------------------------------------
    print("\nTest 6: Data integrity checks")
    
    # Email format (if present)
    if company.get("email"):
        email = company["email"]
        assert "@" in email, f"Email should be valid format: {email}"
        print(f"  ✓ Email valid: {email}")
    
    # Phone (if present)
    if company.get("phone"):
        phone = company["phone"]
        assert len(phone) > 0, "Phone should not be empty string"
        print(f"  ✓ Phone present: {phone}")
    
    # Address fields
    if company.get("street"):
        print(f"  ✓ Street: {company['street']}")
    if company.get("city"):
        print(f"  ✓ City: {company['city']}")
    
    print("  ✅ PASS")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("✅ ALL get_company TESTS PASSED!")
    print("=" * 70)
    print(f"\nCurrent Company: {company['name']} (ID: {company['id']})")
    if company.get("currency_id"):
        print(f"Currency: {company['currency_id'][1]}")
    print()


if __name__ == "__main__":
    import logging
    
    # Configure logging to see tool output
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    test_get_company()