import pytest
from application import app, update_statistic, mongo, badge_milestones
import sys
import os

sys.path.append(os.path.abspath(os.path.join('..')))

TEST_EMAIL = "testemail@gmail.com"


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['MONGO_URI'] = (
        'mongodb://localhost:27017/your_database_test'
    )
    with app.test_client() as client:
        mongo.db.badges.delete_many({})
        mongo.db.stats.delete_many({})
        yield client


def login(client, email):
    with client.session_transaction() as sess:
        sess['email'] = email


# Test that the badges page route is accessible.
def test_badges_route(client):
    login(client, TEST_EMAIL)
    response = client.get('/badges')
    assert response.status_code == 200


def test_populate_stats(client):
    login(client, TEST_EMAIL)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL}) is None
    response = client.get('/badges')
    assert mongo.db.stats.find_one({"email": TEST_EMAIL}) is not None
    for stat_name in badge_milestones:
        assert mongo.db.stats.find_one({"email": TEST_EMAIL})[stat_name] == 0
    assert response.status_code == 200


def test_populate_badges(client):
    login(client, TEST_EMAIL)
    assert mongo.db.badges.find_one({"email": TEST_EMAIL}) is None
    response = client.get('/badges')
    assert mongo.db.badges.find_one({"email": TEST_EMAIL}) is not None
    for stat_name in badge_milestones:
        assert mongo.db.badges.find_one({"email": TEST_EMAIL})[stat_name] == 0
    assert "fake_stat" not in mongo.db.badges.find_one({"email": TEST_EMAIL})
    assert response.status_code == 200


def test_create_existing_stat(client):
    assert mongo.db.stats.find_one({"email": TEST_EMAIL}) is None
    update_statistic(TEST_EMAIL, "highest_streak", 0)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL}) is not None


def test_initialize_stats(client):
    assert mongo.db.stats.find_one({"email": TEST_EMAIL}) is None
    update_statistic(TEST_EMAIL, "highest_streak", 0)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        'highest_streak'] == 0
    update_statistic(TEST_EMAIL, "calories_eaten", 5)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        'calories_eaten'] == 5
    update_statistic(TEST_EMAIL, "calories_burned", -1000)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        'calories_burned'] == -1000


def test_create_nonexistent_stat(client):
    assert mongo.db.stats.find_one({"email": TEST_EMAIL}) is None
    update_statistic(TEST_EMAIL, "fake_statistic", 0)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL}) is not None


def test_set_stats_value(client):
    assert mongo.db.stats.find_one({"email": TEST_EMAIL}) is None
    update_statistic(TEST_EMAIL, "highest_streak", 0)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        "highest_streak"] == 0
    update_statistic(TEST_EMAIL, "highest_streak", 5)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        "highest_streak"] == 5
    update_statistic(TEST_EMAIL, "calories_burned", -1000)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        "calories_burned"] == -1000
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        "highest_streak"] == 5


def test_inc_stats_value(client):
    assert mongo.db.stats.find_one({"email": TEST_EMAIL}) is None
    update_statistic(TEST_EMAIL, "highest_streak", 0, True)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        "highest_streak"] == 0
    update_statistic(TEST_EMAIL, "highest_streak", 5, True)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        "highest_streak"] == 5
    update_statistic(TEST_EMAIL, "highest_streak", -1000, True)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        "highest_streak"] == -995


def test_exactly_match_milestones(client):
    login(client, TEST_EMAIL)
    client.get('/badges')

    for stat_name in badge_milestones:
        milestones = badge_milestones[stat_name]
        for milestone_idx in range(len(milestones)):
            update_statistic(TEST_EMAIL, stat_name, milestones[milestone_idx])
            assert mongo.db.badges.find_one({"email": TEST_EMAIL})[
                stat_name] == milestone_idx


def test_between_values_milestones(client):
    login(client, TEST_EMAIL)
    client.get('/badges')

    for stat_name in badge_milestones:
        milestones = badge_milestones[stat_name]
        for milestone_idx in range(len(milestones)):
            update_statistic(TEST_EMAIL, stat_name,
                             milestones[milestone_idx] + 1)
            assert mongo.db.badges.find_one({"email": TEST_EMAIL})[
                stat_name] == milestone_idx
            if milestone_idx < len(milestones) - 1:
                update_statistic(TEST_EMAIL, stat_name,
                                 milestones[milestone_idx + 1] - 1)
            assert mongo.db.badges.find_one({"email": TEST_EMAIL})[
                stat_name] == milestone_idx


def test_invalid_values(client):
    login(client, TEST_EMAIL)
    client.get('/badges')
    assert mongo.db.stats.find_one({"email": TEST_EMAIL}) is not None

    update_statistic(TEST_EMAIL, "highest_streak", "not a value")
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        "highest_streak"] == 0

    # Correctly change the value of the stat
    # so we can run the assert a second time.
    update_statistic(TEST_EMAIL, "highest_streak", 5)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        "highest_streak"] == 5

    update_statistic(TEST_EMAIL, "highest_streak", "not a value")
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        "highest_streak"] == 5


def test_string_values(client):
    login(client, TEST_EMAIL)
    client.get('/badges')
    assert mongo.db.stats.find_one({"email": TEST_EMAIL}) is not None

    update_statistic(TEST_EMAIL, "highest_streak", "1")
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        "highest_streak"] == 1

    update_statistic(TEST_EMAIL, "highest_streak", "2.0")
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})[
        "highest_streak"] == 2


# Adding 10 test cases.

def test_update_statistic_with_zero_value_again(client):
    """Test updating a statistic with a zero value again."""
    update_statistic(TEST_EMAIL, "calories_eaten", 0 if isinstance(0, (int, float)) else 0)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})["calories_eaten"] == 0


def test_update_statistic_with_positive_value(client):
    """Test updating a statistic with a positive value."""
    update_statistic(TEST_EMAIL, "calories_eaten", 100 if isinstance(100, (int, float)) else 0)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})["calories_eaten"] == 100


def test_update_statistic_with_negative_value_again(client):
    """Test updating a statistic with a negative value again."""
    update_statistic(TEST_EMAIL, "calories_burned", -200 if isinstance(-200, (int, float)) else 0)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})["calories_burned"] == -200


def test_update_statistic_with_large_positive_value(client):
    """Test updating a statistic with a large positive value."""
    update_statistic(TEST_EMAIL, "calories_eaten", 1000000 if isinstance(1000000, (int, float)) else 0)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})["calories_eaten"] == 1000000


def test_update_statistic_with_large_negative_value_again(client):
    """Test updating a statistic with a large negative value again."""
    update_statistic(TEST_EMAIL, "calories_burned", -1000000 if isinstance(-1000000, (int, float)) else 0)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})["calories_burned"] == -1000000


def test_update_statistic_with_floating_point_value(client):
    """Test updating a statistic with a floating-point value."""
    update_statistic(TEST_EMAIL, "calories_eaten", 123.45 if isinstance(123.45, (int, float)) else 0)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})["calories_eaten"] == 123.45


def test_update_statistic_with_negative_floating_point_value(client):
    """Test updating a statistic with a negative floating-point value."""
    update_statistic(TEST_EMAIL, "calories_burned", -123.45 if isinstance(-123.45, (int, float)) else 0)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})["calories_burned"] == -123.45


def test_update_statistic_with_increment_positive_value(client):
    """Test incrementing a statistic with a positive value."""
    update_statistic(TEST_EMAIL, "highest_streak", 10 if isinstance(10, (int, float)) else 0, True)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})["highest_streak"] == 10


def test_update_statistic_with_increment_negative_value(client):
    """Test incrementing a statistic with a negative value."""
    update_statistic(TEST_EMAIL, "highest_streak", -5 if isinstance(-5, (int, float)) else 0, True)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})["highest_streak"] == -5


def test_update_statistic_with_increment_zero_value(client):
    """Test incrementing a statistic with a zero value."""
    update_statistic(TEST_EMAIL, "highest_streak", 0 if isinstance(0, (int, float)) else 0, True)
    assert mongo.db.stats.find_one({"email": TEST_EMAIL})["highest_streak"] == 0