import pytest
from flaskr.db import get_db

def test_location(client, auth, app):
    auth.login()
    assert client.get('/location').status_code == 200
    response = client.post('/location', data={'locList': ''})
    assert b'Please choose a city from the dropdown.' in response.data
    client.post('/location', data={'locList': '5206379'})
    
    with app.app_context():
        db = get_db()
        city = db.execute('SELECT * FROM user WHERE username=?', ("test" ,)).fetchone()
        assert city['location_id'] == 5206379

def test_searchCities(client, auth):
    auth.login()
    response = client.get('/searchcities/Pittsburgh/')
    assert response.status_code == 200
    assert b'Pittsburgh' in response.data
    assert b'East Pittsburgh' in response.data

