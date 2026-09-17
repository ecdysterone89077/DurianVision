import { Request, Response, NextFunction } from 'express';
import { AnyZodObject } from 'zod';
import { error } from '../utils/api-response.js';

export const validate = (schema: AnyZodObject) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });
      next();
    } catch (e: any) {
      return res.status(400).json(error('Validation Error', 400));
    }
  };
};
