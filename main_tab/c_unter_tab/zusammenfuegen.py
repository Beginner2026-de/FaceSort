from pathlib import Path
from PySide6.QtWidgets import QWidget
from src.DBManager import FaceDB
from src.add_button_and_pcitures_in_two_widgets import ButtonUndBilder

def start_personen_zusammenfuegen(ui:QWidget):
    load_person_buttons_left(ui=ui)
    load_person_buttons_right(ui=ui)

def load_person_buttons_left(ui):
    folder_path = ui.selected_folder_path.text()
    db_path = str(Path(folder_path) / "db.db")
    
    if not folder_path:
        ui.nachrichten.error(text="Kein Ordner gewähl")
        return
    
    bilder_db = FaceDB(db_path=db_path)
    ui.zusammenfuegen_bilder_und_namen_left = ButtonUndBilder(ui=ui, 
                                    button_widget=ui.zusamnenfegen_person_eins,
                                    bilder_widget=ui.zusamnenfegen_person_eins_bilder,
                                    face_only=True)
    names = bilder_db.get_all_person_names()
    ui.zusammenfuegen_bilder_und_namen_left.add_person_buttons(names=names)

def load_person_buttons_right(ui):
    folder_path = ui.selected_folder_path.text()
    db_path = str(Path(folder_path) / "db.db")
    
    if not folder_path:
        ui.nachrichten.error(text="Kein Ordner gewähl")
        return
    
    bilder_db = FaceDB(db_path=db_path)
    ui.zusammenfuegen_bilder_und_namen_right = ButtonUndBilder(ui=ui, 
                                    button_widget=ui.zusamnenfegen_person_zwei,
                                    bilder_widget=ui.zusamnenfegen_person_zwei_bilder,
                                    face_only=True)
    names = bilder_db.get_all_person_names()
    ui.zusammenfuegen_bilder_und_namen_right.add_person_buttons(names=names)

def zusammenfuegen_button_gedrückt(ui):
    folder_path = ui.selected_folder_path.text()
    db_path = str(Path(folder_path) / "db.db")
    
    if not folder_path:
        ui.nachrichten.error(text="Kein Ordner gewähl")
        return
    
    bilder_db = FaceDB(db_path=db_path)
    left_name = ui.zusammenfuegen_bilder_und_namen_left.get_aktueller_name()
    right_name = ui.zusammenfuegen_bilder_und_namen_right.get_aktueller_name()
    anser =bilder_db.merge_persons(source_name=left_name,target_name=right_name)
    start_personen_zusammenfuegen(ui=ui)
    if anser["success"] == True:
        ui.nachrichten.info(f"Erfolgreich zusammen gefürt {left_name} und {right_name}")
    ui.zusammenfuegen_bilder_und_namen_right.clear_images()
    ui.zusammenfuegen_bilder_und_namen_left.clear_images()