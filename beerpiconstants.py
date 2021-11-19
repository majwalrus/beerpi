# This defines the constant variables used throughout the project



LIST_ELEMENTS = ["HLT", "Boil","RIMS","Mash"]
LIST_ELEMENTS_ID = [0,1,2,3]
LIST_ELEMENTS_AUTOCONTROL = [True,True,True,False]

LIST_FLOW = ["MashIn","KettleIn"]
LIST_FLOW_ID = [0,1]
LIST_FLOW_GPIO = [19,26]

DEF_HLT         =   LIST_ELEMENTS_ID[0]
DEF_BOIL        =   LIST_ELEMENTS_ID[1]
DEF_RIMS        =   LIST_ELEMENTS_ID[2]
DEF_MASH        =   LIST_ELEMENTS_ID[3]
DEF_RIMSFLOW    =   LIST_FLOW_ID[0]

LIST_ENERGENIE_ID = [1,2]

PUMP_METHOD_ENERGENIE = 1
PUMP_METHOD_ARDWIFI = 2


#   RIMS Calculation Constants

DEFAULT_AMBIENT_TEMPERATURE = 18       # Ambient room temperature, a later extension project would be having a temp probe for ambient temperature
CONST_STEFAN_BOLTZ = 0.00000005670374419
CONST_EMISSIVITY = 0.54
CONST_PIPEINSULATION = 0        #   for calculating surface area of the pipe, set to 0 if no insulation
CONST_INSULATIONK = 0.05        #   k value for piping insulation
CONST_PIPEOUTER = 21            #   outer diameter of 1/2 BSP in mm
CONST_PIPEINNER = 19.1          #   inner diameter of 1/2 BSP in mm
CONST_PIPEK = 16.2              #   k value for piping (stainless steel)
CONST_PIPELENGTH = 2            #   length of piping in m
CONST_ELEMENTSTRENGTH = 2200    #   strength of the RIMS element in W