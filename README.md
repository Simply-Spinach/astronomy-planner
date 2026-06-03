# astronomy-planner
An astronomy app showing you what days are best used for viewing the skies at night based on weather and what's visible

## Current Todo list:
- [ ] Create SQLite database to hold data on each planet's visibility
- [ ] Create Python script to fill database (to be called incrementally)
- [ ] Import and modify calendar app to use database instead of APIs I didn't like

## How it works
This planner will be divided into 3 key components:

- A SQLite database containing Space and Weather information
- A website GUI
- A Python script using Skyfield and Open-Meteo to fill SQLite database

### SQLite Database:
The database contains a few tables including:
- PlanetsGeneral: planet information such as a name, or any other additional information we want
- PlanetsRiseSet: Planet information regarding when they set and rise, configurable through Python
- WeatherDaily: Weather information for a day

These tables get loaded by Python and can recieve edits from there

### Python Script:
The Python section of the code is responsible for interfacing and processing Skyfield and Open-Meteo to fill the SQLite database's tables.  It will also be responsible for other actions such as determining location of the user, and handling notifications.

### Website Interface:
The website interface of course is going to display information from the SQLite database as something human-readable