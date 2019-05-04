# Class PiHealth
#  This is for monitoring the health of the raspberry pi, so that it can be shutdown
#  if there are problems such as overheating.

import os

class PiHealth:

    piTemp=0
    piTempStr=""

    def getPiTemp(self):    # Uses vcgencmd to obtain the Pi's temperature
        self.piTemp=os.popen("vcgencmd measure_temp").readline()
        self.piTemp=self.temp.replace("temp=","")
        self.piTempStr=str(self.piTemp)
        
    def __init__(self):
        self.getPiTemp()
    
    
