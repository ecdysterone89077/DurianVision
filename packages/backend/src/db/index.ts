import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';
import * as schema from './schema/index.js';
import { env } from '../env.js';

const client = createClient({
  url: env.DATABASE_URL.startsWith('file:') || env.DATABASE_URL.startsWith('libsql:') 
    ? env.DATABASE_URL 
    : `file:${env.DATABASE_URL}`
});

export const db = drizzle(client, { schema });
