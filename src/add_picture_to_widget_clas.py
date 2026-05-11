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
    

    def show_all_images(self, file_name):
        self.clear()
        for file in file_name:
            self._add_image(file)
        
    def show_first_n_images(self, file_name: str, n: int = 10):
        """Zeigt die ersten n Bilder einer bestimmten Person"""
        self.clear()

        # Nur die ersten n Bilder anzeigen
        for i, file in enumerate(file_name):
            if i >= n:
                break
            self._add_image(file.file_name)  # Neue Methode für Bilder einer Person

    def _get_db(self):
        folder = self.ui.selected_folder_path.text()
        return FaceDB(f"{folder}/db.db")
    
    def _add_image(self, file_name):
        db = self._get_db()
        
        file_name, bbox = db.get_person_hauptbild_data(file_name)
        if not file_name or not bbox:
            return
        
        path = f"{self.ui.selected_folder_path.text()}/{file_name}"
        pix = QPixmap(path)
        x1, y1, x2, y2 = bbox
        cropped = pix.copy(x1, y1, x2-x1, y2-y1)
        scaled = cropped.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        item = QListWidgetItem(QIcon(scaled))
        item.setData(Qt.UserRole, file_name)
        self.widget.addItem(file_name)
        QApplication.processEvents()