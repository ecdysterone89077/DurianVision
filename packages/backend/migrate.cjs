const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const schemaDir = path.join(process.cwd(), 'src/db/schema');
const files = fs.readdirSync(schemaDir).filter(f => f.endsWith('.ts'));

for (const file of files) {
  const filePath = path.join(schemaDir, file);
  let content = fs.readFileSync(filePath, 'utf8');

  content = content.replace(/import \{[^}]+\} from 'drizzle-orm\/pg-core';/, ""import { sqliteTable, text, integer, real } from 'drizzle-orm/sqlite-core';"");
  content = content.replace(/pgTable/g, 'sqliteTable');
  content = content.replace(/uuid\('id'\)\.primaryKey\(\)\.defaultRandom\(\)/g, ""text('id').primaryKey().$defaultFn(() => crypto.randomUUID())"");
  content = content.replace(/uuid\(/g, 'text(');
  content = content.replace(/jsonb\('([^']+)'\)/g, ""text('$1', { mode: 'json' })"");
  content = content.replace(/boolean\('([^']+)'\)/g, ""integer('$1', { mode: 'boolean' })"");
  content = content.replace(/timestamp\('([^']+)'\)/g, ""integer('$1', { mode: 'timestamp_ms' })"");
  content = content.replace(/serial\('([^']+)'\)/g, ""integer('$1', { mode: 'number' }).primaryKey({ autoIncrement: true })"");
  content = content.replace(/bigint\('([^']+)'\)/g, ""integer('$1', { mode: 'number' })"");
  
  content = content.replace(/\.primaryKey\(\{ autoIncrement: true \}\)\.primaryKey\(\)/g, '.primaryKey({ autoIncrement: true })');
  content = content.replace(/\.default\(sql\
ow\(\)\\)/g, '.$defaultFn(() => new Date())');

  fs.writeFileSync(filePath, content);
}
console.log('Schema migrated to SQLite');
