from skyfield.api import load
from skyfield.api import wgs84 #handles positioning

ts = load.timescale()
t = ts.now()

PLANET_ORDER = ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']

lat = 48.02
lon = -122.08

curLocation = wgs84.latlon(lat,lon);

planets = load('de442s.bsp');
earth = planets['earth']

for planet in PLANET_ORDER:
        print(curLocation.rotation_at(t).locate(planets[planet]))

