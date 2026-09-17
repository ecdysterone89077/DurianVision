import { sqliteTable, text, integer, real, index } from 'drizzle-orm/sqlite-core';
import { sql } from 'drizzle-orm';
import { aiModels } from './models.js';

export const detectionSessions = sqliteTable('detection_sessions', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  aiModelId: text('ai_model_id').references(() => aiModels.id, { onDelete: 'cascade' }),
  status: text('status').notNull().default('idle'),
  roiX: integer('roi_x'),
  roiY: integer('roi_y'),
  roiWidth: integer('roi_width'),
  roiHeight: integer('roi_height'),
  deviceType: text('device_type'),
  aspectRatio: text('aspect_ratio'),
  confidenceThreshold: real('confidence_threshold').notNull().default(0.5),
  fpsLimit: integer('fps_limit').notNull().default(10),
  inferenceSize: integer('inference_size').notNull().default(640),
  config: text('config', { mode: 'json' }),
  startedAt: integer('started_at', { mode: 'timestamp_ms' }),
  endedAt: integer('ended_at', { mode: 'timestamp_ms' }),
  createdAt: integer('created_at', { mode: 'timestamp_ms' }).notNull().$defaultFn(() => new Date()),
  updatedAt: integer('updated_at', { mode: 'timestamp_ms' }).notNull().$defaultFn(() => new Date()),
}, (table) => ({
  aiModelIdx: index('detection_sessions_ai_model_idx').on(table.aiModelId),
}));
