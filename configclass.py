import ConfigParser
import os

class BeerConfig:

    configFile = './beer.ini'
    valHLTTargetTemp=0
    valHLTTaperTemp=0
    valBoilTargetTemp=0
    valBoilTaperTemp=0

    sensorHLT=""
    sensorBoil=""

    config = ConfigParser.ConfigParser(allow_no_value=True)

    def __init__(self):
        if not os.path.isfile(self.configFile):
            self.createDefaultFile()
        else:
            self.loadConfigFile()

    def createDefaultFile(self):
        self.config.add_section("DEFAULT")
        self.config.set("DEFAULT","mainpower","10")
        self.config.set("DEFAULT","taperpower","6")
        self.config.set("DEFAULT","overpower","0")

        self.config.add_section("HLT")
        self.config.set("HLT","targettemp","76")
        self.config.set("HLT","tapertemp","75")

        self.config.add_section("Boil")
        self.config.set("Boil","targettemp","101")
        self.config.set("Boil","tapertemp","99")

        self.config.add_section("Sensors")
        self.config.set("Sensors","hlt","")
        self.config.set("Sensors","boil","")

        with open(self.configFile,"wb") as config_file:
            self.config.write(config_file)

    def getConfig(self,section,value,fallback):
        if not self.config.has_section(section):
            return False
        else:
            return self.config.get(section,value,fallback)


    def loadConfigFile(self):
        self.config.read(self.configFile)
        #self.valHLTTargetTemp=int(self.config.get("HLT","targettemp"),"74")
        self.valHLTTargetTemp=int(self.getConfig("HLT","targettemp","74"))

        self.valBoilTargetTemp=int(self.config.get("Boil","targettemp","101"))

        self.sensorBoil=self.config.get("Sensors","boil","")
        self.sensorHLT=self.config.get("Sensors","hlt","")


        print("\n\rConfig File Dump\n\r")
        print(self.valHLTTargetTemp)
        print("\n\rEnd Config File Dump\n\r\n\r")

    def updateConfigFile(self):
        with open(self.configFile,"wb") as config_file:
            self.config.write(config_file)






