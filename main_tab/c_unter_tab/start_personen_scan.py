from src.custom_logging import setup_logger
from PySide6.QtWidgets import QApplication
from src.DBManager import FaceDB
import numpy as np
from sklearn.cluster import DBSCAN
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
    
    if len(faces) == 0:
        person_nachrichten_handler(ui=ui,level="error",text="Keine Gesichter in der Datenbank gefunden")
        return
    
    # Embeddings in Matrix umwandeln
    embeddings = []
    face_ids = []
    for face in faces:
        emb = np.frombuffer(face["embedding"], dtype=np.float32)
        embeddings.append(emb)
        face_ids.append(face["face_id"])
        clusterbar.update()
    clusterbar.fertig()
    
    embeddings = np.array(embeddings)
    
    # Clustering
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
    labels = clustering.fit_predict(embeddings)
    person_nachrichten_handler(ui=ui,text="Starte Gesicht zu ordnung")
    clusterbar2 = ProgressBar(ui=ui,max=len(faces),list_widget=ui.gefundene_personen_scan_progressBar)

    # Cluster zu Personen zuordnen
    clusters = {}
    for face_id, label in zip(face_ids, labels):
        if label == -1:  # Einzelgesicht ohne Cluster
            cluster_key = f"single_{face_id}"
            clusters[cluster_key] = [face_id]
        else:
            clusters.setdefault(label, []).append(face_id)
        clusterbar2.update()
    clusterbar2.fertig()


    person_nachrichten_handler(ui,text=f"Gefundene Gesichter: {len(clusters)}")
    
    return clusters

def auto_assign_persons(ui, eps=0.5, min_samples=2, similarity_threshold=0.6):
    scan_bild_liste = PersonImageDisplay(ui=ui,list_widget=ui.starte_personen_scan_bild_liste,face_only=True)
    scan_bild_liste.clear()
    folder_path = ui.selected_folder_path.text()
    db_path = f"{folder_path}/db.db"

    if not folder_path:
        person_nachrichten_handler(ui=ui,level="error",text=f"Kein Ordner Geladen")

    bilder_db = FaceDB(db_path=db_path)
    clusters = cluster_faces(ui=ui)
    
    if not clusters:
        person_nachrichten_handler(ui=ui,text="Keine Cluster gefunden",level="error")
        return

    # Bestehende Personen und ihre Embeddings laden
    existing_persons = {}
    for person_name in bilder_db.get_all_person_names():  # Diese Methode musst du in FaceDB haben
        face_ids = bilder_db.get_faces_by_person(person_name)  # Diese Methode musst du in FaceDB haben
        if face_ids:
            embeddings = []
            for face_id in face_ids:
                embedding = bilder_db.get_face_embedding(face_id)  # Diese Methode musst du in FaceDB haben
                embeddings.append(embedding)
            existing_persons[person_name] = {'embeddings': embeddings, 'face_ids': face_ids}

    clusterbar3 = ProgressBar(ui=ui,max=len(clusters),list_widget=ui.gefundene_personen_scan_progressBar)

    for cluster_id, face_ids in clusters.items():
        # Embeddings des neuen Clusters laden
        new_embeddings = []
        for face_id in face_ids:
            embedding = bilder_db.get_face_embedding(face_id)
            new_embeddings.append(embedding)
        
        # Nach ähnlicher existierender Person suchen
        matched_person = None
        best_similarity = 0
        
        for person_name, person_data in existing_persons.items():
            for existing_emb in person_data['embeddings']:
                for new_emb in new_embeddings:
                    sim = np.dot(existing_emb, new_emb) / (np.linalg.norm(existing_emb) * np.linalg.norm(new_emb))
                    if sim > similarity_threshold and sim > best_similarity:
                        best_similarity = sim
                        matched_person = person_name
        
        if matched_person:
            # Zu existierender Person hinzufügen
            for face_id in face_ids:
                bilder_db.assign_face_to_person(face_id, matched_person, confidence=best_similarity)
            bilder_db.set_haupt_bild_zu_person(person_name=matched_person)
            person_nachrichten_handler(ui=ui,text=f"Zu '{matched_person}' hinzugefügt ({len(face_ids)} Gesichter)")
        else:
            # Neue Person anlegen
            person_name = f"Person_{cluster_id}"
            for face_id in face_ids:
                bilder_db.assign_face_to_person(face_id, person_name, confidence=1.0)
            bilder_db.set_haupt_bild_zu_person(person_name=person_name)
            # Zu existing_persons hinzufügen
            existing_persons[person_name] = {'embeddings': new_embeddings, 'face_ids': face_ids}
            person_nachrichten_handler(ui=ui,text=f"Neue Person '{person_name}' erstellt")
        clusterbar3.update()
    clusterbar3.fertig()
    
    neue_personen_liste = bilder_db.get_all_person_names()
    clusterbar4 = ProgressBar(ui=ui,max=len(neue_personen_liste),list_widget=ui.gefundene_personen_scan_progressBar)
    for person_name in neue_personen_liste:   
        haupt_bild = bilder_db.get_person_hauptbild_data(person_name)
        scan_bild_liste.show_all_images(file_names=haupt_bild)
        clusterbar4.update()
    clusterbar4.fertig(abschluss_text="Alle Hauptbilder geladen")