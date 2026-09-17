import { sqliteTable, text, integer, real } from 'drizzle-orm/sqlite-core';
import { sql } from 'drizzle-orm';

export const aiModels = sqliteTable('ai_models', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  name: text('name').notNull(),
  filename: text('filename').notNull(),
  filepath: text('filepath').notNull(),
  framework: text('framework').notNull().default('yolov11'),
  version: text('version'),
  classNames: text('class_names', { mode: 'json' }).notNull(),
  isActive: integer('is_active', { mode: 'boolean' }).notNull().default(false),
  fileSize: integer('file_size', { mode: 'number' }),
  createdAt: integer('created_at', { mode: 'timestamp_ms' }).notNull().$defaultFn(() => new Date()),
  updatedAt: integer('updated_at', { mode: 'timestamp_ms' }).notNull().$defaultFn(() => new Date()),
});
