import functools
from flask import (
    Blueprint, jsonify, flash, g, redirect, render_template, request, session, url_for
)
from pyowm import OWM
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.wrappers import weatherWrapper
import json

bp = Blueprint('userprefs', __name__)

@bp.route('/userprefs', methods=['GET'])
@login_required
def userprefs():
    db = get_db()

    user = db.execute('SELECT * FROM user WHERE id=?', (session.get('user_id'),)).fetchone()
    locationID = user['location_id']

    clothesList = db.execute('SELECT * FROM clothes c JOIN user_x_clothes uxc ON c.id = uxc.clothes_id WHERE uxc.user_id=?', (session.get('user_id'),)).fetchall()
    return render_template('prefs/userPrefs.html', locationName=locationID, clothes=clothesList)    

@bp.route('/location', methods=('GET', 'POST'))
@login_required
def location():
    if request.method == 'POST':
        city_id = request.form['locList']
        user_id = session.get('user_id')
        error = None

        if not city_id:
            error = "Please choose a city from the dropdown."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE user SET location_id = '+ str(city_id) +' WHERE id = ' + str(user_id)
            )
            db.commit()
            session['location_id'] = city_id
            return redirect(url_for('index'))

    return render_template('prefs/locationPref.html')

@bp.route('/clothing', methods=('GET', 'POST'))
@login_required
def clothing():
    if request.method == 'POST':
        clothesListStr = request.form['listOfSelectedClothes']
        
        clothesList = clothesListStr.split(",")
        error = None

        if not clothesList:
            error = "Please choose some clothes."

        if error is not None:
            flash(error)
        else:
            db = get_db()

            db.execute('DELETE FROM user_x_clothes WHERE user_id=?', (session['user_id'],))
            db.commit()
            for clothes in clothesList:
                c = db.execute(
                    'SELECT id FROM clothes WHERE name = ?', (clothes,)
                ).fetchone()

                if c is not None:
                    
                    db.execute(
                        'INSERT INTO user_x_clothes (user_id, clothes_id) VALUES (?, ?)',
                        (session["user_id"],c['id'])
                    )
            db.commit()
            return redirect(url_for('index'))


    return render_template('prefs/clothingPref.html')

@bp.route('/searchcities/<city_string>/', methods=["GET"])
def searchCities(city_string=None):
    owm = weatherWrapper.getOWM()
    reg = owm.city_id_registry()

    ret = []
    cityTup =()
    if city_string:
        list_of_locations = reg.locations_for(city_string, matching='like')
        for city in list_of_locations:
            cityTup = (city.id, city.name, city.country)
            ret.append(cityTup)

    return json.dumps(ret)

