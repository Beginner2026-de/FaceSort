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
    
    def clear(self):
        self.widget.clear()
    
    def show_all(self):
        self.clear()
        names = self._get_db().get_all_person_names()
        for name in names:
            self._add_person(name)
    
    def show_selected(self, names):
        self.clear()
        for name in names:
            self._add_person(name)
    
    def show_first_n(self, n):
        self.clear()
        names = self._get_db().get_all_person_names()[:n]
        for name in names:
            self._add_person(name)
    
    def _get_db(self):
        folder = self.ui.selected_folder_path.text()
        return FaceDB(f"{folder}/db.db")
    
    def _add_person(self, name):
        file_name, bbox = self._get_db().get_person_hauptbild_data(name)
        if not file_name or not bbox:
            return
        path = f"{self.ui.selected_folder_path.text()}/{file_name}"
        pix = QPixmap(path)
        x1, y1, x2, y2 = bbox
        cropped = pix.copy(x1, y1, x2-x1, y2-y1)
        scaled = cropped.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        item = QListWidgetItem(QIcon(scaled), name)
        self.widget.addItem(item)
        QApplication.processEvents()
        