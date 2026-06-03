# Notes for development:

## Current Todo list:
- [ ] Create SQLite database to hold data on each planet's visibility
- [ ] Create Python script to fill database (to be called incrementally)
- [ ] Import and modify calendar app to use database instead of APIs I didn't like

## How this project works
This planner will be divided into 3 key components:

- A SQLite database containing Space and Weather information
- A website GUI
- A Python script using Skyfield and Open-Meteo to fill SQLite database

These will be updated about once a day automatically to fulfill notifications, or when the user desires to access them.  When to update them will be determined later, but it will most likely be early in the morning to leave you time to plan a late night viewing.

### SQLite Database:
The database contains a few tables including:
- PlanetsGeneral: planet information such as a name, or any other additional information we want
    #### Contains:
    - BodyID: Key
    - Name: Text
    This can be easily be expanded in the future with additional features 
- AstronomyEvents: Events happening in the sky.  Typically, this will contain timeframes when planets are visible in the sky, but could be updated to contain other events such as meteor showers or Artemis launches later
    #### Contains:
    - BodyID: Forgein key
    - EventStart: Time
    - EventEnd: Time
    - EventDescription: Text
- DateInfo: General information for a date
    #### Contains:
    - Date
    - Clouds
    - Sunset
    - Sunrise
These tables get loaded by Python and can recieve edits from there

### Python Script:
The Python section of the code is responsible for interfacing and processing Skyfield and Open-Meteo to fill the SQLite database's tables.  It will also be responsible for other actions such as determining location of the user, and handling notifications.

Useful links:
- [Open-Meteo playground](https://open-meteo.com/en/docs?hourly=temperature_2m,precipitation_probability,weather_code,cloud_cover,visibility&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=auto)
- [Skyfield documentation](https://rhodesmill.org/skyfield/)

### Website Interface:
The website interface of course is going to display information from the SQLite database as something human-readable.
This can be a modified version of [my DTC 477 final](https://github.com/Simply-Spinach/DTC-477-Class-Site/tree/main/major_project) where all we change is that now the javascript integrates with my database instead of the libraries I previously complained about.

## Putting it all together:
There are a few tools to enable this to allow an app to be made from this.  For one, we could do something similar to tools like Jupyter Notebook where we run a local server ourselves and open the viewable app in a browser window.  This doesn't make any sense for this app, but allows me to use the data elsewhere at the very least, and enables us to easily replace modules.
The better solution in my opinion would be to use a tool to convert html to an app the users can use.  This makes far more sense to me so then we could update the app with the user's location and means I don't need a server to run this app.