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
    
    # tank top/crop top (wear as little as possible)
    # t-shirt
    # long sleeve
    # sweater
    # jacket/hoodie
    # coat
    # heavy duty coat
    # shorts/skirt
    # long pants
    # dress
    # capri pants
    # hat/gloves/scarf
    # sunglasses

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

