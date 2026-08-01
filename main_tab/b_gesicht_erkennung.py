import cv2
from pathlib import Path
from insightface.app import FaceAnalysis
from src.g_db_settings_handler import SettingsHandler
from src.custom_logging import APP_LOGGER_NAME
import logging
from PySide6.QtCore import Qt  
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QApplication
import shutil
from src.DBManager import FaceDB
from src.progressbar_clas import ProgressBar
import time

logger = logging.getLogger(APP_LOGGER_NAME)

def starte_gesicht_erkennung_alle(ui):
    logger.info("=== Starte Gesichtserkennung für alle Bilder ===")
    clear_images(ui)
    folder_path = ui.selected_folder_path.text()
    logger.debug(f"Ordner-Pfad: {folder_path}")
    db_path = str(Path(folder_path) / "db.db")
    logger.debug(f"Datenbank-Pfad: {db_path}")

    try:
        bilder_db = FaceDB(db_path=db_path)
        logger.info(f"Bilder-Datenbank erfolgreich geladen")
    except Exception as e:
        logger.error(f"Fehler beim Laden der Bilder-Datenbank: {e}", exc_info=True)
        return
    
    try:
        settings_db = SettingsHandler(db_path=db_path)
        logger.info(f"Einstellungen-Datenbank erfolgreich geladen")
    except Exception as e:
        logger.error(f"Fehler beim Laden der Einstellungen-Datenbank: {e}", exc_info=True)
        return
    
    alle_bilder_ojekte = bilder_db.get_all_images()
    logger.info(f"Gesamt Bilder zu verarbeiten: {len(alle_bilder_ojekte)}")

    bar = ProgressBar(ui=ui,max=len(alle_bilder_ojekte),list_widget=ui.scan_progressBar)
    logger.debug("Fortschrittsleiste initialisiert")

    for i, bilder in enumerate(alle_bilder_ojekte):
        clear_images(ui)
        if ui.stope_scan == True:
            ui.stope_scan = False
            ui.nachrichten.info(f"Gesicht Erkennung gestopt")
            logger.info("Gesicht Erkennung gestopt")

            return
        logger.debug(f"[{i+1}/{len(alle_bilder_ojekte)}] Verarbeite Bild: {bilder['image_path']}")
        
    # 1. ORIGINALBILD path
        faces_by_image = bilder_db.get_faces_by_image(bilder["image_path"])
        if faces_by_image:
            logger.debug(f"Bild bereits verarbeitet - {len(faces_by_image)} Gesichter gefunden. Überspringe.")
            bar.update()
            continue

        if bilder_db.is_image_scanned(bilder["image_id"]):
            logger.debug("Bild bereits gescannt, aber keine Gesichter gefunden. Überspringe.")
            bar.update()
            continue
        
        bild_path = bilder["image_path"]
        voller_pfad = str(Path(folder_path) / bild_path)
        logger.debug(f"Voller Pfad: {voller_pfad}")

        try:
            pixmap = QPixmap(voller_pfad)
            if pixmap.isNull():
                logger.warning(f"Pixmap ist null für: {voller_pfad}")
            else:
                logger.debug(f"Pixmap erfolgreich geladen - Größe: {pixmap.width()}x{pixmap.height()}")
            scalier_und_anzeigen_in_objekt(element=ui.label,pixmap=pixmap)
        except Exception as e:
            logger.error(f"Fehler beim Laden des Pixmaps: {e}", exc_info=True)
            bar.update()
            continue

        # 2. Modell laden für Gesichtserkennung
        try:
            ui.nachrichten.info(f"Lade Modell für Gesichtserkennung und scanne Bild: {bild_path}")
            logger.debug("Lade FaceAnalysis Modell...")
            app = FaceAnalysis(name='antelopev2')
            logger.debug("FaceAnalysis Modell geladen")
            
            if settings_db.mode == "CPU":
                mode = -1
                logger.debug("Verwende CPU-Modus")
            elif settings_db.mode == "GPU":
                mode = 0
                logger.debug("Verwende GPU-Modus")
            else:
                logger.error(f"Unplausible Einstellung für Modus in DB: {settings_db.mode}")
                return

            logger.debug(f"Bereite Modell mit ctx_id={mode} vor...")
            app.prepare(ctx_id=mode)
            logger.debug("Modell erfolgreich vorbereitet")
        except Exception as e:
            logger.error(f"Fehler beim Laden/Vorbereiten des Modells: {e}", exc_info=True)

            try:
                _fix_insightface_model_folder(name='antelopev2')
                logger.info("Versuche Modell erneut zu laden nach Fix des Modellordners")
                app = FaceAnalysis(name='antelopev2')
                app.prepare(ctx_id=mode)
                logger.debug("Modell nach Ordnerfix erfolgreich vorbereitet")
            except Exception as e2:
                logger.error(f"Erneuter Versuch nach Modellordner-Fix fehlgeschlagen: {e2}", exc_info=True)
                bar.update()
                continue

        # 3. Bild mit OpenCV laden und Gesichter erkennen
        try:
            logger.debug(f"Lade Bild mit OpenCV: {voller_pfad}")
            img = cv2.imread(voller_pfad)
            if img is None:
                logger.error(f"OpenCV konnte Bild nicht laden: {voller_pfad}")
                bar.update()
                continue
            logger.debug(f"Bild erfolgreich geladen - Größe: {img.shape}")
            
            logger.debug("Führe Gesichtserkennung durch...")
            faces = app.get(img)
            logger.info(f"Gesichtserkennung abgeschlossen - {len(faces)} Gesichter erkannt")
        except Exception as e:
            logger.error(f"Fehler bei Gesichtserkennung: {e}", exc_info=True)
            bar.update()
            continue

        # 4. Rechtecke auf das Bild zeichnen
        try:
            logger.debug("Verarbeite erkannte Gesichter...")
            faces_list = []
            for idx, face in enumerate(faces):
                bbox_int = list(map(int, face.bbox))
                faces_list.append({
                    'embedding': face.embedding,  # numpy array
                    'bbox': bbox_int,  # [x1,y1,x2,y2]
                    'age': None,  # optional
                    'gender': None  # optional
                })
                logger.debug(f"Gesicht {idx+1}: BBox={bbox_int}, Embedding-Form={face.embedding.shape}")
                
                x1, y1, x2, y2 = bbox_int
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 8)
            
            logger.debug(f"Speichere {len(faces_list)} Gesichter in Datenbank...")
            face_ids = bilder_db.add_faces(bilder, faces_list)
            logger.info(f"Gesichter erfolgreich gespeichert - IDs: {face_ids}")
        except Exception as e:
            logger.error(f"Fehler beim Verarbeiten/Speichern der Gesichter: {e}", exc_info=True)
            bar.update()
            continue

        # Konvertiere OpenCV-Bild (BGR) zu QPixmap
        try:
            logger.debug("Konvertiere OpenCV-Bild zu QPixmap...")
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = img_rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            modifizierte_pixmap = QPixmap.fromImage(qt_image)
            logger.debug(f"Konvertierung erfolgreich - Größe: {modifizierte_pixmap.width()}x{modifizierte_pixmap.height()}")
            scalier_und_anzeigen_in_objekt(element=ui.label_2,pixmap=modifizierte_pixmap)
        except Exception as e:
            logger.error(f"Fehler beim Konvertieren des Bildes: {e}", exc_info=True)
            bar.update()
            continue

        logger.info(f"Bild verarbeitet: {voller_pfad} - erkannte Gesichter IDs: {face_ids}")
        time.sleep(0.2)  # Kurze Pause, damit UI-Updates sichtbar sind
        bar.update()
    
    logger.info("=== Gesichtserkennung abgeschlossen ===" )
    bar.fertig()

def scalier_und_anzeigen_in_objekt(element,pixmap):
    element.setScaledContents(False)
    label_size = element.size()
    scaled_pixmap = pixmap.scaled(
        label_size.width(), 
        label_size.height(),
        Qt.AspectRatioMode.KeepAspectRatio,  # Behält Seitenverhältnis
        Qt.TransformationMode.SmoothTransformation  # Sanfte Skalierung
    )
    element.setPixmap(scaled_pixmap)
    element.setAlignment(Qt.AlignmentFlag.AlignCenter)
    QApplication.processEvents()  # Qt aktualisieren

def clear_images(ui):
    ui.label.clear()
    ui.label_2.clear()


def _fix_insightface_model_folder(name: str):
    logger = logging.getLogger(APP_LOGGER_NAME)
    home_dir = Path.home()
    logger.debug(f"Überprüfe insightface-Modellordner für '{name}' im Verzeichnis: {home_dir}")
    model_dir = home_dir / ".insightface" / "models" /name
    logger.debug(f"Erwarteter Modellordner: {model_dir}")
    nested_dir = model_dir / name
    logger.debug(f"Überprüfe auf verschachteltes Verzeichnis: {nested_dir}")

    if not nested_dir.is_dir():
        return

    logger.warning(
        f"Gefundenes verschachteltes insightface-Modellverzeichnis: {nested_dir}. "
        "Verschiebe Inhalte eine Ebene nach oben..."
    )

    for child in nested_dir.iterdir():
        target = model_dir / child.name
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        shutil.move(str(child), str(target))

    try:
        nested_dir.rmdir()
        logger.info(f"Verschachteltes Modellverzeichnis {nested_dir} entfernt.")
    except OSError:
        logger.debug(f"Konnte verschachteltes Verzeichnis {nested_dir} nicht entfernen; eventuell nicht leer.")
