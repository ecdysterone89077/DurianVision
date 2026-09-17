class DeviceDetector:
    @staticmethod
    def detect_device(width: int, height: int) -> dict:
        return {
            "width": width,
            "height": height,
            "aspect_ratio": width / height if height else 0,
            "orientation": "landscape" if width > height else "portrait"
        }
