from peewee import *
import cv2
from insightface.app import FaceAnalysis
from src.g_db_settings_handler import SettingsHandler
from src.custom_logging import setup_logger
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QPixmap, QImage,QIcon
from PySide6.QtWidgets import QApplication,QListWidgetItem,QListWidget
import cv2
from src.DBManager import FaceDB
import os
import numpy as np
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import cosine
import time


def start_personen_scan(ui):
    person_nachrichten_handler(ui,display=True, text="Scan gestartet")
    auto_assign_persons(ui=ui)

loger = setup_logger(__name__)

def person_nachrichten_handler(ui ,display:bool=True ,text:str="", level:str= "info"):
    nachricht = text
    if not display == False:
        if level=="info":
            loger.info(nachricht)
            ui.personen_nachrichten.setVisible(display)
            ui.personen_nachrichten.setText(f"Meldung: {text}")
            return
        if level=="error":
            loger.error(nachricht)
            ui.personen_nachrichten.setVisible(display)
            ui.personen_nachrichten.setText(f"Error: {text}")
            return
    ui.personen_nachrichten.setVisible(display)
    QApplication.processEvents()

def progresbar_handler(ui,wert:int=0,init:bool=False,min:int=0,max:int=int,fertig:bool=False):
    if init == True:
        ui.ordner_loading_pictures_progressbar.setMaximum(max)
        ui.ordner_loading_pictures_progressbar.setMinimum(min)
        ui.ordner_loading_pictures_progressbar.setValue(0)
        ui.ordner_loading_pictures_progressbar.setVisible(True)
        ui.ordner_loading_pictures_progressbar.setFormat("%p% - %v von %m")

    if fertig == True:
        ui.ordner_loading_pictures_progressbar.setFormat("Fertig! %v ")
    
    ui.ordner_loading_pictures_progressbar.setValue(wert)



def cluster_faces(ui,eps=0.5, min_samples=2):
    folder_path = ui.selected_folder_path.text()
    db_path = f"{folder_path}/db.db"
    if not folder_path:
        person_nachrichten_handler(ui=ui,level="error",text=f"Kein Ordner Gelden")
    person_nachrichten_handler(ui=ui,display=False)

    bilder_db = FaceDB(db_path=db_path)
    """Gruppiert ähnliche Gesichter mit DBSCAN"""
    # Alle Faces mit Embeddings holen
    faces = list(bilder_db.get_all_faces())
    progresbar_handler(ui=ui,init=True,max=len(faces))

    person_nachrichten_handler(ui,text=f"Insgesant gefundene Gesichter in allen Fotos: {len(faces)} Starte datei verarbeitung" )
    time.sleep(2)
    
    if len(faces) < min_samples:
        person_nachrichten_handler(ui=ui,level="error",text=f"Nicht genug Gesichter zum Clustern ({len(faces)})")
        return
    
    # Embeddings in Matrix umwandeln
    embeddings = []
    face_ids = []
    wert = 1
    for face in faces:
        emb = np.frombuffer(face.embedding, dtype=np.float32)
        embeddings.append(emb)
        face_ids.append(face.id)
        wert =+ 1
        progresbar_handler(ui=ui,wert=wert)
    progresbar_handler(ui=ui,fertig=True)
    
    embeddings = np.array(embeddings)
    
    # Clustering
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
    labels = clustering.fit_predict(embeddings)
    person_nachrichten_handler(ui=ui,text="Starte Gesicht zu ordnung")
    progresbar_handler(ui=ui,init=True,max=len(faces))
    wert = 1
    # Cluster zu Personen zuordnen
    clusters = {}
    for face_id, label in zip(face_ids, labels):
        if label != -1:  # -1 = Rauschen (kein Cluster)
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(face_id)
        wert +=1
        progresbar_handler(ui=ui,wert=wert)
    progresbar_handler(ui=ui,fertig=True)


    person_nachrichten_handler(ui,text=f"Gefundene Gesichter: {len(clusters)}")
    
    return clusters

def auto_assign_persons(ui, eps=0.5, min_samples=2):
    ui.starte_personen_scan_bild_liste.clear()
    """Automatisch Personen aus Clustern erstellen"""
    folder_path = ui.selected_folder_path.text()
    db_path = f"{folder_path}/db.db"

    if not folder_path:
        person_nachrichten_handler(ui=ui,level="error",text=f"Kein Ordner Gelden")

    bilder_db = FaceDB(db_path=db_path)
    clusters = cluster_faces(ui=ui)
    
    if not clusters:
        person_nachrichten_handler(ui=ui,text="Keine Cluster gefunden",level="error")
        return

    person_nachrichten_handler(ui=ui,text=f"Alle gesichter werden angelegt: {len(clusters)}")
    progresbar_handler(ui=ui,init=True,max=len(clusters))
    wert = 1
    for cluster_id, face_ids in clusters.items():
        # Temporärer Personenname (später vom Benutzer umbenennen)
        person_name = f"Person_{cluster_id}"
        person = bilder_db.create_person(name=person_name)
        
        # Alle Faces dieser Person zuordnen
        for face_id in face_ids:
            bilder_db.assign_face_to_person(face_id, person_name, confidence=1.0)

        bilder_db.set_haupt_bild_zu_person(person_name=person_name)
        add_person_picture_to_widget(ui=ui,widget=ui.starte_personen_scan_bild_liste,person_name=person_name)

        person_nachrichten_handler(ui=ui,text=f"Person '{person_name}' mit {len(face_ids)} Gesichtern erstellt")
        progresbar_handler(ui=ui,wert=wert)
        wert  +=1
    progresbar_handler(ui=ui,fertig=True)
    person_nachrichten_handler(ui=ui,text=f"Alle Gesichter Gefunden, {len(clusters)} Gefunden und Gespeichert")


def add_person_picture_to_widget(ui, widget, person_name):
    QApplication.processEvents()
    widget.setViewMode(QListWidget.IconMode)      # Rasteransicht
    widget.setMovement(QListWidget.Static)        # Verschieben verhindern
    widget.setWrapping(True)                      # Zeilenumbruch
    widget.setFlow(QListWidget.LeftToRight)       # links → rechts (Standard)
    widget.setIconSize(QSize(80, 80))
    widget.setIconSize(QSize(80, 80))
    
    folder_path = ui.selected_folder_path.text()
    db_path = f"{folder_path}/db.db"
    if not folder_path:
        person_nachrichten_handler(ui=ui, level="error", text="Kein Ordner gewählt")
        return
    
    bilder_db = FaceDB(db_path=db_path)
    if person_name == "all":
        persons = bilder_db.get_all_person_names()
        for person_name in persons:
                # Holt (file_name, bbox)
            file_name, bbox = bilder_db.get_person_hauptbild_data(person_name=person_name)
            real_file_path = f"{folder_path}/{file_name}"
            
            if file_name is None or bbox is None:
                return
            
            img = QPixmap(real_file_path)
            # bbox ist Liste/Tupel: [x1, y1, x2, y2]
            x1, y1, x2, y2 = bbox
            cropped = img.copy(x1, y1, x2 - x1, y2 - y1)
            scaled = cropped.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            item = QListWidgetItem(QIcon(scaled), person_name)
            item.setData(Qt.UserRole, person_name)  # oder Person-ID
            widget.addItem(item)
            QApplication.processEvents()
        return

    
    # Holt (file_name, bbox)
    file_name, bbox = bilder_db.get_person_hauptbild_data(person_name=person_name)
    real_file_path = f"{folder_path}/{file_name}"
    
    if file_name is None or bbox is None:
        return
    
    img = QPixmap(real_file_path)
    # bbox ist Liste/Tupel: [x1, y1, x2, y2]
    x1, y1, x2, y2 = bbox
    cropped = img.copy(x1, y1, x2 - x1, y2 - y1)
    scaled = cropped.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    item = QListWidgetItem(QIcon(scaled), person_name)
    item.setData(Qt.UserRole, person_name)  # oder Person-ID
    widget.addItem(item)
    QApplication.processEvents()