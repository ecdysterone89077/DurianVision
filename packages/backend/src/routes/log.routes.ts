import { Router } from 'express';
import { getLogs, getStats, getDistribution, exportCSV, exportXLSX, clearLogs } from '../services/log.service.js';
import { success } from '../utils/api-response.js';
import { requireAuth } from '../middleware/auth.middleware.js';

const router = Router();

router.use(requireAuth);

router.get('/', async (req, res, next) => {
  try {
    const { sessionId, variety, minConfidence, limit, offset } = req.query;
    const data = await getLogs({
      sessionId: sessionId as string,
      variety: variety as string,
      minConfidence: minConfidence ? Number(minConfidence) : undefined,
      limit: limit ? Number(limit) : undefined,
      offset: offset ? Number(offset) : undefined
    });
    const responseData = Array.isArray(data) ? { data, meta: { total: data.length } } : data;
    if (Array.isArray(data)) {
      res.json({ success: true, data: data, meta: { total: data.length } });
    } else {
      res.json(success(data));
    }
  } catch (e) {
    next(e);
  }
});

router.get('/stats', async (req, res, next) => {
  try {
    const data = await getStats(req.query.sessionId as string);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.get('/distribution', async (req, res, next) => {
  try {
    const data = await getDistribution(req.query.sessionId as string);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.get('/export/csv', async (req, res, next) => {
  try {
    const buffer = await exportCSV(req.query);
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename=logs.csv');
    res.send(buffer);
  } catch (e) {
    next(e);
  }
});

router.get('/export/xlsx', async (req, res, next) => {
  try {
    const buffer = await exportXLSX(req.query);
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', 'attachment; filename=logs.xlsx');
    res.send(buffer);
  } catch (e) {
    next(e);
  }
});

router.delete('/', async (req, res, next) => {
  try {
    await clearLogs(req.query.sessionId as string);
    res.json(success(null, 'Logs cleared'));
  } catch (e) {
    next(e);
  }
});

export default router;
