from fastapi.testclient import TestClient

from app import app, activities

client = TestClient(app)


def test_signup_duplicate_and_unregister():
    activity_name = "Soccer Club"
    email = "newstudent@mergington.edu"

    activities[activity_name]["participants"] = []

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]

    duplicate = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert duplicate.status_code == 400

    remove = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert remove.status_code == 200
    assert email not in activities[activity_name]["participants"]
