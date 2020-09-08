import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from flaskr.objects.clothing import Clothing
from flaskr.objects.clothingType import ClothingType

bp = Blueprint('auth', __name__)

@bp.route('/')
def index():
    return render_template('auth/index.html')

@bp.route('/registerUserPass', methods=('GET', 'POST'))
def registerUserPass():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()

            user = db.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()

            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('auth.registerLocation'))

        flash(error)

    return render_template('auth/registerUserPass.html')

@bp.route('/registerLocation', methods=('GET', 'POST'))
def registerLocation():
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
            return redirect(url_for('auth.registerClothing'))

    return render_template('auth/registerLocation.html')

@bp.route('/registerClothing', methods=('GET', 'POST'))
def registerClothing():
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
            dbReturn = db.execute('SELECT c.* FROM clothes c WHERE user_id = ? ORDER BY c.rank', (user_id,)).fetchall()
            # 0 = id, 1 = user_id, 2 = clothes_type_id, 3 = temp_min, 4 = temp_max, 5 = rank

            for d in dbReturn:
                ct = ClothingType(d['clothes_type_id'])
                c = Clothing(d['temp_min'],d['temp_max'],d['id'],d['user_id'],ct,d['rank'])
                oldClothesList.append(c)

            newClothesList = []
            # 0 = id, 1 = name, 2 = cat_id, 3 = default_rank, 4=default_temp_min, 5=default_temp_max
            for clothes in clothesList:
                d = db.execute('SELECT * FROM clothing_types WHERE name = ?', (clothes,)).fetchone()
                if d is None:
                    continue
                ct = ClothingType(d['id'])
                newClothesList.append(ct)

            # 2. loop through old ones, check to see if there are any old ones that aren't there anymore.
            removedList = []
            for oldClothes in oldClothesList:
                found = False
                for newClothes in newClothesList:
                    if newClothes.id == oldClothes.clothesType.id:
                        found = True
                
                if found == False:
            #       a. if so, find all ranks below and subtract 1 from them.
                    if oldClothes.rank != '':
                        sameRankList = []
                        for o in oldClothesList:
                            if o.clothesType.categoryID == oldClothes.clothesType.categoryID and o.rank == oldClothes.rank:
                                sameRankList.append(o)
                        if len(sameRankList) <= 1:
                            for o in oldClothesList:
                                if (o.rank != '') and (o.clothesType.categoryID == oldClothes.clothesType.categoryID) and (o.rank > oldClothes.rank):
                                    o.rank = o.rank - 1
                    removedList.append(oldClothes)
            for r in removedList:
                oldClothesList.remove(r)

            # 3. loop through new ones, see if there are any that weren't in the old ones.
            for newClothes in newClothesList:
                found = False

                oldClothesInCat = []
                for o in oldClothesList:
                    if newClothes.categoryID == o.clothesType.categoryID:
                        oldClothesInCat.append(o)
                
                for oldClothes in oldClothesInCat:
                    if newClothes.id == oldClothes.clothesType.id:
                        found = True
                if found == False:
                    if newClothes.defaultRank == '':    
                        c = Clothing(newClothes.defaultMinTemp,newClothes.defaultMaxTemp,"",session['user_id'],newClothes,'')
                        oldClothesList.append(c)
                    elif len(oldClothesInCat) <= 0:   
                        c = Clothing(newClothes.defaultMinTemp,newClothes.defaultMaxTemp,"",session['user_id'],newClothes,1)
                        oldClothesList.append(c)
                    else:
                        same = -1
                        for oldClothes in oldClothesInCat:
                            # this case is for adding new clothing of same default rank, just copy from other clothes
                            if newClothes.defaultRank == oldClothes.clothesType.defaultRank:
                                same = oldClothes.rank
                                
                                c = Clothing(oldClothes.minTemp,oldClothes.maxTemp,"",session['user_id'],newClothes,oldClothes.rank)
                                oldClothesList.append(c)
                                break
                        if same == -1:      # need to insert into rank and push any below it -1      
                            # make user rank = to one below it, mark as added, find all ranks below and add 1 to them.
                            newUserRank = -1
                            someRankedLower = False
                            lowestRankInCategory = 1
                            for oldClothes in oldClothesInCat:
                                if oldClothes.rank > lowestRankInCategory:
                                    lowestRankInCategory = oldClothes.rank
                                if oldClothes.clothesType.defaultRank > newClothes.defaultRank:
                                    someRankedLower = True
                                    if newUserRank == -1:
                                        newUserRank = oldClothes.rank
                                    else:
                                        if oldClothes.rank < newUserRank:
                                            newUserRank = oldClothes.rank
                                    oldClothes.rank = oldClothes.rank + 1

                            if someRankedLower == False:
                                # if there were none in the category with a lower rank, then set it equal to the lowest rank
                                newUserRank = lowestRankInCategory + 1

                            c = Clothing(newClothes.defaultMinTemp,newClothes.defaultMaxTemp,"",session['user_id'],newClothes,newUserRank)
                            oldClothesList.append(c)

            for oldClothes in oldClothesList:
                sameCatList = []
                for o in oldClothesList:
                    if o.clothesType.categoryID == oldClothes.clothesType.categoryID:
                        sameCatList.append(o)

                if oldClothes.rank == 1:
                    oldClothes.maxTemp = -1
                    if len(sameCatList) == 1:
                        oldClothes.minTemp = -1

            # 2. loop through new changed list, looking for maxes and mins that leave gaps or overlap.
            for oldClothes in oldClothesList:   
                currentRank = oldClothes.rank
                if currentRank == '':
                    continue
                currentCategory = oldClothes.clothesType.categoryID


                oldClothesInCat = []
                for o in oldClothesList:
                    if o.clothesType.categoryID == currentCategory:
                        oldClothesInCat.append(o)
                
                oldClothesInCat.sort(key=lambda x: x.rank,reverse=True)
                lowerRankClothes = []
                evenLowerRankClothes = []
                for o in oldClothesInCat:
                    if o.rank ==  (currentRank+1):
                        lowerRankClothes.append(o)
                for o in oldClothesInCat:
                    if o.rank == (currentRank + 2):
                        evenLowerRankClothes.append(o)
                
                if len(lowerRankClothes) == 0:
                    # there is no lower ranked clothing in category, so there can't be a gap or overlap. Set min to -1.
                    oldClothes.minTemp = -1
                    continue

                if (lowerRankClothes[0].maxTemp != -1) and (oldClothes.minTemp > lowerRankClothes[0].maxTemp):     # a gap exists
                    higherMin = oldClothes.minTemp
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
                elif (oldClothes.minTemp < lowerRankClothes[0].maxTemp) or (lowerRankClothes[0].maxTemp == -1):       # an overlap exists
                    currentMin = oldClothes.minTemp
                    currentMax = oldClothes.maxTemp
                    lowerMin = lowerRankClothes[0].minTemp
                    lowerMax = lowerRankClothes[0].maxTemp

                    if lowerMin >= 45:
                        if currentMin < (lowerMin +5):
                            #make lower max = lower min + 5 and current min = same value
                            for o in lowerRankClothes:
                                o.maxTemp = lowerMin+5
                            oldClothes.minTemp = lowerMin+5
                        else:
                            oldClothes.minTemp = lowerMax
                    else:
                        if lowerMax > (currentMax -5):
                            # make currentMin = currentMax -5 and lowerMax = same value
                            oldClothes.minTemp = currentMax -5
                            for o in lowerRankClothes:
                                o.maxTemp = currentMax -5
                        else:
                            o.maxTemp = currentMin
            # 3. delete all old clothes for user_id.
            # 4. add new clothes.
            db.execute('DELETE FROM clothes WHERE user_id=?', (session['user_id'],))
            
            clothesToAddList = []
            for c in oldClothesList:
                clothesToAddList.append((c.user_id,c.clothesType.id,c.minTemp,c.maxTemp,c.rank))

            db.executemany('INSERT INTO clothes(user_id,clothes_type_id,temp_min,temp_max,rank) VALUES (?,?,?,?,?)', clothesToAddList)

            db.commit()
            return redirect(url_for('auth.registerConfirmation'))


    return render_template('auth/registerClothing.html')


@bp.route('/registerConfirmation', methods=('GET', 'POST'))
def registerConfirmation():
    return render_template('auth/registerConfirmation.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['location_id'] = user['location_id']
            return redirect(url_for('prediction.prediction'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view