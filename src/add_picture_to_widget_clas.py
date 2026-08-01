from types import NoneType

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QListWidgetItem, QListView
from src.DBManager import FaceDB
from src.custom_logging import APP_LOGGER_NAME
import logging
from src.progressbar_clas import ProgressBar
from pathlib import Path

class PersonImageDisplay:

    logger = logging.getLogger(APP_LOGGER_NAME)
    """
    Zeigt Bilder einer Person an - entweder Originalbilder oder Gesichtsausschnitte
    """
    def __init__(self, ui, list_widget,bar=None,face_only:bool= False):
        self.current_image_item = None  
        self.current_image_path = None
        self.bar = bar
        self.ui = ui
        self.widget = list_widget
        self.face_only = face_only  # Merkt sich den aktuellen Modus
        self.widget.itemClicked.connect(self.on_image_clicked)
        self.init_widget()
        
    def init_widget(self):
        self.widget.setViewMode(QListView.ViewMode.IconMode)
        self.widget.setMovement(QListView.Movement.Static)
        self.widget.setFlow(QListView.Flow.LeftToRight)
        self.widget.setIconSize(QSize(150, 150))
        self.widget.clear()

    def on_image_clicked(self, item):
        self.current_image_item = item  # Store the clicked item
        self.current_image_path = item.text()  # Store the display text (file path)
    
    def get_current_image_path(self):
        if self.current_image_path is None:
            self.logger.warning("Kein Bild ausgewählt")
            return
        """Gibt den Pfad des aktuell ausgewählten Bildes zurück"""
        return self.current_image_path
    
    def clear(self):
        self.widget.clear()
    
    def show_all_images(self, file_names:list):
        logger = logging.getLogger(APP_LOGGER_NAME)
        try:
            # falls einzelnes dict → in liste packen
            if isinstance(file_names, dict):
                file_names = [file_names]

            for face in file_names:
                self._add_picture(
                    file_name=face["image_path"],
                    bbox=face["bbox"]
                )
        except Exception as e:
            logger.exception("Fehler in show_first_n_images")

    def show_first_n_images(self, file_names: list, n: int = 10):
        """Zeigt die ersten n Bilder an"""
        logger = logging.getLogger(APP_LOGGER_NAME)
        try:
            
            for i, file in enumerate(file_names):
                if i >= n:
                    break
                self._add_picture(
                    file_name=file["image_path"],
                    bbox=file["bbox"])
                
        except Exception as e:
            logger.exception("Fehler in show_first_n_images")

    def _get_db(self):
        """Holt die Datenbank-Instanz"""
        folder = self.ui.selected_folder_path.text()
        return FaceDB(str(Path(folder) / "db.db"))
    
    
    def _add_picture(self, file_name, bbox=None):
        """Fügt ein einzelnes Bild zur Anzeige hinzu"""
        logger = logging.getLogger(APP_LOGGER_NAME)

        try:
            base_path = self.ui.selected_folder_path.text()

            image_path = str(Path(base_path) / file_name)

            pix = QPixmap(image_path)

            if pix.isNull():
                logger.error(f"Bild konnte nicht geladen werden: {image_path}")
                return

            if self.face_only and bbox:

                # bbox = [x1, y1, x2, y2]
                x1, y1, x2, y2 = bbox

                w = x2 - x1
                h = y2 - y1

                pix = pix.copy(x1, y1, w, h)

                display_text = (f"{file_name}")

            else:
                display_text = file_name

            scaled = pix.scaled(
                150,
                150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            item = QListWidgetItem(QIcon(scaled), display_text)

            self.widget.addItem(item)
            if  self.bar == NoneType or self.bar == None:
                pass
            else:
                self.bar.update()
            QApplication.processEvents()

        except Exception as e:
            logger.exception(f"Fehler in _add_picture für Datei: {file_name}")