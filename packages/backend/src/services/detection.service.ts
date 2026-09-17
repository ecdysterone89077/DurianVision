import { db } from '../db/index.js';
import { detectionSessions, detectionLogs } from '../db/schema/index.js';
import { eq, desc } from 'drizzle-orm';

export const createSession = async (data: any) => {
  const [session] = await db.insert(detectionSessions).values(data).returning();
  return session;
};

export const getSessions = async () => {
  return await db.select().from(detectionSessions).orderBy(desc(detectionSessions.createdAt));
};

export const getSession = async (id: string) => {
  const [session] = await db.select().from(detectionSessions).where(eq(detectionSessions.id, id));
  return session;
};

export const updateSession = async (id: string, data: any) => {
  const [session] = await db.update(detectionSessions).set({ ...data, updatedAt: new Date() }).where(eq(detectionSessions.id, id)).returning();
  return session;
};

export const deleteSession = async (id: string) => {
  await db.delete(detectionLogs).where(eq(detectionLogs.sessionId, id));
  const [session] = await db.delete(detectionSessions).where(eq(detectionSessions.id, id)).returning();
  return session;
};

export const updateStatus = async (id: string, status: string) => {
  const [session] = await db.update(detectionSessions).set({ status, updatedAt: new Date() }).where(eq(detectionSessions.id, id)).returning();
  return session;
};
