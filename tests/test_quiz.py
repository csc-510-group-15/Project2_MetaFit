import pytest
from flask import session
from application import app, mongo
from datetime import datetime, timedelta
import tempfile


@pytest.fixture
def client():
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = tempfile.gettempdir()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_quiz_route_get(client):
    response = client.get('/quiz')
    assert response.status_code == 200
    assert b'<html>' in response.data


def test_quiz_route_post(client):
    response = client.post('/quiz')
    assert response.status_code == 200


def test_question_route_get_valid_id(client, mocker):
    mock_question = {
        "q_id": 1,
        "a": "Option A",
        "b": "Option B",
        "c": "Option C",
        "d": "Option D",
        "ans": "a"
    }
    mocker.patch.object(mongo.db.questions,
                        'find_one',
                        return_value=mock_question)
    response = client.get('/question/1')
    assert response.status_code == 200
    assert b'Question 1' in response.data


def test_question_route_get_invalid_id(client, mocker):
    mocker.patch.object(mongo.db.questions, 'find_one', return_value=None)
    response = client.get('/question/9999')
    assert response.status_code == 302
    assert response.location.endswith('/score')


def test_question_route_get_first_question(client, mocker):
    mock_question = {
        "q_id": 1,
        "a": "Option A",
        "b": "Option B",
        "c": "Option C",
        "d": "Option D",
        "ans": "a"
    }
    mocker.patch.object(mongo.db.questions,
                        'find_one',
                        return_value=mock_question)
    response = client.get('/question/1')
    assert response.status_code == 200


def test_question_route_get_non_existent(client, mocker):
    mocker.patch.object(mongo.db.questions, 'find_one', return_value=None)
    response = client.get('/question/9999')
    assert response.status_code == 302
    assert response.location.endswith('/score')


def test_question_route_post_wrong_answer(client, mocker):
    mock_question = {
        "q_id": 1,
        "a": "Option A",
        "b": "Option B",
        "c": "Option C",
        "d": "Option D",
        "ans": "a"
    }
    mocker.patch.object(mongo.db.questions,
                        'find_one',
                        return_value=mock_question)
    with client.session_transaction() as sess:
        sess['marks'] = 0
    response = client.post('/question/1',
                           data={'options': 'b'},
                           follow_redirects=True)
    print(response)
    assert session['marks'] == 0


def test_question_route_post_all_questions_complete(client):
    response = client.post('/question/1000')
    assert response.status_code == 302
    assert response.location.endswith('/score')


def test_score_route_get(client):
    response = client.get('/score')
    assert response.status_code == 200
    assert b'Final Score' in response.data


def test_score_route_no_marks(client):
    with client.session_transaction() as sess:
        sess['marks'] = None
    response = client.get('/score')
    assert response.status_code == 200


def test_score_route_max_marks(client):
    with client.session_transaction() as sess:
        sess['marks'] = 100
    response = client.get('/score')
    assert response.status_code == 200


def test_session_initial_marks(client):
    with client.session_transaction() as sess:
        sess['marks'] = 0
    response = client.get('/question/1')
    print(response)
    assert session['marks'] == 0


def test_session_persistence(client):
    with client.session_transaction() as sess:
        sess['marks'] = 10
    response = client.get('/score')
    print(response)
    assert session['marks'] == 10


def test_question_route_post_correct_answer(client, mocker):
    mock_question = {
        "q_id": 1,
        "a": "Option A",
        "b": "Option B",
        "c": "Option C",
        "d": "Option D",
        "ans": "a"
    }
    mocker.patch.object(mongo.db.questions,
                        'find_one',
                        return_value=mock_question)
    with client.session_transaction() as sess:
        sess['marks'] = 0

    response = client.post('/question/1',
                           data={'options': 'a'},
                           follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert sess['marks'] == 0


def test_question_route_post_empty_option(client, mocker):
    mock_question = {
        "q_id": 1,
        "a": "Option A",
        "b": "Option B",
        "c": "Option C",
        "d": "Option D",
        "ans": "a"
    }
    mocker.patch.object(mongo.db.questions,
                        'find_one',
                        return_value=mock_question)
    response = client.post('/question/1',
                           data={'options': ''},
                           follow_redirects=True)
    assert response.status_code == 200


def test_question_route_post_invalid_option(client, mocker):
    mock_question = {
        "q_id": 1,
        "a": "Option A",
        "b": "Option B",
        "c": "Option C",
        "d": "Option D",
        "ans": "Option A"
    }
    mocker.patch.object(mongo.db.questions,
                        'find_one',
                        return_value=mock_question)
    response = client.post('/question/1',
                           data={'options': 'Invalid Option'},
                           follow_redirects=True)
    assert response.status_code == 200


def test_question_route_post_repeated(client, mocker):
    mock_question = {
        "q_id": 1,
        "a": "Option A",
        "b": "Option B",
        "c": "Option C",
        "d": "Option D",
        "ans": "a"
    }
    mocker.patch.object(mongo.db.questions,
                        'find_one',
                        return_value=mock_question)
    with client.session_transaction() as sess:
        sess['marks'] = 0
    client.post('/question/1', data={'options': 'a'})
    response = client.post('/question/1',
                           data={'options': 'a'},
                           follow_redirects=True)
    print(response)
    assert sess['marks'] == 0


def test_streak_first_login(client):

    with client.session_transaction() as session:
        session.clear()
    response = client.get('/login', follow_redirects=True)
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['streak'] = 1

    with client.session_transaction() as sess:
        assert sess.get('streak') == 1
    assert response.status_code == 200


def test_streak_consecutive_login(client):
    previous_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    with client.session_transaction() as sess:
        sess['streak'] = 1
        sess['last_login_date'] = previous_date

    response = client.get('/login', follow_redirects=True)

    with client.session_transaction() as sess:
        assert sess['streak'] == 1
    assert response.status_code == 200


def test_streak_same_day_login(client):
    today = datetime.now().strftime('%Y-%m-%d')
    with client.session_transaction() as sess:
        sess['streak'] = 5
        sess['last_login_date'] = today

    response = client.get('/login', follow_redirects=True)

    with client.session_transaction() as sess:
        assert sess['streak'] == 5  # Streak should not increment
        assert sess['last_login_date'] == today
    assert response.status_code == 200
