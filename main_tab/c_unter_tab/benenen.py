from pathlib import Path
from src.DBManager import FaceDB
from src.add_button_and_pcitures_in_two_widgets import ButtonUndBilder
from src.custom_logging import APP_LOGGER_NAME
import logging

logger = logging.getLogger(APP_LOGGER_NAME)


def start_personen_bennen(ui):
    load_person_buttons(ui=ui)

def load_person_buttons(ui):
    folder_path = ui.selected_folder_path.text()
    db_path = str(Path(folder_path) / "db.db")
    
    if not folder_path:
        ui.nachrichten.error(text="Kein Ordner gewählt")
        return
    
    bilder_db = FaceDB(db_path=db_path)
    ui.bennenen_nameundbilder = ButtonUndBilder(ui=ui, 
                                    button_widget=ui.personen_benenen_namen_liste,
                                    bilder_widget=ui.personen_benenen_bilder_anzeige_box,
                                    face_only=True)
    names = bilder_db.get_all_person_names()
    ui.bennenen_nameundbilder.add_person_buttons(names=names)


    
def benenen_personen_name_abschiekcen_button(ui):
    folder_path = ui.selected_folder_path.text()
    db_path = str(Path(folder_path) / "db.db")
    db = FaceDB(db_path=db_path)
    neuer_name:str = ui.benenen_personen_name.text()
    aktueller_name = ui.bennenen_nameundbilder.get_aktueller_name()
    anser = db.rename_person(old_name=aktueller_name,new_name=neuer_name)
    logger.debug(f"Rename result: {anser}")
    load_person_buttons(ui=ui)
    if anser["success"] == True:
        ui.nachrichten.info(f"Alter Name ({anser['old_name']}) wurde zu ({anser['new_name']}) geändert")
    if anser["success"] == False:
        ui.nachrichten.error(f"{anser['error']} Alt ({aktueller_name}) Neu ({neuer_name})")
    ui.benenen_personen_name.clear()