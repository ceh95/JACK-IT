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
    
    cityList = []
    if request.method == 'POST':
        city = request.form['city']

    return render_template('prefs/locationPref.html', cityList=cityList)

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

