import { db } from '../db/index.js';
import { aiModels } from '../db/schema/index.js';
import { eq } from 'drizzle-orm';
import { loadModel as loadInferenceModel } from './inference.service.js';
import { MODEL_CLASS_MAP } from '../utils/labels.js';
import fs from 'fs';

const MODEL_CLASS_NAMES = Object.values(MODEL_CLASS_MAP);

export const uploadModel = async (file: Express.Multer.File, name?: string) => {
  const [model] = await db.insert(aiModels).values({
    name: name || file.originalname,
    filepath: file.path,
    filename: file.originalname,
    fileSize: file.size,
    classNames: MODEL_CLASS_NAMES,
    isActive: false,
  }).returning();
  return model;
};

export const getModels = async () => {
  return await db.select().from(aiModels);
};

export const getModel = async (id: string) => {
  const [model] = await db.select().from(aiModels).where(eq(aiModels.id, id));
  return model;
};

export const activateModel = async (id: string) => {
  await db.update(aiModels).set({ isActive: false });
  const [model] = await db.update(aiModels).set({ isActive: true, updatedAt: new Date() }).where(eq(aiModels.id, id)).returning();
  
  try {
    await loadInferenceModel(model.filepath);
  } catch (error) {
    console.error('Failed to hot-reload model in inference service', error);
  }
  
  return model;
};

export const deleteModel = async (id: string) => {
  const [model] = await db.select().from(aiModels).where(eq(aiModels.id, id));
  if (model && fs.existsSync(model.filepath)) {
    fs.unlinkSync(model.filepath);
  }
  await db.delete(aiModels).where(eq(aiModels.id, id));
  return model;
};

export const getActiveModel = async () => {
  const [model] = await db.select().from(aiModels).where(eq(aiModels.isActive, true));
  return model;
};
