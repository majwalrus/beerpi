import ConfigParser
import os

class BeerConfig:

    configFile = './beer.ini'

    def __init__(self):
        if not os.path.isfile(self.configFile):
            self.createDefaultFile()

    valHLTTargetTemp=0
    valHLTTaperTemp=0
    valBoilTargetTemp=0
    valBoilTaperTemp=0

    config = ConfigParser.ConfigParser()

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
        valHLTTargetTemp=self.config.get("HLT","targettemp")

        print("\n\rConfig File Dump\n\r")
        print(valHLTTargetTemp)
        print("\n\rEnd Config File Dump\n\r\n\r")






