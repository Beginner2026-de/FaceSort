from PySide6.QtWidgets import QFileDialog,QApplication
from pathlib import Path
from src.g_db_settings_handler import SettingsHandler
from src.DBManager import FaceDB
from src.progressbar_clas import ProgressBar
from src.add_picture_to_widget_clas import PersonImageDisplay
from src.custom_logging import APP_LOGGER_NAME
import logging
import os
import re


def _index_to_short_name(index: int) -> str:
    """Konvertiert eine Ganzzahl in eine kurze Base-26 Buchstabenfolge (a, b, ..., z, aa, ab, ...)."""
    if index < 0:
        raise ValueError("Index must be non-negative")
    letters = []
    while True:
        letters.append(chr(ord('a') + (index % 26)))
        index = index // 26 - 1
        if index < 0:
            break
    return ''.join(reversed(letters))


def _rename_images_recursive(folder_path, image_extensions, logger=None):
    """Rekursiv alle Bilddateien in `folder_path` umbenennen.
    Die Dateiendungen bleiben erhalten. Namen werden kurz erzeugt (a, b, ..., z, aa, ...).
    Falls ein Zielname bereits existiert, wird weitergezählt, bis ein freier Name gefunden ist.
    """
    folder = Path(folder_path)
    # Zuerst alle Bilddateien deterministisch sammeln (sortiert)
    files = sorted([f for f in folder.glob('**/*') if f.is_file() and f.suffix.lower() in image_extensions])

    short_name_re = re.compile(r'^[a-z]+$')
    # Reserviere bereits vorhandene kurze Namen, damit sie nicht neu vergeben werden
    used_names = set()
    for f in files:
        if short_name_re.match(f.stem):
            used_names.add(f.stem)

    counter = 0
    for f in files:
        # Wenn der Name bereits im gewünschten Schema ist, überspringen
        if short_name_re.match(f.stem):
            if logger:
                logger.debug(f"Überspringe bereits passendes Bild: {f}")
            continue

        # Finde nächsten freien kurzen Namen (global über alle Ordner hinweg)
        while True:
            candidate = _index_to_short_name(counter)
            counter += 1
            if candidate not in used_names:
                used_names.add(candidate)
                break

        target = f.with_name(candidate + f.suffix.lower())
        try:
            f.rename(target)
            if logger:
                logger.info(f"Umbenannt: {f} -> {target}")
        except Exception as e:
            if logger:
                logger.exception(f"Fehler beim Umbenennen von {f}: {e}")
            # Bei Fehlern weiterfahren
            continue

def start_select_folder(parent_widget):
    logger = logging.getLogger(APP_LOGGER_NAME)
    folder_path = select_folder(parent_widget)
    if folder_path == None:
        return
    db_path = add_db_to_folder(folder_path)
    if parent_widget.bilder_umbenene.isChecked():
        logger.info("Bilder umbenennen aktiviert, starte Bilder umbenennen")
    else:
        logger.info("Bilder umbenennen nicht aktiviert, überspringe Bilder umbenennen")

    Settingsdb = SettingsHandler(db_path)
    Settingsdb.folder_path=folder_path
    Settingsdb.db_path=db_path
    parent_widget.selected_folder_path.setText(Settingsdb.folder_path)

    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    folder = Path(folder_path)

    # Falls aktiviert: Bilder rekursiv umbenennen (nur Basisname, Endung bleibt)
    if parent_widget.bilder_umbenene.isChecked():
        try:
            _rename_images_recursive(folder_path, image_extensions, logger)
        except Exception as e:
            parent_widget.ui.nachrichten.error(f"Fehler beim Umbenennen der Bilder: {e}")

    # Alle Bilddateien sammeln
    image_files = [f for f in folder.glob('**/*') 
        if f.is_file() and f.suffix.lower() in image_extensions]
            # ProgressBar konfigurieren
 
    
    parent_widget.nachrichten.info(f"{len(image_files)} Fotos gefunden starte mit dem hinzufügen der fotos zu DB")
    bar = ProgressBar(ui=parent_widget,max=len(image_files),list_widget=parent_widget.ordner_loading_names_to_progressbar)
    try:
        for file_path in image_files:
            # Ermöglicht UI-Updates während des Ladens
            QApplication.processEvents()
            path_image_name = file_path.relative_to(folder)
            bilder_db = FaceDB(db_path=db_path)
            bilder_db.add_image(file_name=path_image_name)
            bar.update()
    except Exception as e:
        parent_widget.nachrichten.error(f"Fehler beim speichern des Bild namens in die DB {e}")

    bar.fertig(abschluss_text=f"Alle bilder geladen")
    
    Settingsdb.close()

def select_folder(parent_widget):
    logger = logging.getLogger(APP_LOGGER_NAME)
    home_dir = str(Path.home())
    folder = QFileDialog.getExistingDirectory(
        parent_widget, 
        "Ordner auswählen", 
        home_dir

    )
    if not folder:
        logger.error("Kein Ordner wurde gewählt")
        return None
    logger.info(f"Ordner gewählt: {folder}")
    return folder if folder else None

def add_db_to_folder(folder_path):
    logger = logging.getLogger(APP_LOGGER_NAME)
    db_path = str(Path(folder_path) / "db.db")
    try:
        FaceDB(db_path)
        logger.info(f"DB erstellt oder bereits vorhanden: {db_path}")

    except Exception as e:
        logger.exception(f"Fehler bei Datenbankverbindung: {e}")

    return db_path

def start_show_images_from_folder_in_qlistwidget(list_widget,bilder_zum_anzeigen):
    logger = logging.getLogger(APP_LOGGER_NAME)
    logger.info(f"Anzahl der Bilder, die angezeigt werden sollen: {bilder_zum_anzeigen}")
    folder_path = list_widget.selected_folder_path.text()
    db_path = str(Path(folder_path) / "db.db")
    if not folder_path:
        logger.error("Kein Ordner gesetzt")
        list_widget.bilder_laden_meldung.setVisible(True)
        return
    list_widget.bilder_laden_meldung.setVisible(False)
    db_path = str(Path(folder_path) / "db.db")
    """Zeigt Bilder mit Fortschrittsanzeige an"""
    if not folder_path:
        logger.error("Kein Ordner-Pfad vorhanden")
        return
    bilder_db = FaceDB(db_path=db_path)
    
    image_files = bilder_db.get_all_images()
    ende_der_bilder_index = bilder_zum_anzeigen
    if len(image_files)< bilder_zum_anzeigen:
        ende_der_bilder_index = len(image_files)

    logger.info(f"Anzahl der Bilder in DB: {len(image_files)}")
    logger.info(f"Ende-Index für Anzeige: {ende_der_bilder_index}")
    image_files = image_files[:ende_der_bilder_index]
    
    # Fortschritt in der Konsole (optional)
    logger.info(f"Starte Laden von {len(image_files)} Bildern")

    bar = ProgressBar(ui=list_widget,max=len(image_files),list_widget=list_widget.ordner_loading_pictures_progressbar)
    bilder_widget = PersonImageDisplay(ui=list_widget,list_widget=list_widget.ordner_list_bilder,bar=bar)
    bilder_widget.show_all_images(file_names=image_files)

    bar.fertig(abschluss_text="Bilder Geladen")