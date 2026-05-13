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
    clusterbar = ProgressBar(ui=ui,max=len(faces),list_widget=ui.gefundene_personen_scan_progressBar)

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
        clusterbar.update()
    clusterbar.fertig()
    
    embeddings = np.array(embeddings)
    
    # Clustering
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
    labels = clustering.fit_predict(embeddings)
    person_nachrichten_handler(ui=ui,text="Starte Gesicht zu ordnung")
    clusterbar2 = ProgressBar(ui=ui,max=len(faces),list_widget=ui.gefundene_personen_scan_progressBar)

    wert = 1
    # Cluster zu Personen zuordnen
    clusters = {}
    for face_id, label in zip(face_ids, labels):
        if label != -1:  # -1 = Rauschen (kein Cluster)
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(face_id)
        wert +=1
        clusterbar2.update()
    clusterbar2.fertig()


    person_nachrichten_handler(ui,text=f"Gefundene Gesichter: {len(clusters)}")
    
    return clusters

def auto_assign_persons(ui, eps=0.5, min_samples=2):
    scan_bild_liste = PersonImageDisplay(ui=ui,list_widget=ui.starte_personen_scan_bild_liste,face_only=True)
    scan_bild_liste.clear()
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
    clusterbar3 = ProgressBar(ui=ui,max=len(clusters),list_widget=ui.gefundene_personen_scan_progressBar)

    wert = 1
    for cluster_id, face_ids in clusters.items():
        # Temporärer Personenname (später vom Benutzer umbenennen)
        person_name = f"Person_{cluster_id}"
        person = bilder_db.create_person(name=person_name)
        
        # Alle Faces dieser Person zuordnen
        for face_id in face_ids:
            bilder_db.assign_face_to_person(face_id, person_name, confidence=1.0)

        bilder_db.set_haupt_bild_zu_person(person_name=person_name)
        bild_der_person = bilder_db.get_person_hauptbild_data(person_name=person_name)
        print (bild_der_person)
        scan_bild_liste.show_all_images(file_names=bild_der_person)

        person_nachrichten_handler(ui=ui,text=f"Person '{person_name}' mit {len(face_ids)} Gesichtern erstellt")
        clusterbar3.update()
        wert  +=1
    clusterbar3.fertig()
    person_nachrichten_handler(ui=ui,text=f"Alle Gesichter Gefunden, {len(clusters)} Gefunden und Gespeichert")

