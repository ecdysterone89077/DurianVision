import { Router } from 'express';
import { getLogs, countLogs, getStats, getDistribution, exportCSV, exportXLSX, clearLogs } from '../services/log.service.js';
import { success } from '../utils/api-response.js';
import { requireAuth } from '../middleware/auth.middleware.js';

const router = Router();

router.use(requireAuth);

router.get('/', async (req, res, next) => {
  try {
    const { sessionId, variety, minConfidence, limit, offset, page } = req.query;
    const limitNum = limit ? Number(limit) : 50;
    const pageNum = page ? Math.max(1, Number(page)) : 1;
    const offsetNum = offset ? Number(offset) : (pageNum - 1) * limitNum;

    const filters = {
      sessionId: sessionId as string,
      variety: variety as string,
      minConfidence: minConfidence ? Number(minConfidence) : undefined
    };

    const [data, total] = await Promise.all([
      getLogs({ ...filters, limit: limitNum, offset: offsetNum }),
      countLogs(filters)
    ]);

    res.json({
      success: true,
      data,
      meta: { total, page: pageNum, limit: limitNum, totalPages: Math.max(1, Math.ceil(total / limitNum)) }
    });
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
