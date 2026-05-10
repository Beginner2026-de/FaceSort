from peewee import IntegerField
from peewee import CharField
from email.charset import Charset
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import QCoreApplication
from PySide6.QtUiTools import QUiLoader
from src.custom_logging import setup_logger
from main_tab.a_ordner_auswählen import start_select_folder
from peewee import SqliteDatabase, Model


loger = setup_logger(__name__)



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
    loger.info(f"Modus: {mode} und threds: {threds} voreingestellt ")
    return mode, threds



#def change_mode_in_db():
    

    

