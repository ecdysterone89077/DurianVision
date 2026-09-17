import { sqliteTable, text, integer, real } from 'drizzle-orm/sqlite-core';
import { sql } from 'drizzle-orm';

export const userSettings = sqliteTable('user_settings', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  confidenceThreshold: real('confidence_threshold').notNull().default(0.5),
  iouThreshold: real('iou_threshold').notNull().default(0.45),
  fpsLimit: integer('fps_limit').notNull().default(10),
  inferenceSize: integer('inference_size').notNull().default(640),
  device: text('device').notNull().default('auto'),
  showLabels: integer('show_labels', { mode: 'boolean' }).notNull().default(true),
  showConfidence: integer('show_confidence', { mode: 'boolean' }).notNull().default(true),
  boxThickness: integer('box_thickness').notNull().default(2),
  fontSize: integer('font_size').notNull().default(14),
  overlayOpacity: real('overlay_opacity').notNull().default(0.7),
  autoSnapshot: integer('auto_snapshot', { mode: 'boolean' }).notNull().default(false),
  autoSnapshotInterval: integer('auto_snapshot_interval').notNull().default(30),
  hotkeySnapshot: text('hotkey_snapshot').notNull().default('space'),
  hotkeyToggle: text('hotkey_toggle').notNull().default('f5'),
  theme: text('theme').notNull().default('dark'),
  language: text('language').notNull().default('id'),
  updatedAt: integer('updated_at', { mode: 'timestamp_ms' }).notNull().$defaultFn(() => new Date()),
});
