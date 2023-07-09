import json
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for



def isCompetitionActive(competition_date):
    competition_date = datetime.strptime(competition_date, "%Y-%m-%d %X")
    today = datetime.today()
    return True if competition_date > today else False


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        for competition in listOfCompetitions:
            competition['isActive'] = isCompetitionActive(competition['date'])
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

# max number of places per competitions per club
LIMIT_RESERVATION = 12


@app.route('/')
def index():
    return render_template('index.html'), 200


@app.route('/showSummary',methods=['POST'])
def showSummary():
    try:
        club = [club for club in clubs if club['email'] == request.form['email']][0]
        return render_template('welcome.html',club=club, competitions=competitions), 200
    except IndexError:
        return render_template('email_error.html'), 401


@app.route('/book/<competition>/<club>')
def book(competition, club):
    try:
        foundClub = [c for c in clubs if c['name'] == club][0]
        foundCompetition = [c for c in competitions if c['name'] == competition][0]
        if foundClub and foundCompetition:
            return render_template('booking.html', club=foundClub, competition=foundCompetition)
    except:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions), 302


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])

    if int(club['points']) < placesRequired:
        flash("You do not have enough points")
        return render_template('welcome.html', club=club, competitions=competitions), 400
    
    if club['name'] in competition:
        placesBooked = competition[club['name']]
    else:
        placesBooked = 0
    totalPlaces = placesBooked + placesRequired

    if totalPlaces > LIMIT_RESERVATION:
        flash("You cannot book more than 12 places per competition")
        flash(f"you already have {placesBooked} places")
        return render_template('welcome.html', club=club, competitions=competitions), 400
     
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    competition[club['name']] = totalPlaces
    club['points'] = int(club['points'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions), 200


@app.route('/pointResume', methods=['GET'])
def pointsDisplay():
    headings = ("club name", "available points")
    return render_template('points_board.html', listOfClubs=clubs, headings=headings), 200


@app.route('/logout')
def logout():
    return redirect(url_for('index')), 200