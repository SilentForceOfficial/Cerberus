from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = None
Session = None
session = None
Base = None
conn = None

# Create or link to a database
def db_link(project):
    import os

    global engine
    global Session
    global session
    global Base
    global conn

    # Ruta bbdd - (Ruta actual + /static/projects/ + nombre bbdd)
    ruta_base_de_datos = os.path.join(os.path.dirname(os.path.abspath(__file__)),f"static/projects/{project}.db")
    
    # Crear conexión a la bbdd
    engine = create_engine(f'sqlite:///{ruta_base_de_datos}')
    Session = sessionmaker(bind=engine)
    session = Session()
    Base = declarative_base()

    from . import models
    # Crear bbdd si no existe
    # Base.metadata.bind = engine
    # Base.metadata.create_all(engine)


# Connect to a database
def db_connect():
    global conn
    conn = engine.connect()     

# Close connection to a database
def db_disconnect():
    global engine
    global Session
    global session
    global Base
    global conn
    
    session.close()