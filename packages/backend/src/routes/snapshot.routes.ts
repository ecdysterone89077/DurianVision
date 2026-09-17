import { Router } from 'express';
import { saveSnapshot, getSnapshots, getSnapshot, deleteSnapshot } from '../services/snapshot.service.js';
import { imageUpload } from '../middleware/upload.middleware.js';
import { success, error } from '../utils/api-response.js';
import { requireAuth } from '../middleware/auth.middleware.js';


const router = Router();

router.use(requireAuth);

router.post('/', imageUpload.single('file'), async (req, res, next) => {
  try {
    if (!req.file) throw new Error('File required');
    const { sessionId, detections, metadata } = req.body;
    const data = await saveSnapshot(req.file, sessionId, detections ? JSON.parse(detections) : undefined, metadata ? JSON.parse(metadata) : undefined);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.get('/', async (req, res, next) => {
  try {
    const { limit, offset } = req.query;
    const data = await getSnapshots(limit ? Number(limit) : undefined, offset ? Number(offset) : undefined);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.get('/:id', async (req, res, next) => {
  try {
    const data = await getSnapshot(req.params.id);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.get('/:id/download', async (req, res, next) => {
  try {
    const data = await getSnapshot(req.params.id);
    if (!data) return res.status(404).json(error('Not found', 404));
    res.download(data.filepath, data.filename, (err) => { if (err) next(err); });
  } catch (e) {
    next(e);
  }
});

router.delete('/:id', async (req, res, next) => {
  try {
    await deleteSnapshot(req.params.id);
    res.json(success(null, 'Snapshot deleted'));
  } catch (e) {
    next(e);
  }
});

export default router;
