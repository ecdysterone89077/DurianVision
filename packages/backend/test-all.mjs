import fs from 'fs';

async function run() {
  console.log('--- STARTING COMPREHENSIVE END-TO-END TEST ---');
  
  let cookie = '';
  let modelId = '';
  
  try {
    console.log('[1/8] Testing Authentication...');
    const loginRes = await fetch('http://localhost:3005/api/auth/sign-in/email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Origin': 'http://localhost:5173' },
      body: JSON.stringify({ email: 'faunas@gmail.com', password: 'faunas123' })
    });
    if (!loginRes.ok) throw new Error('Auth failed');
    cookie = loginRes.headers.get('set-cookie');
    console.log('  -> Auth SUCCESS');
    
    console.log('[2/8] Testing Settings...');
    const settingsRes = await fetch('http://localhost:3005/api/settings', { headers: { 'Cookie': cookie }});
    if (!settingsRes.ok) throw new Error('Settings GET failed');
    console.log('  -> Settings GET SUCCESS');
    
    const patchSettings = await fetch('http://localhost:3005/api/settings', {
      method: 'PATCH',
      headers: { 'Cookie': cookie, 'Content-Type': 'application/json' },
      body: JSON.stringify({ confidenceThreshold: 0.6 })
    });
    if (!patchSettings.ok) throw new Error('Settings PATCH failed: ' + await patchSettings.text());
    console.log('  -> Settings PATCH SUCCESS');
    
    console.log('[3/8] Testing Model Upload & Fetch...');
    const imgData = new FormData();
    const fileBuffer = fs.readFileSync('D:\\GUI Duren\\durian-yolov11-results\\weights\\best.pt');
    imgData.append('file', new Blob([fileBuffer]), 'best.pt');
    imgData.append('name', 'test_model');
    const uploadRes = await fetch('http://localhost:3005/api/models/upload', {
      method: 'POST', headers: { 'Cookie': cookie }, body: imgData
    });
    const uploadData = await uploadRes.json();
    if (!uploadRes.ok) throw new Error('Upload failed');
    modelId = uploadData.data.id;
    console.log('  -> Model Upload SUCCESS (' + modelId + ')');
    
    console.log('[4/8] Testing Model Activation...');
    const actRes = await fetch('http://localhost:3005/api/models/' + modelId + '/activate', {
      method: 'PATCH', headers: { 'Cookie': cookie }
    });
    if (!actRes.ok) throw new Error('Activation failed: ' + await actRes.text());
    console.log('  -> Model Activation SUCCESS');
    
    console.log('[5/8] Testing Inference Prediction...');
    const pData = new FormData();
    const pBuffer = fs.readFileSync('D:\\GUI Duren\\duren ngetes.jpeg');
    pData.append('file', new Blob([pBuffer], { type: 'image/jpeg' }), 'duren.jpeg');
    const predRes = await fetch('http://localhost:3005/api/models/' + modelId + '/predict', {
      method: 'POST', headers: { 'Cookie': cookie }, body: pData
    });
    if (!predRes.ok) throw new Error('Predict failed');
    console.log('  -> Prediction SUCCESS');
    
    console.log('[6/8] Testing Logs Retrieval...');
    const logsRes = await fetch('http://localhost:3005/api/logs?limit=5', { headers: { 'Cookie': cookie }});
    if (!logsRes.ok) throw new Error('Logs failed');
    console.log('  -> Logs GET SUCCESS');
    
    console.log('[7/8] Testing Log Stats & Distribution...');
    const statsRes = await fetch('http://localhost:3005/api/logs/stats', { headers: { 'Cookie': cookie }});
    if (!statsRes.ok) throw new Error('Stats failed');
    console.log('  -> Stats GET SUCCESS');
    
    console.log('[8/8] Testing Log Exports (CSV)...');
    const csvRes = await fetch('http://localhost:3005/api/logs/export/csv', { headers: { 'Cookie': cookie }});
    if (!csvRes.ok) throw new Error('CSV Export failed');
    console.log('  -> CSV Export SUCCESS (Status ' + csvRes.status + ')');
    
    console.log('--- ALL TESTS PASSED SUCCESSFULLY! ---');
    
  } catch (err) {
    console.error('TEST FAILED:', err);
  }
}
run();
