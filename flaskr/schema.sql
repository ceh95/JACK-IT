DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS clothes;
DROP TABLE IF EXISTS clothing_types;
DROP TABLE IF EXISTS clothing_categories;

CREATE TABLE user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    location_id INTEGER 
);

CREATE TABLE clothing_types(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cat_id INTEGER NOT NULL,
    default_rank INTEGER,
    default_temp_min INTEGER NOT NULL,
    default_temp_max INTEGER NOT NULL,
    FOREIGN KEY (cat_id)
       REFERENCES clothing_categories (id)
);

CREATE TABLE clothing_categories(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE clothes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    clothes_type_id INTEGER NOT NULL,
    temp_min INTEGER NOT NULL,
    temp_max INTEGER NOT NULL,
    rank INTEGER NOT NULL,
    FOREIGN KEY (user_id)
       REFERENCES user (id)
    FOREIGN KEY (clothes_type_id)
        REFERENCES clothing_types (id) 
);
