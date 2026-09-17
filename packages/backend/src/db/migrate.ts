import { migrate } from 'drizzle-orm/libsql/migrator';
import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';
import { env } from '../env.js';

async function main() {
  console.log('Running migrations...');
  const client = createClient({
    url: env.DATABASE_URL.startsWith('file:') || env.DATABASE_URL.startsWith('libsql:') 
      ? env.DATABASE_URL 
      : `file:${env.DATABASE_URL}`
  });
  const db = drizzle(client);
  
  await migrate(db, { migrationsFolder: './drizzle' });
  console.log('Migrations completed successfully.');
  
  process.exit(0);
}

main().catch((err) => {
  console.error('Migration error:', err);
  process.exit(1);
});
