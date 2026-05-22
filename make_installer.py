import os
import sys
import platform
import subprocess

def build_linux_appimage(base_dir, dist_dir):
    print("\n--- Baue Linux AppImage ---")
    appdir = os.path.join(base_dir, "dist", "Photo-Face-sort.AppDir")
    os.makedirs(appdir, exist_ok=True)
    
    # 1. Erstelle die .desktop Datei (Der Starter für Linux)
    desktop_content = """[Desktop Entry]
Name=Photo Face Sort
Exec=Start-Ui.bin
Icon=photo_icon
Type=Application
Categories=Utility;
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
    os.symlink("Start-Ui.bin", apprun_path)

    # 4. Kopiere den Inhalt aus deinem Nuitka-Ordner ins AppDir
    print("Bereite AppDir-Struktur vor...")
    src_dist = os.path.join(dist_dir, "Start-Ui.dist")
    if not os.path.exists(src_dist):
        print(f"❌ Fehler: Nuitka-Ordner nicht gefunden unter: {src_dist}\nBitte zuerst build.py ausführen!")
        return

    # Inhalt synchronisieren/kopieren
    subprocess.run(f"cp -r {src_dist}/* {appdir}/", shell=True, check=True)

    # 5. AppImage kompilieren
    print("Generiere finale .AppImage Datei...")
    try:
        # Setzt voraus, dass 'appimagetool' auf deinem Linux installiert ist
        subprocess.run(["appimagetool", appdir, os.path.join(base_dir, "dist", "Photo-Face-sort-x86_64.AppImage")], check=True)
        print("🎉 Erfolg! Dein Linux AppImage liegt in dist/Photo-Face-sort-x86_64.AppImage")
    except FileNotFoundError:
        print("❌ Fehler: 'appimagetool' wurde auf deinem Linux-System nicht gefunden.")
        print("Bitte installiere es (z.B. per 'sudo apt install appimagetool' oder lade es von GitHub).")

def build_windows_setup(base_dir, dist_dir):
    print("\n--- Baue Windows Inno Setup ---")
    src_dist = os.path.join(dist_dir, "Start-Ui.dist")
    
    if not os.path.exists(src_dist):
        print(f"❌ Fehler: Nuitka-Ordner nicht gefunden unter: {src_dist}\nBitte zuerst build.py ausführen!")
        return

    # Erstelle das Inno Setup Skript (.iss) dynamisch
    iss_content = f"""
[Setup]
AppName=Photo Face Sort
AppVersion=1.0.0
DefaultDirName={{autopf}}\\PhotoFaceSort
DefaultGroupName=Photo Face Sort
OutputDir={base_dir}\\dist
OutputBaseFilename=Photo-Face-sort-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "{src_dist}\\*"; DestDir: "{{app}}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\Photo Face Sort"; Filename: "{{app}}\\Start-Ui.exe"
Name: "{{autodesktop}}\\Photo Face Sort"; Filename: "{{app}}\\Start-Ui.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{{{{"Create a &desktop icon"; GroupDescription: "{{{{"Additional icons:"

[Run]
Filename: "{{app}}\\Start-Ui.exe"; Description: "Launch Photo Face Sort"; Flags: nowait postinstall skipifsilent
"""
    
    iss_path = os.path.join(base_dir, "dist", "installer_config.iss")
    with open(iss_path, "w", encoding="utf-8") as f:
        f.write(iss_content)

    print("Rufe Inno Setup Compiler (ISCC) auf...")
    # Standard-Installationspfad von Inno Setup unter Windows
    inno_compiler = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    
    if not os.path.exists(inno_compiler):
        print(f"❌ Fehler: Inno Setup Compiler nicht gefunden unter {inno_compiler}")
        print("Bitte installiere Inno Setup 6 auf deinem Windows-PC, um den Installer zu bauen.")
        return

    try:
        subprocess.run([inno_compiler, iss_path], check=True)
        print("🎉 Erfolg! Deine Windows-Installationdatei liegt in dist/Photo-Face-sort-Setup.exe")
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Inno Setup-Bau: {e}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    current_os = platform.system().lower()
    dist_dir = os.path.join(base_dir, "dist", current_os)

    if current_os == "linux":
        build_linux_appimage(base_dir, dist_dir)
    elif current_os == "windows":
        build_windows_setup(base_dir, dist_dir)
    else:
        print(f"Das Betriebssystem {platform.system()} wird von diesem Skript nicht unterstützt.")

if __name__ == "__main__":
    main()