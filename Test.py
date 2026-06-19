import time
from enum import Enum

from skyfield.api import load as sf_load
from skyfield.api import wgs84 #handles positioning

from skyfield.almanac import find_discrete, risings_and_settings

class AO_type(Enum):
        PLANET = 0
        MOON = 1
        DWARF_PLANET = 2

#general "struct" to help bridge the gap between astrodata and skyfield data
class AstroObject:
        def __init__(self, ad_name, sf_name, type):
                self.sf_name = sf_name
                self.ad_name = ad_name
                self.type = type

        

PLANETS = [
        AstroObject('mercury', 'mercury',AO_type.PLANET), 
        AstroObject('venus', 'venus', AO_type.PLANET),
        AstroObject('moon', 'moon', AO_type.MOON), 
        AstroObject('mars', 'mars barycenter', AO_type.PLANET),
        AstroObject('jupiter', 'jupiter barycenter', AO_type.PLANET),
        AstroObject('saturn', 'saturn barycenter', AO_type.PLANET),
        AstroObject('uranus', 'uranus barycenter', AO_type.PLANET),
        AstroObject('neptune', 'neptune barycenter', AO_type.PLANET),
        AstroObject('pluto', 'pluto barycenter', AO_type.DWARF_PLANET)
        ]

#test coordinates
lat = 0
lon = 0

curLocation = wgs84.latlon(lat,lon)

#load planets
sf_planets = sf_load('de442s.bsp')
earth = sf_planets['earth']

#load timescale
ts = sf_load.timescale()
#CHANGE THESE TO BE ACTUAL DESIRED TIMES TO CHECK LATER
t0 = ts.utc(2026,6,18)
t1 = ts.utc(2026,6,21)


#print off if rising or not
for planet in PLANETS:
        target = sf_planets[planet.sf_name]

        #set triggers
        testFunc = risings_and_settings(sf_planets, target, curLocation)
        
        rises_at = t0.utc #set to current time as default (doesn't matter if it really started earlier right?)

        #find rise and set events
        for t, is_rising in zip(*find_discrete(t0,t1, testFunc)):
                #note that t is in Julian date format, which is in days that need to be converted
                selected_time = t.utc

                if (is_rising):
                   rises_at = selected_time
                else: # not is_rising or in other words, setting
                       sets_at = selected_time
                       print(planet.ad_name, 'rising at', rises_at.hour, ':', rises_at.minute, 'setting at', sets_at.hour, ':', sets_at.minute)
