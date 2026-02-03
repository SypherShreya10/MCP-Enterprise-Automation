"""
Pre-integration tests for Tool 012: update_lead_stage
"""

from tools.crm import update_lead_stage
from odoo_client import OdooClient
import traceback

client = OdooClient()


def print_header(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def get_any_active_lead():
    leads = client.search_read(
        model="crm.lead",
        domain=[("active", "=", True)],
        fields=["id", "stage_id"],
        limit=1,
    )
    return leads[0] if leads else None


def get_any_stage(exclude_stage_id=None):
    domain = []
    if exclude_stage_id:
        domain.append(("id", "!=", exclude_stage_id))

    stages = client.search_read(
        model="crm.stage",
        domain=domain,
        fields=["id", "name"],
        limit=1,
        apply_company_scope=False,
    )
    return stages[0] if stages else None


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

def test_successful_stage_update():
    print_header("TEST 1: Successful stage update")

    lead = get_any_active_lead()
    assert lead is not None

    new_stage = get_any_stage(exclude_stage_id=lead["stage_id"][0])

    result = update_lead_stage(
        lead_id=lead["id"],
        stage_id=new_stage["id"],
    )

    assert result["lead_id"] == lead["id"]
    assert result["new_stage_id"] == new_stage["id"]
    print("PASS:", result)


def test_nonexistent_lead():
    print_header("TEST 2: Non-existent lead")

    try:
        update_lead_stage(
            lead_id=999999,
            stage_id=1,
        )
        raise AssertionError("Expected failure not raised")
    except ValueError as e:
        print("Correctly failed:", e)


def test_nonexistent_stage():
    print_header("TEST 3: Non-existent stage")

    lead = get_any_active_lead()
    assert lead is not None

    try:
        update_lead_stage(
            lead_id=lead["id"],
            stage_id=999999,
        )
        raise AssertionError("Expected failure not raised")
    except ValueError as e:
        print("Correctly failed:", e)


def test_invalid_lead_id_type():
    print_header("TEST 4: Invalid lead_id type")

    try:
        update_lead_stage(
            lead_id="abc",  # invalid
            stage_id=1,
        )
        raise AssertionError("Expected failure not raised")
    except ValueError as e:
        print("Correctly failed:", e)


def test_invalid_stage_id_type():
    print_header("TEST 5: Invalid stage_id type")

    try:
        update_lead_stage(
            lead_id=1,
            stage_id="xyz",  # invalid
        )
        raise AssertionError("Expected failure not raised")
    except ValueError as e:
        print("Correctly failed:", e)

def test_archived_lead_cannot_be_updated():
    print_header("TEST: Archived lead cannot be updated")

    archived = client.search_read(
        model="crm.lead",
        domain=[("active", "=", False)],
        fields=["id"],
        limit=1,
    )

    if not archived:
        print("SKIP: No archived leads found")
        return

    try:
        update_lead_stage(
            lead_id=archived[0]["id"],
            stage_id=1,
        )
        raise AssertionError("Archived lead update should have failed")
    except ValueError as e:
        print("Correctly blocked archived lead:", e)

def test_update_to_same_stage_is_allowed():
    print_header("TEST: Updating to same stage (no-op)")

    lead = get_any_active_lead()
    assert lead is not None

    current_stage_id = lead["stage_id"][0]

    result = update_lead_stage(
        lead_id=lead["id"],
        stage_id=current_stage_id,
    )

    assert result["old_stage_id"] == result["new_stage_id"]
    print("PASS: Same-stage update allowed:", result)


# ------------------------------------------------------------------
# RUNNER
# ------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_successful_stage_update,
        test_nonexistent_lead,
        test_nonexistent_stage,
        test_invalid_lead_id_type,
        test_invalid_stage_id_type,
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
        print("✅ ALL update_lead_stage TESTS PASSED")
    else:
        print(f"❌ {failures} TEST(S) FAILED")
    print("=" * 80)
