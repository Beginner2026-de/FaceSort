from PySide6.QtWidgets import QApplication, QProgressBar

class ProgressBar:
    def __init__(self, ui, max: int, list_widget: QProgressBar):
        self.ui = ui
        self.widget = list_widget
        self.max = max
        self.wert = 0  # Start bei 0
        self.init_bar()
    
    def init_bar(self):
        self.widget.setMaximum(self.max)
        self.widget.setMinimum(0)
        self.widget.setValue(0)
        self.widget.setVisible(True)
        self.widget.setFormat("%p% - %v von %m")
    
    def update(self):
        self.wert += 1
        self.widget.setValue(self.wert)
    
    def fertig(self, abschluss_text: str = ""):
        self.widget.setFormat(f"Fertig! %v {abschluss_text}")
        QApplication.processEvents()