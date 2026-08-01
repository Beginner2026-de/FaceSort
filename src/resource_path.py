import sys
from pathlib import Path

def resource_path(relative_path):
    """ Ermittelt den Pfad zur UI-Datei, passend für Entwicklung und Nuitka-Standalone """
    if hasattr(sys, "_MEIPASS"): # Falls du mal PyInstaller testen solltest
        base_path = Path(sys._MEIPASS)
    else:
        # Bei Nuitka zeigt das Verzeichnis von sys.argv[0] im Standalone-Modus 
        # immer direkt in den .dist-Ordner, wo auch dein 'QT-Ui'-Ordner landen wird.
        base_path = Path(sys.argv[0]).resolve().parent
        
    return str(base_path / relative_path)