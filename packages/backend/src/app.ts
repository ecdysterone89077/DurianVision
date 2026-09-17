import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import path from 'path';
import routes from './routes/index.js';
import { errorHandler } from './middleware/error.middleware.js';

export const app = express();

app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
  credentials: true
}));

app.use(helmet({
  crossOriginResourcePolicy: false // Allows serving local images
}));

import { expressAuthHandler } from './auth/index.js';

// Mount Better Auth before express.json() so it can read the raw request stream
app.all('/api/auth/*', expressAuthHandler);

app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Serve uploads statically
app.use('/uploads', express.static(path.join(process.cwd(), 'uploads')));

// API routes
app.use('/api', routes);

// Error handling
app.use(errorHandler);
