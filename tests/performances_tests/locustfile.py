from random import randrange

from locust import HttpUser, task
from server import competitions, clubs


class ProjectTestPref(HttpUser):

    @task
    def showSummary(self):
        self.client.post(
            "/showSummary",
            data={
                "email": "john@simplylift.co"
            }
        )

    @task
    def bookPlaces(self):
        club = clubs[randrange(len(clubs))]

        competition = competitions[randrange(len(competitions))]
        competition['isActive'] = True

        self.client.get(f'/book/{competition["name"]}/{club["name"]}')
        self.client.post(
            '/purchasePlaces',
            data={
                "competition": competition["name"],
                "club": club["name"],
                "places": 0,
            }
        )
