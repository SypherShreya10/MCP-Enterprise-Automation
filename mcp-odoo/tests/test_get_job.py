from tools.hr import get_job


def test_get_job():
    print("=" * 70)
    print("Testing get_job tool")
    print("=" * 70)

    # --------------------------------------------------
    # Test 1: List ALL job roles
    # --------------------------------------------------
    print("\nTest 1: List all job roles")
    jobs = get_job(limit=100)

    print(f"Found {len(jobs)} job(s)")
    for job in jobs:
        print(
            f"  - ID={job['id']}, "
            f"Name={job['name']}, "
            f"Department={job.get('department_id')}"
        )

    print("  ✅ PASS")

    # --------------------------------------------------
    # Test 2: Search by job name
    # --------------------------------------------------
    print("\nTest 2: Search by job name")
    result = get_job(name="a", limit=50)

    for job in result:
        print(f"  - {job['name']}")

    print("  ✅ PASS")

    # --------------------------------------------------
    # Test 3: Dynamic job_id lookup
    # --------------------------------------------------
    print("\nTest 3: Search by job_id")
    if jobs:
        job_id = jobs[-1]["id"]
        result = get_job(job_id=job_id)

        assert len(result) == 1
        print(f"  Found job: {result[0]['name']}")
        print("  ✅ PASS")

    # --------------------------------------------------
    # Test 4: Field safety
    # --------------------------------------------------
    print("\nTest 4: Forbidden fields check")
    forbidden = {"salary", "wage", "company_salary"}

    for job in jobs:
        for f in forbidden:
            assert f not in job

    print("  ✅ PASS")

    # --------------------------------------------------
    # Test 5: Invalid limit
    # --------------------------------------------------
    print("\nTest 5: Invalid limit")
    try:
        get_job(limit=0)
        assert False
    except ValueError:
        print("  Correctly rejected invalid limit")
        print("  ✅ PASS")

    print("\n✅ ALL get_job TESTS PASSED")


if __name__ == "__main__":
    test_get_job()
