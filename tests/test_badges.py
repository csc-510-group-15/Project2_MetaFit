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


# Test that attempting to update any statistic creates a stats DB entry for the current user.
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
    update_statistic(TEST_EMAIL, "highest_streak", 0, True)
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

    # Correctly change the value of the stat so we can run the assert a second time.
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