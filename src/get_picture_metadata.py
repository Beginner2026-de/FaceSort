from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def extract_clean_metadata(image_path):
    result = {
        "datetime_original": None,
        "datetime_digitized": None,
        "datetime_modified": None,
        "latitude": 0,
        "longitude": 0
    }
    
    try:
        with Image.open(image_path) as img:
            exifdata = img.getexif()
            if not exifdata:
                return result  # Keine Exif-Daten vorhanden
            
            # 1. Datumsfelder auslesen (Sicheres Fallback über IFD 34665)
            result["datetime_modified"] = exifdata.get(306)
            
            exif_ifd = exifdata.get_ifd(34665)
            if exif_ifd:
                result["datetime_original"] = exif_ifd.get(36867)
                result["datetime_digitized"] = exif_ifd.get(36868)
            
            # 2. GPS-Daten robust auslesen
            gps_info = exifdata.get_ifd(34853)
            if gps_info:
                gps_decoded = {}
                for tag_id, value in gps_info.items():
                    tag_name = GPSTAGS.get(tag_id, tag_id)
                    gps_decoded[tag_name] = value
                
                # Prüfen, ob die kritischen GPS-Tags überhaupt existieren
                required_tags = ['GPSLatitude', 'GPSLatitudeRef', 'GPSLongitude', 'GPSLongitudeRef']
                if all(tag in gps_decoded for tag in required_tags):
                    
                    # Hilfsfunktion zur sicheren Konvertierung von (Grad, Minuten, Sekunden)
                    def convert_to_degrees(coords, ref):
                        try:
                            # Robustes Auflösen, falls Werte Brüche (Rational) sind
                            d = float(coords[0])
                            m = float(coords[1])
                            s = float(coords[2])
                            
                            decimal = d + (m / 60.0) + (s / 3600.0)
                            if ref in ['S', 'W']:
                                decimal = -decimal
                            return decimal
                        except (IndexError, TypeError, ZeroDivisionError):
                            return None

                    lat = convert_to_degrees(gps_decoded['GPSLatitude'], gps_decoded['GPSLatitudeRef'])
                    lon = convert_to_degrees(gps_decoded['GPSLongitude'], gps_decoded['GPSLongitudeRef'])
                    
                    if lat is not None and lon is not None:
                        result["latitude"] = lat
                        result["longitude"] = lon
                        
    except Exception as e:
        print(f"Fehler beim Verarbeiten von {image_path}: {e}")
        
    return result