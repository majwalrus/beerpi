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
        if not os.path.isfile(self.configFile):     # check config file exists
            self.createDefaultFile()                # it doesn't, so write the default file and continue
        self.loadConfigFile()                       # now read the config file

    def createDefaultFile(self):
        #self.config.add_section("DEFAULT")          # DEFAULT value section
        self.config.set("DEFAULT","mainpower","10")
        self.config.set("DEFAULT","taperpower","6")
        self.config.set("DEFAULT","overpower","0")

        self.config.add_section("HLT")              # HLT value section
        self.config.set("HLT","targettemp","76")
        self.config.set("HLT","tapertemp","75")

        self.config.add_section("Boil")             # Boil value section
        self.config.set("Boil","targettemp","101")
        self.config.set("Boil","tapertemp","99")

        self.config.add_section("Sensors")          # Sensors  value section
        self.config.set("Sensors","hlt","")
        self.config.set("Sensors","boil","")

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
        self.valHLTTargetTemp=int(self.getConfig("HLT","targettemp","74"))
        self.valBoilTargetTemp=int(self.getConfig("Boil","targettemp","101"))
        self.sensorBoil=self.getConfig("Sensors","boil","")
        self.sensorHLT=self.getConfig("Sensors","hlt","")

        print("\n\rConfig File Dump\n\r")
        print(self.valHLTTargetTemp)
        print(self.valBoilTargetTemp)
        print(self.sensorHLT)
        print(self.sensorBoil)
        print("\n\rEnd Config File Dump\n\r\n\r")

    def updateConfigFile(self):
        self.config.set("Sensors","hlt",self.sensorHLT)
        self.config.set("Sensors","boil",self.sensorBoil)

        with open(self.configFile,"wb") as config_file:
            self.config.write(config_file)






