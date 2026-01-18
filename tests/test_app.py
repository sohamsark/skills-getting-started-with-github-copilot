import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app

transport = ASGITransport(app=app)

@pytest.mark.asyncio
async def test_get_activities():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)

@pytest.mark.asyncio
async def test_signup_for_activity():
    test_email = "testuser@mergington.edu"
    activity = "Drama Club"
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post(f"/activities/{activity}/signup?email=remove_{test_email}")
        response = await ac.post(f"/activities/{activity}/signup?email={test_email}")
    assert response.status_code == 200
    assert f"Signed up {test_email} for {activity}" in response.text

@pytest.mark.asyncio
async def test_signup_duplicate():
    test_email = "duplicate@mergington.edu"
    activity = "Art Workshop"
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post(f"/activities/{activity}/signup?email={test_email}")
        response = await ac.post(f"/activities/{activity}/signup?email={test_email}")
    assert response.status_code == 400
    assert "already signed up" in response.text

@pytest.mark.asyncio
async def test_signup_full_activity():
    activity = "Math Olympiad"
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Sign up max participants
        for i in range(10):
            email = f"user{i}@mergington.edu"
            response = await ac.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        # Try to sign up one more
        response = await ac.post(f"/activities/{activity}/signup?email=extra@mergington.edu")
    assert response.status_code == 400
    assert "Activity is full" in response.text
