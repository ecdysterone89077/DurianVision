import { createServer } from 'http';
import { app } from './app.js';
import { setupSocket } from './socket/index.js';
import { logger } from './utils/logger.js';

const PORT = process.env.PORT || 3005;

const startServer = () => {
  const httpServer = createServer(app);
  
  setupSocket(httpServer);

  httpServer.listen(PORT, () => {
    logger.info(`Server is running on port ${PORT}`);
  });
};

startServer();
