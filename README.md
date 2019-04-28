# beerpi
Display and control application for Raspberry PI for brewing (hopefully) better beer.

The aim of this project is to help automate some of my homebrewing process. Specifically
the Hot Liquor Tank (HLT) and the boil kettle.

Both have 5.5kW elements, and anynone that does homebrewing will know that tight
temperature control of the HLT water is important for the mash and sparging processes.

In addition bringing a kettle to the boil with a 5.5kW element is faster and therefore
better, however it is overkill for maintaining the boil and could do with being controlled
at that stage to have a nice rolling boil using less electricity (so less £/$), less risk of
scorching and also less boil off so again more control over the process. This will hopefully
lead to better beer.

Also its a good excuse to mess around with a Pi.

Current Version 0.01a

Version History

0.1a

* probeclass.py completed for managing the temperature probes


TODO:

* SOFTWARE create GUI elements using Kivi
* SOFTWARE assign temperature probes easily in menu system
* SOFTWARE calibrate temperature probes to ensure accurate temperatures recorded
* SOFTWARE record temperature calibration and load on startup
* SOFTWARE set desired HLT temperature

* HARDWARE wire in SSRs

* SOFTWARE control SSRs and switch elements off and on
* SOFTWARE switch off SSR if greater than desired HLT temperature
* SOFTWARE feather SSR as approaching HLT temperature
* SOFTWARE feather SSR at boil temperature
