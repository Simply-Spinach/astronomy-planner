CREATE TABLE Location (
    loc_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    lat INTEGER NOT NULL, 
    lon INTEGER NOT NULL,

    UNIQUE(lat, lon)
);

CREATE TABLE AstroObject (
    ast_obj_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name varchar NOT NULL,
    information varchar
);

CREATE TABLE CelestialEvent (
    loc_id INTEGER NOT NULL,
    ast_obj_id INTEGER NOT NULL,
    astro_event_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME NOT NULL,

    FOREIGN KEY (loc_id) REFERENCES location(loc_id)
    FOREIGN KEY (ast_obj_id) REFERENCES AstroObject(ast_obj_id)
);

CREATE TABLE LocationDate (
    loc_id INTEGER NOT NULL,
    loc_date_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    view_date date,
    sunrise time,
    sunset time,

    FOREIGN KEY (loc_id) REFERENCES location(loc_id),
    UNIQUE(loc_id, loc_date_id)
);

CREATE TABLE Weather (
    loc_date_id INTEGER,
    hr integer,
    temp float,
    cloud_cover float,
    visibility float,

    FOREIGN KEY (loc_date_id) REFERENCES LocationDate(loc_date_id),
    UNIQUE(loc_date_id, hr)
);