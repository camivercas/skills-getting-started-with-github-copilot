import pytest
from httpx import AsyncClient, ASGITransport

from src.app import app, activities


@pytest.mark.asyncio
async def test_get_activities():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Expect activities to be a dict and contain known keys from in-memory data
    assert isinstance(data, dict)
    assert "Chess Club" in data


@pytest.mark.asyncio
async def test_signup_and_unregister():
    activity_name = "Chess Club"
    test_email = "tester@mergington.edu"

    # Ensure not present
    if test_email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(test_email)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Signup
        resp = await ac.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert resp.status_code == 200
        assert test_email in activities[activity_name]["participants"]

        # Signup again should fail (already registered)
        resp2 = await ac.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert resp2.status_code == 400

        # Unregister
        resp3 = await ac.post(f"/activities/{activity_name}/unregister?email={test_email}")
        assert resp3.status_code == 200
        assert test_email not in activities[activity_name]["participants"]

        # Unregister again should fail
        resp4 = await ac.post(f"/activities/{activity_name}/unregister?email={test_email}")
        assert resp4.status_code == 400
