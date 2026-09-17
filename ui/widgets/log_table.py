"""
Log table widget for DurianVision.
Displays detection log entries in a table format.
"""
from PyQt6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class LogTable(QWidget):
    """Table widget displaying detection log entries."""
    
    COLUMNS = ['Waktu', 'Varietas', 'Akurasi', 'Jumlah']
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        
        self.lbl_total = QLabel("Total Catatan: 0")
        
        layout.addWidget(self.table)
        layout.addWidget(self.lbl_total)
    
    def add_entry(self, timestamp: str, variety: str, 
                  confidence: str, count: str) -> None:
        """Add a new log entry row."""
        self.table.setSortingEnabled(False)
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.table.setItem(row, 1, QTableWidgetItem(variety))
        self.table.setItem(row, 2, QTableWidgetItem(confidence))
        self.table.setItem(row, 3, QTableWidgetItem(count))
        self.lbl_total.setText(f"Total Catatan: {self.table.rowCount()}")
        self.table.setSortingEnabled(True)
        
        MAX_LOG_ROWS = 1000
        if self.table.rowCount() > MAX_LOG_ROWS:
            self.table.removeRow(0)
            
        self.lbl_total.setText(f"Total Catatan: {self.table.rowCount()}")
        
        # Auto-scroll to latest entry
        self.table.scrollToBottom()
    
    def clear_entries(self) -> None:
        """Remove all log entries."""
        self.table.setRowCount(0)
        self.lbl_total.setText("Total Catatan: 0")
    
    def get_row_count(self) -> int:
        """Get number of rows."""
        return self.table.rowCount()
