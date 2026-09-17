import { Request, Response, NextFunction } from 'express';
import { error } from '../utils/api-response.js';
import { logger } from '../utils/logger.js';

export const errorHandler = (err: any, req: Request, res: Response, next: NextFunction) => {
  if (res.headersSent) { return next(err); }
  logger.error(err);
  const statusCode = err.status || 500;
  const message = err.message || 'Internal Server Error';
  res.status(statusCode).json(error(message, statusCode));
};
