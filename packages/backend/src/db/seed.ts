import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';
import { env } from '../env.js';
import { durianVarieties } from './schema/varieties.js';

async function main() {
  const client = createClient({
    url: env.DATABASE_URL.startsWith('file:') || env.DATABASE_URL.startsWith('libsql:') 
      ? env.DATABASE_URL 
      : `file:${env.DATABASE_URL}`
  });
  const db = drizzle(client);

  const varieties = [
    { name: 'Bawor', colorHex: '#22C55E', sortOrder: 1 },
    { name: 'Black Thorn', colorHex: '#10B981', sortOrder: 2 },
    { name: 'Montong', colorHex: '#3B82F6', sortOrder: 3 },
    { name: 'Musang King', colorHex: '#EAB308', sortOrder: 4 },
    { name: 'Petruk', colorHex: '#A855F7', sortOrder: 5 },
    { name: 'Monthong', colorHex: '#EC4899', sortOrder: 6 },
    { name: 'Sunan', colorHex: '#F97316', sortOrder: 7 },
    { name: 'Kani', colorHex: '#06B6D4', sortOrder: 8 },
    { name: 'Matahari', colorHex: '#EF4444', sortOrder: 9 },
    { name: 'Sitokong', colorHex: '#84CC16', sortOrder: 10 },
    { name: 'Lainnya', colorHex: '#94A3B8', sortOrder: 11 },
  ];

  console.log('Seeding durian varieties...');
  for (const variety of varieties) {
    await db.insert(durianVarieties)
      .values(variety)
      .onConflictDoNothing({ target: durianVarieties.name });
  }

  console.log('Seeding completed.');
  process.exit(0);
}

main().catch((err) => {
  console.error('Seed error:', err);
  process.exit(1);
});
