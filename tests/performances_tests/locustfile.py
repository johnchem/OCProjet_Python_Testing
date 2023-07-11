from locust import HttpUser, task
from server import competitions, clubs

class ProjectTestPref(HttpUser):

    @task
    def showSummary(self):
        reponse = self.client.post(
            "/showSummary",{
                "email":"john@simplylift.co"
            }
        )

    @task
    def bookPlaces(self):
        club = clubs[0]
        print(club)
        competition = competitions[0]

        self.client.get(f'/book/{competition["name"]}/{club["name"]}')
        response = self.client.post("/purchasePlaces",{
            "competition": competition,
            "club": club,
            "places":1,
            })
