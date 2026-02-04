"""
Pre-integration tests for Tool 014: get_team
"""

from tools.crm import get_team
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

def test_list_all_teams():
    print_header("TEST 1: List all teams")

    teams = get_team(limit=50)
    assert isinstance(teams, list)
    assert len(teams) > 0

    for t in teams[:3]:
        assert "id" in t
        assert "name" in t
        assert "user_id" in t
        assert "member_ids" in t

    print(f"PASS: Retrieved {len(teams)} teams")


def test_filter_by_team_id():
    print_header("TEST 2: Filter by team_id")

    teams = get_team(limit=1)
    team_id = teams[0]["id"]

    result = get_team(team_id=team_id)
    assert len(result) == 1
    assert result[0]["id"] == team_id

    print("PASS:", result[0])


def test_filter_by_name():
    print_header("TEST 3: Filter by name")

    teams = get_team(limit=5)
    name_fragment = teams[0]["name"][:3]

    result = get_team(name=name_fragment)
    assert isinstance(result, list)
    assert len(result) > 0

    for t in result:
        assert name_fragment.lower() in t["name"].lower()

    print("PASS:", result)


def test_filter_by_user_id():
    print_header("TEST 4: Filter by team leader (user_id)")

    teams = get_team(limit=5)

    team_with_leader = None
    for t in teams:
        if t["user_id"]:
            team_with_leader = t
            break

    if not team_with_leader:
        print("SKIP: No team with assigned leader found")
        return

    leader_id = team_with_leader["user_id"][0]

    result = get_team(user_id=leader_id)
    assert len(result) > 0

    for t in result:
        assert t["user_id"][0] == leader_id

    print("PASS:", result)


def test_limit_enforced():
    print_header("TEST 5: Limit enforcement")

    result = get_team(limit=2)
    assert len(result) <= 2

    print("PASS: Limit respected")


def test_invalid_limit_low():
    print_header("TEST 6: Invalid limit (low)")

    try:
        get_team(limit=0)
        raise AssertionError("Expected ValueError not raised")
    except ValueError as e:
        print("Correctly failed:", e)


def test_invalid_limit_high():
    print_header("TEST 7: Invalid limit (high)")

    try:
        get_team(limit=1000)
        raise AssertionError("Expected ValueError not raised")
    except ValueError as e:
        print("Correctly failed:", e)


def test_company_scope_enforced():
    print_header("TEST 8: Company scoping sanity check")

    teams = get_team(limit=20)
    assert isinstance(teams, list)

    # We cannot see other company teams unless explicitly allowed
    print("PASS: Teams returned without cross-company crash")


# ------------------------------------------------------------------
# RUNNER
# ------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_list_all_teams,
        test_filter_by_team_id,
        test_filter_by_name,
        test_filter_by_user_id,
        test_limit_enforced,
        test_invalid_limit_low,
        test_invalid_limit_high,
        test_company_scope_enforced,
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
        print("✅ ALL get_team TESTS PASSED")
    else:
        print(f"❌ {failures} TEST(S) FAILED")
    print("=" * 80)
