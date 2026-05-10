from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QPixmap,QIcon
from PySide6.QtWidgets import QApplication, QListWidgetItem, QListWidget, QVBoxLayout, QPushButton, QListView
from src.DBManager import FaceDB


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
    
    def show_all(self):
        self.clear()
        names = self._get_db().get_all_person_names()
        for name in names:
            self._add_person(name)
    

    def show_selected(self, names):
        print(f"Übergebene Namen: {names}")  # Debug: Was kommt an?
        self.clear()
        for name in names:
            self._add_person(name)
        
    def show_first_n_off_name(self, name: str, n: int = 10):
        """Zeigt die ersten n Bilder einer bestimmten Person"""
        self.clear()
        db = self._get_db()
        
        # Alle Bilder dieser Person holen
        images = db.get_images_by_person(name)
        
        # Nur die ersten n Bilder anzeigen
        for i, image in enumerate(images):
            if i >= n:
                break
            self._add_person(image.file_name)  # Neue Methode für Bilder einer Person

    def show_person(self, name):
        self._add_person(name)
    
    def _get_db(self):
        folder = self.ui.selected_folder_path.text()
        return FaceDB(f"{folder}/db.db")
    
    def _add_person(self, name):
        db = self._get_db()
        if name not in db.get_all_person_names():
            print(f"Person '{name}' existiert nicht in DB")
            return
        
        # Anzahl der Bilder holen
        image_count = db.get_person_image_count(name)
        
        file_name, bbox = db.get_person_hauptbild_data(name)
        if not file_name or not bbox:
            return
        
        path = f"{self.ui.selected_folder_path.text()}/{file_name}"
        pix = QPixmap(path)
        x1, y1, x2, y2 = bbox
        cropped = pix.copy(x1, y1, x2-x1, y2-y1)
        scaled = cropped.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        # Text mit Bildanzahl
        display_text = f"{name}\n({image_count} Bilder)"
        
        item = QListWidgetItem(QIcon(scaled), display_text)
        item.setData(Qt.UserRole, name)
        self.widget.addItem(item)
        QApplication.processEvents()