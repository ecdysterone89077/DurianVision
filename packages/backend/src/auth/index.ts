import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { db } from '../db/index.js';
import * as schema from '../db/schema/index.js';

export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "sqlite",
    schema: {
      user: schema.users,
      session: schema.sessions,
      account: schema.accounts,
      verification: schema.verifications
    }
  }),
  emailAndPassword: {
    enabled: true,
  },
  trustedOrigins: [process.env.CORS_ORIGIN || "http://localhost:5173"],
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3005",
});

import { toNodeHandler } from 'better-auth/node';

export const expressAuthHandler = toNodeHandler(auth);
