import json
import pytest
from application import app  # Ensure your Flask app is importable

# Fixture to provide a test client.


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# --------------------------
# Tests for /meal_plan Route
# --------------------------


def test_meal_plan_template_rendering(client):
    """Verify that GET /meal_plan returns a page containing 'Meal Plan'."""
    response = client.get("/meal_plan")
    assert response.status_code == 200
    assert b"Meal Plan" in response.data


def test_meal_plan_contains_title(client):
    """Check that the rendered HTML from /meal_plan includes a <title>
    tag with 'Meal Plan'."""
    response = client.get("/meal_plan")
    assert response.status_code == 200
    # Adjust the assertion to check for a <title> tag and the phrase 'Meal Plan'
    assert b"<title>" in response.data
    assert b"Meal Plan" in response.data


def test_meal_plan_post_content_type(client):
    """Ensure that a POST request to /meal_plan returns HTML content."""
    response = client.post("/meal_plan")
    assert response.status_code == 200
    assert response.content_type.startswith("text/html")


def test_meal_plan_post_form(client):
    """Send POST form data to /meal_plan (even though it ignores data)
    and verify output."""
    response = client.post("/meal_plan", data={"dummy": "data"})
    assert response.status_code == 200
    assert b"Meal Plan" in response.data

# ------------------------------------
# Tests for /recommend_meal_plan Endpoint
# ------------------------------------


def test_recommend_meal_plan_endpoint_valid(client):
    """POST valid JSON to /recommend_meal_plan and check for a JSON list of meals."""
    payload = {
        "goal": "Maintenance",
        "calories": 2000,
        "protein": 100,
        "carbs": 250,
        "fat": 70
    }
    response = client.post("/recommend_meal_plan", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    for meal in data:
        assert "score" in meal
        assert "image_url" in meal


def test_recommend_meal_plan_endpoint_get(client):
    """Verify that a GET request to /recommend_meal_plan fails when provided
    with an empty JSON body."""
    # Expect that the GET call raises a ValueError because required keys are missing.
    with pytest.raises(ValueError):
        client.get(
            "/recommend_meal_plan",
            data=json.dumps({}),
            content_type="application/json"
        )


def test_recommend_meal_plan_missing_keys(client):
    """Omit required keys in the JSON payload and expect a ValueError."""
    payload = {
        "goal": "Maintenance",
        "calories": 2000
        # Missing protein, carbs, and fat
    }
    # Since the endpoint raises ValueError, we check for that.
    with pytest.raises(ValueError):
        client.post("/recommend_meal_plan", json=payload)


def test_recommend_meal_plan_extra_keys(client):
    """Include extra (unexpected) keys in the payload and verify the endpoint
    still returns 200."""
    payload = {
        "goal": "Maintenance",
        "calories": 2000,
        "protein": 100,
        "carbs": 250,
        "fat": 70,
        "extra": "unexpected"
    }
    response = client.post("/recommend_meal_plan", json=payload)
    assert response.status_code == 200


def test_recommend_meal_plan_zero_values(client):
    """Test with zero values for numeric inputs (if allowed) and expect a valid
    response."""
    payload = {
        "goal": "Weight Loss",
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0
    }
    response = client.post("/recommend_meal_plan", json=payload)
    assert response.status_code == 200


def test_recommend_meal_plan_non_json(client):
    """Test: Sending plain text (non‑JSON) to /recommend_meal_plan should raise
    an AttributeError."""
    with pytest.raises(AttributeError):
        client.post(
            "/recommend_meal_plan",
            data="plain text",
            content_type="text/plain"
        )


def test_recommend_meal_plan_malformed_json(client):
    """Test: Sending malformed JSON to /recommend_meal_plan should yield a 400
    error."""
    # Intentionally malformed JSON: missing quotes around Maintenance.
    malformed_data = (
        '{"goal": Maintenance, "calories": 2000, "protein": 100, "carbs": 250, '
        '"fat": 70}'
    )
    response = client.post(
        "/recommend_meal_plan",
        data=malformed_data,
        content_type="application/json"
    )
    # Update expected status code to 400.
    assert response.status_code == 400

# -------------------------------
# Tests for /bmi_advice Endpoint
# -------------------------------


def test_bmi_advice_not_logged_in(client):
    """Access /bmi_advice without a session to ensure a 401 error is returned."""
    response = client.get("/bmi_advice")
    assert response.status_code == 401
    data = response.get_json()
    assert data.get("error") == "User not logged in"


def test_bmi_advice_profile_not_found(client, monkeypatch):
    """Simulate a valid session but no profile found in the database."""
    fake_mongo = type(
        "FakeMongo",
        (),
        {
            "db": type(
                "FakeDB",
                (),
                {
                    "user": type(
                        "FakeCollection",
                        (),
                        {"find_one": lambda self, q: None}
                    )()
                }
            )()
        }
    )
    monkeypatch.setattr("application.mongo", fake_mongo)
    with client.session_transaction() as sess:
        sess["email"] = "nonexistent@example.com"
    response = client.get("/bmi_advice")
    assert response.status_code == 404
    data = response.get_json()
    assert data.get("error") == "Profile not found"


def test_bmi_advice_invalid_profile_data(client, monkeypatch):
    """Provide non-numeric weight and height to trigger a 400 error."""
    fake_profile = {
        "email": "test@example.com",
        "weight": "invalid",
        "height": "invalid"
    }
    fake_mongo = type(
        "FakeMongo",
        (),
        {
            "db": type(
                "FakeDB",
                (),
                {
                    "user": type(
                        "FakeCollection",
                        (),
                        {"find_one": lambda self, q: fake_profile}
                    )()
                }
            )()
        }
    )
    monkeypatch.setattr("application.mongo", fake_mongo)
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/bmi_advice")
    assert response.status_code == 400
    data = response.get_json()
    assert data.get("error") == "Invalid weight or height data"


def test_bmi_advice_normal_profile(client, monkeypatch):
    """Provide a profile with normal BMI and verify the advice includes 'normal'."""
    fake_profile = {"email": "test@example.com",
                    "weight": "70", "height": "175"}
    fake_mongo = type(
        "FakeMongo",
        (),
        {
            "db": type(
                "FakeDB",
                (),
                {
                    "user": type(
                        "FakeCollection",
                        (),
                        {"find_one": lambda self, q: fake_profile}
                    )()
                }
            )()
        }
    )
    monkeypatch.setattr("application.mongo", fake_mongo)
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/bmi_advice")
    assert response.status_code == 200
    data = response.get_json()
    bmi_expected = 70 / ((175 / 100) ** 2)
    assert abs(data.get("bmi") - bmi_expected) < 0.1
    assert "normal" in data.get("advice").lower()


def test_bmi_advice_underweight_profile(client, monkeypatch):
    """Provide a profile with underweight BMI and check that advice indicates
    underweight."""
    fake_profile = {"email": "test@example.com",
                    "weight": "50", "height": "175"}
    fake_mongo = type(
        "FakeMongo",
        (),
        {
            "db": type(
                "FakeDB",
                (),
                {
                    "user": type(
                        "FakeCollection",
                        (),
                        {"find_one": lambda self, q: fake_profile}
                    )()
                }
            )()
        }
    )
    monkeypatch.setattr("application.mongo", fake_mongo)
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/bmi_advice")
    data = response.get_json()
    assert response.status_code == 200
    assert data.get("bmi") < 18.5
    assert "underweight" in data.get("advice").lower()


def test_bmi_advice_overweight_profile(client, monkeypatch):
    """Provide a profile with overweight BMI and verify that the advice
    suggests weight loss."""
    fake_profile = {"email": "test@example.com",
                    "weight": "90", "height": "165"}
    fake_mongo = type(
        "FakeMongo",
        (),
        {
            "db": type(
                "FakeDB",
                (),
                {
                    "user": type(
                        "FakeCollection",
                        (),
                        {"find_one": lambda self, q: fake_profile}
                    )()
                }
            )()
        }
    )
    monkeypatch.setattr("application.mongo", fake_mongo)
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/bmi_advice")
    data = response.get_json()
    assert response.status_code == 200
    assert data.get("bmi") >= 25
    advice = data.get("advice").lower()
    assert "overweight" in advice or "deficit" in advice


def test_bmi_advice_json_structure(client, monkeypatch):
    """Ensure that a valid /bmi_advice response contains all expected keys."""
    fake_profile = {"email": "test@example.com",
                    "weight": "80", "height": "180"}
    fake_mongo = type(
        "FakeMongo",
        (),
        {
            "db": type(
                "FakeDB",
                (),
                {
                    "user": type(
                        "FakeCollection",
                        (),
                        {"find_one": lambda self, q: fake_profile}
                    )()
                }
            )()
        }
    )
    monkeypatch.setattr("application.mongo", fake_mongo)
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/bmi_advice")
    data = response.get_json()
    expected_keys = {
        "bmi",
        "weight",
        "height",
        "advice",
        "calorie_suggestion",
        "goal_suggestion",
        "reference_values",
    }
    assert expected_keys.issubset(set(data.keys()))


def test_bmi_advice_missing_weight(client, monkeypatch):
    """Provide a profile missing the weight field and expect a 400 error."""
    fake_profile = {"email": "test@example.com", "height": "170"}
    fake_mongo = type(
        "FakeMongo",
        (),
        {
            "db": type(
                "FakeDB",
                (),
                {
                    "user": type(
                        "FakeCollection",
                        (),
                        {"find_one": lambda self, q: fake_profile}
                    )()
                }
            )()
        }
    )
    monkeypatch.setattr("application.mongo", fake_mongo)
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/bmi_advice")
    assert response.status_code == 400


def test_bmi_advice_missing_height(client, monkeypatch):
    """Provide a profile missing the height field and expect a 400 error."""
    fake_profile = {"email": "test@example.com", "weight": "70"}
    fake_mongo = type(
        "FakeMongo",
        (),
        {
            "db": type(
                "FakeDB",
                (),
                {
                    "user": type(
                        "FakeCollection",
                        (),
                        {"find_one": lambda self, q: fake_profile}
                    )()
                }
            )()
        }
    )
    monkeypatch.setattr("application.mongo", fake_mongo)
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/bmi_advice")
    assert response.status_code == 400


def test_bmi_advice_reference_values(client, monkeypatch):
    """For a valid normal profile, verify that 'reference_values' contains
    expected keys."""
    fake_profile = {"email": "test@example.com",
                    "weight": "70", "height": "175"}
    fake_mongo = type(
        "FakeMongo",
        (),
        {
            "db": type(
                "FakeDB",
                (),
                {
                    "user": type(
                        "FakeCollection",
                        (),
                        {"find_one": lambda self, q: fake_profile}
                    )()
                }
            )()
        }
    )
    monkeypatch.setattr("application.mongo", fake_mongo)
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/bmi_advice")
    data = response.get_json()
    assert isinstance(data.get("reference_values"), dict)
    if data.get("goal_suggestion") == "Maintenance":
        expected = {"goal", "calories", "protein", "carbs", "fat"}
        assert expected.issubset(data.get("reference_values").keys())


def test_bmi_advice_boundary_normal(client, monkeypatch):
    """Simulate a boundary BMI of approximately 18.5 and verify the response
    categorizes it as normal."""
    fake_profile = {"email": "test@example.com",
                    "weight": "53.5", "height": "170"}
    fake_mongo = type(
        "FakeMongo",
        (),
        {
            "db": type(
                "FakeDB",
                (),
                {
                    "user": type(
                        "FakeCollection",
                        (),
                        {"find_one": lambda self, q: fake_profile}
                    )()
                }
            )()
        }
    )
    monkeypatch.setattr("application.mongo", fake_mongo)
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/bmi_advice")
    data = response.get_json()
    assert abs(data.get("bmi") - 18.5) < 0.5
    assert data.get("goal_suggestion") == "Maintenance"


def test_bmi_advice_post_method(client, monkeypatch):
    """Verify that POST requests to /bmi_advice work correctly (the endpoint
    accepts both GET and POST)."""
    fake_profile = {"email": "test@example.com",
                    "weight": "75", "height": "175"}
    fake_mongo = type(
        "FakeMongo",
        (),
        {
            "db": type(
                "FakeDB",
                (),
                {
                    "user": type(
                        "FakeCollection",
                        (),
                        {"find_one": lambda self, q: fake_profile}
                    )()
                }
            )()
        }
    )
    monkeypatch.setattr("application.mongo", fake_mongo)
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.post("/bmi_advice")
    assert response.status_code == 200
    data = response.get_json()
    assert "bmi" in data


def test_meal_plan_delete_method(client):
    """Ensure that using an unsupported HTTP method (DELETE) on /meal_plan
    returns 405."""
    response = client.delete("/meal_plan")
    assert response.status_code == 405


def test_bmi_advice_boundary_overweight(client, monkeypatch):
    """For a profile near the BMI boundary, verify the endpoint categorizes
    as overweight."""
    fake_profile = {"email": "test@example.com",
                    "weight": "73", "height": "170"}
    fake_mongo = type(
        "FakeMongo",
        (),
        {
            "db": type(
                "FakeDB",
                (),
                {
                    "user": type(
                        "FakeCollection",
                        (),
                        {"find_one": lambda self, q: fake_profile}
                    )()
                }
            )()
        }
    )
    monkeypatch.setattr("application.mongo", fake_mongo)
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
    response = client.get("/bmi_advice")
    data = response.get_json()
    bmi = data.get("bmi")
    assert bmi >= 25
    advice = data.get("advice").lower()
    assert "overweight" in advice or "deficit" in advice
