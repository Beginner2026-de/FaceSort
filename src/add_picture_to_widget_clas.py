from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QPixmap,QIcon
from PySide6.QtWidgets import QApplication, QListWidgetItem, QListWidget, QVBoxLayout, QPushButton, QListView
from src.DBManager import FaceDB
from src.custom_logging import setup_logger


class PersonImageDisplay:
    def __init__(self, ui, list_widget):
        self.ui = ui
        self.widget = list_widget
        self.init_widget()
        
    
    def init_widget(self):
        self.widget.setViewMode(QListView.ViewMode.IconMode)
        self.widget.setViewMode(QListView.ViewMode.IconMode)
        self.widget.setMovement(QListView.Movement.Static)
        self.widget.setFlow(QListView.Flow.LeftToRight)
        self.widget.setIconSize(QSize(150, 150))
        self.widget.clear()
    
    def clear(self):
        self.widget.clear()
    

    def show_all_images(self, file_name):
        self.clear()
        for name in names:
            self._add_picture(file_name=name)
        
    def show_first_n_off_name(self, name: str, n: int = 10):
        loger = setup_logger(__name__)
        #"""Zeigt die ersten n Bilder einer bestimmten Person"""
        try:
            self.clear()
            db = self._get_db()
            
            # Alle Bilder dieser Person holen
            images = db.get_images_by_person(name)
            loger.info(f"Bilder der Person Gefunden {len(images)}")
            
            # Nur die ersten n Bilder anzeigen
            for i, image in enumerate(images):
                loger.info(f"{i} Bild gefunden von person {name}")
                if i >= n:
                    break
                self._add_picture(file_name=image.file_name)  # Neue Methode für Bilder einer Person
        except Exception as e:
            loger.error(f"Fehler bekommen {e}")

    
    def get_person_hauptbild(self, name):
            db = self._get_db()
            if name not in db.get_all_person_names():
                print(f"Person '{name}' existiert nicht in DB")
                return
            
            # Anzahl der Bilder holen
            image_count = db.get_person_image_count(name)
            
            file_name, bbox = db.get_person_hauptbild_data(name)
            if not file_name or not bbox:
                return
            self._add_picture(bbox=bbox,file_name=file_name)

    def _get_db(self):
        folder = self.ui.selected_folder_path.text()
        return FaceDB(f"{folder}/db.db")
    
    
        


    def _add_picture(self,file_name,bbox=None):
        path = f"{self.ui.selected_folder_path.text()}/{file_name}"
        pix = QPixmap(path)
        if bbox:
            x1, y1, x2, y2 = bbox
            cropped = pix.copy(x1, y1, x2-x1, y2-y1)
            scaled = cropped.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        else:
            scaled = pix.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # Text mit Bildanzahl
        display_text = f"{file_name}"
        
        item = QListWidgetItem(QIcon(scaled), display_text)
        item.setData(Qt.UserRole, name)
        self.widget.addItem(item)
        QApplication.processEvents()