import { Router } from 'express';
import authRoutes from './auth.routes.js';
import detectionRoutes from './detection.routes.js';
import logRoutes from './log.routes.js';
import snapshotRoutes from './snapshot.routes.js';
import modelRoutes from './model.routes.js';
import performanceRoutes from './performance.routes.js';
import varietyRoutes from './variety.routes.js';
import settingsRoutes from './settings.routes.js';

const router = Router();

router.use('/detection', detectionRoutes);
router.use('/logs', logRoutes);
router.use('/snapshots', snapshotRoutes);
router.use('/models', modelRoutes);
router.use('/performance', performanceRoutes);
router.use('/varieties', varietyRoutes);
router.use('/settings', settingsRoutes);

export default router;
