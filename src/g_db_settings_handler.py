from peewee import SqliteDatabase,Model,CharField,IntegerField,DoesNotExist
from src.custom_logging import APP_LOGGER_NAME
import logging

logger = logging.getLogger(APP_LOGGER_NAME)

class SettingsHandler:
    def __init__(self, db_path):
        self.db = SqliteDatabase(db_path)
        
        class Settings(Model):
            class Meta:
                database = self.db
            db_path = CharField(unique=True)
            folder_path = CharField()
            mode = CharField()
            threads = IntegerField()
        
        self.db.connect()
        self.db.create_tables([Settings])
        self.Settings = Settings
        self._load_or_create()
    
    def _load_or_create(self):
        """Lädt existierende Einstellungen oder erstellt neue"""
        try:
            self._setting = self.Settings.get()
        except DoesNotExist:
            self._setting = self.Settings.create(
                db_path="",
                folder_path="",
                mode="CPU",
                threads=1
            )
    
    @property
    def db_path(self):
        return self._setting.db_path
    
    @db_path.setter
    def db_path(self, value):
        self._setting.db_path = value
        self._setting.save()
        logger.info(f"db_path = {value}")
    
    @property
    def folder_path(self):
        return self._setting.folder_path
    
    @folder_path.setter
    def folder_path(self, value):
        self._setting.folder_path = value
        self._setting.save()
        logger.info(f"folder_path = {value}")
    
    @property
    def mode(self):
        return self._setting.mode
    
    @mode.setter
    def mode(self, value):
        self._setting.mode = value
        self._setting.save()
        logger.info(f"mode = {value}")
    
    @property
    def threads(self):
        return self._setting.threads
    
    @threads.setter
    def threads(self, value):
        self._setting.threads = value
        self._setting.save()
        logger.info(f"threads = {value}")
    
    def close(self):
        self.db.close()