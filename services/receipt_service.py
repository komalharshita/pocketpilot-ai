from pathlib import Path
import shutil

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"

# Ensure folder exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_receipt(file):
    """
    Save uploaded receipt file to disk.
    Returns saved file path.
    """
    if file is None:
        return None

    destination = UPLOAD_DIR / Path(file.name).name
    shutil.copy(file.name, destination)

    return str(destination)
