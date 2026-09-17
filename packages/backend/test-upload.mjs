import fs from 'fs';

async function run() {
  try {
    const loginRes = await fetch('http://localhost:3005/api/auth/sign-in/email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Origin': 'http://localhost:5173' },
      body: JSON.stringify({ email: 'faunas@gmail.com', password: 'faunas123' })
    });
    
    if (!loginRes.ok) throw new Error('Login failed: ' + await loginRes.text());
    const loginData = await loginRes.json();
    const token = loginData.token;
    console.log('Token:', token);
    
    const formData = new FormData();
    const fileBuffer = fs.readFileSync('D:\\GUI Duren\\durian-yolov11-results\\weights\\best.pt');
    const blob = new Blob([fileBuffer]);
    formData.append('file', blob, 'best.pt');
    formData.append('name', 'best');
    
    const uploadRes = await fetch('http://localhost:3005/api/models/upload', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Origin': 'http://localhost:5173'
      },
      body: formData
    });
    
    if (!uploadRes.ok) throw new Error('Upload failed: ' + await uploadRes.text());
    const uploadData = await uploadRes.json();
    console.log('Upload success:', uploadData);
    
    const modelId = uploadData.data.id;
    const activateRes = await fetch('http://localhost:3005/api/models/' + modelId + '/activate', {
      method: 'PATCH',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Origin': 'http://localhost:5173'
      }
    });
    if (!activateRes.ok) throw new Error('Activate failed: ' + await activateRes.text());
    console.log('Activate success:', await activateRes.json());
  } catch (err) {
    console.error(err);
  }
}
run();
