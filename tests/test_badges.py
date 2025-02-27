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

def test_access_badges_page(client):
    authenticate(client, TEST_EMAIL)
    result = client.get('/badges')
    assert result.status_code == 200


def test_initialize_statistics(client):
    authenticate(client, TEST_EMAIL)
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL}) is None
    result = client.get('/badges')
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL}) is not None
    for metric in badge_milestones:
        assert mongo.db.statistics.find_one({"email": TEST_EMAIL})[metric] == 0
    assert result.status_code == 200


def test_initialize_badges(client):
    authenticate(client, TEST_EMAIL)
    assert mongo.db.achievements.find_one({"email": TEST_EMAIL}) is None
    result = client.get('/badges')
    assert mongo.db.achievements.find_one({"email": TEST_EMAIL}) is not None
    for metric in badge_milestones:
        assert mongo.db.achievements.find_one({"email": TEST_EMAIL})[metric] == 0
    assert "nonexistent_metric" not in mongo.db.achievements.find_one({"email": TEST_EMAIL})
    assert result.status_code == 200


def test_update_existing_stat(client):
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL}) is None
    modify_stat(TEST_EMAIL, "longest_streak", 0)
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL}) is not None


def test_assign_initial_stats(client):
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL}) is None
    modify_stat(TEST_EMAIL, "longest_streak", 0)
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})['longest_streak'] == 0
    modify_stat(TEST_EMAIL, "food_intake", 10)
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})['food_intake'] == 10
    modify_stat(TEST_EMAIL, "energy_expended", -500)
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})['energy_expended'] == -500


def test_create_new_stat(client):
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL}) is None
    modify_stat(TEST_EMAIL, "undefined_stat", 0)
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL}) is not None


def test_update_stat_value(client):
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL}) is None
    modify_stat(TEST_EMAIL, "longest_streak", 0)
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})["longest_streak"] == 0
    modify_stat(TEST_EMAIL, "longest_streak", 10)
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})["longest_streak"] == 10
    modify_stat(TEST_EMAIL, "energy_expended", -500)
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})["energy_expended"] == -500


def test_increment_stat_value(client):
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL}) is None
    modify_stat(TEST_EMAIL, "longest_streak", 0, True)
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})["longest_streak"] == 0
    modify_stat(TEST_EMAIL, "longest_streak", 7, True)
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})["longest_streak"] == 7
    modify_stat(TEST_EMAIL, "longest_streak", -3, True)
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})["longest_streak"] == 4


def test_exact_milestone_reach(client):
    authenticate(client, TEST_EMAIL)
    client.get('/badges')
    
    for metric in badge_milestones:
        levels = badge_milestones[metric]
        for index in range(len(levels)):
            modify_stat(TEST_EMAIL, metric, levels[index])
            assert mongo.db.achievements.find_one({"email": TEST_EMAIL})[metric] == index


def test_milestone_thresholds(client):
    authenticate(client, TEST_EMAIL)
    client.get('/badges')
    
    for metric in badge_milestones:
        levels = badge_milestones[metric]
        for index in range(len(levels)):
            modify_stat(TEST_EMAIL, metric, levels[index] + 1)
            assert mongo.db.achievements.find_one({"email": TEST_EMAIL})[metric] == index
            if index < len(levels) - 1:
                modify_stat(TEST_EMAIL, metric, levels[index + 1] - 1)
            assert mongo.db.achievements.find_one({"email": TEST_EMAIL})[metric] == index


def test_invalid_stat_inputs(client):
    authenticate(client, TEST_EMAIL)
    client.get('/badges')
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL}) is not None

    modify_stat(TEST_EMAIL, "longest_streak", "invalid")
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})["longest_streak"] == 0

    modify_stat(TEST_EMAIL, "longest_streak", 8)
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})["longest_streak"] == 8

    modify_stat(TEST_EMAIL, "longest_streak", "wrong_value")
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})["longest_streak"] == 8


def test_string_input_handling(client):
    authenticate(client, TEST_EMAIL)
    client.get('/badges')
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL}) is not None

    modify_stat(TEST_EMAIL, "longest_streak", "3")
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})["longest_streak"] == 3

    modify_stat(TEST_EMAIL, "longest_streak", "5.0")
    assert mongo.db.statistics.find_one({"email": TEST_EMAIL})["longest_streak"] == 5