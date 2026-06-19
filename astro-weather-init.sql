CREATE TABLE Location (
    loc_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    lat INTEGER NOT NULL, 
    lon INTEGER NOT NULL,

    UNIQUE(lat, lon)
);

CREATE TABLE AstroObject (
    ast_obj_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    skyfield_name varchar NOT NULL,
    display_name varchar NOT NULL,
    display_info varchar,
    UNIQUE (skyfield_name),
    UNIQUE (display_name)
);

CREATE TABLE CelestialEvent (
    loc_id INTEGER NOT NULL,
    ast_obj_id INTEGER NOT NULL,
    astro_event_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME NOT NULL,

    FOREIGN KEY (loc_id) REFERENCES location(loc_id),
    FOREIGN KEY (ast_obj_id) REFERENCES AstroObject(ast_obj_id),
    UNIQUE (loc_id, ast_obj_id, end_datetime)
);

CREATE TABLE LocationDate (
    loc_date_id INTEGER PRIMARY KEY NOT NULL,
    loc_id INTEGER NOT NULL,
    view_date datetime,
    sunrise datetime,
    sunset datetime,

    FOREIGN KEY (loc_id) REFERENCES location(loc_id),
    UNIQUE(loc_id, view_date)
);

CREATE TABLE Weather (
    loc_date_id INTEGER,
    hr integer,
    temp float,
    cloud_cover float,
    visibility float,
    chance_precipitation float,

    FOREIGN KEY (loc_date_id) REFERENCES LocationDate(loc_date_id),
    UNIQUE(loc_date_id, hr)
);