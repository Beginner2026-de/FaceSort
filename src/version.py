import os
from src.custom_logging import APP_LOGGER_NAME, logging
import requests

logger = logging.getLogger(APP_LOGGER_NAME)

def get_version_from_env(default="v0.0.0"):
    """Read VERSION from project.env located at repository root.

    Returns the version string (e.g. 'v1.0.0') or `default` if not found.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, "project.env")
    if not os.path.exists(env_path):
        return default

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip().upper() == "VERSION":
                        return v.strip()
    except Exception:
        return default

    return default

def get_version_from_webseite(INSTERLIERTE_VERSION = get_version_from_env()) -> str:
    try:
        Version_nachricht = ""
        url = "https://codeberg.org/api/v1/repos/beginner2026/FaceSort/releases/latest"
        
        try:
            data = requests.get(url).json()
        except Exception as e:
            logger.error("Fehler in der webseiten verbindung")
            return "Fehler in der webseiten verbindung"

        logger.info(f"Aktuelle Version: {INSTERLIERTE_VERSION}")
        latest_version = data["tag_name"]
        logger.info(f"Neueste Version: {latest_version}")

        if latest_version > INSTERLIERTE_VERSION:
            logger.info("Update verfügbar!")
            Version_nachricht = f"Update verfügbar! Aktuelle Version: {INSTERLIERTE_VERSION}, Neueste Version: {latest_version}"
            download_url = data["html_url"]
            logger.info(f"Download-Link: {download_url}")
            return Version_nachricht
        else:
            logger.info("Du hast die neueste Version.")
            Version_nachricht = f"Du hast die neueste Version: {INSTERLIERTE_VERSION}"
            return Version_nachricht
    except Exception as e:
        logger.error("Fehler beim Abrufen der Version:", e)
        return "Fehler beim herausfinden der APP Version "
