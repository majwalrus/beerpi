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
    piTemp = PiTemp()
    piTempLabel = StringProperty()

    def update(self, dt):
        self.piTemp.getPiTemp()
        self.piTempLabel = self.piTemp.tempstr
        pass

    def __init__(self, **kwargs):
        super(BeerStatus, self).__init__(**kwargs)
        self.menu = DefaultRightBar()
        self.add_widget(self.menu)


class BeerHLT(Screen):
    piTemp = PiTemp()

    def update(self, dt):
        pass


class BeerBoil(Screen):
    piTemp = PiTemp()

    def update(self, dt):
        pass


class BeerConfig(Screen):
    piTemp = PiTemp()

    def update(self, dt):
        pass

    def __init__(self, **kwargs):
        super(BeerConfig, self).__init__(**kwargs)
        self.menu = ConfigRightBar()
        self.add_widget(self.menu)


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


if __name__ == '__main__':
    SimpleApp().run()
