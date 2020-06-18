from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.wrappers import weatherWrapper

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

    return render_template('prediction/index.html', weather=w, heat_index=heat_index)

def getHeatIndex(T, RH):
    simple = 0.5 * (T + 61.0 + ((T-68.0)*1.2) + (RH*0.094))
    avg = (simple + T) / 2

    if avg < 80:
        ret = avg
    else:
        ret = -42.379 + 2.04901523*T + 10.14333127*RH - .22475541*T*RH - .00683783*T*T - .05481717*RH*RH + .00122874*T*T*RH + .00085282*T*RH*RH - .00000199*T*T*RH*RH
        if RH < 80 and (T >=80 and T <= 112):
            ADJ = ((13-RH)/4)* math.sqrt((17-abs(T-95.))/17)
            ret = ret - ADJ
        
        if RH > 85 and (T >= 80 and T <= 87):
            ADJ = ((RH-85)/10) * ((87-T)/5)
            ret = ret + ADJ
    return ret