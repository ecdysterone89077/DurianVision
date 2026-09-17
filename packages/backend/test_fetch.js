import fs from 'fs';

async function run() {
  const buf = fs.readFileSync('durian tes.png');
  const formData = new FormData();
  formData.append('file', new Blob([buf], { type: 'image/png' }), 'image.png');
  
  const res = await fetch('http://localhost:8001/predict', {
    method: 'POST',
    body: formData
  });
  
  console.log(res.status);
  const text = await res.text();
  console.log(text);
}

run();
