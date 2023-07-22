from random import randrange
import re

from bs4 import BeautifulSoup
import json

import server
from tests.test_server import MOCK_CLUBS, MOCK_COMPETITIONS


def test_user_connect_book_quit(tmp_path, monkeypatch, client):
    # creation of the mock file
    test_clubs_file = tmp_path/"clubs.json"
    test_clubs_file.write_text("")

    test_competitions_file = tmp_path/"competitions.json"
    test_competitions_file.write_text("")

    # print the json content
    json.dump(MOCK_CLUBS, test_clubs_file.open(mode="w"))
    json.dump(MOCK_COMPETITIONS, test_competitions_file.open(mode="w"))

    # monkeypath the working directory to the tmp_dir
    monkeypatch.chdir(tmp_path)

    # load clubs, competitions and monkeypatch them
    clubs, competitions = server.loadClubs(), server.loadCompetitions()
    monkeypatch.setattr(server, 'clubs', clubs)
    monkeypatch.setattr(server, 'competitions', competitions)

    club = clubs[randrange(len(clubs))]

    with client:
        # landing page
        response = client.get('/')
        assert response.status_code == 200

        # login
        response = client.post(
            '/showSummary',
            data={
                "email": club["email"]
                }
            )
        data = response.data.decode()
        assert data.find(
            "Sorry, this email is not registered"
            ) == -1, print(club["email"])

        # select competition to book place
        soup = BeautifulSoup(response.data, "html.parser")
        links = soup.find_all("a", string="Book Places")
        book_compt_link = links[randrange(len(links))]

        # get to the book page for the selected competition
        response = client.get(book_compt_link["href"])
        assert response.status_code == 200

        # parse the html
        soup = BeautifulSoup(response.data, "html.parser")
        form_element = soup.body.form
        # get club name
        club_name = form_element.find("input", attrs={"name": "club"})["value"]
        # get competition name
        competition_name = form_element.find(
            "input",
            attrs={"name": "competition"}
            )["value"]
        # get available places
        places_available_element = soup.find(string=re.compile("Places"))
        places_available = re.search(
            r"Places available: (\d+)",
            places_available_element
            ).group(1)

        assert club["name"] == club_name

        places_to_buy = 5
        # check that the club has enough point to buy the places
        if int(club["points"]) < places_to_buy:
            club["points"] = 5

        # check that there are enough place in the competition
        if int(places_available) < places_to_buy:
            places_to_buy = places_available

        response = client.post(
            "/purchasePlaces",
            data={
                "club": club_name,
                "competition": competition_name,
                "places": places_to_buy,
            }
        )
        data = response.data.decode()
        assert data.find("<li>Great-booking complete!</li>") != -1

        response = client.get("/logout")
        assert response.status_code == 200
