import { db } from '../db/index.js';
import { userSettings } from '../db/schema/index.js';
import { eq } from 'drizzle-orm';

export const getSettings = async () => {
  const settings = await db.select().from(userSettings);
  if (settings.length === 0) {
    const [newSettings] = await db.insert(userSettings).values({}).returning();
    return newSettings;
  }
  return settings[0];
};

export const updateSettings = async (data: any) => {
  const current = await getSettings();
  const [settings] = await db.update(userSettings).set({ ...data, updatedAt: new Date() }).where(eq(userSettings.id, current.id)).returning();
  return settings;
};

export const resetSettings = async () => {
  const current = await getSettings();
  await db.delete(userSettings).where(eq(userSettings.id, current.id));
  const [newSettings] = await db.insert(userSettings).values({}).returning();
  return newSettings;
};
