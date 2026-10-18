import re
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def tip_real(cale):
  try:
    cap = open(cale, "rb").read(8)
    if cap.startswith(b"%PDF"):
      return "pdf"
    elif cap.startswith(b"\x89PNG"):
      return "png"
    elif cap.startswith(b"\xff\xd8"):
      return "jpeg"
    elif cap.startswith(b"PK\x03\x04"):
      return "zip/docx"
    return cap.hex()
  except Exception:
    return "Fisier indisponibil"


print("Script de forensics pregatit cu succes!")
