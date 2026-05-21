import cv2
from insightface.app import FaceAnalysis
from src.g_db_settings_handler import SettingsHandler
from src.custom_logging import setup_logger
from PySide6.QtCore import Qt  
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QApplication
import cv2
from src.DBManager import FaceDB
from src.progressbar_clas import ProgressBar

loger = setup_logger(__name__)

def starte_gesicht_erkennung_alle(ui):
    clear_images(ui)
    folder_path = ui.selected_folder_path.text()
    db_path = f"{folder_path}/db.db"

    bilder_db = FaceDB(db_path=db_path)
    settings_db = SettingsHandler(db_path=db_path)
    alle_bilder_ojekte = bilder_db.get_all_images()

    bar = ProgressBar(ui=ui,max=len(alle_bilder_ojekte),list_widget=ui.scan_progressBar)

    for i, bilder in enumerate(alle_bilder_ojekte):
    # 1. ORIGINALBILD path
        faces_by_image = bilder_db.get_faces_by_image(bilder.file_name)
        if faces_by_image:
            bar.update()
            continue
        bild_path = bilder.file_name
        voller_pfad = f"{folder_path}/{bild_path}"
        

        pixmap = QPixmap(voller_pfad)
        scalier_und_anzeigen_in_objekt(element=ui.label,pixmap=pixmap)


        # 2. Modell laden für Gesichtserkennung
        app = FaceAnalysis(name='antelopev2')
        if settings_db.mode == "CPU":
            mode = -1
        elif settings_db.mode == "GPU":  # elif statt if
            mode = 0
        else:
            loger.error(f"unplausible einstellung CPU oder GPU modus aus DB: {settings_db.mode}")
            return
        
        app.prepare(ctx_id=mode)

        # 3. Bild mit OpenCV laden und Gesichter erkennen
        img = cv2.imread(voller_pfad)
        faces = app.get(img)

        # 4. Rechtecke auf das Bild zeichnen
        faces_list = []
        for face in faces:
            faces_list.append({
                'embedding': face.embedding,  # numpy array
                'bbox': list(map(int, face.bbox)),  # [x1,y1,x2,y2]
                'age': None,  # optional
                'gender': None  # optional
            })
            
            x1, y1, x2, y2 = map(int, face.bbox)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 8)
        face_ids = bilder_db.add_faces(bilder, faces_list)

        # Konvertiere OpenCV-Bild (BGR) zu QPixmap
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        modifizierte_pixmap = QPixmap.fromImage(qt_image)
        scalier_und_anzeigen_in_objekt(element=ui.label_2,pixmap=modifizierte_pixmap)

        loger.info(f"Bild mit {face_ids} Gesichtern erkannt")
        i + 1
        
        bar.update()
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