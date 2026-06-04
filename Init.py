import sqlite3
import os

#openmeto imports
import openmeteo_requests

import requests_cache
from retry_requests import retry

#skyfield imports
import skyfield

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
        #get lat and lon on the fly and update it here
        print("TODO: GET LAT AND LON UPDATED AUTOMATICALLY WITH USER")
        lat = 20
        lon = 100

        cursor = self.sql.cursor()

        # Retrieve new data
        meteoData = AstroData.getOpenMeteoUpdate(lat,lon)

        #lat and lon may vary slightly but technically be for the same spot so merge them
        lat = meteoData.Latitude()
        lon = meteoData.Longitude()

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
        
        #compute day
        daily = meteoData.Daily()
            
       
        #cleanup
        cursor.close()
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