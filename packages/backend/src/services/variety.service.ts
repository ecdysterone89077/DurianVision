import { db } from '../db/index.js';
import { durianVarieties } from '../db/schema/index.js';
import { eq, desc } from 'drizzle-orm';

export const getVarieties = async () => {
  return await db.select().from(durianVarieties).orderBy(durianVarieties.sortOrder);
};

export const getVariety = async (id: string) => {
  const [variety] = await db.select().from(durianVarieties).where(eq(durianVarieties.id, Number(id)));
  return variety;
};

export const createVariety = async (data: any) => {
  const [variety] = await db.insert(durianVarieties).values(data).returning();
  return variety;
};

export const updateVariety = async (id: string, data: any) => {
  const [variety] = await db.update(durianVarieties).set({ ...data }).where(eq(durianVarieties.id, Number(id))).returning();
  return variety;
};

export const deleteVariety = async (id: string) => {
  const [variety] = await db.delete(durianVarieties).where(eq(durianVarieties.id, Number(id))).returning();
  return variety;
};
