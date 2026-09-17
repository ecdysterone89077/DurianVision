export const MODEL_CLASS_MAP: Record<string, string> = {
  'bawor': 'Bawor',
  'black thorn': 'Black Thorn',
  'kanyao': 'Kani',
  'monthong': 'Monthong',
  'musang king': 'Musang King',
  'not durian': 'Lainnya',
};

export const toDisplayName = (name: string): string =>
  MODEL_CLASS_MAP[String(name || '').toLowerCase()] ?? name;

export const mapDetection = <T extends { class_name?: string }>(det: T): T => ({
  ...det,
  class_name: toDisplayName(det.class_name ?? ''),
});

export const mapDetections = (detections: any[] = []): any[] => detections.map(mapDetection);
