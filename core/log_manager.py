"""
Log manager for DurianVision.
Handles storing, exporting, and managing detection logs.
"""

import csv
import os
from collections import deque

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class LogManager:
    """Manages detection log entries and exports."""
    
    MAX_ENTRIES = 50000  # Memory cap
    
    def __init__(self, save_dir: str = 'logs') -> None:
        """Initialize the log manager."""
        self.save_dir = save_dir
        
        try:
            os.makedirs(self.save_dir, exist_ok=True)
        except PermissionError:
            from PyQt6.QtWidgets import QMessageBox
            if QMessageBox:
                QMessageBox.critical(None, "Error Akses", 
                    f"Tidak memiliki izin untuk membuat folder log di:\n{self.save_dir}\n\n"
                    "Harap jalankan aplikasi sebagai Administrator atau ubah lokasi penyimpanan.")
            
            # Fallback ke direktori sementara yang dijamin aman
            self.save_dir = os.path.join(os.path.expanduser('~'), 'DurianVision_Logs_Fallback')
            os.makedirs(self.save_dir, exist_ok=True)
            
        self._entries: deque = deque(maxlen=self.MAX_ENTRIES)

    def add_entry(self, timestamp: str, variety: str, confidence: float, count: int) -> None:
        """Append a new detection entry."""
        self._entries.append({
            'timestamp': timestamp,
            'variety': variety,
            'confidence': confidence,
            'count': count
        })

    def get_entries(self) -> list[dict]:
        """Return a copy of the log entries."""
        return list(self._entries)

    def export_csv(self, filepath: str) -> bool:
        """Write log entries to a CSV file."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['timestamp', 'variety', 'confidence', 'count'])
                writer.writeheader()
                writer.writerows(self._entries)
            return True
        except Exception as e:
            print(f"[LogManager] Gagal ekspor CSV: {e}")
            return False

    def export_xlsx(self, filepath: str) -> bool:
        """Write log entries to an Excel (XLSX) file."""
        if not OPENPYXL_AVAILABLE:
            print("[LogManager] openpyxl tidak tersedia untuk ekspor XLSX")
            return False
            
        try:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            wb = openpyxl.Workbook()
            ws = wb.active
            if ws:
                ws.title = "Detection Logs"
                
                headers = ['timestamp', 'variety', 'confidence', 'count']
                ws.append(headers)
                
                for entry in self._entries:
                    ws.append([entry.get(h) for h in headers])
                    
                wb.save(filepath)
            return True
        except Exception as e:
            print(f"[LogManager] Gagal ekspor XLSX: {e}")
            return False

    def clear(self) -> None:
        """Clear all entries in memory."""
        self._entries.clear()

    @property
    def entry_count(self) -> int:
        """Return the number of entries currently logged."""
        return len(self._entries)
