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
    { name: 'D24', colorHex: '#14B8A6', sortOrder: 2 },
    { name: 'Duri Hitam', colorHex: '#111827', sortOrder: 3 },
    { name: 'Lokal', colorHex: '#A16207', sortOrder: 4 },
    { name: 'Merah', colorHex: '#DC2626', sortOrder: 5 },
    { name: 'Montong', colorHex: '#3B82F6', sortOrder: 6 },
    { name: 'Musang King', colorHex: '#EAB308', sortOrder: 7 },
    { name: 'Pelangi', colorHex: '#8B5CF6', sortOrder: 8 },
    { name: 'Sane', colorHex: '#0EA5E9', sortOrder: 9 },
    { name: 'Sunan', colorHex: '#F97316', sortOrder: 10 },
    { name: 'Super Tembaga', colorHex: '#B45309', sortOrder: 11 },
    { name: 'Lainnya', colorHex: '#94A3B8', sortOrder: 12 },
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
