import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self):
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        # Check structure of first activity
        first_activity = next(iter(data.values()))
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Signed up {email} for {activity}" in data["message"]

        # Verify participant was added
        resp = client.get("/activities")
        activities = resp.json()
        assert email in activities[activity]["participants"]

    def test_signup_duplicate(self):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self):
        # Arrange
        activity = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_empty_email(self):
        # Arrange
        activity = "Chess Club"
        email = ""

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200  # Backend doesn't validate email format
        data = response.json()
        assert "message" in data

    def test_signup_special_characters(self):
        # Arrange
        activity = "Programming Class"
        email = "test+special@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_success(self):
        # Arrange
        activity = "Programming Class"
        email = "emma@mergington.edu"  # Already signed up

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Unregistered {email} from {activity}" in data["message"]

        # Verify participant was removed
        resp = client.get("/activities")
        activities = resp.json()
        assert email not in activities[activity]["participants"]

    def test_unregister_not_signed_up(self):
        # Arrange
        activity = "Programming Class"
        email = "notsignedup@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity(self):
        # Arrange
        activity = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_empty_email(self):
        # Arrange
        activity = "Gym Class"
        email = ""

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400  # Should fail since empty email not in participants
        data = response.json()
        assert "detail" in data