import functools
from flask import (
    Blueprint, jsonify, flash, g, redirect, render_template, request, session, url_for
)
from pyowm import OWM
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.wrappers import weatherWrapper
from flaskr.objects.clothing import Clothing
from flaskr.objects.clothingType import ClothingType
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

            user_id = session['user_id']
            db = get_db()

            # 1. get all clothes for user from db and store in tuple set.
            oldClothesList= []
            dbReturn = db.execute('SELECT c.*, ct.name, ct.default_temp_min, ct.default_temp_max, ct.id as ct_id, ct.cat_id, ct.default_rank FROM clothes c JOIN clothing_types ct on c.clothes_type_id = ct.id WHERE user_id = ? ORDER BY c.rank', (user_id,)).fetchall()
            # 0 = id, 1 = user_id, 2 = clothes_type_id, 3 = temp_min, 4 = temp_max, 5 = rank

            for d in dbReturn:
                ct = ClothingType(d['name'],d['default_temp_min'],d['default_temp_max'],d['ct_id'],d['cat_id'],d['default_rank'])
                c = Clothing(d['temp_min'],d['temp_max'],d['id'],d['user_id'],ct,d['rank'])
                oldClothesList.append(c)

            newClothesList = []
            # 0 = id, 1 = name, 2 = cat_id, 3 = default_rank, 4=default_temp_min, 5=default_temp_max
            for clothes in clothesList:
                d = db.execute('SELECT * FROM clothing_types WHERE name = ?', (clothes,)).fetchone()
                ct = ClothingType(d['name'],d['default_temp_min'],d['default_temp_max'],d['ct_id'],d['cat_id'],d['default_rank'])
                newClothesList.append(ct)

            # 2. loop through old ones, check to see if there are any old ones that aren't there anymore.
            for oldClothes in oldClothesList:
                found = False
                for newClothes in newClothesList:
                    if newClothes.id == oldClothes.clothesType.id:
                        found = True
                
                if found == False:
            #       a. if so, find all ranks below and subtract 1 from them.
                    for o in oldClothesList:
                        o.rank = o.rank - 1

            # 3. loop through new ones, see if there are any that weren't in the old ones.
            for newClothes in newClothesList:
                found = False
                for oldClothes in oldClothesList:
                    if newClothes.id == oldClothes.clothesType.id:
                        found = True
                if found == False:
                    same = -1
                    newUserRank = -1
                    for oldClothes in oldClothesList:
                        if newClothes.defaultRank == oldClothes.clothesType.defaultRank:
                            same = oldClothes.rank
                            
                            c = Clothing(oldClothes.minTemp,oldClothes.maxTemp,"",session['user_id'],newClothes.id,oldClothes.rank)
                            oldClothes.append(c)
                            newClothes.defaultRank = oldClothes.rank
                            #newClothes['']
                    if same == -1:      # need to insert into rank and push any below it -1      
            #           make user rank = to one below it, mark as added, find all ranks below and add 1 to them.
            #   a.  if so, check default ranks of old list to find which clothes should rank below it
                        for oldClothes in oldClothesList:
                            if oldClothes.clothesType.defaultRank > newClothes.defaultRank:
                                if newUserRank == -1:
                                    newUserRank = oldClothes.rank
                                oldClothes.rank = oldClothes.rank + 1
                                
                        c = Clothing(newClothes.defaultMinTemp,newClothes.defaultMaxTemp,"",session['user_id'],newClothes.id,same)
                        oldClothes.append(c)
                        oldClothesList.append(c)


            
            # 2. loop through new changed list, looking for maxes and mins that leave gaps or overlap.
            for oldClothes in oldClothesList:   
                currentRank = oldClothes.rank
                
                lowerRankClothes = []
                evenLowerRankClothes = []
                for o in oldClothesList:
                    if o.rank > currentRank:
                        lowerRankClothes.append(o)
                for o in oldClothesList:
                    if o.rank > (currentRank + 1):
                        evenLowerRankClothes.append(o)
                
                if oldClothes.minTemp > lowerRankClothes[0].maxTemp:     # a gap exists
                    higherMin = oldClothes.min
                    lowerMax = lowerRankClothes[0].maxTemp
                    if higherMin > 50 and lowerMax > 50:
                        #           bth over 50, so extend upper's min to old min.
                        oldClothes.minTemp = lowerMax
                    elif higherMin <= 50 and lowerMax <= 50:
                        #           both below 50, s0 extend lower's max to old max.
                        for o in lowerRankClothes:
                            o.maxTemp = higherMin 
                    else:
                        #           50 is in the middle, so split the difference between upper and lower.
                        oldClothes.minTemp = 50
                        for o in lowerRankClothes:
                            o.maxTemp = 50
                else:       # an overlap exists
                    currentMin = oldClothes.minTemp
                    currentMax = oldClothes.maxTemp
                    lowerMin = lowerRankClothes[0].minTemp
                    lowerMax = lowerRankClothes[0].maxTemp
                    evenLowerMin = evenLowerRankClothes[0].minTemp
                    evenLowerMax = evenLowerRankClothes[0].maxTemp

                    if lowerMin > currentMin:
                        # lower is totally inside of current (lower rank inside of higher rank)
                        oldClothes.minTemp = lowerMax
                    elif lowerMax < evenLowerMax:
                        # lower is totally inside of even lower (higher rank inside of lower rank)
                        for o in lowerRankClothes:
                            o.minTemp = evenLowerMax
                    elif currentMin < lowerMax and lowerMin == evenLowerMax:
                    #   current's min < lower's max ONLY overlap:
                    #       one was added as lightest yet, so lower's max changes to current's min
                        for o in lowerRankClothes:
                            o.maxTemp = currentMin
                    elif evenLowerMax > lowerMin and lowerMax == currentMin:
                    #   evenLower's max > lower's min ONLY overlap:
                    #       one was added as heaviest yet, so lower's min changes to evenLower's max
                        for o in lowerRankClothes:
                            o.minTemp = evenLowerMax
                    else:
                    #   so overlaps 2
                    #       current's min changes to lowers' max and evenLowers' max changes to lowers' min
                        oldClothes.minTemp = lowerMax
                        for o in evenLowerRankClothes:
                            o.maxTemp = lowerMin

            #   (if you ever run into multi ple clothes that fit criteria or share a rank, do it to all of them.)
            #   (if you are adding a new clothing that matches rank of old, match that old rank and don't push anything)
            #   (if clothing is left with less than 5 degrees, push things around it)
            # 3. delete all old clothes for user_id.
            # 4. add new clothes.
            db.execute('DELETE FROM clothes WHERE user_id=?', (session['user_id'],))
            
            db.executemany('INSERT INTO clothes(user_id,clothes_type_id,temp_min,temp_max,rank) VALUES (?,?,?,?,?)', oldClothesList)

            db.commit()
            # for clothes in clothesList:
            #     c = db.execute(
            #         'SELECT * FROM clothes WHERE name = ?', (clothes,)
            #     ).fetchone()

            #     if c is not None:
                    
            #         db.execute(
            #             'INSERT INTO user_x_clothes (user_id, clothes_id) VALUES (?, ?)',
            #             (session["user_id"],c['id'])
            #         )

            #         t = db.execute(
            #             'SELECT * FROM threshold WHERE user_id=? AND clothes_id=?', (session['user_id'],c['id'])
            #         ).fetchone()

            #         if t is None:   #insert new threshold
            #             db.execute(
            #                 'INSERT INTO threshold (user_id, clothes_id, threshold_min, threshold_max) VALUES (?, ?, ?, ?)',
            #                 (session["user_id"],c['id'],c['temp_min'],c['temp_max'])
            #             )

            # db.commit()
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

