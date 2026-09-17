import { Router } from 'express';
import { uploadModel, getModels, getModel, activateModel, deleteModel } from '../services/model.service.js';
import { predict, reloadModel } from '../services/inference.service.js';
import { modelUpload, imageUpload } from '../middleware/upload.middleware.js';
import { success } from '../utils/api-response.js';
import { requireAuth } from '../middleware/auth.middleware.js';
import fs from 'fs';

const router = Router();

router.use(requireAuth);

router.post('/upload', modelUpload.single('file'), async (req, res, next) => {
  try {
    if (!req.file) throw new Error('File required');
    const { name } = req.body;
    const data = await uploadModel(req.file, name);
    try {
      await reloadModel();
    } catch (err) {
      console.error('Failed to reload model in Python sidecar:', err);
    }
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.get('/', async (req, res, next) => {
  try {
    const data = await getModels();
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.get('/:id', async (req, res, next) => {
  try {
    const data = await getModel(req.params.id);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.patch('/:id/activate', async (req, res, next) => {
  try {
    const data = await activateModel(req.params.id);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.delete('/:id', async (req, res, next) => {
  try {
    await deleteModel(req.params.id);
    res.json(success(null, 'Model deleted'));
  } catch (e) {
    next(e);
  }
});

router.post('/:id/predict', imageUpload.single('file'), async (req, res, next) => {
  try {
    if (!req.file) throw new Error('File required');
    const buffer = fs.readFileSync(req.file.path);
    const { config } = req.body;
    const data = await predict(buffer, config ? JSON.parse(config) : undefined);
    res.json(success(data));
  } catch (e) {
    next(e);
  } finally {
    if (req.file) {
      try {
        fs.unlinkSync(req.file.path); // clean up
      } catch (err) {
        console.error('Failed to unlink file:', err);
      }
    }
  }
});

export default router;
