"""
Device detection module for determining optimal inference settings based on screen resolution.
"""
from typing import Any


class DeviceDetector:
    """Detects device type from screen dimensions and returns optimal settings."""
    
    @staticmethod
    def detect_device(width: int, height: int, mode: str = 'auto') -> dict[str, Any]:
        """
        Detects the device type based on screen dimensions and returns
        recommended settings including styling parameters.
        """
        if mode != 'auto':
            if mode == 'smartphone':
                return DeviceDetector._build_result('smartphone', f'{width}:{height}', 5, 416, 0.65, 1, 10, False, width, height)
            elif mode == 'desktop':
                return DeviceDetector._build_result('desktop', f'{width}:{height}', 10, 640, 1.0, 2, 14, True, width, height)
                

        if width <= 0 or height <= 0:
            return DeviceDetector._build_result(
                'unknown', 'unknown', 5, 416, 1.0, 1, 10, False
            )
            
        ratio = max(width, height) / min(width, height)
        
        # Square (~1:1) - likely smartphone crop or custom window
        if ratio < 1.2:
            return DeviceDetector._build_result(
                'smartphone', f'{width}:{height}',
                5, 416, 0.65, 1, 10, False, width, height
            )
        
        # Portrait orientation - likely smartphone
        if height > width:
            if 1.5 <= ratio <= 2.5:
                # Calculate display ratio (e.g. 9:16, 9:19.5, 9:20)
                short_side = 9
                long_side = round(ratio * short_side, 1)
                return DeviceDetector._build_result(
                    'smartphone', f'{short_side}:{long_side}',
                    5, 416, 0.65, 1, 10, False, width, height
                )
        
        # Landscape orientation - likely desktop/monitor
        elif width > height:
            if 1.5 <= ratio <= 1.8:
                # Standard desktop ratios: 16:9, 16:10
                aspect_h = round(16 / ratio)
                return DeviceDetector._build_result(
                    'desktop', f'16:{aspect_h}',
                    10, 640, 1.0, 2, 14, True, width, height
                )
            elif 1.8 < ratio <= 2.5:
                # Ultra-wide desktop
                return DeviceDetector._build_result(
                    'desktop', f'21:{round(21 / ratio)}',
                    10, 640, 1.0, 2, 14, True, width, height
                )
                
        # Default fallback
        return DeviceDetector._build_result(
            'unknown', f'{width}:{height}',
            5, 416, 1.0, 2, 12, True, width, height
        )
    
    @staticmethod
    def _build_result(device_type: str, aspect_ratio: str,
                      recommended_fps: int, recommended_inference_size: int,
                      scale_factor: float, line_thickness: int,
                      font_size: int, show_mini_status: bool,
                      width: int = 0, height: int = 0) -> dict[str, Any]:
        """Build a standardized result dictionary."""
        return {
            'type': device_type,
            'aspect_ratio': aspect_ratio,
            'resolution': f'{width}x{height}' if width > 0 and height > 0 else '-',
            'recommended_fps': recommended_fps,
            'recommended_inference_size': recommended_inference_size,
            'scale_factor': scale_factor,
            'line_thickness': line_thickness,
            'font_size': font_size,
            'show_mini_status': show_mini_status,
        }
