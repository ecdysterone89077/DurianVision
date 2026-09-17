"""
Global hotkeys module for DurianVision.
Listens for keyboard shortcuts even when the app is in the background/system tray.
"""
import os
import sys

from PyQt6.QtCore import QObject, pyqtSignal

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


def _typing_context() -> bool:
    """True jika window aktif saat ini sedang menampilkan kursor teks (user mengetik).

    Heuristik: GetGUIThreadInfo.hwndCaret != 0. Cukup untuk mencegah hotkey
    tombol polos (mis. Space) mencuri ketikan di aplikasi lain.
    """
    if sys.platform != 'win32':
        return False
    try:
        import ctypes
        from ctypes import wintypes

        class GUITHREADINFO(ctypes.Structure):
            _fields_ = [
                ('cbSize', wintypes.DWORD),
                ('flags', wintypes.DWORD),
                ('hwndActive', wintypes.HWND),
                ('hwndFocus', wintypes.HWND),
                ('hwndCapture', wintypes.HWND),
                ('hwndMenuOwner', wintypes.HWND),
                ('hwndMoveSize', wintypes.HWND),
                ('hwndCaret', wintypes.HWND),
                ('rcCaret', wintypes.RECT),
            ]

        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        pid = wintypes.DWORD()
        tid = user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == os.getpid():
            return False
        info = GUITHREADINFO()
        info.cbSize = ctypes.sizeof(GUITHREADINFO)
        if user32.GetGUIThreadInfo(tid, ctypes.byref(info)):
            return bool(info.hwndCaret)
    except Exception:
        pass
    return False


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

        hotkey_map = {hk: self._guard_bare_key(hk, cb) for hk, cb in hotkey_map.items()}
        
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
    
    @staticmethod
    def _is_bare_key(hotkey: str) -> bool:
        """True jika hotkey hanya satu tombol tanpa modifier (mis. <space>)."""
        return '+' not in hotkey

    def _guard_bare_key(self, hotkey: str, callback):
        """Bungkus hotkey polos agar tidak trigger saat user sedang mengetik."""
        if not self._is_bare_key(hotkey):
            return callback

        def guarded() -> None:
            if _typing_context():
                return
            callback()

        return guarded

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


if __name__ == '__main__':
    assert GlobalHotkeys._convert_hotkey_format('Space') == '<space>'
    assert GlobalHotkeys._convert_hotkey_format('Ctrl+Shift+D') == '<ctrl>+<shift>+d'
    assert GlobalHotkeys._convert_hotkey_format('<ctrl>+<shift>+h') == '<ctrl>+<shift>+h'
    assert GlobalHotkeys._is_bare_key('<space>') is True
    assert GlobalHotkeys._is_bare_key('<ctrl>+<shift>+d') is False
    assert isinstance(_typing_context(), bool)
    assert GlobalHotkeys({'snapshot': 'Space'})._guard_bare_key('<space>', lambda: None) is not None
    print('GlobalHotkeys self-check OK')
