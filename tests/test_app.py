from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    original_participants = list(activities[activity_name]["participants"])

    try:
        response = client.delete(
            f"/activities/{quote(activity_name)}/participants/{quote(email)}"
        )

        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants


def test_unregister_participant_returns_404_for_missing_email():
    activity_name = "Soccer Team"
    email = "missing@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )

    assert response.status_code == 404
