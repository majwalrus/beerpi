from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import *
from kivy.uix.screenmanager import *
from kivy.lang import Builder

import os
import threading
import time
import ConfigParser


import pihealth
import probeclass
import configclass
#
# Global Variables
# ==================
# Used as globals as less overheads and in will be updated by using multiple threads.


glob_pihealth = pihealth.PiHealth()
glob_beerProbes = probeclass.BeerProbes()
glob_config = configclass.BeerConfig()


#
# KIVY
#

class BeerRightBar:
    def defaultBar(self, menuCanvas):
        pass

    def configBar(self, menuCanvas):
        pass

    def drawMenuBar(self, menuBar, menuCanvas):
        switcher = {
            "default": self.defaultBar,
            "config": self.configBar
        }
        func = switcher.get(menuBar, lambda: self.defaultBar)
        func(menuCanvas)


class DefaultRightBar(Widget):
    pass


class ConfigRightBar(Widget):
    pass


class BeerStatus(Screen):
    piTempLabel = StringProperty()
    hltTempLabel = StringProperty()
    boilTempLabel = StringProperty()
    hltSetTempLabel = StringProperty()
    boilSetTempLabel = StringProperty()

    def update(self, dt):
        self.piTempLabel = glob_pihealth.piTempStr
        self.hltTempLabel = glob_beerProbes.returnStrProbeVal(0)
        self.boilTempLabel = glob_beerProbes.returnStrProbeVal(1)

        self.hltSetTempLabel = str(glob_config.valHLTTargetTemp)
        self.boilSetTempLabel = str(glob_config.valBoilTargetTemp)
        pass

    def addhlt(self, *args):
        glob_config.valHLTTargetTemp +=1
        glob_config.valHLTTaperTemp +=1

    def subhlt(self, *args):
        glob_config.valHLTTargetTemp +=-1
        glob_config.valHLTTaperTemp +=-1


    def __init__(self, **kwargs):
        super(BeerStatus, self).__init__(**kwargs)
        self.menu = DefaultRightBar()
        self.add_widget(self.menu)


class BeerHLT(Screen):

    def update(self, dt):
        pass


class BeerBoil(Screen):

    def update(self, dt):
        pass


class BeerConfig(Screen):

    def update(self, dt):
        pass

    def __init__(self, **kwargs):
        super(BeerConfig, self).__init__(**kwargs)
        self.menu = ConfigRightBar()
        self.add_widget(self.menu)

class BeerSensors(Screen):

    def update(self,dt):
        for  tmp_probe in glob_beerProbes.probeList:
            tmp_LabelVal=str(tmp_probe.name)+" T: "+tmp_probe.probevalstr
            #self.probeLabelValue.append(tmp_LabelVal)
        pass

    probeLabelValue=[]
    tmp_LabelVal=StringProperty()

    def __init__(self, **kwargs):
        super(BeerSensors,self).__init__(**kwargs)
        self.menu = ConfigRightBar()
        self.add_widget(self.menu)
        self.add_widget(Label(text="Sensors",top=self.top+220))
        self.add_widget(Label(text="Total Beer Probes : "+str(glob_beerProbes.countProbes()),top=self.top+200))
        num=0
        #self.probeLabelValue.clear()
        for  tmp_probe in glob_beerProbes.probeList:
            tmp_LabelVal=str(tmp_probe.name)+" T: "+tmp_probe.probevalstr
            self.probeLabelValue.append(tmp_LabelVal)
            self.add_widget(Label(text=self.probeLabelValue[num], top=self.top + 160 - (num*30),x=self.x-220))
            num+=1


class BeerScreenManagement(ScreenManager):
    pass


class SimpleApp(App):
    screenmanager = Builder.load_file("main.kv")

    def update(self, dt):
        statusscreen = self.screenmanager.get_screen('Status')
        statusscreen.update(dt)

    def build(self):
        Clock.schedule_interval(self.update, 1)
        return self.screenmanager

#
# THREADS
#  These are used to do the intermittent monitoring and updating global values to reduce overhead of the
#  main program calling slow processes all the time.

def piHealthThread():
    while True:
        time.sleep(5)
        glob_pihealth.getPiTemp()

def tempProbeThread():
    while True:
        glob_beerProbes.updateProbes()

def elementThread():
    while True:
        pass

#
# MAIN
#  This is the main startup code. This will start the relevant threads, run the startup config code and
#  then start the Kivy App.

if __name__ == '__main__':

    print(glob_config.valHLTTargetTemp)

    threadTemp = threading.Thread(target=tempProbeThread)
    threadTemp.daemon=True
    threadTemp.start()

    threadHealth = threading.Thread(target=piHealthThread)
    threadHealth.daemon=True
    threadHealth.start()


    SimpleApp().run()
