import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_activity_data(reset_activities):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_participant(reset_activities):
    activity_name = "Soccer Team"
    email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate_email(reset_activities):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_404(reset_activities):
    activity_name = "Not Real Club"
    email = "student@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_email_from_activity(reset_activities):
    activity_name = "Soccer Team"
    email = "newstudent@mergington.edu"
    activities[activity_name]["participants"].append(email)

    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_participant_returns_404_for_missing_email(reset_activities):
    activity_name = "Soccer Team"
    email = "missing@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
