"""
Global hotkeys module for DurianVision.
Listens for keyboard shortcuts even when the app is in the background/system tray.
"""
from PyQt6.QtCore import QObject, pyqtSignal

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class GlobalHotkeys(QObject):
    """Global keyboard shortcut listener."""
    
    snapshot_triggered = pyqtSignal()
    toggle_detection_triggered = pyqtSignal()
    select_roi_triggered = pyqtSignal()
    hide_triggered = pyqtSignal()
    
    def __init__(self, hotkey_config: dict | None = None) -> None:
        super().__init__()
        self._listener = None
        self._hotkey_config = hotkey_config or {
            'snapshot': '<space>',
            'toggle_detection': '<ctrl>+<shift>+d',
            'select_roi': '<ctrl>+<shift>+r',
            'hide': '<ctrl>+<shift>+h'
        }
        self._is_running = False
    
    @staticmethod
    def _convert_hotkey_format(qt_hotkey: str) -> str:
        """Convert Qt-style hotkey string to pynput format.
        e.g. 'Ctrl+Shift+D' -> '<ctrl>+<shift>+d'
             'Space' -> '<space>'
        """
        # Already in pynput format
        if '<' in qt_hotkey:
            return qt_hotkey
        
        parts = qt_hotkey.split('+')
        converted = []
        for part in parts:
            p = part.strip().lower()
            if p in ('ctrl', 'shift', 'alt', 'cmd', 'space', 'tab', 'enter', 'esc',
                     'backspace', 'delete', 'home', 'end', 'pageup', 'pagedown',
                     'up', 'down', 'left', 'right', 'f1', 'f2', 'f3', 'f4', 'f5',
                     'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'):
                converted.append(f'<{p}>')
            else:
                converted.append(p)
        return '+'.join(converted)

    def start(self) -> None:
        """Start listening for global hotkeys."""
        if not PYNPUT_AVAILABLE:
            print("[GlobalHotkeys] pynput tidak tersedia, hotkey global dinonaktifkan")
            return
        if self._is_running:
            return
            
        hotkey_map = {}
        snapshot_hk = self._convert_hotkey_format(self._hotkey_config.get('snapshot', '<space>'))
        if snapshot_hk:
            hotkey_map[snapshot_hk] = self._on_snapshot
            
        toggle_hk = self._convert_hotkey_format(self._hotkey_config.get('toggle_detection', '<ctrl>+<shift>+d'))
        if toggle_hk:
            hotkey_map[toggle_hk] = self._on_toggle_detection
            
        roi_hk = self._convert_hotkey_format(self._hotkey_config.get('select_roi', '<ctrl>+<shift>+r'))
        if roi_hk:
            hotkey_map[roi_hk] = self._on_select_roi
            
        hide_hk = self._convert_hotkey_format(self._hotkey_config.get('hide', '<ctrl>+<shift>+h'))
        if hide_hk:
            hotkey_map[hide_hk] = self._on_hide
        
        try:
            self._listener = keyboard.GlobalHotKeys(hotkey_map)
            self._listener.daemon = True
            self._listener.start()
            self._is_running = True
        except Exception as e:
            print(f"[GlobalHotkeys] Gagal memulai listener: {e}")
    
    def stop(self) -> None:
        """Stop listening for global hotkeys."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
        self._is_running = False
    
    def update_hotkeys(self, hotkey_config: dict) -> None:
        """Update hotkey bindings (requires restart of listener)."""
        self._hotkey_config = hotkey_config
        if self._is_running:
            self.stop()
            self.start()
    
    def _on_snapshot(self) -> None:
        self.snapshot_triggered.emit()
    
    def _on_toggle_detection(self) -> None:
        self.toggle_detection_triggered.emit()
    
    def _on_select_roi(self) -> None:
        self.select_roi_triggered.emit()
    
    def _on_hide(self) -> None:
        self.hide_triggered.emit()
    
    @property
    def is_running(self) -> bool:
        return self._is_running
