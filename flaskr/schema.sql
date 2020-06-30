DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS clothes;
DROP TABLE IF EXISTS user_x_clothes;

CREATE TABLE user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    location_id INTEGER 
);

CREATE TABLE clothes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE user_x_clothes(
    user_id INTEGER NOT NULL,
    clothes_id INTEGER NOT NULL,
    FOREIGN KEY (user_id)
       REFERENCES user (id)
    FOREIGN KEY (clothes_id)
        REFERENCES clothes (id)     
);
