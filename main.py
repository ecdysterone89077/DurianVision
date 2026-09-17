import sys
import os
import argparse
import traceback
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter
from PyQt6.QtCore import Qt

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Menangkap SEMUA crash yang tidak tertangani agar tidak muncul pop-up jelek bawaan PyInstaller."""
    # 1. Rekam ke file log di tempat yang aman (AppData)
    log_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'DurianVision', 'crash_logs')
    os.makedirs(log_dir, exist_ok=True)
    crash_file = os.path.join(log_dir, f"CRASH_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    with open(crash_file, "w") as f:
        f.write("=== DURIANVISION CRASH REPORT ===\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
    
    # 2. Tampilkan pesan error yang profesional ke pengguna
    error_msg = f"Terjadi kesalahan sistem yang tidak terduga.\n\nDetail telah disimpan di:\n{crash_file}\n\nHarap kirimkan file ini ke tim pengembang."
    
    # Pastikan QApplication ada untuk memunculkan QMessageBox
    if QApplication.instance():
        QMessageBox.critical(None, "DurianVision - Fatal Error", error_msg)
    else:
        # Fallback jika crash terjadi sebelum UI sempat dimuat
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, error_msg, "DurianVision - Fatal Error", 0x10)
        except:
            pass
    
    sys.exit(1)

# Pasang pengaman ini sebelum aplikasi melakukan hal lain
sys.excepthook = global_exception_handler

from ui.app import DurianVisionApp

def create_default_icon():
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor('#22C55E'))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(0, 0, 32, 32)
    painter.end()
    return QIcon(pixmap)

def parse_args():
    parser = argparse.ArgumentParser(description='DurianVision - Durian Detection System')
    parser.add_argument('--autostart', action='store_true', help='Auto-start fullscreen detection')
    parser.add_argument('--minimize', action='store_true', help='Start minimized to tray')
    return parser.parse_args()

def main():
    # Phase 1.1: Windows DPI Awareness for precise bounding boxes
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception as e:
        print(f"[Main] Gagal set DPI Awareness: {e}")

    # Initialize AppData directories for writable data (Fixes WinError 5 PermissionError)
    from core.paths import get_user_data_dir
    appdata_dir = get_user_data_dir()
    os.makedirs(os.path.join(appdata_dir, 'snapshots'), exist_ok=True)
    os.makedirs(os.path.join(appdata_dir, 'logs'), exist_ok=True)
    
    config_dir = os.path.join(appdata_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)
    
    # Copy default config if it doesn't exist in AppData
    appdata_config = os.path.join(config_dir, 'default_config.json')
    if not os.path.exists(appdata_config):
        # When frozen, files are in sys._MEIPASS or current directory
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        bundled_config = os.path.join(base_dir, 'config', 'default_config.json')
        if os.path.exists(bundled_config):
            import shutil
            shutil.copy2(bundled_config, appdata_config)

    args = parse_args()
    app = QApplication(sys.argv)
    
    # Single Instance Lock using QSharedMemory
    from PyQt6.QtCore import QSharedMemory
    shared_memory = QSharedMemory("DurianVision_Single_Instance_Lock")
    if not shared_memory.create(1):
        QMessageBox.warning(None, "DurianVision", "Aplikasi sudah berjalan di latar belakang!")
        sys.exit(0)
        
    app.setApplicationName('DurianVision')
    
    # Load stylesheet if exists (use absolute path)
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    stylesheet_path = os.path.join(base_dir, 'ui', 'styles', 'stylesheet.qss')
    if os.path.exists(stylesheet_path):
        try:
            with open(stylesheet_path, 'r', encoding='utf-8') as f:
                app.setStyleSheet(f.read())
        except IOError:
            pass
            
    # Set default app icon
    app.setWindowIcon(create_default_icon())
    
    # Create main app logic component
    durian_app = DurianVisionApp(app, autostart=args.autostart, minimize=args.minimize)
    
    app.aboutToQuit.connect(durian_app.quit_app)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
