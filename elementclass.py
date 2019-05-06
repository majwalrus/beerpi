import time
import glob
import os

class ElementControlClass:
    mainPower = 10  # The intensity of the element when under taperTemp
    taperPower = 6  # Lower intensity to this when over targetTemp but under targetTemp
    overPower = 0   # Intensity of element when over targetTemp

    targetTemp = 76
    taperTemp = 75

    def __init__(self):
        pass

    def setTaperPower(self,pow):
        if pow>10:
            return False
        if pow<0:
            return False
        self.taperPower=pow
        return True

    def setOverPower(self,pow):
        if pow>10:
            return False
        if pow<0:
            return False
        self.overPower=pow
        return True

    def setMainPower(self,pow):
        if pow>10:
            return False
        if pow<0:
            return False
        self.mainPower=pow
        return True

    def setTargetTemp(self,temp):
        if temp>105:
            return False
        if temp<0
            return False
        self.targetTemp=temp
        return True

    def setTaperTemp(self,temp):
        if temp>105:
            return False
        if temp<0
            return False
        self.taperTemp=temp
        return True

    def returnPower(self,temp):
        if temp<self.targetTemp and temp<self.taperTemp:
            return self.mainPower
        if temp>self.targetTemp:
            return self.overPower
        if temp>self.taperTemp and temp<self.targetTemp:
            return self.taperPower
        return 0

