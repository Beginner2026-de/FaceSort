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

aktueller_button_name:str = ""

def start_personen_bennen(ui):
    load_person_buttons(ui=ui)

def load_person_buttons(ui):
    personen_nachrichten = Nachrichten(ui=ui,widget=ui.personen_nachrichten)
    folder_path = ui.selected_folder_path.text()
    db_path = f"{folder_path}/db.db"
    
    if not folder_path:
        personen_nachrichten.error(text="Kein Ordner gewähl")
        return
    
    bilder_db = FaceDB(db_path=db_path)
    nameundbilder = ButtonUndBilder(ui=ui, 
                                    button_widget=ui.personen_benenen_namen_liste,
                                    bilder_widget=ui.personen_benenen_bilder_anzeige_box,
                                    face_only=True)
    names = bilder_db.get_all_person_names()
    nameundbilder.add_person_buttons(names=names)


    
def benenen_personen_name_abschiekcen_button(ui):
    folder_path = ui.selected_folder_path.text()
    db_path = f"{folder_path}/db.db"
    db = FaceDB(db_path=db_path)
    nachrichten_class = Nachrichten(ui=ui,widget=ui.personen_nachrichten)
    neuer_name:str = ui.benenen_personen_name.text()
    anser = db.rename_person(old_name=ui.bennen_aktuelle_person,new_name=neuer_name)
    print(anser)
    load_person_buttons(ui=ui)
    if anser["success"] == True:
        nachrichten_class.info(f"Alter Name ({anser["old_name"]}) wurde zu ({anser["new_name"]}) geändert")
    if anser["success"] == False:
        nachrichten_class.error(f"{anser["error"]} Alt ({aktueller_button_name}) Neu ({neuer_name})")
    ui.benenen_personen_name.clear()