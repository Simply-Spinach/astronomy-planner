import sqlite3
import os
from enum import Enum
from datetime import datetime

#openmeto imports
import openmeteo_requests

import requests_cache
from retry_requests import retry

#skyfield imports
import skyfield
from skyfield import api as sf_api
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


class AstroData:
    def __init__(self):
        self.DB_PATH = './astro_weather.db'
        dbReady = self._check_database_ready()
        self.sql = sqlite3.connect(self.DB_PATH)

        if (not dbReady):
            self._exec_SQL_file('astro-weather-init.sql')

        #update database with new source values
        self.updateDatabase()

    def updateDatabase(self):
        #get lat and lon on the fly and update it here (used everywhere, so it's computed here)
        print("TODO: GET LAT AND LON UPDATED AUTOMATICALLY WITH USER")
        lat = 20
        lon = 100

        #create new cursor
        cursor = self.sql.cursor()

        # Retrieve new data
        meteoData = AstroData.getOpenMeteoUpdate(lat,lon)

        #lat and lon may vary slightly but technically be for the same spot so merge them
        lat = meteoData.Latitude()
        lon = meteoData.Longitude()
        timezone = meteoData.Timezone()

        #insert into location, or find matching location if exists
        #KNOWN BUG: INCREMENTS ON IGNORE, RESULTING IN RUNAWAY COUNTING.
        #NOT SURE IF THIS IS A REAL ISSUE, BUT IS ANNOYING TO LOOK AT IN DB BROWSER
        cursor.execute('''
        INSERT OR IGNORE INTO Location(lat, lon) VALUES
                        (? , ?)
        ''', (lat, lon))
        cursor.execute('''
        SELECT loc_id FROM
                       (
                       SELECT loc_id, lat, lon FROM Location 
                       WHERE lat = ? AND lon = ?);
        ''', (lat, lon))
        loc_id = cursor.fetchone()[0]
        self.sql.commit()

        #load openMeteoData
        self.loadOpenMeteoData(meteoData, loc_id)

        print("TODO: update timescales to update with current date")
        ts = sf_load.timescale()
        time_start = ts.utc(2026,6,19)
        time_end = ts.utc(2026,6,22)

        self._loadCelestialEvents(loc_id, lat, lon, time_start, time_end)
        
        print(self.DB_PATH, "automatically updated with latest data")
        #cleanup
        cursor.close()
        self.sql.commit()

    def loadOpenMeteoData(self, meteoData, loc_id):
        #create new cursor
        cursor = self.sql.cursor()
             
        #compute day
        daily = meteoData.Daily()
        daily_sunrise = daily.Variables(0).ValuesInt64AsNumpy().tolist()
        daily_sunset = daily.Variables(1).ValuesInt64AsNumpy().tolist()
        
        day_start = daily.Time()
        day_end = daily.TimeEnd()
        day_interval = daily.Interval()

        hourly = meteoData.Hourly()
        hourly_temp = hourly.Variables(0).ValuesAsNumpy().tolist()
        hourly_precipitation_prob = hourly.Variables(1).ValuesAsNumpy().tolist()
        hourly_weather_code = hourly.Variables(2).ValuesAsNumpy().tolist()
        hourly_cloud_cover = hourly.Variables(3).ValuesAsNumpy().tolist()
        hourly_vis = hourly.Variables(4).ValuesAsNumpy().tolist()

        for day in range(day_start, day_end, day_interval):
            i = (day - day_start) // day_interval #just to keep track of indexes

            #insert into LocationDate
            cursor.execute('''
                INSERT OR REPLACE INTO LocationDate (loc_id, view_date, sunrise, sunset) VALUES
                           (?, date(?, 'unixepoch'), time(?, 'unixepoch'), time(?, 'unixepoch'))
                           ''', (loc_id, day, daily_sunrise[i], daily_sunset[i]))
            #get loc_date_id for weather
            cursor.fetchall()
            cursor.execute('''
                SELECT loc_date_id FROM
                           (SELECT loc_date_id, loc_id, view_date FROM LocationDate
                           WHERE loc_id = ? AND view_date = date(?, 'unixepoch'))
                           ''', (loc_id, day))
            loc_date_id = cursor.fetchone()[0]

            for hour in range(24):
                hour_index_offset = (i - 1) * 24
                hour_index = hour_index_offset + hour
                time = day + (hourly.Interval() * hour)

                temp = hourly_temp[hour_index]
                cloud_cover = hourly_cloud_cover[hour_index]
                visibility = hourly_vis[hour_index]
                precipitation_prob = hourly_precipitation_prob[hour_index]

                #insert into Weather
                cursor.execute('''
                    INSERT INTO Weather (loc_date_id, hr, temp, cloud_cover, visibility, chance_precipitation) VALUES
                               (?, ?, ? ,? ,? , ?)
                               ''', (loc_date_id, hour, temp, cloud_cover, visibility, precipitation_prob))

    def _loadCelestialEvents(self, loc_id, lat, lon, time_start, time_end):
            #set cursor
            sql_cursor = self.sql.cursor()
            
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
                            self.sql.commit()
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
                                                    (?, ?, datetime(?, 'julianday'), datetime(?, 'julianday'))
                                                    ''', [loc_id,ast_obj_id, rises_at, sets_at])
            
            #cleanup (still part of function)
            sql_cursor.close()
            self.sql.commit()

    def getOpenMeteoUpdate(lat, lon):# Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ["sunrise", "sunset"],
            "hourly": ["temperature_2m", "precipitation_probability", "weather_code", "cloud_cover", "visibility"],
            "timezone": "auto",
            "wind_speed_unit": "mph",
            "temperature_unit": "fahrenheit",
            "precipitation_unit": "inch",
        }
        return openmeteo.weather_api(url, params = params)[0]

    def _exec_SQL_file(self, fileName):
        #prep variables
        file = open(fileName)
        cursor = self.sql.cursor()

        #call script
        cursor.executescript(file.read())
        self.sql.commit()
        
        #cleanup
        cursor.close()
        file.close()

    def _check_database_ready(self):
        return os.access(self.DB_PATH, os.F_OK)
    
astroData = AstroData()