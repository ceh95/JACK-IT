from flaskr.objects.clothing import Clothing

class Threshold:
    
    def __init__(self, clothing, minTemp, maxTemp):
        self.clothing = Clothing(clothing.name, clothing.minTemp, clothing.maxTemp)
        self.minTemp = minTemp
        self.maxTemp = maxTemp