from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.wrappers import weatherWrapper
from flaskr.objects.clothing import Clothing
from flaskr.objects.clothingType import ClothingType

import math
bp = Blueprint('prediction', __name__)

@bp.route('/')
@login_required
def index():
    owm = weatherWrapper.getOWM()
    mgr = owm.weather_manager()

    obs = mgr.weather_at_id(int(session['location_id']))
    w = obs.weather

    heat_index = getHeatIndex(w.temperature('fahrenheit')['temp'], w.humidity)

    db = get_db()
    dbReturn = db.execute('SELECT c.*, ct.cat_id FROM clothes c JOIN clothing_types ct on c.clothes_type_id = ct.id WHERE user_id=? ORDER BY ct.cat_id', (session['user_id'],)).fetchall()
    
    clothesList = []
    for c in dbReturn:
        ct = ClothingType(c['clothes_type_id'])
        c = Clothing(c['temp_min'],c['temp_max'],c['id'],c['user_id'],ct,c['rank'])
        clothesList.append(c)

    prediction = getPrediction(w, clothesList)

    return render_template('prediction/index.html', weather=w, heat_index=heat_index, predictions=prediction)

def getHeatIndex(T, RH):
    simple = 0.5 * (T + 61.0 + ((T-68.0)*1.2) + (RH*0.094))
    avg = (simple + T) / 2

    if avg < 80:
        ret = avg
    else:
        ret = -42.379 + 2.04901523*T + 10.14333127*RH - .22475541*T*RH - .00683783*T*T - .05481717*RH*RH + .00122874*T*T*RH + .00085282*T*RH*RH - .00000199*T*T*RH*RH
        if RH < 13 and (T >=80 and T <= 112):
            ADJ = ((13-RH)/4)* math.sqrt((17-abs(T-95.))/17)
            ret = ret - ADJ
        
        if RH > 85 and (T >= 80 and T <= 87):
            ADJ = ((RH-85)/10) * ((87-T)/5)
            ret = ret + ADJ
    return ret

def getWindChill(T,V):
    if T < 50 and V > 3:
        ret = 35.74 + 0.6215*T - 35.75*(V**0.16) + 0.4275*T*(V**0.16)
    else:
        ret = T
    return ret

def getPrediction(weather, clothes):
    # notes: each clothing type will have a temperature range and one or more additional triggers (eg. sunglasses if 
    # sunny, raincoat if raining, etc.). If a user does not have a particular type of clothing, then default to wider
    # range. (ex: no shorts, so suggest next lightest clothes). If the mins/maxes extend into another range, figure
    # out what to do with that.
    #
    # ranges:
    #   Tank Top: above 80
    #   Short Sleeve Shirt: above 65
    #   Long Sleeve Shirt: between 55 and 64
    #   Sweater: between 40 and 64
    #   Hoodie: between 40 and 64
    #   Jacket: between 40 and 55
    #   Coat: below 40
    #   Shorts: above 70
    #   Capri Pants: between 60 and 75
    #   Long Pants: below 70
    #   Hat: below 40
    #   Scarf: below 30 or windy
    #   Gloves: below 30 
    #   Sunglasses: sunny
    #   Sunscreen: sunny 
    ret = ''
    temp = weather.temperature('fahrenheit')['temp']
    tempMin = weather.temperature('fahrenheit')['temp_min']
    tempMax = weather.temperature('fahrenheit')['temp_max']
    status = weather.detailed_status
    windSpeed = weather.wind(unit='miles_hour')['speed']
    if weather.wind(unit='miles_hour').get('gust'):
        wind_gust = weather.wind(unit='miles_hour')['gust']
    humidity = weather.humidity
    if weather.rain.get('1h'):
        rainAmount = weather.rain['1h']
    if weather.snow.get('1h'):
        snowAmount = weather.snow['1h']

    heat_index_min = getHeatIndex(tempMin, humidity)
    heat_index = getHeatIndex(temp, humidity)
    heat_index_max = getHeatIndex(tempMax, humidity)

    wind_chill_min = getWindChill(heat_index_min, windSpeed)
    wind_chill = getWindChill(heat_index, windSpeed)
    wind_chill_max = getWindChill(heat_index_max, windSpeed)

    suggestions = []
    for c in clothes:
        if (c.minTemp == -1 or c.minTemp < wind_chill) and (c.maxTemp == -1 or c.maxTemp >= wind_chill):
            if c.clothesType.status != "":
                if c.clothesType.status in status.lower():
                    suggestions.append(c)
            else:
                suggestions.append(c)

    # check for mins/maxes that are different suggestions
    ret = suggestions
    return ret