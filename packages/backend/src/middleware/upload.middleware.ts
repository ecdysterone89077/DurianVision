import multer from 'multer';
import fs from 'fs';
import path from 'path';

const storage = (dir: string) => multer.diskStorage({
  destination: (req, file, cb) => {
    const fullPath = path.join(process.cwd(), 'uploads', dir);
    if (!fs.existsSync(fullPath)) {
      fs.mkdirSync(fullPath, { recursive: true });
    }
    cb(null, fullPath);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + path.extname(file.originalname));
  }
});

const modelStorage = multer.diskStorage({
  destination: (req, file, cb) => {
    const fullPath = path.resolve(process.cwd(), '../inference/models');
    if (!fs.existsSync(fullPath)) {
      fs.mkdirSync(fullPath, { recursive: true });
    }
    cb(null, fullPath);
  },
  filename: (_req, file, cb) => {
    const timestamp = Date.now();
    const safeName = file.originalname.replace(/[^a-zA-Z0-9._-]/g, '_');
    cb(null, `${timestamp}_${safeName}`);
  }
});

export const modelUpload = multer({
  storage: modelStorage,
  limits: { fileSize: 500 * 1024 * 1024 }, // 500MB
  fileFilter: (req, file, cb) => {
    if (file.originalname.endsWith('.pt')) {
      cb(null, true);
    } else {
      cb(new Error('Only .pt files are allowed'));
    }
  }
});

export const imageUpload = multer({
  storage: storage('snapshots'),
  limits: { fileSize: 20 * 1024 * 1024 }, // 20MB
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only images are allowed'));
    }
  }
});
