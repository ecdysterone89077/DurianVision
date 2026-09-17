import { Server as SocketIOServer } from 'socket.io';
import { Server as HttpServer } from 'http';
import { logger } from '../utils/logger.js';
import { predict, predictBase64 } from '../services/inference.service.js';
import { addBatchLogs } from '../services/log.service.js';

let io: SocketIOServer;

export const setupSocket = (httpServer: HttpServer) => {
  io = new SocketIOServer(httpServer, {
    cors: {
      origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
      methods: ['GET', 'POST'],
      credentials: true
    }
  });

  const detectionNamespace = io.of('/detection');

  detectionNamespace.on('connection', (socket) => {
    logger.info(`Socket connected: ${socket.id}`);

    socket.on('join-session', (sessionId: string) => {
      socket.join(`session_${sessionId}`);
      logger.info(`Socket ${socket.id} joined session_${sessionId}`);
    });

    socket.on('leave-session', (sessionId: string) => {
      socket.leave(`session_${sessionId}`);
      logger.info(`Socket ${socket.id} left session_${sessionId}`);
    });

    socket.on('start-detection', (data) => {
      logger.info(`Starting detection...`, data);
      // Logic could go here or simply emit status
      detectionNamespace.to(`session_${data.sessionId}`).emit('session-status', { status: 'running' });
    });

    socket.on('stop-detection', (data) => {
      logger.info(`Stopping detection...`, data);
      detectionNamespace.to(`session_${data.sessionId}`).emit('session-status', { status: 'stopped' });
    });

    socket.on('update-config', (config) => {
      logger.info(`Updating config...`, config);
      detectionNamespace.to(`session_${config.sessionId}`).emit('config-updated', config);
    });

    // --- BATCH FLUSH OPTIMIZATION ---
    let logBuffer: any[] = [];
    let flushTimeout: NodeJS.Timeout | null = null;

    const flushLogs = async () => {
      if (logBuffer.length === 0) return;
      const toFlush = [...logBuffer];
      logBuffer = [];
      try {
        await addBatchLogs(toFlush);
        // logger.debug(`Flushed ${toFlush.length} logs to DB`);
      } catch (err) {
        logger.warn('Failed to bulk persist detection logs: %s', String(err));
      }
    };

    // --- DOS PROTECTION: RATE LIMITER ---
    const lastFrameMap = new Map<string, number>();

    socket.on('process-frame', async (data) => {
      // SECURITY: Throttle to max ~33 FPS (30ms per frame) to protect FastAPI
      const now = Date.now();
      const lastTime = lastFrameMap.get(socket.id) || 0;
      if (now - lastTime < 30) {
        return; // Drop frame silently to save CPU
      }
      lastFrameMap.set(socket.id, now);

      // data: { image: Buffer | string, sessionId: string, config?: any }
      try {
        let result;
        if (Buffer.isBuffer(data.image) || data.image instanceof Uint8Array || data.image instanceof ArrayBuffer) {
          result = await predict(Buffer.from(data.image), data.config);
        } else {
          result = await predictBase64(data.image, data.config);
        }
        
        // Emit result back to the specific session room
        io.of('/detection').to(`session_${data.sessionId}`).emit('detection-result', {
          detections: result.detections,
          inferenceTimeMs: result.inference_time_ms,
        });

        // Buffer detections to database (Ring Buffer Optimization)
        if (data.sessionId && result.detections && result.detections.length > 0) {
          const logEntries = result.detections.map((d: any) => ({
            sessionId: data.sessionId,
            variety: d.class_name,
            confidence: d.confidence,
            bboxX: Math.round(d.bbox.x1),
            bboxY: Math.round(d.bbox.y1),
            bboxW: Math.round(d.bbox.w),
            bboxH: Math.round(d.bbox.h),
            inferenceTimeMs: result.inference_time_ms,
          }));
          
          logBuffer.push(...logEntries);

          // Flush if threshold reached
          if (logBuffer.length >= 50) {
            if (flushTimeout) clearTimeout(flushTimeout);
            flushLogs();
          } else if (!flushTimeout) {
            flushTimeout = setTimeout(() => {
              flushTimeout = null;
              flushLogs();
            }, 2000); // 2 seconds fallback flush
          }
        }
      } catch (err) {
        logger.error('Frame processing error: %s', String(err));
      }
    });

    socket.on('disconnect', () => {
      logger.info(`Socket disconnected: ${socket.id}`);
      lastFrameMap.delete(socket.id);
    });
  });

  return io;
};

export const getIO = () => {
  if (!io) {
    throw new Error('Socket.io not initialized');
  }
  return io;
};
