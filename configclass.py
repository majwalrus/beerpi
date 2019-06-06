import ConfigParser
import os

from beerpiconstants import *

class ValElement:
    mainPower=0
    taperPower=0
    overPower=0

    targetTemp=0
    taperTemp=0

    sensorName=""

    gpio=0

    elementOn=0


    def __init__(self,mainpower,taperpower,overpower,elementon,targettemp,tapertemp,sensorname,tgpio):
        self.mainPower=mainpower
        self.taperPower=taperpower
        self.overPower=overpower
        self.elementOn=elementon
        self.targetTemp=targettemp
        self.taperTemp=tapertemp
        self.sensorName=sensorname
        self.gpio=tgpio

    def dumpData(self):
        strdump="mainPower=%s, taperPower=%s, overPower=%s, elementOn=%s, targetTemp=%s, taperTemp=%s, sensorName=%s, gpio=%s.\n"  % (self.mainPower,self.taperPower,self.overPower,self.elementOn,self.targetTemp,self.taperTemp,self.sensorName,self.gpio)
        return strdump

    def __str__(self):
        return self.dumpData()

    def __repr__(self):
        return self.dumpData()


class BeerConfig:

    listElement=["HLT","Boil"]

    configFile = './beer.ini'
    valHLTTargetTemp=0
    valHLTTaperTemp=0
    valBoilTargetTemp=0
    valBoilTaperTemp=0

    boolHLTElementOn=False
    boolBoilElementOn=False

    valHLTMainPower=0
    valBoilMainPower=0
    valHLTTaperPower=0
    valBoilTaperPower=0
    valHLTOverPower=0
    valBoilOverPower=0

    valElement = []

    sensorHLT=""
    sensorBoil=""
    gpioHLT=""
    gpioBoil=""

    config = ConfigParser.ConfigParser(allow_no_value=True)

    def __init__(self):
        if not os.path.isfile(self.configFile):     # check config file exists
            self.createDefaultFile()                # it doesn't, so write the default file and continue
        self.loadConfigFile()                       # now read the config file

    def createDefaultFile(self):
        #self.config.add_section("DEFAULT")          # DEFAULT value section
        self.config.set("DEFAULT","mainpower","10")
        self.config.set("DEFAULT","taperpower","6")
        self.config.set("DEFAULT","overpower","0")
        self.config.set("DEFAULT","targettemp","100")
        self.config.set("DEFAULT","tapertemp","97")

        self.config.add_section("HLT")              # HLT value section
        self.config.set("HLT","targettemp","76")
        self.config.set("HLT","tapertemp","72")
        self.config.set("HLT","gpio","6")
        self.config.set("HLT","taperpower","5")

        self.config.add_section("Boil")             # Boil value section
        self.config.set("Boil","targettemp","100")
        self.config.set("Boil","tapertemp","97")
        self.config.set("Boil","gpio","5")

        self.config.add_section("Sensors")          # Sensors  value section

        for tempElement in self.listElement:
            self.config.set("Sensors",tempElement,"")

#        self.config.set("Sensors","boil","")

        self.config.add_section("Calibration")          # Sensors  value section
        with open(self.configFile,"wb") as config_file: # Now write the default value file
            self.config.write(config_file)

    def getConfig(self,section,value,fallback):
        if not self.config.has_section(section):            # check section exists, this stops exception errors
            self.config.add_section(section)                # it doesn't so add it for future reference
            self.config.set(section,value,fallback)         # now add the value and fallback
            return fallback                                 # return fallback
        else:
            if not self.config.has_option(section,value):   # check value exists
                self.config.set(section, value, fallback)   # it doesn't so add it and set it to fallback
                return fallback
            else:
                return self.config.get(section,value,fallback)  # section exists so attempt to get value, if not fallback


    def loadConfigFile(self):
        self.config.read(self.configFile)

        for tempElement in self.listElement:
            tMainPower=int(self.getConfig(tempElement,"mainpower","10"))
            tTaperPower=int(self.getConfig(tempElement,"taperpower","6"))
            tOverPower=int(self.getConfig(tempElement,"overpower","2"))
            tTargetTemp=int(self.getConfig(tempElement,"targettemp","100"))
            tTaperTemp=int(self.getConfig(tempElement,"tapertemp","97"))
            tSensor=self.getConfig("Sensors",tempElement,"")
            tGPIO=self.getConfig(tempElement,"gpio","0")
            self.valElement.append(ValElement(tMainPower,tTaperPower,tOverPower,False,tTargetTemp,tTaperTemp,tSensor,tGPIO))

        self.valHLTTargetTemp=int(self.getConfig("HLT","targettemp","76"))
        self.valHLTTaperTemp=int(self.getConfig("HLT","tapertemp","75"))
        self.valBoilTargetTemp=int(self.getConfig("Boil","targettemp","101"))
        self.valBoilTaperTemp=int(self.getConfig("Boil","tapertemp","98"))
        self.sensorBoil=self.getConfig("Sensors","boil","")
        self.sensorHLT=self.getConfig("Sensors","hlt","")
        self.gpioHLT=self.getConfig("HLT","gpio","6")
        self.gpioBoil=self.getConfig("Boil","gpio","5")

        self.valHLTMainPower = int(self.getConfig("HLT","mainpower","10"))
        self.valBoilMainPower = int(self.getConfig("Boil","mainpower","10"))
        self.valHLTTaperPower = int(self.getConfig("HLT","taperpower","5"))
        self.valBoilTaperPower = int(self.getConfig("Boil","taperpower","6"))
        self.valHLTOverPower = int(self.getConfig("HLT","overpower","2"))
        self.valBoilOverPower = int(self.getConfig("Boil","overpower","2"))


        for tempArr in self.valElement:
            print(tempArr)

#        print("\n\rConfig File Dump\n\r")
#        print(self.valHLTTargetTemp)
#        print(self.valBoilTargetTemp)
#        print(self.sensorHLT)
#        print(self.sensorBoil)
#        print("\n\rEnd Config File Dump\n\r\n\r")

    def updateConfigFile(self):
        self.config.set("Sensors","hlt",self.sensorHLT)
        self.config.set("Sensors","boil",self.sensorBoil)

        with open(self.configFile,"wb") as config_file:
            self.config.write(config_file)

    def returnConfigVal(self,value,id):
        if value=="TaperPower":
            if id==DEF_HLT:
                return self.valHLTTaperPower
            if id==DEF_BOIL:
                return self.val





