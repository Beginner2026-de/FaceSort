from PySide6.QtWidgets import QApplication, QLineEdit
from src.custom_logging import setup_logger

class Nachrichten():
    def __init__(self, ui, widget:QLineEdit,display:bool=True):
        self.ui = ui
        self.widget = widget
        self.display=display 
        self.loger = setup_logger(__name__)
        

    def info(self,text:str=""):
        if not self.display == False:
            self.loger.info(text)
            self.widget.setVisible(self.display)
            self.widget.setText(f"Meldung: {text}")
            return
  
        self.widget.setVisible(self.display)
        QApplication.processEvents()

    def error(self,text:str=""):
        if not self.display == False:
            self.loger.error(text)
            self.widget.setVisible(self.display)
            self.widget.setText(f"Error: {text}")
            return
        self.widget.setVisible(self.display)
        QApplication.processEvents()