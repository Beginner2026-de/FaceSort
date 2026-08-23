# Test
from operator import mod
import os
import sys
from pathlib import Path

# Erzwingt den korrekten Pfad zu den PySide6-Plugins im fertigen Nuitka-Ordner
base_dist_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(base_dist_dir, "shiboken6", "plugins", "platforms")
os.environ["OPENCV_HEADLESS"] = "1"
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices, QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QStyleFactory
from main_tab.a_ordner_auswählen import start_select_folder, start_show_images_from_folder_in_qlistwidget
from main_tab.b_gesicht_erkennung import starte_gesicht_erkennung_alle
from src.g_db_settings_handler import SettingsHandler
from src.resource_path import resource_path
from src.nachrichten_clas import Nachrichten
from main_tab.c_unter_tab.start_personen_scan import start_personen_scan
from main_tab.c_unter_tab.benenen import start_personen_bennen, benenen_personen_name_abschiekcen_button
from main_tab.c_unter_tab.zusammenfuegen import start_personen_zusammenfuegen, zusammenfuegen_button_gedrückt
from main_tab.c_unter_tab.hauptbild_aendern import start_personen_hauptbild, hauptbild_button_gedrückt
from main_tab.c_unter_tab.personen_loeschen import start_personen_loeschen, loeschen_button_gedrückt
from main_tab.d_export import export_start ,start_personen_export,select_export_destination
from src.custom_logging import setup_logger,APP_LOGGER_NAME, logging
from src.version import get_version_from_webseite

logger = setup_logger(APP_LOGGER_NAME, level=logging.DEBUG)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        

        # UI laden (passen Sie den Dateinamen an)
        loader = QUiLoader()
        self.ui = loader.load(resource_path("QT-Ui/Main.ui"))

        logger.info("UI geladen")
        self.ui.show()
        if "Update" in get_version_from_webseite():
            self.ui.lade_neuer_version_herunter.setVisible(True)
        else:
            self.ui.lade_neuer_version_herunter.setVisible(False)

        self.ui.exit_app.clicked.connect(lambda: save_imports())
        self.shortcut_enter = QShortcut(QKeySequence(Qt.Key_Return), self.ui)
        self.shortcut_enter.activated.connect(lambda: on_enter_pressed(self))

        def on_enter_pressed(self):
            if self.ui.tabWidget.currentIndex() == 2 and self.ui.personen_tabWidget.currentIndex() == 1:   
                benenen_personen_name_abschiekcen_button(ui=self.ui)
            if self.ui.tabWidget.currentIndex() == 2 and self.ui.personen_tabWidget.currentIndex() == 2:
                zusammenfuegen_button_gedrückt(ui=self.ui)
            if self.ui.tabWidget.currentIndex() == 2 and self.ui.personen_tabWidget.currentIndex() == 3:
                hauptbild_button_gedrückt(ui=self.ui)
            if self.ui.tabWidget.currentIndex() == 2 and self.ui.personen_tabWidget.currentIndex() == 4:
                loeschen_button_gedrückt(ui=self.ui)
        
        def save_imports():
            path_for_os = "make-reports/windows" if os.name == "nt" else "make-reports/linux"
            Path(f"{path_for_os}").mkdir(parents=True, exist_ok=True)
            with open(Path(f"{path_for_os}/runtime_imports.txt"), "w") as f:
                for mod in sorted(sys.modules):
                    #check if module is already in runtime_imports.txt
                    with open(Path(f"{path_for_os}/runtime_imports.txt")) as nofollow_file:
                        nofollow_modules = [line.strip() for line in nofollow_file if line.strip()]
                    if mod not in nofollow_modules: 
                        f.write(mod + "\n")
            sys.exit(app.exec())

        self.ui.nachrichten = Nachrichten(ui=self.ui,widget=self.ui.nachrichten_main)
        self.ui.nachrichten.info(get_version_from_webseite())
        
        gesammt_anzahl_zu_ladener_bilder= 100
        # Bilder
        self.ui.btn_load_folder.clicked.connect(lambda: start_select_folder(self.ui))
        self.ui.bilder_anzeigen.clicked.connect(lambda: start_show_images_from_folder_in_qlistwidget(self.ui,gesammt_anzahl_zu_ladener_bilder))
        self.ui.bilder_laden_meldung.setVisible(False)
        self.ui.lade_neuer_version_herunter.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(download_url)))

        #Scan
        self.ui.btn_start_scan.clicked.connect( lambda: starte_gesicht_erkennung_alle(self.ui))
        self.ui.btn_stop_scan.clicked.connect(lambda: btn_stop_scan_pressed(self.ui))
        self.ui.stope_scan = False
        def btn_stop_scan_pressed(ui):
            logger.info("Scan Stop Button Gedrückt")
            self.ui.stope_scan = True

        # Personen
        #Personen Grupierung
        self.ui.starte_personen_scan.clicked.connect(lambda: start_personen_scan(ui=self.ui))        
        #Personen unbennen
        self.ui.personen_tabWidget.currentChanged.connect(lambda: on_chnage_in_person_tab(ui=self.ui))
        self.ui.benenen_personen_name_abschiekcen_button.clicked.connect(lambda: benenen_personen_name_abschiekcen_button(ui=self.ui))
        #Personen zusammenfuegen
        self.ui.zusammenfuegen_button.clicked.connect(lambda: zusammenfuegen_button_gedrückt(ui=self.ui))
        #Hauptbild ändern
        self.ui.hauptbild_setzen.clicked.connect(lambda: hauptbild_button_gedrückt(ui=self.ui))
        #Personen löschen
        self.ui.person_loeschen_button.clicked.connect(lambda: loeschen_button_gedrückt(ui=self.ui))

        # Export
        self.ui.btn_start_export.clicked.connect(lambda: export_start(self.ui))
        self.ui.btn_select_export_destination.clicked.connect(lambda: select_export_destination(self.ui))
 
        def on_chnage_in_person_tab(ui):
            index = ui.personen_tabWidget.currentIndex()
            logger.info(f"Personen Tab gewechselt zu index: {index}")
            if index == 1:
                start_personen_bennen(ui)
            if index == 2:
                start_personen_zusammenfuegen(ui=ui)
            if index == 3:
                start_personen_hauptbild(ui=ui)
            if index == 4:                
                start_personen_loeschen(ui=ui)

        # Einstellungen
            # In den Tab wechseln
        self.ui.tabWidget.currentChanged.connect(lambda: on_change_in_tab(self))
            # Thread anzahl ändern
        self.ui.spin_threads.valueChanged.connect(lambda: on_thread_changed())
            # Modus umstellen
        self.ui.combo_mode.currentTextChanged.connect(lambda: on_modus_changed())

        def make_settings_invisible():
            self.ui.spin_threads.setVisible(False)
            self.ui.label_threads.setVisible(False)
            self.ui.label_gpu_or_cpu.setVisible(False)
            self.ui.combo_mode.setVisible(False)

        def make_settings_visible():
            self.ui.spin_threads.setVisible(True)
            self.ui.label_threads.setVisible(True)
            self.ui.label_gpu_or_cpu.setVisible(True)
            self.ui.combo_mode.setVisible(True)

        def on_modus_changed():
            modus = self.ui.combo_mode.currentText()
            logger.info(f"Modus geändert: {modus}")
            folder_path = self.ui.selected_folder_path.text()
            db_path = str(Path(folder_path) / "db.db")
            Settingsdb = SettingsHandler(db_path)
            Settingsdb.mode = modus
            on_change_in_tab(self)

        def on_thread_changed():
            threads = self.ui.spin_threads.value()
            logger.info(f"Thread-Anzahl geändert: {threads}")
            folder_path = self.ui.selected_folder_path.text()
            db_path = str(Path(folder_path) / "db.db")
            Settingsdb = SettingsHandler(db_path)
            Settingsdb.threads = threads
            on_change_in_tab(self)

        def on_change_in_tab(self):
            index = self.ui.tabWidget.currentIndex()
            logger.info(f"Tab gewechselt zu index: {index}")

            if index == 2:
                pass
            if index == 3:
                start_personen_export(self.ui)
            # Oder nach Tab-Name
            if index == 4:
                folder_path = self.ui.selected_folder_path.text()
                if not folder_path:
                    make_settings_invisible()
                    self.ui.einstellungen_nachrichten_text.setText("Kein Ordner gelden")
                    logger.error("Kein Ordner gefunden (Einstellungen)")
                    return
                make_settings_visible()
                self.ui.einstellungen_nachrichten_text.setText("Ordner gefunden")
                db_path = str(Path(folder_path) / "db.db")
                logger.info(f"DB-Pfad: {db_path}")
                Settingsdb = SettingsHandler(db_path)
                threads = Settingsdb.threads
                mode = Settingsdb.mode

                self.ui.combo_mode.setCurrentText(mode) 
                self.ui.spin_threads.setValue(threads)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    
    window = MainWindow()
    sys.exit(app.exec())

