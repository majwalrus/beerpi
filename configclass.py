import configparser
import os

class BeerConfig:

    def __init__(self):
        if not os.path.exists(self.configFile)
            self.createDefaultFile()



    configFile = './beer.ini'
    configParser = configparser.ConfigParser()

    def createDefaultFile(self):
        config.add_section("HLT")
        config.set("Settings","targettemp","76")
        config.set("Settings","tapertemp","75")

        config.add_section("Boil")
        config.set("Settings","targettemp","101")
        config.set("Settings","tapertemp","99")

        config.add_section("Probes")





