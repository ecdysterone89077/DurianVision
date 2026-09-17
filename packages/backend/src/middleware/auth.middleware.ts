import { Request, Response, NextFunction } from 'express';
import { auth } from '../auth/index.js';
import { error } from '../utils/api-response.js';
import { fromNodeHeaders } from 'better-auth/node';

export const requireAuth = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const session = await auth.api.getSession({ headers: fromNodeHeaders(req.headers) });
    if (!session || !session.user) {
      return res.status(401).json(error('Unauthorized', 401));
    }
    (req as any).user = session.user;
    next();
  } catch (e: any) {
    if (e.message?.includes('headers')) {
      return res.status(401).json(error('Unauthorized', 401));
    }
    next(e);
  }
};

export const optionalAuth = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const session = await auth.api.getSession({ headers: fromNodeHeaders(req.headers) });
    if (session && session.user) {
      (req as any).user = session.user;
    }
    next();
  } catch (e) {
    next();
  }
};
