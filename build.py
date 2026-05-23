import os
import sys
import platform
import subprocess

def run_build():
    # 1. Betriebssystem automatisch erkennen
    current_os = platform.system().lower()
    print(f"--- Starte Build-Prozess für: {platform.system()} ---")

    # 2. Pfade definieren
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(base_dir, "Start-Ui.py") 
    output_dir = os.path.join(base_dir, "dist", current_os)
    ui_dir_source = os.path.join(base_dir, "QT-Ui")

    # 3. Nuitka-Befehl vorbereiten (JETZT WIEDER MIT STANDALONE)
    nuitka_cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",                              # <-- ABSOLUT NOTWENDIG FÜR QT-APPS
        "--enable-plugin=pyside6",
        f"--output-dir={output_dir}",
        f"--include-data-dir={ui_dir_source}=QT-Ui", # Kopiert den UI-Ordner in das Paket
        "--remove-output",                           # Löscht temporären C++ Müll nach Erfolg
        main_script
    ]

    # 4. Betriebssystem-spezifische Optionen
    if current_os == "windows":
        nuitka_cmd.append("--windows-console-mode=disable")
        
    elif current_os == "linux":
        pass

    # 5. Build ausführen
    print(f"Ausgabe wird gespeichert in: {output_dir}")
    print("Führe Nuitka aus... (inklusive UI-Dateien)")
    
    try:
        subprocess.run(nuitka_cmd, check=True)
        print(f"\n🎉 Erfolg! Deine App für {platform.system()} wurde inkl. UI gebaut.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Fehler beim Bauen: {e}", file=sys.stderr)

if __name__ == "__main__":
    run_build()