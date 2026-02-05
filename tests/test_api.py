"""
Tests for the Mergington High School API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    # Store initial state
    initial_state = {
        name: {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": details["participants"].copy()
        }
        for name, details in activities.items()
    }
    
    yield
    
    # Restore initial state
    for name, details in initial_state.items():
        activities[name]["participants"] = details["participants"].copy()


def test_root_redirect(client):
    """Test that root redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_for_activity(client, reset_activities):
    """Test signing up for an activity"""
    email = "test@mergington.edu"
    activity_name = "Chess Club"
    
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verify participant was added
    assert email in activities[activity_name]["participants"]


def test_signup_already_registered(client, reset_activities):
    """Test signing up when already registered"""
    email = "michael@mergington.edu"  # Already in Chess Club
    activity_name = "Chess Club"
    
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"].lower()


def test_signup_nonexistent_activity(client, reset_activities):
    """Test signing up for a non-existent activity"""
    email = "test@mergington.edu"
    activity_name = "Nonexistent Activity"
    
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_unregister_participant(client, reset_activities):
    """Test unregistering a participant from an activity"""
    email = "michael@mergington.edu"  # Already in Chess Club
    activity_name = "Chess Club"
    
    # Verify participant exists
    assert email in activities[activity_name]["participants"]
    
    response = client.post(
        f"/activities/{activity_name}/unregister",
        json={"email": email},
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    
    # Verify participant was removed
    assert email not in activities[activity_name]["participants"]


def test_unregister_nonexistent_participant(client, reset_activities):
    """Test unregistering a participant who is not enrolled"""
    email = "notregistered@mergington.edu"
    activity_name = "Chess Club"
    
    response = client.post(
        f"/activities/{activity_name}/unregister",
        json={"email": email},
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_unregister_nonexistent_activity(client, reset_activities):
    """Test unregistering from a non-existent activity"""
    email = "test@mergington.edu"
    activity_name = "Nonexistent Activity"
    
    response = client.post(
        f"/activities/{activity_name}/unregister",
        json={"email": email},
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_signup_and_unregister_workflow(client, reset_activities):
    """Test complete workflow: signup then unregister"""
    email = "workflow@mergington.edu"
    activity_name = "Programming Class"
    
    # Sign up
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    
    # Unregister
    response = client.post(
        f"/activities/{activity_name}/unregister",
        json={"email": email},
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_activities_have_correct_structure(client):
    """Test that all activities have the correct data structure"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    for activity_name, activity_details in data.items():
        assert "description" in activity_details
        assert "schedule" in activity_details
        assert "max_participants" in activity_details
        assert "participants" in activity_details
        assert isinstance(activity_details["participants"], list)
        assert isinstance(activity_details["max_participants"], int)
        assert activity_details["max_participants"] > 0
