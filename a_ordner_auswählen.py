from cv2.detail import VoronoiSeamFinder
from os import replace
from sre_constants import BIGCHARSET
from PySide6.QtWidgets import QFileDialog,QListWidgetItem,QApplication
from PySide6.QtCore import QSize,Qt
from PySide6.QtGui import QPixmap, QIcon
from pathlib import Path
from peewee import *
from src.custom_logging import setup_logger
from src.g_db_settings_handler import SettingsHandler
from src.DBManager import FaceDB

loger = setup_logger(__name__)




def start_select_folder(parent_widget):
    folder_path = select_folder(parent_widget)
    if folder_path == None:
        return
    db_path = add_db_to_folder(folder_path)

    Settingsdb = SettingsHandler(db_path)
    Settingsdb.folder_path=folder_path
    Settingsdb.db_path=db_path
    parent_widget.selected_folder_path.setText(Settingsdb.folder_path)

    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    folder = Path(folder_path)

    # Alle Bilddateien sammeln
    image_files = [f for f in folder.glob('**/*') 
        if f.is_file() and f.suffix.lower() in image_extensions]
            # ProgressBar konfigurieren
    parent_widget.ordner_loading_names_to_progressbar.setMaximum(len(image_files))
    parent_widget.ordner_loading_names_to_progressbar.setMinimum(0)
    parent_widget.ordner_loading_names_to_progressbar.setValue(0)
    parent_widget.ordner_loading_names_to_progressbar.setVisible(True)
    
    # Optional: Text-Format für Prozentanzeige
    parent_widget.ordner_loading_names_to_progressbar.setFormat("%p% - %v von %m Bildern")
    for i, file_path in enumerate(image_files):
        # Ermöglicht UI-Updates während des Ladens
        QApplication.processEvents()
    
        image_name = str(file_path).replace(folder_path+"/","")
        bilder_db = FaceDB(db_path=db_path)
        bilder_db.add_image(file_name=image_name)
        #add_picture_names_to_db(picture_name=image_name,db_path=db_path)
        # Fortschritt aktualisieren
        progress_value = i + 1
        parent_widget.ordner_loading_names_to_progressbar.setValue(progress_value)


    # Nach dem Laden: Text ändern
    parent_widget.ordner_loading_names_to_progressbar.setFormat("Fertig! %v Bilder geladen")
    
    
    Settingsdb.close()


def select_folder(parent_widget):
    folder = QFileDialog.getExistingDirectory(
        parent_widget, 
        "Ordner auswählen", 
        "",
        QFileDialog.ShowDirsOnly
    )
    if not folder:
        loger.error("Kein Ordner wurde gewählt:")
        return None
    loger.info(f"Der Ordner wurde gewählt: {folder}")
    return folder if folder else None

def add_db_to_folder(folder_path):
    db_path = f"{folder_path}/db.db"
    try:
        db = FaceDB(db_path)
        db.connect()
        loger.info(f"DB erstellt oder existiert schon im pfad {db_path}")
        db.close()

    except Exception as e:
        loger.error(f"Fehler bei Datenbankverbindung: {e}")

    return db_path


    
def start_show_images_from_folder_in_qlistwidget(list_widget,bilder_zum_anzeigen):
    loger.info(f"anzahl der bilder die angezeit werden sollen {bilder_zum_anzeigen}")
    folder_path = list_widget.selected_folder_path.text()
    db_path = f"{folder_path}/db.db"
    if not folder_path:
        loger.error(f"Kein Ordner Gelden")
        list_widget.bilder_laden_meldung.setVisible(True)
        return
    list_widget.bilder_laden_meldung.setVisible(False)
    db_path = folder_path+"/db.db"
    """Zeigt Bilder mit Fortschrittsanzeige an"""
    if not folder_path:
        loger.error("No Folder Path")
        return
    bilder_db = FaceDB(db_path=db_path)
    
    image_files = bilder_db.get_all_images()
    ende_der_bilder_index = bilder_zum_anzeigen
    if len(image_files)< bilder_zum_anzeigen:
        ende_der_bilder_index = len(image_files)

    loger.info(f"Anzahl der Bilder {len(image_files)}")
    loger.info(f"Ende index für das anzeigen der bilder {ende_der_bilder_index}")
    image_files = image_files[:ende_der_bilder_index]
    
    # Fortschritt in der Konsole (optional)
    loger.info(f"Lade {len(image_files)} Bilder...")

        # ProgressBar konfigurieren
    list_widget.ordner_loading_pictures_progressbar.setMaximum(len(image_files))
    list_widget.ordner_loading_pictures_progressbar.setMinimum(0)
    list_widget.ordner_loading_pictures_progressbar.setValue(0)
    list_widget.ordner_loading_pictures_progressbar.setVisible(True)
    list_widget.ordner_loading_pictures_progressbar.setFormat("%p% - %v von %m Bildern")
    
    list_widget.ordner_list_bilder.clear()

    for i, bild_obj in enumerate(image_files):
        file_path = bild_obj.file_name
        real_file_path = f"{folder_path}/{file_path}"
        loger.info(f"Bild Path {real_file_path}")
        pixmap = QPixmap(str(real_file_path))
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            item = QListWidgetItem()
            item.setIcon(QIcon(scaled_pixmap))
            item.setText(file_path)
            list_widget.ordner_list_bilder.addItem(item)
            
            # Ermöglicht UI-Updates während des Ladens
            QApplication.processEvents()
        else:
            return

        # Fortschritt aktualisieren
        progress_value = i + 1
        
        list_widget.ordner_loading_pictures_progressbar.setValue(progress_value)


    # Nach dem Laden: Text ändern
    list_widget.ordner_loading_pictures_progressbar.setFormat("Fertig! %v Bilder geladen")