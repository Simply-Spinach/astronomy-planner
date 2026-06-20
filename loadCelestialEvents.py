import time
import sqlite3 as sql
from enum import Enum
from datetime import datetime

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

def loadCelestialEvents(loc_id, time_start, time_end, sql):

        sql_cursor = sql.cursor()
        #set location
        sql_cursor.execute('''
                SELECT lat, lon FROM Location
                WHERE loc_id = ?
        ''', [loc_id] )

        loc = sql_cursor.fetchone()
        if (loc == None):
                raise Exception("Expected loc_id to return valid location")
        lat = loc[0]
        lon = loc[1]

        curLocation = wgs84.latlon(lat,lon)

        #load planets
        sf_planets = sf_load('de442s.bsp')
        earth = sf_planets['earth']

        #print off if rising or not
        for planet in PLANETS:
                target = sf_planets[planet.sf_name]

                #gets ast_obj_id from sql file
                ast_obj_id = sql_cursor.execute('''
                        SELECT ast_obj_id FROM AstroObject
                        WHERE skyfield_name = ?
                        ''', [planet.sf_name])
                ast_obj_id = sql_cursor.fetchone()
                if ast_obj_id == None: #object doesn't exist yet.  Insert simple version without display_info
                        print("Inserting non-existant AstroObject", planet.ad_name)
                        sql_cursor.execute('''
                                INSERT INTO AstroObject (skyfield_name, display_name)
                                VALUES (?,?)
                                ''', [planet.sf_name, planet.ad_name])
                        sql.commit()
                        sql_cursor.execute('''
                                SELECT ast_obj_id FROM AstroObject
                                WHERE skyfield_name = ?
                                ''', [planet.sf_name])
                        ast_obj_id = sql_cursor.fetchone()
                ast_obj_id = ast_obj_id[0]


                #set triggers
                testFunc = risings_and_settings(sf_planets, target, curLocation)
                

                #find rise and set events
                rises_at = time_start.tt #set to current time as default (doesn't matter if it really started earlier right?)
                for t, is_rising in zip(*find_discrete(time_start,time_end, testFunc)):
                        #note that t is in Julian date format, which is in days that need to be converted
                        selected_time = t.tt

                        if (is_rising):
                                rises_at = selected_time
                        else: # not is_rising or in other words, setting
                                sets_at = selected_time
                                sql_cursor.execute(''' INSERT OR IGNORE INTO CelestialEvent (loc_id, ast_obj_id, start_datetime, end_datetime) VALUES
                                                   (?, ?, julianday(?), julianday(?))
                                                   ''', [loc_id,ast_obj_id, rises_at, sets_at])
        
        #cleanup (still part of function)
        sql_cursor.close()
        sql.commit()

sql_inst = sql.connect("astro_weather.db")

ts = sf_load.timescale()
time_start = ts.utc(2026,6,19)
time_end = ts.utc(2026,6,22)
loadCelestialEvents(1, time_start, time_end, sql_inst)

sql_inst.close()
