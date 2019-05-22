import ConfigParser
import os

class BeerConfig:

    configFile = './beer.ini'

    def __init__(self):
        if not os.path.isfile(self.configFile):
            self.createDefaultFile()



    config = ConfigParser.ConfigParser()

    def createDefaultFile(self):
        self.config.add_section("HLT")
        self.config.set("Settings","targettemp","76")
        self.config.set("Settings","tapertemp","75")

        self.config.add_section("Boil")
        self.config.set("Settings","targettemp","101")
        self.config.set("Settings","tapertemp","99")

        self.config.add_section("Probes")





