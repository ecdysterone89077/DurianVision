import { db } from '../db/index.js';
import { snapshots } from '../db/schema/index.js';
import { eq, desc } from 'drizzle-orm';
import fs from 'fs';

export const saveSnapshot = async (file: Express.Multer.File, sessionId?: string, detections?: any, metadata?: any) => {
  const [snapshot] = await db.insert(snapshots).values({
    sessionId,
    filename: file.filename,
    filepath: file.path,
    url: `/uploads/snapshots/${file.filename}`,
    numDetections: Array.isArray(detections) ? detections.length : 0,
    detections: detections || {},
    metadata: metadata || {},
  }).returning();
  return snapshot;
};

export const getSnapshots = async (limit = 20, offset = 0) => {
  return await db.select().from(snapshots).orderBy(desc(snapshots.createdAt)).limit(limit).offset(offset);
};

export const getSnapshot = async (id: string) => {
  const [snapshot] = await db.select().from(snapshots).where(eq(snapshots.id, id));
  return snapshot;
};

export const deleteSnapshot = async (id: string) => {
  const [snapshot] = await db.select().from(snapshots).where(eq(snapshots.id, id));
  if (snapshot && fs.existsSync(snapshot.filepath)) {
    fs.unlinkSync(snapshot.filepath);
  }
  await db.delete(snapshots).where(eq(snapshots.id, id));
  return snapshot;
};
