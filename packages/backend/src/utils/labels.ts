export const MODEL_CLASS_MAP: Record<string, string> = {
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
};

export const toDisplayName = (name: string): string =>
  MODEL_CLASS_MAP[String(name || '').toLowerCase()] ?? name;

export const mapDetection = <T extends { class_name?: string }>(det: T): T => ({
  ...det,
  class_name: toDisplayName(det.class_name ?? ''),
});

export const mapDetections = (detections: any[] = []): any[] => detections.map(mapDetection);
