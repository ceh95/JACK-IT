import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    init_clothing_objects()

def init_clothing_objects():
    db = get_db()
    clothing_cats = [(1,'shirts'),(2,'pants'),(3,'accessories')]
    db.executemany('INSERT INTO clothing_categories(id,name) VALUES (?,?)', clothing_cats)

    clothes = [('Tank Top',1,1,80,-1,'','','',''), ('Short Sleeve Shirt',1,2,65,80,'','','',''), ('Long Sleeve Shirt',1,3,55,65,'','','',''), ('Sweater',1,4,40,65,'','','',''), ('Jacket',2,'',40,55,'','','',''), ('Hoodie',1,5,40,65,'','','',''), ('Coat',2,'',-1,40,'','','',''), ('Shorts',3,1,70,-1,'','','',''), ('Capri Pants',3,2,60,75,'','','',''), ('Long Pants',3,3,-1,70,'','','',''), ('Hat',4,'',-1,40,'','','',''), ('Scarf',4,'',-1,30,'','','',''), ('Gloves',4,'',-1,30,'','','',''), ('Sunglasses',4,'',-1,-1,'sunny','','','')]
    db.executemany('INSERT INTO clothing_types(name,cat_id,default_rank,default_temp_min,default_temp_max,status,rain_only,snow_only,windy_only) VALUES (?,?,?,?,?,?,?,?,?)', clothes)
    db.commit()

@click.command('init_db')
@with_appcontext
def init_db_command():
    """CLear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')    

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)   