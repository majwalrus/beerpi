# beerpi
Display and control application for Raspberry PI for brewing (hopefully) better beer.

The aim of this project is to help automate some of my homebrewing process. Specifically
the Hot Liquor Tank (HLT) and the boil kettle.

In my setup both have 5.5kW elements, and anyone that does homebrewing will know that tight
temperature control of the HLT water is important for the mash and sparging processes. This
program could be used for most setups, and indeed as the SSRs I used to control the elements
are rated up to 40A potentially much larger elements that I have in my setup.

In addition bringing a kettle to the boil with a 5.5kW element is faster and therefore
better, however it is overkill for maintaining the boil and could do with being controlled
at that stage to have a nice rolling boil using less electricity (so less £/$), less risk of
scorching and also less boil off so again more control over the process. This will hopefully
lead to better beer.

Note: this is developed to work using Kivy on the offical Raspberry Pi 7" touchscreen. If you
wish to alter the code for a different screen you will need to adjust the .kv file and also
the dynamically created widgets with main.py.

Also its a good excuse to mess around with a Pi.

Current Version 0.1a

Version History

0.1a

* probeclass.py completed for managing the temperature probes.
* pihealth.py added, has temperature monitoring code for making sure the Raspberry Pi does not overheat.
* set desired HLT temperature.
* configclass.py added, for loading and saving config files.

TODO:

* SOFTWARE complete GUI elements using Kivi
* SOFTWARE assign temperature probes easily in menu system
* SOFTWARE calibrate temperature probes to ensure accurate temperatures recorded
* SOFTWARE record temperature calibration and load on startup
* SOFTWARE create shutdown button and confirmation

* SOFTWARE control SSRs and switch elements off and on
* SOFTWARE switch off SSR if greater than desired HLT temperature
* SOFTWARE feather SSR as approaching HLT temperature
* SOFTWARE feather SSR at boil temperature
