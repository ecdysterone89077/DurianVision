import { db } from '../db/index.js';
import { detectionLogs } from '../db/schema/index.js';
import { eq, and, gte, desc, sql, count, avg } from 'drizzle-orm';
import { exportCSV as exportCSVUtil, exportXLSX as exportXLSXUtil } from '../utils/export.js';

export const addLog = async (data: any) => {
  const [log] = await db.insert(detectionLogs).values(data).returning();
  return log;
};

export const addBatchLogs = async (logs: any[]) => {
  if (logs.length === 0) return [];
  return await db.insert(detectionLogs).values(logs).returning();
};

const buildConditions = (filters: { sessionId?: string; variety?: string; minConfidence?: number }) => {
  const conditions = [];
  if (filters.sessionId) conditions.push(eq(detectionLogs.sessionId, filters.sessionId));
  if (filters.variety) conditions.push(eq(detectionLogs.variety, filters.variety));
  if (filters.minConfidence !== undefined && filters.minConfidence !== null) {
    conditions.push(gte(detectionLogs.confidence, filters.minConfidence));
  }
  return conditions;
};

export const getLogs = async (filters: { sessionId?: string; variety?: string; minConfidence?: number; limit?: number; offset?: number }) => {
  let query = db.select().from(detectionLogs).$dynamic();
  const conditions = buildConditions(filters);

  if (conditions.length > 0) {
    query = query.where(and(...conditions));
  }

  query = query.orderBy(desc(detectionLogs.detectedAt));

  if (filters.limit) query = query.limit(filters.limit);
  if (filters.offset) query = query.offset(filters.offset);

  return await query;
};

export const countLogs = async (filters: { sessionId?: string; variety?: string; minConfidence?: number }) => {
  let query = db.select({ value: count() }).from(detectionLogs).$dynamic();
  const conditions = buildConditions(filters);
  if (conditions.length > 0) {
    query = query.where(and(...conditions));
  }
  const rows = await query;
  return Number(rows[0]?.value ?? 0);
};

export const getStats = async (sessionId?: string) => {
  let query = db.select({
    name: detectionLogs.variety,
    count: count(),
    avgConfidence: avg(detectionLogs.confidence)
  }).from(detectionLogs).$dynamic();

  if (sessionId) {
    query = query.where(eq(detectionLogs.sessionId, sessionId));
  }

  const byVariety = await query.groupBy(detectionLogs.variety);
  
  let totalCount = 0;
  let totalConfidence = 0;
  for (const v of byVariety) {
    totalCount += Number(v.count);
    totalConfidence += Number(v.avgConfidence) * Number(v.count);
  }

  return {
    total: totalCount,
    avgConfidence: totalCount > 0 ? totalConfidence / totalCount : 0,
    byVariety
  };
};

export const getDistribution = async (sessionId?: string) => {
  const stats = await getStats(sessionId);
  if (stats.total === 0) return [];
  return stats.byVariety.map((v) => ({
    name: v.name,
    percentage: (Number(v.count) / stats.total) * 100
  }));
};

export const exportCSV = async (filters: any) => {
  const logs = await getLogs(filters);
  const data = logs.map(l => ({ ...l }));
  return await exportCSVUtil(data, ['id', 'sessionId', 'variety', 'confidence', 'detectedAt']);
};

export const exportXLSX = async (filters: any) => {
  const logs = await getLogs(filters);
  const data = logs.map(l => ({ ...l }));
  return await exportXLSXUtil(data, ['id', 'sessionId', 'variety', 'confidence', 'detectedAt'], 'Logs');
};

export const clearLogs = async (sessionId?: string) => {
  if (sessionId) {
    await db.delete(detectionLogs).where(eq(detectionLogs.sessionId, sessionId));
  } else {
    await db.delete(detectionLogs);
  }
};
