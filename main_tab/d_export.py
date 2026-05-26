import shutil
from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QApplication
from src.DBManager import FaceDB, Image, Face, Person, FacePerson
from src.nachrichten_clas import Nachrichten
from src.custom_logging import setup_logger

loger = setup_logger(__name__)

def start_personen_export(ui):
    load_export_persons(ui)

def select_export_destination(ui):
    folder = QFileDialog.getExistingDirectory(ui, "Export-Zielordner wählen", "")
    if not folder:
        nachrichten = Nachrichten(ui=ui,widget=ui.exportnachrichten_nachrichten)
        nachrichten.info("Kein Exportziel gewählt")
        return
    ui.line_export_destination.setText(folder)



def load_export_persons(ui):
    ui.list_export_persons.clear()
    folder_path = ui.selected_folder_path.text().strip()
    if not folder_path:
        ui.list_export_persons.setEnabled(False)
        return

    db_path = f"{folder_path}/db.db"
    bilder_db = FaceDB(db_path=db_path)
    names = bilder_db.get_all_person_names()
    if not names:
        ui.list_export_persons.addItem("Keine Personen gefunden")
        ui.list_export_persons.setEnabled(False)
        return

    ui.list_export_persons.setEnabled(True)
    ui.list_export_persons.addItems(names)


def export_start(ui):
    nachrichten = Nachrichten(ui=ui, widget=ui.personen_nachrichten)

    folder_path = ui.selected_folder_path.text().strip()
    export_path = ui.line_export_destination.text().strip()

    if not folder_path:
        nachrichten.error("Kein Quellordner ausgewählt.")
        return
    if not export_path:
        nachrichten.error("Kein Exportziel gewählt.")
        return

    if ui.radio_export_filter.isChecked():
        nachrichten.error("Filter-Export ist noch nicht implementiert. Bitte wähle Nach Person.")
        return

    if not ui.radio_export_person.isChecked():
        nachrichten.error("Bitte wähle einen Exportmodus.")
        return

    selected_persons = [item.text() for item in ui.list_export_persons.selectedItems()]
    if not selected_persons:
        nachrichten.error("Bitte wähle mindestens eine Person zum Exportieren aus.")
        return

    filter_mode = _get_person_filter_mode(ui)
    db_path = f"{folder_path}/db.db"
    bilder_db = FaceDB(db_path=db_path)

    images = _collect_images_for_persons(bilder_db, selected_persons, filter_mode)
    if not images:
        nachrichten.error("Keine passenden Bilder für den ausgewählten Filter gefunden.")
        return

    export_summary = _copy_images(folder_path, export_path, bilder_db, images, selected_persons, ui)
    nachrichten.info(f"Export abgeschlossen: {export_summary['copied']} Dateien in {export_summary['folders']} Ordnern.")


def _get_person_filter_mode(ui):
    if ui.radio_export_person_only.isChecked():
        return "only"
    if ui.radio_export_person_with_others.isChecked():
        return "with_others"
    if ui.radio_export_person_any.isChecked():
        return "any"
    return "any"


def _collect_images_for_persons(bilder_db: FaceDB, selected_persons, filter_mode):
    selected_set = set(selected_persons)
    image_persons = {}

    query = (
        FacePerson
        .select(FacePerson)
        .join(Person)
        .switch(FacePerson)
        .join(Face)
        .join(Image)
    )

    # Eindeutige Zuordnungen aufbauen
    for fp in query:
        image_path = fp.face.image.file_name
        person_name = fp.person.name
        image_persons.setdefault(image_path, set()).add(person_name)

    ausgewählte_bilder = set()
    for image_path, person_names in image_persons.items():
        if filter_mode == "any":
            if person_names & selected_set:
                ausgewählte_bilder.add(image_path)
        elif filter_mode == "only":
            if person_names and person_names <= selected_set:
                ausgewählte_bilder.add(image_path)
        elif filter_mode == "with_others":
            if person_names & selected_set and len(person_names - selected_set) > 0:
                ausgewählte_bilder.add(image_path)

    return sorted(ausgewählte_bilder)


def _copy_images(folder_path, export_path, bilder_db, images, selected_persons, ui):
    root = Path(export_path)
    persons = set(selected_persons)
    root.mkdir(parents=True, exist_ok=True)

    structure = ui.combo_folder_structure.currentText()
    copied = 0
    folders = set()

    for image_path in images:
        source = Path(folder_path) / image_path
        if not source.exists():
            loger.warning(f"Quelldatei nicht gefunden: {source}")
            continue

        if structure == "Alle in einem Ordner":
            target = root / source.name
            target = _unique_path(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            copied += 1
            folders.add(str(root))
        else:
            # Name\Bild: je ausgewählte Person einen Ordner erzeugen
            image_persons = _image_persons_for_path(bilder_db, image_path)
            relevant_persons = image_persons & persons
            if not relevant_persons:
                relevant_persons = persons
            for person_name in relevant_persons:
                target = root / person_name / image_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target = _unique_path(target)
                shutil.copy2(source, target)
                copied += 1
                folders.add(str(target.parent))

        QApplication.processEvents()

    return {"copied": copied, "folders": len(folders)}


def _image_persons_for_path(bilder_db, image_path):
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


def _unique_path(target_path: Path):
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
