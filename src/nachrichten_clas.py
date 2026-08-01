from PySide6.QtWidgets import QApplication, QLineEdit
from src.custom_logging import APP_LOGGER_NAME
import logging

class Nachrichten():
    def __init__(self, ui, widget:QLineEdit,display:bool=True):
        self.ui = ui
        self.widget = widget
        self.display=display 
        self.logger = logging.getLogger(APP_LOGGER_NAME)
        

    def info(self,text:str=""):
        if not self.display == False:
            self.logger.info(text)
            self.widget.setVisible(self.display)
            self.widget.setText(f"Meldung: {text}")
            return
  
        self.widget.setVisible(self.display)
        QApplication.processEvents()

    def error(self,text:str=""):
        if not self.display == False:
            self.logger.error(text)
            self.widget.setVisible(self.display)
            self.widget.setText(f"Error: {text}")
            return
        self.widget.setVisible(self.display)
        QApplication.processEvents()

    def hide(self):
        self.widget.setVisible(False)
        QApplication.processEvents()