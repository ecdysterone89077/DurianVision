import { sqliteTable, text, integer, real, index } from 'drizzle-orm/sqlite-core';
import { sql } from 'drizzle-orm';
import { detectionSessions } from './detection-sessions.js';

export const snapshots = sqliteTable('snapshots', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  sessionId: text('session_id').references(() => detectionSessions.id, { onDelete: 'cascade' }),
  filename: text('filename').notNull(),
  filepath: text('filepath').notNull(),
  url: text('url').notNull(),
  numDetections: integer('num_detections').notNull().default(0),
  detections: text('detections', { mode: 'json' }),
  metadata: text('metadata', { mode: 'json' }),
  createdAt: integer('created_at', { mode: 'timestamp_ms' }).notNull().$defaultFn(() => new Date()),
}, (table) => ({
  sessionIdx: index('snapshots_session_idx').on(table.sessionId),
}));
