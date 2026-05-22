import sys
import os

def resource_path(relative_path):
    """ Ermittelt den Pfad zur UI-Datei, passend für Entwicklung und Nuitka-Standalone """
    if hasattr(sys, "_MEIPASS"): # Falls du mal PyInstaller testen solltest
        base_path = sys._MEIPASS
    else:
        # Bei Nuitka zeigt das Verzeichnis von sys.argv[0] im Standalone-Modus 
        # immer direkt in den .dist-Ordner, wo auch dein 'QT-Ui'-Ordner landen wird.
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        
    return os.path.join(base_path, relative_path)