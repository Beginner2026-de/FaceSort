import shutil
from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QApplication
from src.DBManager import FaceDB, Image, Face, Person, FacePerson
from src.custom_logging import APP_LOGGER_NAME
import logging

logger = logging.getLogger(APP_LOGGER_NAME)

def start_personen_export(ui):
    load_export_persons_im_bild(ui)
    load_export_persons_nicht_im_bild(ui)

def select_export_destination(ui):
    try:
        folder = QFileDialog.getExistingDirectory(ui, "Export-Zielordner wählen", "")
        if not folder:
            ui.nachrichten.info("Kein Exportziel gewählt")
            return
        ui.line_export_destination.setText(folder)
    except Exception as e:
        logger.error(f"Fehler beim Öffnen des Exportziel-Dialogs: {e}")
        ui.nachrichten.error("Fehler beim Öffnen des Exportziel-Dialogs. Bitte versuche es erneut.")



def load_export_persons_im_bild(ui):
    try:
        ui.list_export_persons_im_bild.clear()
        folder_path = ui.selected_folder_path.text().strip()
        if not folder_path:
            ui.list_export_persons_im_bild.setEnabled(False)
            return

        db_path = str(Path(folder_path) / "db.db")
        bilder_db = FaceDB(db_path=db_path)
        names = bilder_db.get_all_person_names()
        if not names:
            ui.list_export_persons_im_bild.addItem("Keine Personen gefunden")
            ui.list_export_persons_im_bild.setEnabled(False)
            return

        ui.list_export_persons_im_bild.setEnabled(True)
        ui.list_export_persons_im_bild.addItems(names)
    except Exception as e:
        logger.error(f"Fehler beim Laden der Personen für 'im Bild': {e}")
        ui.nachrichten.error("Fehler beim Laden der Personen für 'im Bild'. Bitte versuche es erneut.")
        
def load_export_persons_nicht_im_bild(ui):
    try:
        ui.list_export_persons_nicht_im_bild.clear()
        folder_path = ui.selected_folder_path.text().strip()
        if not folder_path:
            ui.list_export_persons_nicht_im_bild.setEnabled(False)
            return


        db_path = str(Path(folder_path) / "db.db")
        bilder_db = FaceDB(db_path=db_path)
        names = bilder_db.get_all_person_names()
        if not names:
            ui.list_export_persons_nicht_im_bild.addItem("Keine Personen gefunden")
            ui.list_export_persons_nicht_im_bild.setEnabled(False)
            return

        ui.list_export_persons_nicht_im_bild.setEnabled(True)
        ui.list_export_persons_nicht_im_bild.addItems(names)
    except Exception as e:
        logger.error(f"Fehler beim Laden der Personen für 'nicht im Bild': {e}")
        ui.nachrichten.error("Fehler beim Laden der Personen für 'nicht im Bild'. Bitte versuche es erneut.")
        
def export_start(ui):
    try:

        folder_path = ui.selected_folder_path.text().strip()
        export_path = ui.line_export_destination.text().strip()

        if not folder_path:
            ui.nachrichten.error("Kein Quellordner ausgewählt.")
            return
        if not export_path:
            ui.nachrichten.error("Kein Exportziel gewählt.")
            return


        selected_persons_im_bild = [item.text() for item in ui.list_export_persons_im_bild.selectedItems()]
        if not selected_persons_im_bild:
            ui.nachrichten.error("Bitte wähle mindestens eine Person zum Exportieren aus.")
            return
        
        selected_persons_nicht_im_bild = [item.text() for item in ui.list_export_persons_nicht_im_bild.selectedItems()]
        if not selected_persons_im_bild:
            return []
        for name in selected_persons_nicht_im_bild:
            if name in selected_persons_im_bild:
                return ui.nachrichten.error("Eine Person kann nicht gleichzeitig in beiden Listen sein: " + name)

        person_filter_mode = _get_person_filter_mode(ui)
        ui.nachrichten.info(f"Der ausgewählte personen filter ist: {person_filter_mode}")
        db_path = str(Path(folder_path) / "db.db")
        bilder_db = FaceDB(db_path=db_path)
        images = bilder_db.get_images_by_persons(person_names_included=selected_persons_im_bild,
                                                max_other_persons=person_filter_mode,
                                                person_names_excluded=selected_persons_nicht_im_bild)
        if "error" in images:
            ui.nachrichten.error(f"{images[0]}")
        if not images:
            ui.nachrichten.error("Keine passende Bilder für den ausgewählten Filter gefunden.")
            return
        
        wanted_namelist = ""
        for name in selected_persons_im_bild:
            wanted_namelist = wanted_namelist + f"{name}, "
        wanted_namelist = wanted_namelist [:-2]  

        unwanted_namelist = ""
        for name in selected_persons_nicht_im_bild:
            unwanted_namelist = unwanted_namelist + f"{name}, "
        unwanted_namelist = unwanted_namelist [:-2]

        modus = ""
        if person_filter_mode == 0:
            modus = "Selfies"
        elif person_filter_mode == 1000:
            modus = "Alle Fotos"
        else:
            modus = f"mit {person_filter_mode} weiteren Personen"


        export_path = str(Path(export_path) / f"{modus} mit {wanted_namelist}  ")
        if unwanted_namelist:
            export_path = export_path + f"ohne {unwanted_namelist}"
        export_path = export_path.strip().rstrip("\\/")
        logger.info(f"Exportziel: {export_path}")

        export_summary = _copy_images(folder_path, export_path, bilder_db, images, ui)
        ui.nachrichten.info(f"Export abgeschlossen: {export_summary['copied']} Dateien in {export_summary['folders']} Ordnern.")
    except Exception as e:
        logger.error(f"Fehler während des Exports: {e}")
        ui.nachrichten.error("Fehler während des Exports. Bitte versuche es erneut.")

def _get_person_filter_mode(ui):
    try:
        if ui.export_personen_selfie.isChecked():
            return 0
        if ui.export_personen_mit_mehr_personen.isChecked():
            mit_andren_personen_anzahl = ui.export_personen_spinbox_anzahl_der_personen.value()
            return int(mit_andren_personen_anzahl)
        if ui.export_personen_alle_fotos.isChecked():
            return 1000
        return -1
    except Exception:
        logger.error(f"Fehler in _get_person_filter_mode {Exception}")




def _copy_images(folder_path, export_path, bilder_db, images, ui):
    try:
        root = Path(export_path)
        root.mkdir(parents=True, exist_ok=True)

        structure = ui.export_umgebung_comboBox_folder_structure.currentText()
        copied = 0
        folders = set()

        for image_path in images:
            source = Path(folder_path) / image_path

            logger.info(f"folder_path = {folder_path}")
            logger.info(f"image_path = {image_path}")
            logger.info(f"source = {source}")

            if not source.exists():
                logger.warning(f"Quelldatei nicht gefunden: {source}")
                continue

            if structure == "Automatisch":
                target = root / source.name
                target = _unique_path(target)
                target.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"target = {target}")
                logger.info(f"target parent exists = {target.parent.exists()}")
                shutil.copy2(source, target)
                copied += 1
                folders.add(str(root))

            QApplication.processEvents()

        return {"copied": copied, "folders": len(folders)}
    
    except Exception as e:
        logger.error(f"Fehler in _copy_images: {e}")
        return {"copied": 0, "folders": 0}


def _image_persons_for_path(bilder_db, image_path):
    try:
        person_names = set()
        query = (
            FacePerson
            .select(FacePerson)
            .join(Face)
            .join(Image)
            .switch(FacePerson)
            .join(Person)
            .where(Image.file_name == image_path)
        )
        for fp in query:
            person_names.add(fp.person.name)
        return person_names
    except Exception as e:
        logger.error(f"Fehler in _image_persons_for_path: {e}")
        return set()


def _unique_path(target_path: Path):
    try:
        if not target_path.exists():
            return target_path
        stem = target_path.stem
        suffix = target_path.suffix
        parent = target_path.parent
        counter = 1
        while True:
            candidate = parent / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1
    except Exception as e:
        logger.error(f"Fehler in _unique_path: {e}")
        return target_path
