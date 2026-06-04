#openmeto imports
import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

class OpenMeteoHandler:
    def __init__(self, lat, lon):
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
        self.responses = openmeteo.weather_api(url, params = params)

    def getResponseFull(self):
        return self.responses
    
    def getHourlyData(self):
        # Process first location. Add a for-loop for multiple locations or weather models
        response = self.responses[0]
        print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation: {response.Elevation()} m asl")
        print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_precipitation_probability = hourly.Variables(1).ValuesAsNumpy()
        hourly_weather_code = hourly.Variables(2).ValuesAsNumpy()
        hourly_cloud_cover = hourly.Variables(3).ValuesAsNumpy()
        hourly_visibility = hourly.Variables(4).ValuesAsNumpy()

        hourly_data = {
            "date": pd.date_range(
                start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
                end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
                freq = pd.Timedelta(seconds = hourly.Interval()),
                inclusive = "left"
            ).tz_convert(response.Timezone().decode())
        }

        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["precipitation_probability"] = hourly_precipitation_probability
        hourly_data["weather_code"] = hourly_weather_code
        hourly_data["cloud_cover"] = hourly_cloud_cover
        hourly_data["visibility"] = hourly_visibility

        hourly_dataframe = pd.DataFrame(data = hourly_data)
        print("\nHourly data\n", hourly_dataframe)


def getDailyData(self):
        response = self.responses[0]
        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_sunrise = daily.Variables(0).ValuesInt64AsNumpy()
        daily_sunset = daily.Variables(1).ValuesInt64AsNumpy()

        daily_data = {
            "date": pd.date_range(
                start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
                end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
                freq = pd.Timedelta(seconds = daily.Interval()),
                inclusive = "left"
            ).tz_convert(response.Timezone().decode())
        }

        daily_data["sunrise"] = daily_sunrise
        daily_data["sunset"] = daily_sunset

        daily_dataframe = pd.DataFrame(data = daily_data)
        print("\nDaily data\n", daily_dataframe)
        return daily_dataframe