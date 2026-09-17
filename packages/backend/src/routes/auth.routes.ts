import { Router } from 'express';
import { expressAuthHandler } from '../auth/index.js';

const router = Router();

router.all('/*', (req, res, next) => {
  req.url = req.originalUrl;
  return expressAuthHandler(req, res);
});

export default router;
