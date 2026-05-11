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
    container = ui.personen_benenen_namen_liste
    
    # Vorhandene Buttons löschen
    for child in container.findChildren(QPushButton):
        child.deleteLater()
    
    # Layout erstellen oder vorhandenes nehmen
    if container.layout() is None:
        layout = QVBoxLayout(container)
    else:
        layout = container.layout()
        # Vorhandene Widgets aus Layout entfernen
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    # Neue Buttons hinzufügen
    for name in bilder_db.get_all_person_names():
        btn = QPushButton(name)
        btn.clicked.connect(lambda checked, n=name: on_person_clicked(ui=ui, name=n))
        layout.addWidget(btn)

def on_person_clicked(ui,name):
    nachrichten_class = Nachrichten(ui=ui,widget=ui.personen_nachrichten)
    nachrichten_class.info(text=f"Person geklickt: {name}")
    bilder_widget = PersonImageDisplay(ui=ui,list_widget=ui.personen_benenen_bilder_anzeige_box)
    bilder_widget.show_first_n_off_name(name=name)