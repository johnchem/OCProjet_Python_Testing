import pytest
import json
import server
from server import *
import re

MOCK_COMPETITIONS = {
    "competitions": [
        {
            "name": "Test 1",
            "date": "2020-03-27 10:00:00",
            "numberOfPlaces": "25"
        },
        {
            "name": "Test 2",
            "date": "2020-10-22 13:30:00",
            "numberOfPlaces": "5"
        },
        {
            "name": "Test 3",
            "date": "2025-01-01 01:01:00",
            "numberOfPlaces": "25"
        }
    ]
}

MOCK_CLUBS = {
    "clubs":[
    {
        "name":"test club 1",
        "email":"test1@test.com",
        "points":"13"
    },
    {
        "name":"test club 2",
        "email": "test2@test.com",
        "points":"4"
    },
    {   "name":"test club 3",
        "email": "test3@test.com",
        "points":"12"
    }
]}

def _list_of_clubs():
    return MOCK_CLUBS["clubs"]

def _list_of_competitions():
    return MOCK_COMPETITIONS["competitions"]

### DB reading function ###	

def test_load_clubs(tmp_path, monkeypatch):
    # creation of the mock file
    test_clubs_file = tmp_path/"clubs.json"
    test_clubs_file.write_text("")
    # print the json content
    json.dump(MOCK_CLUBS, test_clubs_file.open(mode="w"))
    # monkeypath the working directory to the tmp_dir
    monkeypatch.chdir(tmp_path)
    
    results = loadClubs()
    
    assert results[0] == {
        "name":"test club 1",
        "email":"test1@test.com",
        "points":"13",
    }
    assert results[1] == {
        "name":"test club 2",
        "email": "test2@test.com",
        "points":"4",
    }
    assert results[2] == {
        "name":"test club 3",
        "email": "test3@test.com",
        "points":"12",
    }
    
def test_load_competitions(tmp_path, monkeypatch):
    # creation of the mock file
    test_clubs_file = tmp_path/"competitions.json"
    test_clubs_file.write_text("")
    # print the json content
    json.dump(MOCK_COMPETITIONS, test_clubs_file.open(mode="w"))
    # monkeypath the working directory to the tmp_dir
    monkeypatch.chdir(tmp_path)
    
    results = loadCompetitions()
    control_data = MOCK_COMPETITIONS["competitions"]

    assert results[0]['name'] == control_data[0]["name"]
    assert results[0]['date'] == control_data[0]["date"]
    assert results[0]['numberOfPlaces'] == control_data[0]["numberOfPlaces"]
    
    assert results[1]['name'] == control_data[1]["name"]
    assert results[1]['date'] == control_data[1]["date"]
    assert results[1]['numberOfPlaces'] == control_data[1]["numberOfPlaces"]
    
    assert results[2]['name'] == control_data[2]["name"]
    assert results[2]['date'] == control_data[2]["date"]
    assert results[2]['numberOfPlaces'] == control_data[2]["numberOfPlaces"]

### Logic verification ###

def test_isCompetitionActive():
    list_competitions = MOCK_COMPETITIONS["competitions"]
    results = [isCompetitionActive(compet["date"]) for compet in list_competitions]
    assert results[0] == False
    assert results[1] == False
    assert results[2] == True

def test_club_without_points_cant_book(client, monkeypatch):
    clubs = _list_of_clubs()
    competitions = _list_of_competitions()
    monkeypatch.setattr(server, 'clubs', clubs)
    monkeypatch.setattr(server, 'competitions', competitions)

    
    club = MOCK_CLUBS["clubs"][0]
    club["points"] = 0
    competition = MOCK_COMPETITIONS["competitions"][0]
        
    result = client.post('/purchasePlaces', data={
        "competition": competition["name"],
        "club": club["name"],
        "places":1,
    })
    data = result.data.decode()

    assert result.status_code == 400
    assert data.find("<li>You do not have enough points</li>") != -1
    
def test_limit_booking_places(client, monkeypatch):
    clubs = _list_of_clubs()
    competitions = _list_of_competitions()
    monkeypatch.setattr(server, 'clubs', clubs)
    monkeypatch.setattr(server, 'competitions', competitions)

    club = MOCK_CLUBS["clubs"][0]
    club["points"] = 25
    competition = MOCK_COMPETITIONS["competitions"][0]
    competition["numberOfPlaces"] = 25
        
    result = client.post('/purchasePlaces', data={
        "competition": competition["name"],
        "club": club["name"],
        "places":15,
    })
    data = result.data.decode()

    assert result.status_code == 400
    assert data.find("<li>You cannot book more than 12 places per competition</li>") != -1, print(data)
    
def test_points_are_used(client, monkeypatch):
    ## necessaire de fixer la fonction avant ##
    clubs = _list_of_clubs()
    competitions = _list_of_competitions()
    monkeypatch.setattr(server, 'clubs', clubs)
    monkeypatch.setattr(server, 'competitions', competitions)

    club = MOCK_CLUBS["clubs"][0]
    club["points"] = 25
    competition = MOCK_COMPETITIONS["competitions"][0]
    competition["numberOfPlaces"] = 25
        
    result = client.post('/purchasePlaces', data={
        "competition": competition["name"],
        "club": club["name"],
        "places":10,
    })

    assert result.status_code == 200
    assert club["points"] == 15  

def test_limit_booking_places_through_multiple_order(client, monkeypatch):
    clubs = _list_of_clubs()
    competitions = _list_of_competitions()
    monkeypatch.setattr(server, 'clubs', clubs)
    monkeypatch.setattr(server, 'competitions', competitions)

    club = MOCK_CLUBS["clubs"][0]
    club["points"] = 25
    competition = MOCK_COMPETITIONS["competitions"][0]
    competition["numberOfPlaces"] = 25
        
    client.post('/purchasePlaces', data={
        "competition": competition["name"],
        "club": club["name"],
        "places":5,
    })

    client.post('/purchasePlaces', data={
        "competition": competition["name"],
        "club": club["name"],
        "places":5,
    })

    result = client.post('/purchasePlaces', data={
        "competition": competition["name"],
        "club": club["name"],
        "places":5,
    })
    data = result.data.decode()

    assert result.status_code == 400
    assert data.find("<li>You cannot book more than 12 places per competition</li>") != -1
    
### Page status code compliant ###

def test_index_status_code_ok(client):
    response = client.get('/')
    assert response.status_code == 200
    
def test_point_board_should_status_code_ok(client):
    response = client.get('/pointResume')
    assert response.status_code == 200 

def test_showSummary_status_code_ok(client, monkeypatch):
    clubs = MOCK_CLUBS["clubs"]
    competitions = MOCK_COMPETITIONS["competitions"]

    monkeypatch.setattr(server, 'clubs', clubs)
    monkeypatch.setattr(server, 'competitions', competitions)

    club = clubs[0]
    
    response = client.post('/showSummary',
        data = {
            "email": club["email"] 
        })
    
    assert response.status_code == 200

def test_book_statut_code_ok(client, monkeypatch):
    clubs = MOCK_CLUBS["clubs"]
    competitions = MOCK_COMPETITIONS["competitions"]

    monkeypatch.setattr(server, 'clubs', clubs)
    monkeypatch.setattr(server, 'competitions', competitions)

    club = clubs[1]
    competition = competitions[1]
    
    response = client.get(f'/book/{competition["name"]}/{club["name"]}')
    
    assert response.status_code == 200

def test_purchasePlaces_statut_code_ok(client, monkeypatch):
    clubs = MOCK_CLUBS["clubs"]
    competitions = MOCK_COMPETITIONS["competitions"]
    monkeypatch.setattr(server, 'clubs', clubs)
    monkeypatch.setattr(server, 'competitions', competitions)

    club = clubs[1]
    club["points"] = 10
    competition = competitions[1]
    competition["numberOfPlaces"] = 10
    response = client.post('/purchasePlaces', data={
        "competition": competition["name"],
        "club": club["name"],
        "places":5,
    })
    assert response.status_code == 200, print(response.data)

def test_pointsDisplay_statut_code_ok(client, monkeypatch):
    clubs = _list_of_clubs()
    competitions = _list_of_competitions()
    monkeypatch.setattr(server, 'clubs', clubs)
    monkeypatch.setattr(server, 'competitions', competitions)
    result = client.get('/pointResume')
    assert result.status_code == 200

def test_logout_statut_code_ok(client):
    result = client.get('/logout')
    assert result.status_code == 200

### UI verification

def test_display_actual_point(client, monkeypatch):
    clubs = _list_of_clubs()
    competitions = _list_of_competitions()
    monkeypatch.setattr(server, 'clubs', clubs)
    monkeypatch.setattr(server, 'competitions', competitions)

    club = MOCK_CLUBS["clubs"][0]
    club["points"] = 25
        
    result = client.post('/showSummary', data={
        "email": club["email"],
        })
    
    data = result.data.decode()
    m = re.search(r'Points available: (\d+)', data)
    displayed_point = m.group(1)

    assert result.status_code == 200
    assert int(displayed_point) == 25

def test_display_score_board(client, monkeypatch):
    clubs = _list_of_clubs()
    competitions = _list_of_competitions()
    monkeypatch.setattr(server, 'clubs', clubs)
    monkeypatch.setattr(server, 'competitions', competitions)

    result = client.get('/pointResume')
    
    data = result.data.decode()
    results = re.findall(r'<td class=\"table__cell\">(\d+)<\/td>', data)
    
    assert result.status_code == 200
    for club, value in zip(clubs, results):
        assert int(club["points"]) == int(value)