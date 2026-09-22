import copy

import pytest
from fastapi.testclient import TestClient

from app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_list_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "participants" in response.json()["Chess Club"]


def test_signup_activity():
    activity_name = "Soccer Club"
    email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate():
    activity_name = "Soccer Club"
    email = "newstudent@mergington.edu"

    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    duplicate = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Student already signed up for this activity"


def test_signup_unknown_activity():
    response = client.post(
        "/activities/Unknown Club/signup", params={"email": "student@example.com"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_activity():
    activity_name = "Soccer Club"
    email = "newstudent@mergington.edu"

    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    response = client.delete(
        f"/activities/{activity_name}/unregister", params={"email": email}
    )

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_nonparticipant():
    response = client.delete(
        "/activities/Soccer Club/unregister",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_unknown_activity():
    response = client.delete(
        "/activities/Unknown Club/unregister",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"
