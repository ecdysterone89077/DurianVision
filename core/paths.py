import os
import sys
from pathlib import Path

def get_app_dir() -> Path:
    """Mengembalikan lokasi instalasi (.exe) untuk membaca file model/aset."""
    if getattr(sys, 'frozen', False):
        # Jika dijalankan sebagai .exe
        return Path(sys.executable).parent
    else:
        # Jika dijalankan sebagai script .py
        return Path(__file__).parent.parent

def get_meipass_dir() -> Path:
    """Mengembalikan direktori virtual (sys._MEIPASS) saat dijalankan via PyInstaller."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent.parent

def get_user_data_dir() -> str:
    """Mengembalikan path %APPDATA% untuk menyimpan file config & logs."""
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    data_dir = Path(appdata) / "DurianVision"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir)

def get_user_media_dir() -> str:
    """Mengembalikan path Documents untuk menyimpan hasil Snapshots."""
    docs = Path(os.path.expanduser('~')) / "Documents" / "DurianVision_Snapshots"
    docs.mkdir(parents=True, exist_ok=True)
    return str(docs)
