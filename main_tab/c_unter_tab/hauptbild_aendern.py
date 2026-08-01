from pathlib import Path
from PySide6.QtWidgets import QWidget
from src.DBManager import FaceDB
from src.add_button_and_pcitures_in_two_widgets import ButtonUndBilder

def start_personen_hauptbild(ui:QWidget):
    load_person_buttons(ui=ui)

def load_person_buttons(ui):
    folder_path = ui.selected_folder_path.text()
    db_path = str(Path(folder_path) / "db.db")
    
    if not folder_path:
        ui.nachrichten.error(text="Kein Ordner gewählt")
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
    folder_path = ui.selected_folder_path.text()
    db_path = str(Path(folder_path) / "db.db")
    
    if not folder_path:
        ui.nachrichten.error(text="Kein Ordner gewählt")
        return

    bilder_db = FaceDB(db_path=db_path)

    name = ui.hauptbild_alle_button_und_bilder.get_aktueller_name()
    bild_path = ui.hauptbild_alle_button_und_bilder.get_current_image_path()

    

    if not name:
        ui.nachrichten.error(text="Keine Person ausgewählt")
        return
    if not bild_path:
        ui.nachrichten.error(text="Kein Bild ausgewählt")
        return
    try:
        bilder_db.set_haupt_bild_zu_person(person_name=name,image_path=bild_path)
        ui.nachrichten.info("Neues Hauptbild gesetzt")
    except Exception as e:
        ui.nachrichten.error(f"Hauptbild setzen fehlgeschalgen {e}")
    ui.hauptbild_alle_button_und_bilder.set_hauptbild_bild(name)