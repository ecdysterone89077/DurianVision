import fs from 'fs';
async function run() {
  try {
    const loginRes = await fetch('http://localhost:3005/api/auth/sign-in/email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Origin': 'http://localhost:5173' },
      body: JSON.stringify({ email: 'faunas@gmail.com', password: 'faunas123' })
    });
    const cookie = loginRes.headers.get('set-cookie');
    const modelsRes = await fetch('http://localhost:3005/api/models', { headers: { 'Cookie': cookie } });
    const models = (await modelsRes.json()).data;
    const bestModel = models.find(m => m.filename === 'best.pt');
    
    const imgData = new FormData();
    const imgBuffer = fs.readFileSync('D:\\GUI Duren\\duren ngetes.jpeg');
    imgData.append('file', new Blob([imgBuffer], { type: 'image/jpeg' }), 'duren ngetes.jpeg');
    imgData.append('config', JSON.stringify({ device: 'auto' }));
    
    const predictRes = await fetch('http://localhost:3005/api/models/' + bestModel.id + '/predict', {
      method: 'POST',
      headers: { 'Cookie': cookie, 'Origin': 'http://localhost:5173' },
      body: imgData
    });
    const result = await predictRes.json();
    console.log(JSON.stringify(result.data.detections, null, 2));
  } catch(e) { console.error(e) }
}; run();
