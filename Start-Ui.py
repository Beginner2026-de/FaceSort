import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import QCoreApplication
from PySide6.QtUiTools import QUiLoader
from src.custom_logging import setup_logger
from main_tab.a_ordner_auswählen import start_select_folder, start_show_images_from_folder_in_qlistwidget
from main_tab.b_gesicht_erkennung import starte_gesicht_erkennung_alle
from src.g_db_settings_handler import SettingsHandler
from src.resource_path import resource_path
from main_tab.c_unter_tab.start_personen_scan import start_personen_scan, person_nachrichten_handler
from main_tab.c_unter_tab.benenen import start_personen_bennen, benenen_personen_name_abschiekcen_button
from main_tab.c_unter_tab.zusammenfuegen import start_personen_zusammenfuegen, zusammenfuegen_button_gedrückt
from main_tab.c_unter_tab.hauptbild_aendern import start_personen_hauptbild, hauptbild_button_gedrückt
from main_tab.c_unter_tab.personen_loeschen import start_personen_loeschen, loeschen_button_gedrückt

loger = setup_logger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        

        # UI laden (passen Sie den Dateinamen an)
        loader = QUiLoader()
        self.ui = loader.load(resource_path("QT-Ui/Main.ui"))

        loger.info("UI geladen")
        self.ui.show()
        
        gesammt_anzahl_zu_ladener_bilder= 100
        # Bilder
        self.ui.btn_load_folder.clicked.connect(lambda: start_select_folder(self.ui))
        self.ui.bilder_anzeigen.clicked.connect(lambda: start_show_images_from_folder_in_qlistwidget(self.ui,gesammt_anzahl_zu_ladener_bilder))
        self.ui.bilder_laden_meldung.setVisible(False)

        #Scan
        self.ui.btn_start_scan.clicked.connect( lambda: starte_gesicht_erkennung_alle(self.ui))

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

        def on_chnage_in_person_tab(ui):
            index = ui.personen_tabWidget.currentIndex()
            loger.info(f"Personen Tab gewechselt zu index: {index}")
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
            loger.info(f"Modus size changed to {modus}")
            folder_path = self.ui.selected_folder_path.text()
            db_path = str(folder_path)+"/db.db"
            Settingsdb = SettingsHandler(db_path)
            Settingsdb.mode = modus
            on_change_in_tab(self)

        def on_thread_changed():
            threads = self.ui.spin_threads.value()
            loger.info(f"Thread size changed to {threads}")
            folder_path = self.ui.selected_folder_path.text()
            db_path = str(folder_path)+"/db.db"
            Settingsdb = SettingsHandler(db_path)
            Settingsdb.threads = threads
            on_change_in_tab(self)

        def on_change_in_tab(self):
            index = self.ui.tabWidget.currentIndex()
            loger.info(f"Tab gewechselt zu index: {index}")

            if index == 2:
                person_nachrichten_handler(ui=self.ui,display=False)
            # Oder nach Tab-Name
            if index == 6:
                folder_path = self.ui.selected_folder_path.text()
                if not folder_path:
                    make_settings_invisible()
                    self.ui.einstellungen_nachrichten_text.setText("Kein Ordner gelden")
                    loger.error(f"kein ordner gelden")
                    return
                make_settings_visible()
                self.ui.einstellungen_nachrichten_text.setText("Ordner gefunden")
                db_path = str(folder_path)+"/db.db"
                loger.info(f"db path {db_path}")
                Settingsdb = SettingsHandler(db_path)
                threads = Settingsdb.threads
                mode = Settingsdb.mode

                self.ui.combo_mode.setCurrentText(mode) 
                self.ui.spin_threads.setValue(threads)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

