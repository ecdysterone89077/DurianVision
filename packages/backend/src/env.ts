import { z } from 'zod';
import * as dotenv from 'dotenv';

dotenv.config();

const envSchema = z.object({
  DATABASE_URL: z.string(),
  PORT: z.string().transform(Number).default('3005'),
  BETTER_AUTH_SECRET: z.string(),
  BETTER_AUTH_URL: z.string().url().default('http://localhost:3005'),
  INFERENCE_URL: z.string().url().default('http://localhost:8001'),
  UPLOAD_DIR: z.string().default('./uploads'),
  CORS_ORIGIN: z.string().default('http://localhost:5173'),
});

export const env = envSchema.parse(process.env);
