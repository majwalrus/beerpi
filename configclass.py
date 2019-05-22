import ConfigParser
import os

class BeerConfig:

    configFile = './beer.ini'
    valHLTTargetTemp=0
    valHLTTaperTemp=0
    valBoilTargetTemp=0
    valBoilTaperTemp=0

    config = ConfigParser.ConfigParser()

    def __init__(self):
        if not os.path.isfile(self.configFile):
            self.createDefaultFile()
        else:
            self.loadConfigFile()

    def createDefaultFile(self):
        self.config.add_section("HLT")
        self.config.set("HLT","targettemp","76")
        self.config.set("HLT","tapertemp","75")

        self.config.add_section("Boil")
        self.config.set("Boil","targettemp","101")
        self.config.set("Boil","tapertemp","99")

        self.config.add_section("Probes")
        self.config.set("Probes","hlt","")
        self.config.set("Probes","boil","")

        with open(self.configFile,"wb") as config_file:
            self.config.write(config_file)

    def loadConfigFile(self):
        self.config.read(self.configFile)
        self.valHLTTargetTemp=int(self.config.get("HLT","targettemp"))
        self.valBoilTargetTemp=int(self.config.get("Boil","targettemp"))

        print("\n\rConfig File Dump\n\r")
        print(self.valHLTTargetTemp)
        print("\n\rEnd Config File Dump\n\r\n\r")






