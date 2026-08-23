import os
import sys
import platform
import subprocess
import shutil
import multiprocessing
from src.custom_logging import setup_logger, APP_LOGGER_NAME , logging
from src.version import get_version_from_env
from pathlib import Path

RUNWITH_NOFOLLOW = False   # Setze auf False, um alle Module zu bauen (ohne nofollow)

logger = setup_logger(APP_LOGGER_NAME, level=logging.DEBUG)

def load_nofollow():
    try:
        path_for_os = "make-reports/windows" if os.name == "nt" else "make-reports/linux"
        with open(Path(f"{path_for_os}/nofollow_suggestions.txt")) as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []
    
def run_build():
    # 1. Betriebssystem automatisch erkennen
    current_os = platform.system().lower()
    logger.info(f"Starte Build-Prozess für: {platform.system()} ---")

    # 2. Pfade definieren
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(base_dir, "FaceSort.py") 
    version = get_version_from_env()
    output_dir = os.path.join(base_dir, "dist", current_os, version)
    ui_dir_source = os.path.join(base_dir, "QT-Ui")
    cache_dir = os.path.join(base_dir, ".nuitka-cache")
    os.makedirs(cache_dir, exist_ok=True)

    # 3. Nuitka-Befehl vorbereiten (JETZT WIEDER MIT STANDALONE)
    nuitka_cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",            
        #"--enable-plugin=pyside6",
        f"--output-dir={output_dir}",
        #f"--include-data-dir={ui_dir_source}=QT-Ui", # Kopiert den UI-Ordner in das Paket
        #f"--include-data-file=project.env=project.env",
        #f"--include-package=cv2",
        #f"--include-package=insightface",
        #f"--include-package-data=insightface",
        #f"--include-package=skimage",
        #f"--include-package-data=skimage",
        f"--assume-yes-for-downloads",
        main_script
    ]

    # 4. Betriebssystem-spezifische Optionen
    #if current_os == "windows":
    #    nuitka_cmd.append("--windows-console-mode=disable")
    #    nuitka_cmd.append("--include-windows-runtime-dlls=auto")
    #    nuitka_cmd.append(f"--jobs={multiprocessing.cpu_count()}")
    #    nuitka_cmd.append("--noinclude-pytest-mode=nofollow")
    #    nuitka_cmd.append("--noinclude-setuptools-mode=nofollow")
    #    nuitka_cmd.append("--nofollow-import-to=tkinter")
    #    nuitka_cmd.append("--nofollow-import-to=unittest")
    #    nuitka_cmd.append("--nofollow-import-to=test")
    #    nuitka_cmd.append("--noinclude-default-mode=error")
    #
    #elif current_os == "linux":
    #    nuitka_cmd.append(f"--jobs={multiprocessing.cpu_count()}")
        
    
    if RUNWITH_NOFOLLOW:
        nofollow = load_nofollow()
        nuitka_cmd += nofollow
    else:
        path_for_os = "make-reports/windows" if os.name == "nt" else "make-reports/linux"
        report_output = Path(f"{path_for_os}/report_all_imports.xml")
        nuitka_cmd.append(f"--report={report_output}")


    # 5. Build ausführen (mit Cache-Umgebungsvariablen und ccache-Erkennung)
    logger.info(f"Ausgabe wird gespeichert in: {output_dir}")
    logger.info("Führe Nuitka aus... (inklusive UI-Dateien)")

    # Umgebung für Nuitka-Caches vorbereiten
    env = os.environ.copy()
    env['NUITKA_CACHE_DIR'] = cache_dir
    env['NUITKA_CACHE_DIR_CCACHE'] = os.path.join(cache_dir, 'ccache')
    env['NUITKA_CACHE_DIR_DOWNLOADS'] = os.path.join(cache_dir, 'downloads')
    env['NUITKA_CACHE_DIR_BYTECODE'] = os.path.join(cache_dir, 'bytecode')
    env['NUITKA_CACHE_DIR_DLL_DEPENDENCIES'] = os.path.join(cache_dir, 'dll-dependencies')

    for d in (env['NUITKA_CACHE_DIR_CCACHE'], env['NUITKA_CACHE_DIR_DOWNLOADS'], env['NUITKA_CACHE_DIR_BYTECODE'], env['NUITKA_CACHE_DIR_DLL_DEPENDENCIES']):
        os.makedirs(d, exist_ok=True)

    logger.debug(f"NUITKA_CACHE_DIR gesetzt auf: {env['NUITKA_CACHE_DIR']}")


    # Setze NUITKA_CACHE_DIR_*-Variablen zusätzlich über die environment
    # Nuitka pickt diese auf und verwendet sie für downloads, ccache, bytecode, dlls.


    try:
        subprocess.run(nuitka_cmd, check=True, env=env)
        logger.info(f"\n🎉 Erfolg! Deine App für {platform.system()} wurde inkl. UI gebaut.")
    except subprocess.CalledProcessError as e:
        logger.error(f"\n❌ Fehler beim Bauen: {e}", exc_info=True)



def build_linux_appimage(base_dir, dist_dir):
    logger.info("Baue Linux AppImage")
    appdir = os.path.join(base_dir, "dist", "Photo-Face-sort.AppDir")
    os.makedirs(appdir, exist_ok=True)
    
    # 1. Erstelle die .desktop Datei (Der Starter für Linux)
    desktop_content = """[Desktop Entry]
Name=FaceSort
Exec=FaceSort.bin
Icon=photo_icon
Type=Application
Categories=Utility;Graphics;
Terminal=false
"""
    with open(os.path.join(appdir, "Photo-Face-sort.desktop"), "w") as f:
        f.write(desktop_content)
        
    # 2. Erstelle ein Dummy-Icon (oder kopiere dein echtes hinein)
    # Nuitka braucht ein Icon im AppDir-Stammverzeichnis
    icon_path = os.path.join(appdir, "photo_icon.png")
    if not os.path.exists(icon_path):
        with open(icon_path, "w") as f: f.write("") 

    # 3. Erstelle den AppRun-Symlink auf deine Nuitka .bin
    apprun_path = os.path.join(appdir, "AppRun")
    if os.path.exists(apprun_path): os.remove(apprun_path)
    os.symlink("FaceSort.bin", apprun_path)

    # 4. Kopiere den Inhalt aus deinem Nuitka-Ordner ins AppDir
    logger.info("Bereite AppDir-Struktur vor...")
    src_dist = os.path.join(dist_dir, "FaceSort.dist")
    if not os.path.exists(src_dist):
        logger.error(f"Nuitka-Ordner nicht gefunden: {src_dist} - bitte zuerst build.py ausführen")
        return

    # Inhalt synchronisieren/kopieren
    subprocess.run(f"cp -r {src_dist}/* {appdir}/", shell=True, check=True)

    # 5. AppImage kompilieren
    logger.info("Generiere finale .AppImage Datei")
    try:
        # Setzt voraus, dass 'appimagetool' auf deinem Linux installiert ist
        out_appimage = os.path.join(base_dir, "dist", f"FaceSort-{get_version_from_env()}-x86_64.AppImage")
        subprocess.run(["appimagetool", appdir, out_appimage], check=True)
        logger.info(f"Erfolg: Linux AppImage erstellt: {out_appimage}")
    except FileNotFoundError:
        logger.error("'appimagetool' nicht gefunden auf dem System")
        logger.info("Bitte installiere 'appimagetool' (z.B. 'sudo apt install appimagetool')")

def build_windows_setup(base_dir, dist_dir):
    logger.info("Baue Windows Inno Setup")
    src_dist = os.path.join(dist_dir, "FaceSort.dist")
    
    if not os.path.exists(src_dist):
        logger.error(f"Nuitka-Ordner nicht gefunden: {src_dist} - bitte zuerst build.py ausführen")
        return

    # Erstelle das Inno Setup Skript (.iss) dynamisch
    version =   get_version_from_env()

    iss_content = f"""
[Setup]
PrivilegesRequired=admin
AppName=FaceSort
AppVersion={version}
DefaultDirName={{autopf}}\\FaceSort
DefaultGroupName=FaceSort
OutputDir={base_dir}\\dist
OutputBaseFilename=FaceSort-Setup-{version}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "{src_dist}\\*"; DestDir: "{{app}}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\FaceSort"; Filename: "{{app}}\\FaceSort.exe"
Name: "{{autodesktop}}\\FaceSort"; Filename: "{{app}}\\FaceSort.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Run]
Filename: "{{app}}\\FaceSort.exe"; Description: "Launch FaceSort"; Flags: nowait postinstall skipifsilent
"""
    
    iss_path = os.path.join(base_dir, "dist", "installer_config.iss")
    with open(iss_path, "w", encoding="utf-8") as f:
        f.write(iss_content)

    logger.info("Rufe Inno Setup Compiler (ISCC) auf")
    # Standard-Installationspfad von Inno Setup unter Windows
    inno_compiler = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    
    if not os.path.exists(inno_compiler):
        logger.error(f"Inno Setup Compiler nicht gefunden: {inno_compiler}")
        logger.info("Bitte installiere Inno Setup 6 auf deinem Windows-PC, um den Installer zu bauen.")
        return

    try:
        subprocess.run([inno_compiler, iss_path], check=True)
        logger.info(f"Erfolg: Windows-Installer erstellt: dist/FaceSort-Setup-{version}.exe")
    except subprocess.CalledProcessError as e:
        logger.exception(f"Fehler beim Inno Setup-Bau: {e}")

def start_make_instaler():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    current_os = platform.system().lower()
    version =   get_version_from_env()
    dist_dir = os.path.join(base_dir, "dist", current_os, version)

    if current_os == "linux":
        build_linux_appimage(base_dir, dist_dir)
    elif current_os == "windows":
        build_windows_setup(base_dir, dist_dir)
    else:
        logger.error(f"Betriebssystem {platform.system()} wird von diesem Skript nicht unterstützt.")

if __name__ == "__main__":
    run_build()
    start_make_instaler()