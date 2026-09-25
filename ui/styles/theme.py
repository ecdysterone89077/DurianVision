"""
Theme constants for the DurianVision application.
"""

from typing import ClassVar

class Theme:
    # Warna untuk varietas durian (UI-facing)
    VARIETY_COLORS: ClassVar[dict[str, str]] = {
        'Bawor': '#22C55E',
        'D24': '#14B8A6',
        'Duri Hitam': '#111827',
        'Lokal': '#A16207',
        'Merah': '#DC2626',
        'Montong': '#3B82F6',
        'Musang King': '#EAB308',
        'Pelangi': '#8B5CF6',
        'Sane': '#0EA5E9',
        'Sunan': '#F97316',
        'Super Tembaga': '#B45309',
        'Lainnya': '#94A3B8',
    }

    # Dark theme colors
    BG_PRIMARY = '#1a1a2e'
    BG_SECONDARY = '#16213e'
    BG_CARD = '#0f3460'
    ACCENT = '#22C55E'
    TEXT_PRIMARY = '#e4e4e7'
    TEXT_SECONDARY = '#a1a1aa'
    BORDER = '#374151'
    
    # UI Constants
    FONT_SIZE_SMALL = 10
    FONT_SIZE_NORMAL = 12
    FONT_SIZE_LARGE = 14
    FONT_SIZE_HEADER = 18
    
    SPACING_SMALL = 4
    SPACING_NORMAL = 8
    SPACING_LARGE = 16
    
    # Device Constants
    DEVICE_SMARTPHONE = 'smartphone'
    DEVICE_DESKTOP = 'desktop'
    DEVICE_UNKNOWN = 'unknown'
    
    # Common smartphone aspect ratios (width, height)
    SMARTPHONE_RATIOS: ClassVar[list[tuple[int, int]]] = [(9, 16), (9, 19.5), (9, 20), (9, 21)]

    # Mapping from YOLO model class names to UI variety names
    MODEL_CLASS_MAP: ClassVar[dict[str, str]] = {
        'bawor': 'Bawor',
        'd24': 'D24',
        'duri hitam': 'Duri Hitam',
        'lokal': 'Lokal',
        'merah': 'Merah',
        'montong': 'Montong',
        'musang king': 'Musang King',
        'pelangi': 'Pelangi',
        'sane': 'Sane',
        'sunan': 'Sunan',
        'super tembaga': 'Super Tembaga',
    }

    @classmethod
    def get_variety_color(cls, name: str) -> str:
        """Get hex color for a variety name (case-insensitive, with model alias support)."""
        # Direct lookup
        if name in cls.VARIETY_COLORS:
            return cls.VARIETY_COLORS[name]
        # Try model class name mapping
        mapped = cls.MODEL_CLASS_MAP.get(name.lower())
        if mapped and mapped in cls.VARIETY_COLORS:
            return cls.VARIETY_COLORS[mapped]
        # Case-insensitive fallback
        name_lower = name.lower()
        for key, color in cls.VARIETY_COLORS.items():
            if key.lower() == name_lower:
                return color
        return cls.VARIETY_COLORS.get('Lainnya', '#94A3B8')
