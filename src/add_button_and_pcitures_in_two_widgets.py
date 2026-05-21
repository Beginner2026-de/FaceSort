
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QPushButton, QScrollArea
from src.DBManager import FaceDB
from src.custom_logging import setup_logger
from src.add_picture_to_widget_clas import PersonImageDisplay

class ButtonUndBilder:

    logger = setup_logger(__name__)
    """
    Zeigt Bilder einer Person an - entweder Originalbilder oder Gesichtsausschnitte
    """
    def __init__(self, ui, button_widget,bilder_widget,hauptbild_widget=None,face_only:bool= False, with_hauptbild_widget:bool= False):
        self.ui = ui 
        self.with_hauptbild_widget = with_hauptbild_widget
        self.button_widget:QWidget = button_widget
        self.bilder_widget:QListWidget = bilder_widget
        self.aktueller_name:str = ""
        self.face_only = face_only  # Merkt sich den aktuellen Modus
        self.bild_anzeige = PersonImageDisplay(ui=self.ui,list_widget=self.bilder_widget,face_only=self.face_only)
        self._init_button_widget()
        if with_hauptbild_widget == True:
            self.logger.info("Hauptbild erstellt")
            self.hauptbild_widget = PersonImageDisplay(ui=self.ui,list_widget=hauptbild_widget,face_only=True)

    def add_person_buttons(self, names: list):
        for name in names:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: self.on_person_clicked(n))
            self.button_layout.addWidget(btn)
        
    def _init_button_widget(self):
        # 1. Hauptlayout für button_widget
        if self.button_widget.layout() is None:
            main_layout = QVBoxLayout()
            self.button_widget.setLayout(main_layout)
        else:
            main_layout = self.button_widget.layout()
            # Alte Inhalte löschen
            while main_layout.count():
                item = main_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # 2. ScrollArea erstellen
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 3. Container Widget für die Buttons
        container = QWidget()
        self.button_layout = QVBoxLayout(container)
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Oben ausrichten
        scroll_area.setWidget(container)
        
        # 4. ScrollArea zum Hauptlayout hinzufügen
        main_layout.addWidget(scroll_area)


    def on_person_clicked(self, name: str,load_all_images:bool=False):
        self.logger.info(f"Person geklickt: {name}")
        self.aktueller_name = name 
        db = self._get_db()
        try:
            try:
                if self.with_hauptbild_widget == True:
                    self.set_hauptbild_bild(name=name)
                    self.logger.info("Hauptbild geladen")
            except:
                self.logger.info("Kein Hauptbild geladen")
                
            images = db.get_all_persons_faces(person_name=name)

            self._load_images(images,load_all_images=load_all_images)



        except Exception as e:
            self.logger.error(f"Fehle in on_person_clicked: {e}")
    
    
    
    def get_current_image_path(self):
        """Gibt den Pfad des aktuell ausgewählten Bildes zurück"""
        return self.bild_anzeige.get_current_image_path()

    def get_aktueller_name(self) -> str:
        """Gibt den zuletzt geklickten Personennamen zurück"""
        return self.aktueller_name

    def _load_images(self, images,load_all_images):
        # alte löschen
        for i in reversed(range(self.bilder_widget.count())):
            self.bilder_widget.takeItem(i)

        if load_all_images == True:
            self.bild_anzeige.show_all_images(file_names=images)
        else:        
            self.bild_anzeige.show_first_n_images(file_names=images)

    def _get_db(self):
        """Holt die Datenbank-Instanz"""
        folder = self.ui.selected_folder_path.text()
        return FaceDB(f"{folder}/db.db")
    

    def set_hauptbild_bild(self,name):
        try:
            db = self._get_db()
            hauptbild = db.get_person_hauptbild_data(person_name=name)
            self.hauptbild_widget.clear()
            self.hauptbild_widget.show_all_images(file_names=hauptbild)
        except Exception as e:
            self.logger.error(e) 

    def clear_images(self):
        self.bild_anzeige.clear()