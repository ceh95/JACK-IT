class Clothing:

    def __init__(self, minTemp, maxTemp, id="", userId ="", clothesType=None, rank=""):
        self.minTemp = minTemp
        self.maxTemp = maxTemp
        self.id = id
        self.user_id = userId
        self.clothesType = clothesType
        self.rank = rank