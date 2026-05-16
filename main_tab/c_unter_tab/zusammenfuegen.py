import cv2
from insightface.app import FaceAnalysis
from src.g_db_settings_handler import SettingsHandler
from src.custom_logging import setup_logger
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QPixmap, QImage,QIcon
from PySide6.QtWidgets import QApplication,QListWidgetItem,QListWidget,QVBoxLayout,QPushButton, QWidget
import cv2
from src.DBManager import FaceDB
import os
import numpy as np
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import cosine
import time
from src.add_picture_to_widget_clas import PersonImageDisplay
from src.progressbar_clas import ProgressBar
from src.nachrichten_clas import Nachrichten
from src.add_button_and_pcitures_in_two_widgets import ButtonUndBilder

def start_personen_zusammenfuegen(ui:QWidget):
    load_person_buttons_left(ui=ui)
    load_person_buttons_right(ui=ui)

def load_person_buttons_left(ui):
    personen_nachrichten = Nachrichten(ui=ui,widget=ui.personen_nachrichten)
    folder_path = ui.selected_folder_path.text()
    db_path = f"{folder_path}/db.db"
    
    if not folder_path:
        personen_nachrichten.error(text="Kein Ordner gewähl")
        return
    
    bilder_db = FaceDB(db_path=db_path)
    nameundbilder = ButtonUndBilder(ui=ui, 
                                    button_widget=ui.zusamnenfegen_person_eins,
                                    bilder_widget=ui.zusamnenfegen_person_eins_bilder,
                                    face_only=True)
    names = bilder_db.get_all_person_names()
    nameundbilder.add_person_buttons(names=names)

def load_person_buttons_right(ui):
    personen_nachrichten = Nachrichten(ui=ui,widget=ui.personen_nachrichten)
    folder_path = ui.selected_folder_path.text()
    db_path = f"{folder_path}/db.db"
    
    if not folder_path:
        personen_nachrichten.error(text="Kein Ordner gewähl")
        return
    
    bilder_db = FaceDB(db_path=db_path)
    nameundbilder = ButtonUndBilder(ui=ui, 
                                    button_widget=ui.zusamnenfegen_person_zwei,
                                    bilder_widget=ui.zusamnenfegen_person_zwei_bilder,
                                    face_only=True)
    names = bilder_db.get_all_person_names()
    nameundbilder.add_person_buttons(names=names)