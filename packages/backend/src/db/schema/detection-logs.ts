import { sqliteTable, text, integer, real, index } from 'drizzle-orm/sqlite-core';
import { sql } from 'drizzle-orm';
import { detectionSessions } from './detection-sessions.js';

export const detectionLogs = sqliteTable('detection_logs', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  sessionId: text('session_id').notNull().references(() => detectionSessions.id, { onDelete: 'cascade' }),
  variety: text('variety').notNull(),
  confidence: real('confidence').notNull(),
  bboxX: integer('bbox_x').notNull(),
  bboxY: integer('bbox_y').notNull(),
  bboxW: integer('bbox_w').notNull(),
  bboxH: integer('bbox_h').notNull(),
  inferenceTimeMs: real('inference_time_ms'),
  frameNumber: integer('frame_number'),
  detectedAt: integer('detected_at', { mode: 'timestamp_ms' }).notNull().$defaultFn(() => new Date()),
}, (table) => ({
  sessionIdx: index('detection_logs_session_idx').on(table.sessionId),
}));
