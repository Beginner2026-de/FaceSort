import cv2
from insightface.app import FaceAnalysis
from playhouse.reflection import print_table_sql
from src.g_db_settings_handler import SettingsHandler
from src.custom_logging import setup_logger, success
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

def start_personen_hauptbild(ui:QWidget):
    load_person_buttons(ui=ui)

def load_person_buttons(ui):
    personen_nachrichten = Nachrichten(ui=ui,widget=ui.personen_nachrichten)
    folder_path = ui.selected_folder_path.text()
    db_path = f"{folder_path}/db.db"
    
    if not folder_path:
        personen_nachrichten.error(text="Kein Ordner gewähl")
        return
    
    bilder_db = FaceDB(db_path=db_path)
    ui.hauptbild_alle_button_und_bilder = ButtonUndBilder(ui=ui, 
                                    button_widget=ui.hauptbild_button,
                                    bilder_widget=ui.hauptbild_alle_personen_bilder,
                                    face_only=True,
                                    with_hauptbild_widget=True,
                                    hauptbild_widget=ui.hauptbild_hauptbild)
    names = bilder_db.get_all_person_names()
    ui.hauptbild_alle_button_und_bilder.add_person_buttons(names=names)


def hauptbild_button_gedrückt(ui):
    personen_nachrichten = Nachrichten(ui=ui,widget=ui.personen_nachrichten)
    folder_path = ui.selected_folder_path.text()
    db_path = f"{folder_path}/db.db"
    
    if not folder_path:
        personen_nachrichten.error(text="Kein Ordner gewähl")
        return

    bilder_db = FaceDB(db_path=db_path)

    name = ui.hauptbild_alle_button_und_bilder.get_aktueller_name()
    bild_path = ui.hauptbild_alle_button_und_bilder.get_current_image_path()

    

    if not name:
        personen_nachrichten.error(text="Keine Person ausgewählt")
        return
    if not bild_path:
        personen_nachrichten.error(text="Kein Bild ausgewählt")
        return
    try:
        bilder_db.set_haupt_bild_zu_person(person_name=name,image_path=bild_path)
        personen_nachrichten.info("Neues Hauptbild gesetzt")
    except Exception as e:
        personen_nachrichten.error(f"Hauptbild setzen fehlgeschalgen {e}")
    ui.hauptbild_alle_button_und_bilder.set_hauptbild_bild(name)