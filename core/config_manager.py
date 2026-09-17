"""
Configuration manager for DurianVision.
Singleton that loads, saves, and broadcasts configuration changes.
"""
import json
import os
import threading
from typing import Any, Optional

from PyQt6.QtCore import QObject, pyqtSignal


class ConfigManager(QObject):
    """Singleton configuration manager with real-time change broadcasting."""
    
    config_changed = pyqtSignal(str, object)  # (section.key, new_value)
    
    _instance: Optional['ConfigManager'] = None
    
    def __init__(self, config_path: str = 'config/default_config.json') -> None:
        super().__init__()
        self._config_path = config_path
        self._config: dict = {}
        self._lock = threading.Lock()  # Phase 3.3: Prevent Race Conditions
        self.load()
    
    @classmethod
    def get_instance(cls, config_path: str = 'config/default_config.json') -> 'ConfigManager':
        """Get or create the singleton instance (PyQt6-safe)."""
        if cls._instance is None:
            cls._instance = cls(config_path)
        return cls._instance
    
    def load(self) -> None:
        """Load configuration from JSON file."""
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    new_config = json.load(f)
                    with self._lock:
                        self._config = new_config
            except Exception as e:
                print(f"[ConfigManager] Gagal memuat config: {e}")
                with self._lock:
                    self._config = {}
        else:
            with self._lock:
                self._config = {}
    
    def save(self) -> bool:
        """Save current configuration to JSON file."""
        try:
            dirname = os.path.dirname(self._config_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with self._lock:
                config_copy = self._config.copy()
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(config_copy, f, indent=2, ensure_ascii=False)
            return True
        except PermissionError:
            print(f"[ConfigManager] PermissionError: Gagal menyimpan config ke {self._config_path}")
            try:
                from PyQt6.QtWidgets import QMessageBox
                if QMessageBox:
                    QMessageBox.warning(None, "Error Akses Konfigurasi", 
                        f"Tidak memiliki izin untuk menyimpan pengaturan di:\n{self._config_path}\n\n"
                        "Harap jalankan aplikasi sebagai Administrator atau hubungi tim IT.")
            except:
                pass
            return False
        except Exception as e:
            print(f"[ConfigManager] Gagal menyimpan config: {e}")
            return False
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a config value. Example: get('detection', 'confidence_threshold', 0.5)"""
        with self._lock:
            return self._config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any, save_now: bool = False) -> None:
        """Set a config value and broadcast the change."""
        with self._lock:
            if section not in self._config:
                self._config[section] = {}
            self._config[section][key] = value
        
        self.config_changed.emit(f"{section}.{key}", value)
        if save_now:
            self.save()
    
    def get_section(self, section: str) -> dict:
        """Get an entire config section."""
        with self._lock:
            return self._config.get(section, {}).copy()
    
    def get_variety_colors(self) -> dict[str, str]:
        """Get the variety color mapping."""
        return self._config.get('varieties', {})
    
    @property
    def config(self) -> dict:
        """Get full config dict (read-only copy)."""
        return self._config.copy()
