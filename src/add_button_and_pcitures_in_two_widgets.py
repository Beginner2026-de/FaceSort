from tarfile import NUL
from tkinter import Widget

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QListWidgetItem,QWidget, QListWidget, QVBoxLayout, QPushButton, QListView,QScrollArea
from src.DBManager import FaceDB
from src.custom_logging import setup_logger
from src.add_picture_to_widget_clas import PersonImageDisplay

class ButtonUndBilder:

    logger = setup_logger(__name__)
    """
    Zeigt Bilder einer Person an - entweder Originalbilder oder Gesichtsausschnitte
    """
    def __init__(self, ui, button_widget,bilder_widget,face_only:bool= False):
        self.ui = ui
        self.button_widget:QWidget = button_widget
        self.bilder_widget:QListWidget = bilder_widget
        self.aktueller_name:str = ""
        self.face_only = face_only  # Merkt sich den aktuellen Modus
        self._init_button_widget()

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


    def on_person_clicked(self, name: str):
        self.logger.info(f"Person geklickt: {name}")
        self.ui.bennen_aktuelle_person = name 
        db = self._get_db()

        images = db.get_all_persons_faces(person_name=name)

        self._load_images(images)

    def _load_images(self, images):
        # alte löschen
        for i in reversed(range(self.bilder_widget.count())):
            self.bilder_widget.takeItem(i)

        bild_anzeige = PersonImageDisplay(ui=self.ui,list_widget=self.bilder_widget,face_only=self.face_only)
        bild_anzeige.show_first_n_images(file_names=images)

    def _get_db(self):
        """Holt die Datenbank-Instanz"""
        folder = self.ui.selected_folder_path.text()
        return FaceDB(f"{folder}/db.db")