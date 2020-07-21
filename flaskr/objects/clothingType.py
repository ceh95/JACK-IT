from flaskr.db import get_db

class ClothingType:
    
    def __init__(self, id):
        db = get_db()
        dbReturn = db.execute('SELECT * FROM clothing_types ct WHERE id = ?', (id,)).fetchone()
        self.name = dbReturn['name']
        self.defaultMinTemp = dbReturn['default_temp_min']
        self.defaultMaxTemp = dbReturn['default_temp_max']
        self.id = id
        self.categoryID = dbReturn['cat_id']
        self.defaultRank = dbReturn['default_rank']
        self.status = dbReturn['status']
        self.rainy = dbReturn['rain_only']
        self.snowy = dbReturn['snow_only']
        self.windy = dbReturn['windy_only']

    # def __init__(self, name, defaultMinTemp, defaultMaxTemp, id="", categoryID="", defaultRank=""):
    #     self.name = name
    #     self.defaultMinTemp = defaultMinTemp
    #     self.defaultMaxTemp = defaultMaxTemp
    #     self.id = id
    #     self.categoryID = categoryID
    #     self.defaultRank = defaultRank