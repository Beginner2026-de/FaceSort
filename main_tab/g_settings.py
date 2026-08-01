from peewee import IntegerField
from peewee import CharField
from src.custom_logging import APP_LOGGER_NAME
import logging
from peewee import SqliteDatabase, Model


logger = logging.getLogger(APP_LOGGER_NAME)



def start_einstellung_db(db_path):
    db = SqliteDatabase(db_path)

    class BaseModel(Model):
        class Meta:
            database = db

    class Einstellungen(BaseModel):
        mode = CharField()
        threds = IntegerField()


    # Tabelle erstellen (falls nicht existiert)
    db.connect()
    db.create_tables([Einstellungen])

    mode, threds = Einstellungen.select(Einstellungen.mode,Einstellungen.threds)
    logger.info(f"Einstellungen geladen: Modus={mode}, Threads={threds}")
    return mode, threds



#def change_mode_in_db():
    

    

