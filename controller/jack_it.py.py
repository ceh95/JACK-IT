from flask import Flask
from pyowm import OWM

app = Flask(__name__)

API_key = '9a8561a73ff855c7bd462930128a5226'
owm = OWM(API_key)
mgr = owm.weather_manager()

@app.route('/')
# default web page
def hello_world():
    obs = mgr.weather_at_id(5188029)
    w = obs.weather
    return str(w.temperature('fahrenheit')['temp'])
