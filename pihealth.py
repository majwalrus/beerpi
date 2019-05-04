


class PiHealth:

    piTemp=0
    piTempStr=""

    def getPiTemp(self):
        self.piTemp=os.popen("vcgencmd measure_temp").readln()
        self.piTemp=self.temp.replace("temp=","")
        self.piTempStr=str(self.piTemp)
        
    def __init__(self):
        self.getPiTemp()
    
    
