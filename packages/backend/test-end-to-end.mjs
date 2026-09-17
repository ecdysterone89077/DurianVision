import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const IMAGE_PATH = path.join(ROOT, 'duren ngetes.jpeg');

async function run() {
  try {
    let loginRes = await fetch('http://localhost:3005/api/auth/sign-in/email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Origin': 'http://localhost:5173' },
      body: JSON.stringify({ email: 'faunas@gmail.com', password: 'faunas123' })
    });
    if (!loginRes.ok) {
      await fetch('http://localhost:3005/api/auth/sign-up/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Origin': 'http://localhost:5173' },
        body: JSON.stringify({ name: 'Faunas Test', email: 'faunas@gmail.com', password: 'faunas123' })
      });
      loginRes = await fetch('http://localhost:3005/api/auth/sign-in/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Origin': 'http://localhost:5173' },
        body: JSON.stringify({ email: 'faunas@gmail.com', password: 'faunas123' })
      });
    }
    const cookie = loginRes.headers.get('set-cookie');
    const modelsRes = await fetch('http://localhost:3005/api/models', { headers: { 'Cookie': cookie } });
    const models = (await modelsRes.json()).data;
    const bestModel = models.find(m => m.filename === 'best.pt');
    if (!bestModel) throw new Error('Model best.pt tidak ditemukan di DB — upload dulu atau jalankan test-all.mjs');
    
    const imgData = new FormData();
    const imgBuffer = fs.readFileSync(IMAGE_PATH);
    imgData.append('file', new Blob([imgBuffer], { type: 'image/jpeg' }), 'duren ngetes.jpeg');
    imgData.append('config', JSON.stringify({ device: 'auto' }));
    
    const predictRes = await fetch('http://localhost:3005/api/models/' + bestModel.id + '/predict', {
      method: 'POST',
      headers: { 'Cookie': cookie, 'Origin': 'http://localhost:5173' },
      body: imgData
    });
    const result = await predictRes.json();
    console.log(JSON.stringify(result.data.detections, null, 2));
  } catch(e) { console.error(e); process.exitCode = 1 }
}; run();
